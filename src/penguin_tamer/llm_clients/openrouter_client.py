"""
OpenRouter Client - Реализация клиента для OpenRouter API.

Поддерживает потоковые ответы, получение списка моделей и статистику использования.
"""

import threading
from typing import List, Dict, Optional
import time
from dataclasses import dataclass, field
from contextlib import contextmanager

from rich.markdown import Markdown
from rich.live import Live

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.i18n import t
from penguin_tamer.config_manager import config
from penguin_tamer.themes import get_code_theme
from penguin_tamer.debug import debug_print_messages
from penguin_tamer.error_handlers import ErrorHandler, ErrorContext, ErrorSeverity
from penguin_tamer.utils.lazy_import import lazy_import

# Ленивый импорт requests для работы с API
@lazy_import
def get_requests_module():
    """Ленивый импорт requests для API запросов"""
    import requests
    return requests


# Ленивый импорт OpenAI клиента
@lazy_import
def get_openai_client():
    """Ленивый импорт OpenAI клиента для быстрого запуска --version, --help"""
    from openai import OpenAI
    return OpenAI


def _create_markdown(text: str, theme_name: str = "default"):
    """
    Создаёт Markdown объект с правильной темой для блоков кода.

    Args:
        text: Текст в формате Markdown
        theme_name: Название темы

    Returns:
        Markdown объект с применённой темой
    """
    code_theme = get_code_theme(theme_name)
    return Markdown(text, code_theme=code_theme)


