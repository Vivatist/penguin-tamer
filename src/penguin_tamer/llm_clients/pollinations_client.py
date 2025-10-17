"""
Pollinations Client - Реализация клиента для Pollinations API.

Использует OpenAI-совместимый endpoint с SSE streaming:
POST https://text.pollinations.ai/openai
API documentation: https://pollinations.ai/
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.utils.lazy_import import lazy_import

# Ленивый импорт requests для работы с API
@lazy_import
def get_requests_module():
    """Ленивый импорт requests для API запросов"""
    import requests
    return requests

# Ленивый импорт sseclient для SSE streaming
@lazy_import
def get_sseclient_module():
    """Ленивый импорт sseclient для SSE streaming"""
    import sseclient
    return sseclient


@dataclass
class PollinationsClient(AbstractLLMClient):
    """Pollinations-specific implementation of LLM client.
    
    Uses OpenAI-compatible endpoint with SSE streaming:
    POST https://text.pollinations.ai/openai
    No API key required - free and open access.
    
    This class contains ONLY Pollinations API-specific logic:
    - Request parameter preparation (OpenAI format)
    - SSE streaming support
    - Response parsing
    """

    # === API-specific methods (формирование запросов и парсинг ответов) ===

    def _prepare_api_params(self, user_input: str) -> dict:
        """Подготовка параметров для Pollinations API запроса.
        
        Pollinations использует OpenAI-совместимый формат:
        POST https://text.pollinations.ai/openai
        
        Args:
            user_input: Пользовательский ввод
            
        Returns:
            dict: Параметры для передачи в OpenAI-совместимый endpoint
        """
        # Формируем список сообщений включая текущий запрос
        # НЕ добавляем в self.messages - это сделает StreamProcessor
        messages = self.messages + [{"role": "user", "content": user_input}] if user_input else self.messages

        # Pollinations использует OpenAI-совместимый формат
        api_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        # Добавляем seed если указан
        if self.seed is not None:
            api_params["seed"] = self.seed

        # Добавляем опциональные параметры если заданы
        if self.temperature and self.temperature != 1.0:
            api_params["temperature"] = self.temperature

        if self.max_tokens and self.max_tokens > 0:
            api_params["max_tokens"] = self.max_tokens

        if self.top_p and self.top_p != 1.0:
            api_params["top_p"] = self.top_p

        return api_params

    def _create_stream(self, api_params: dict):
        """Создание SSE потока для Pollinations API.
        
        Pollinations поддерживает OpenAI-совместимый streaming через SSE.
        
        Args:
            api_params: Параметры запроса (OpenAI format)
            
        Returns:
            Итератор SSE событий для потоковой обработки
        """
        requests = get_requests_module()
        sseclient = get_sseclient_module()
        
        # OpenAI-compatible endpoint для Pollinations
        url = "https://text.pollinations.ai/openai"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        try:
            response = requests.post(url, headers=headers, json=api_params, stream=True, timeout=30)
            response.raise_for_status()
            client = sseclient.SSEClient(response)
            return client.events()
        except Exception as e:
            raise RuntimeError(f"Pollinations API error: {e}")

    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Извлечение текстового контента из SSE event.
        
        Pollinations использует OpenAI-совместимый формат:
        {"choices": [{"delta": {"content": "..."}}]}
        
        Args:
            chunk: SSE event от Pollinations
            
        Returns:
            str или None: Текст из чанка или None если пусто/завершено
        """
        # chunk это SSE event
        if not hasattr(chunk, 'data'):
            return None
            
        data = chunk.data.strip()
        
        # Проверяем маркер завершения
        if data == '[DONE]':
            return None
            
        try:
            parsed = json.loads(data)
            content = parsed.get('choices', [{}])[0].get('delta', {}).get('content')
            return content
        except (json.JSONDecodeError, IndexError, KeyError):
            return None

    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Извлечение статистики использования токенов из SSE event.
        
        Pollinations может предоставлять usage в последнем чанке.
        
        Args:
            chunk: SSE event от Pollinations
            
        Returns:
            dict или None: {'prompt_tokens': int, 'completion_tokens': int} или None
        """
        if not hasattr(chunk, 'data'):
            return None
            
        data = chunk.data.strip()
        
        if data == '[DONE]':
            return None
            
        try:
            parsed = json.loads(data)
            usage = parsed.get('usage')
            if usage:
                return {
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0)
                }
        except (json.JSONDecodeError, KeyError):
            pass
        
        return None

    def _extract_rate_limits(self, stream) -> dict:
        """Извлечение rate limits из ответа.
        
        Pollinations не предоставляет rate limit информацию,
        т.к. это бесплатный сервис без ограничений.
        
        Args:
            stream: SSEClient stream
            
        Returns:
            Пустой dict
        """
        # Pollinations не возвращает rate limits
        return {}

    # === Основной метод потоковой генерации ===

    def ask_stream(self, user_input: str) -> str:
        """Основной метод для потоковой генерации с Pollinations.
        
        Делегирует UI/orchestration StreamProcessor,
        отвечает только за подготовку параметров.
        
        Args:
            user_input: Запрос пользователя
            
        Returns:
            str: Полный ответ от LLM
        """
        from penguin_tamer.llm_clients.stream_processor import StreamProcessor
        
        processor = StreamProcessor(self)
        return processor.process(user_input)

    # === Методы работы со списком моделей ===

    @staticmethod
    def fetch_models(
        api_list_url: str,
        api_key: str = "",
        model_filter: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Получение списка доступных моделей от Pollinations API.
        
        Фильтрует только модели с tier="anonymous" для бесплатного доступа.
        
        Args:
            api_list_url: URL для получения списка моделей (игнорируется, используется стандартный endpoint)
            api_key: API ключ (не требуется для Pollinations)
            model_filter: Фильтр для моделей (опционально)
            
        Returns:
            List[Dict]: Список моделей в формате [{"id": "model-name", "name": "Model Name"}, ...]
        """
        requests = get_requests_module()
        
        # Pollinations models endpoint
        models_url = "https://text.pollinations.ai/models"
        
        try:
            response = requests.get(models_url, timeout=10)
            response.raise_for_status()
            models_data = response.json()
            
            # Pollinations возвращает массив моделей с полями:
            # {name, description, tier, maxInputChars, reasoning, ...}
            models = []
            
            if isinstance(models_data, list):
                for model in models_data:
                    if isinstance(model, str):
                        # Простой список имён моделей (старый формат)
                        models.append({
                            "id": model,
                            "name": model
                        })
                    elif isinstance(model, dict):
                        # Фильтруем только модели с tier="anonymous"
                        tier = model.get("tier", "").lower()
                        if tier != "anonymous":
                            continue
                        
                        # Объекты с полями
                        model_id = model.get("name", "")  # У Pollinations "name" это ID
                        model_description = model.get("description", model_id)
                        
                        if model_id:
                            # Формируем красивое название с описанием
                            display_name = f"{model_id}"
                            if model_description and model_description != model_id:
                                display_name = f"{model_id} ({model_description})"
                            
                            models.append({
                                "id": model_id,
                                "name": display_name
                            })
            
            # Применяем фильтр если указан
            if model_filter:
                filter_lower = model_filter.lower()
                models = [
                    m for m in models
                    if filter_lower in m["id"].lower() or filter_lower in m["name"].lower()
                ]
            
            return models
            
        except Exception:
            # Возвращаем дефолтную anonymous модель при ошибке
            return [
                {"id": "openai", "name": "OpenAI (GPT-5 Nano)"},
            ]

    def get_available_models(self) -> List[str]:
        """Получение списка ID доступных моделей.
        
        Returns:
            List[str]: Список ID моделей
        """
        models = self.fetch_models(
            api_list_url="",  # Не используется
            api_key="",  # Не требуется
            model_filter=None
        )
        return [model["id"] for model in models]


