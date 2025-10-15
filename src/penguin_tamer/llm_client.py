import threading
from typing import List, Dict, Optional
import time
from dataclasses import dataclass, field
from contextlib import contextmanager

from rich.markdown import Markdown
from rich.live import Live

from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t
from penguin_tamer.config_manager import config
from penguin_tamer.themes import get_code_theme
from penguin_tamer.debug import debug_print_messages
from penguin_tamer.error_handlers import ErrorHandler, ErrorContext, ErrorSeverity
from penguin_tamer.utils.lazy_import import lazy_import


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

    def process(self, user_input: str) -> str:
        """Process user input and return AI response.

        Args:
            user_input: User's message text

        Returns:
            Complete AI response text
        """
        self.client.messages.append({"role": "user", "content": user_input})

        # Create error handler
        debug_mode = config.get("global", "debug", False)
        error_handler = ErrorHandler(console=self.client.console, debug_mode=debug_mode)

        # Phase 1: Connect and wait for first chunk
        stream, first_chunk = self._connect_and_wait(error_handler)
        if stream is None:
            return ""

        # Phase 2: Process stream with live display
        try:
            reply = self._stream_with_live_display(stream, first_chunk)
        except KeyboardInterrupt:
            self.interrupted.set()
            raise

        # Phase 3: Finalize
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
                # Send API request
                api_params = self.client._prepare_api_params()
                stream = self.client.client.chat.completions.create(**api_params)

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
            return ""

        # Add to message history
        self.client.messages.append({"role": "assistant", "content": reply})

        # Debug output if enabled
        self.client._debug_print_if_enabled("response")

        return reply


@dataclass
class LLMConfig:
    """Complete LLM configuration including connection and generation parameters."""
    # Connection parameters
    api_key: str
    api_url: str
    model: str

    # Generation parameters
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    seed: Optional[int] = None


@dataclass
class OpenRouterClient:
    """OpenAI-compatible streaming LLM client with Rich UI integration."""

    # Core parameters
    console: object
    system_message: List[Dict[str, str]]
    llm_config: LLMConfig

    # Internal state (not part of constructor)
    messages: List[Dict[str, str]] = field(init=False)
    _client: Optional[object] = field(default=None, init=False)
    _demo_manager: Optional[object] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize internal state after dataclass construction."""
        self.messages = self.system_message.copy()

    def set_demo_manager(self, demo_manager):
        """Set demo manager for recording LLM chunks.

        Args:
            demo_manager: Demo manager instance
        """
        self._demo_manager = demo_manager

    def init_dialog_mode(self, educational_prompt: List[Dict[str, str]]) -> None:
        """Initialize dialog mode by adding educational prompt to messages.

        Should be called once at the start of dialog mode to teach the model
        to number code blocks automatically.

        Args:
            educational_prompt: Educational messages to add
        """
        self.messages.extend(educational_prompt)

    @classmethod
    def create(cls, console, api_key: str, api_url: str, model: str,
               system_message: List[Dict[str, str]], **llm_params):
        """Factory method for backward compatibility with old constructor signature."""
        llm_config = LLMConfig(
            api_key=api_key,
            api_url=api_url,
            model=model,
            **llm_params
        )
        return cls(
            console=console,
            system_message=system_message,
            llm_config=llm_config
        )

    # Properties for easy access to all LLM parameters
    @property
    def api_key(self) -> str:
        return self.llm_config.api_key

    @property
    def api_url(self) -> str:
        return self.llm_config.api_url

    @property
    def model(self) -> str:
        return self.llm_config.model

    @property
    def temperature(self) -> float:
        return self.llm_config.temperature

    @property
    def max_tokens(self) -> Optional[int]:
        return self.llm_config.max_tokens

    @property
    def top_p(self) -> float:
        return self.llm_config.top_p

    @property
    def frequency_penalty(self) -> float:
        return self.llm_config.frequency_penalty

    @property
    def presence_penalty(self) -> float:
        return self.llm_config.presence_penalty

    @property
    def stop(self) -> Optional[List[str]]:
        return self.llm_config.stop

    @property
    def seed(self) -> Optional[int]:
        return self.llm_config.seed

    def _spinner(self, stop_spinner: threading.Event, status_message: dict) -> None:
        """Визуальный индикатор работы ИИ с динамическим статусом.
        status_message - словарь с ключом 'text' для обновления сообщения.
        """
        try:
            with self.console.status(
                "[dim]" + status_message.get('text', t('Ai thinking...')) + "[/dim]",
                spinner="dots",
                spinner_style="dim"
            ) as status:
                while not stop_spinner.is_set():
                    # Обновляем статус, если он изменился
                    current_text = status_message.get('text', t('Ai thinking...'))
                    status.update(f"[dim]{current_text}[/dim]")
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def _prepare_api_params(self) -> dict:
        """Подготовка параметров для API запроса.

        Returns:
            dict: Параметры для chat.completions.create()
        """
        api_params = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "stream": True
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

    def _debug_print_if_enabled(self, phase: str) -> None:
        """Печать debug информации если режим отладки включён.

        Args:
            phase: 'request' или 'response'
        """
        if config.get("global", "debug", False):
            debug_print_messages(
                self.messages,
                client=self,
                phase=phase
            )

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

    def __str__(self) -> str:
        """Человекочитаемое представление клиента со всеми полями.

        Примечание: значение `api_key` маскируется (видны только последние 4 символа),
        а сложные объекты выводятся кратко.
        """

        items = {}
        for k, v in self.__dict__.items():
            if k == 'messages' or k == 'console' or k == '_client':
                continue
            elif k == 'llm_config':
                # Создаем копию LLMConfig с замаскированным api_key
                config_dict = {
                    'api_key': format_api_key_display(v.api_key),
                    'api_url': v.api_url,
                    'model': v.model,
                    'temperature': v.temperature,
                    'max_tokens': v.max_tokens,
                    'top_p': v.top_p,
                    'frequency_penalty': v.frequency_penalty,
                    'presence_penalty': v.presence_penalty,
                    'stop': v.stop,
                    'seed': v.seed
                }
                config_repr = ', '.join(f'{key}={val!r}' for key, val in config_dict.items())
                items[k] = f"LLMConfig({config_repr})"
            else:
                try:
                    items[k] = v
                except Exception:
                    items[k] = f"<unrepr {type(v).__name__}>"

        parts = [f"{self.__class__.__name__}("]
        for key, val in items.items():
            parts.append(f"  {key}={val!r},")
        parts.append(")")
        return "\n".join(parts)