class StreamProcessor:
    """Processor for handling streaming LLM responses.

    Encapsulates the logic of processing streaming responses from LLM API,
    including error handling, chunk processing, and live display management.
    """

    def __init__(self, client: 'OpenRouterClient'):
        """Initialize stream processor.

        Args:
            client: Parent OpenRouterClient instance
        """
        self.client = client
        self.interrupted = threading.Event()
        self.reply_parts: List[str] = []
        self.user_input: str = ""  # Store user input to add to context only on success

    def process(self, user_input: str) -> str:
        """Process user input and return AI response.

        Args:
            user_input: User's message text

        Returns:
            Complete AI response text
        """
        # Store user input to add to context only if request succeeds
        self.user_input = user_input

        # Create error handler
        debug_mode = config.get("global", "debug", False)
        error_handler = ErrorHandler(console=self.client.console, debug_mode=debug_mode)

        # Phase 1: Connect and wait for first chunk
        stream, first_chunk = self._connect_and_wait(error_handler)
        if stream is None:
            # Error occurred - don't add user message to context
            return ""

        # Phase 2: Process stream with live display
        try:
            reply = self._stream_with_live_display(stream, first_chunk)
        except KeyboardInterrupt:
            self.interrupted.set()
            # Interrupted - don't add to context
            raise

        # Phase 3: Finalize (will add user message to context if successful)
        return self._finalize_response(reply)

    @contextmanager
    def _managed_spinner(self, initial_message: str):
        """Context manager для управления спиннером."""
        stop_spinner = threading.Event()
        status_message = {'text': initial_message}
        spinner_thread = threading.Thread(
            target=self.client._spinner,
            args=(stop_spinner, status_message),
            daemon=True
        )
        spinner_thread.start()

        try:
            yield status_message
        finally:
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)

    def _connect_and_wait(self, error_handler: ErrorHandler) -> tuple:
        """Connect to API and wait for first chunk.

        Returns:
            Tuple of (stream, first_chunk) or (None, None) on error
        """
        with self._managed_spinner(t('Connecting...')) as status_message:
            try:
                # Send API request with user input (but don't add to permanent context yet)
                api_params = self.client._prepare_api_params(self.user_input)
                stream = self.client.client.chat.completions.create(**api_params)

                # Try to extract rate limit info from stream (if available)
                self.client._extract_rate_limits(stream)

                # Wait for first chunk
                status_message['text'] = t('Ai thinking...')
                first_chunk = self._wait_first_chunk(stream)

                if first_chunk:
                    self.reply_parts.append(first_chunk)

                return stream, first_chunk

            except KeyboardInterrupt:
                self.interrupted.set()
                raise
            except Exception as e:
                self.interrupted.set()
                context = ErrorContext(
                    operation="streaming API request",
                    severity=ErrorSeverity.ERROR,
                    recoverable=True
                )
                error_message = error_handler.handle(e, context)
                self.client.console.print(error_message)
                return None, None

    def _wait_first_chunk(self, stream) -> Optional[str]:
        """Ожидание первого чанка с контентом."""
        try:
            for chunk in stream:
                if self.interrupted.is_set():
                    raise KeyboardInterrupt("Stream interrupted")

                if not hasattr(chunk, 'choices') or not chunk.choices:
                    continue
                if not hasattr(chunk.choices[0], 'delta'):
                    continue

                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    return delta.content
        except (AttributeError, IndexError):
            return None
        return None

    def _stream_with_live_display(self, stream, first_chunk: str) -> str:
        """Process stream with live markdown display.

        Args:
            stream: API response stream
            first_chunk: First chunk of content

        Returns:
            Complete response text
        """
        sleep_time = config.get("global", "sleep_time", 0.01)
        refresh_per_second = config.get("global", "refresh_per_second", 10)
        theme_name = config.get("global", "markdown_theme", "default")

        with Live(
            console=self.client.console,
            refresh_per_second=refresh_per_second,
            auto_refresh=True
        ) as live:
            # Show first chunk
            if first_chunk:
                markdown = _create_markdown(first_chunk, theme_name)
                live.update(markdown)
                # Record first chunk for demo
                if self.client._demo_manager:
                    self.client._demo_manager.record_llm_chunk(first_chunk)

            # Process remaining chunks
            try:
                for chunk in stream:
                    if self.interrupted.is_set():
                        raise KeyboardInterrupt("Stream interrupted")

                    if not hasattr(chunk, 'choices') or not chunk.choices:
                        # Check for usage statistics in non-content chunks
                        if hasattr(chunk, 'usage') and chunk.usage:
                            prompt_tokens = getattr(chunk.usage, 'prompt_tokens', 0)
                            completion_tokens = getattr(chunk.usage, 'completion_tokens', 0)
                            self.client.total_prompt_tokens += prompt_tokens
                            self.client.total_completion_tokens += completion_tokens
                            self.client.total_requests += 1
                        continue
                    if not hasattr(chunk.choices[0], 'delta'):
                        continue

                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        self.reply_parts.append(text)
                        # Record chunk for demo
                        if self.client._demo_manager:
                            self.client._demo_manager.record_llm_chunk(text)
                        full_text = "".join(self.reply_parts)
                        markdown = _create_markdown(full_text, theme_name)
                        live.update(markdown)
                        time.sleep(sleep_time)
            except (AttributeError, IndexError):
                pass

        return "".join(self.reply_parts)

    def _finalize_response(self, reply: str) -> str:
        """Finalize response and update messages.

        Args:
            reply: Complete response text

        Returns:
            Final response text
        """
        # Check for empty response
        if not reply or not reply.strip():
            warning = t('Warning: Empty response received from API.')
            self.client.console.print(f"[dim italic]{warning}[/dim italic]")
            # Empty response is an error - don't add to context
            return ""

        # Success! Add both user message and assistant response to context
        self.client.messages.append({"role": "user", "content": self.user_input})
        self.client.messages.append({"role": "assistant", "content": reply})

        # Debug output if enabled
        self.client._debug_print_if_enabled("response")

        return reply


