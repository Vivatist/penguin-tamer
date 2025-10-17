"""
OpenAI Client - Реализация клиента для OpenAI API.

Поддерживает потоковые ответы, получение списка моделей и статистику использования.
Пока является копией OpenRouterClient, в будущем будут добавлены специфичные для OpenAI особенности.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.llm_clients.stream_processor import StreamProcessor
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


@dataclass
class OpenAIClient(AbstractLLMClient):
    """OpenAI-specific implementation of LLM client.
    
    Uses OpenAI API directly without OpenRouter-specific headers.
    Supports streaming responses, model listing, and usage statistics.
    
    This class contains ONLY OpenAI API-specific logic:
    - Request parameter preparation
    - Stream creation
    - Response parsing (chunks, usage, rate limits)
    """

    # OpenAI-specific state
    _client: Optional[object] = field(default=None, init=False)

    # === API-specific methods (формирование запросов и парсинг ответов) ===

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
            # OpenAI API не требует специальных заголовков
            self._client = get_openai_client()(
                api_key=self.api_key,
                base_url=self.api_url
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

    def _create_stream(self, api_params: dict):
        """Create API stream object (OpenAI-specific).
        
        Args:
            api_params: API parameters prepared by _prepare_api_params()
            
        Returns:
            Stream object from OpenAI SDK
        """
        return self.client.chat.completions.create(**api_params)

    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Extract text content from stream chunk (OpenAI-specific).
        
        Args:
            chunk: Stream chunk from API
            
        Returns:
            Text content or None if chunk has no content
        """
        try:
            if not hasattr(chunk, 'choices') or not chunk.choices:
                return None
            if not hasattr(chunk.choices[0], 'delta'):
                return None
            
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content') and delta.content:
                return delta.content
        except (AttributeError, IndexError):
            return None
        return None

    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Extract usage statistics from chunk (OpenAI-specific).
        
        Args:
            chunk: Stream chunk from API
            
        Returns:
            Dict with 'prompt_tokens' and 'completion_tokens', or None
        """
        try:
            if hasattr(chunk, 'usage') and chunk.usage:
                return {
                    'prompt_tokens': getattr(chunk.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(chunk.usage, 'completion_tokens', 0)
                }
        except (AttributeError, IndexError):
            return None
        return None

    def _extract_rate_limits(self, stream) -> None:
        """Extract rate limit information from OpenAI API response.
        
        OpenAI uses standard x-ratelimit-* headers in their responses.
        Extracts both request and token-based rate limits.
        
        Args:
            stream: OpenAI API response stream object
        """
        try:
            # Try common paths to get headers
            headers = None
            if hasattr(stream, 'response') and hasattr(stream.response, 'headers'):
                headers = stream.response.headers
            elif hasattr(stream, '_response') and hasattr(stream._response, 'headers'):
                headers = stream._response.headers
            elif hasattr(stream, 'headers'):
                headers = stream.headers
            
            if headers:
                # OpenAI standard headers
                if 'x-ratelimit-limit-requests' in headers:
                    self.rate_limit_requests = int(headers['x-ratelimit-limit-requests'])
                if 'x-ratelimit-limit-tokens' in headers:
                    self.rate_limit_tokens = int(headers['x-ratelimit-limit-tokens'])
                if 'x-ratelimit-remaining-requests' in headers:
                    self.rate_limit_remaining_requests = int(headers['x-ratelimit-remaining-requests'])
                if 'x-ratelimit-remaining-tokens' in headers:
                    self.rate_limit_remaining_tokens = int(headers['x-ratelimit-remaining-tokens'])
        except (AttributeError, ValueError, KeyError):
            # Silently ignore if headers are not accessible
            pass

    @staticmethod
    def fetch_models(api_list_url: str, api_key: str = "", model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Fetch list of available models from OpenAI API.
        
        OpenAI requires API key for authentication.
        Returns models in format: {"data": [{"id": "...", "name": "..."}]}
        
        Args:
            api_list_url: OpenAI models endpoint (e.g., "https://api.openai.com/v1/models")
            api_key: API key for authentication (required for OpenAI)
            model_filter: Filter string to match against model id/name (case-insensitive, optional)
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Display Name"}, ...]
            Returns empty list on error.
        
        Example:
            >>> models = OpenAIClient.fetch_models(
            ...     "https://api.openai.com/v1/models",
            ...     api_key="sk-..."
            ... )
            >>> print(models[0])
            {'id': 'gpt-4', 'name': 'gpt-4'}
        """
        try:
            requests = get_requests_module()
            
            # OpenAI требует API ключ
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(api_list_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # OpenAI формат: {"data": [{"id": "...", ...}]}
            models = []
            if "data" in data and isinstance(data["data"], list):
                for model in data["data"]:
                    if isinstance(model, dict) and "id" in model:
                        model_id = model["id"]
                        # OpenAI обычно не предоставляет отдельное поле name
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