@dataclass
class OpenRouterClient(AbstractLLMClient):
    """OpenRouter-specific implementation of LLM client.
    
    Uses OpenAI-compatible API with OpenRouter-specific headers and features.
    Supports streaming responses, model listing, and usage statistics.
    """

    # OpenRouter-specific state
    _client: Optional[object] = field(default=None, init=False)

    def _prepare_api_params(self, user_input: Optional[str] = None) -> dict:
        """Подготовка параметров для API запроса.

        Args:
            user_input: Optional user input to include in request (not added to permanent context)

        Returns:
            dict: Параметры для chat.completions.create()
        """
        # Build messages list for this request
        messages = self.messages.copy()
        if user_input:
            messages.append({"role": "user", "content": user_input})
        
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": True,
            "stream_options": {"include_usage": True}  # Request usage data in streaming mode
        }

        # Добавляем опциональные параметры только если они заданы
        if self.max_tokens is not None:
            api_params["max_tokens"] = self.max_tokens
        if self.top_p is not None and self.top_p != 1.0:
            api_params["top_p"] = self.top_p
        if self.frequency_penalty != 0.0:
            api_params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty != 0.0:
            api_params["presence_penalty"] = self.presence_penalty
        if self.stop is not None:
            api_params["stop"] = self.stop
        if self.seed is not None:
            api_params["seed"] = self.seed

        return api_params

    @property
    def client(self):
        """Ленивая инициализация OpenAI клиента"""
        if self._client is None:
            # Добавляем заголовки для OpenRouter
            default_headers = {}
            if "openrouter.ai" in self.api_url.lower():
                default_headers = {
                    "HTTP-Referer": "https://github.com/Vivatist/penguin-tamer",
                    "X-Title": "Penguin Tamer"
                }

            self._client = get_openai_client()(
                api_key=self.api_key,
                base_url=self.api_url,
                default_headers=default_headers
            )
        return self._client

    def ask_stream(self, user_input: str) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени.

        Args:
            user_input: User's message text

        Returns:
            Complete AI response text

        Raises:
            KeyboardInterrupt: При прерывании пользователем
        """
        processor = StreamProcessor(self)
        return processor.process(user_input)

    @staticmethod
    def fetch_models(api_list_url: str, api_key: str = "", model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Fetch list of available models from OpenRouter API.
        
        OpenRouter allows anonymous access - API key is optional.
        Returns models in format: {"data": [{"id": "...", "name": "..."}]}
        
        Args:
            api_list_url: OpenRouter models endpoint (e.g., "https://openrouter.ai/api/v1/models")
            api_key: API key (optional, OpenRouter works without it)
            model_filter: Filter string to match against model id/name (case-insensitive, optional)
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Display Name"}, ...]
            Returns empty list on error.
        
        Example:
            >>> models = OpenRouterClient.fetch_models("https://openrouter.ai/api/v1/models")
            >>> print(models[0])
            {'id': 'openai/gpt-4', 'name': 'GPT-4'}
        """
        try:
            requests = get_requests_module()
            
            # OpenRouter не требует API ключ для получения списка моделей
            response = requests.get(api_list_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # OpenRouter формат: {"data": [{"id": "...", "name": "..."}]}
            models = []
            if "data" in data and isinstance(data["data"], list):
                for model in data["data"]:
                    if isinstance(model, dict) and "id" in model:
                        model_id = model["id"]
                        model_name = model.get("name", model_id)
                        models.append({"id": model_id, "name": model_name})
            
            # Применяем фильтр если указан
            if model_filter:
                filter_lower = model_filter.lower()
                models = [
                    model for model in models
                    if filter_lower in model["id"].lower() or filter_lower in model["name"].lower()
                ]
            
            return models
        
        except Exception:
            # Возвращаем пустой список при любых ошибках
            return []

    def get_available_models(self, model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get list of available models for current client configuration.
        
        Instance method that uses client's api_url with "/models" endpoint
        and client's api_key for authentication.
        
        Args:
            model_filter: Optional filter string to match against model id/name
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Name"}, ...]
            Returns empty list on error.
        
        Example:
            >>> client = OpenRouterClient(...)
            >>> models = client.get_available_models(model_filter="gpt")
        """
        # Определяем URL для получения списка моделей
        # Обычно это base_url + "/models"
        base_url = self.api_url.rstrip('/')
        
        # Если URL уже содержит "/chat/completions" или другой endpoint, убираем его
        if '/chat/completions' in base_url:
            base_url = base_url.split('/chat/completions')[0]
        
        api_list_url = f"{base_url}/models"
        
        # Используем статический метод для получения моделей
        return self.fetch_models(api_list_url, self.api_key, model_filter)


