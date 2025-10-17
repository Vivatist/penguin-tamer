"""
Pollinations Client - Реализация клиента для Pollinations API.

Использует OpenAI-совместимый endpoint для текстовой генерации.
API documentation: https://pollinations.ai/
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
    """Ленивый импорт OpenAI клиента (Pollinations использует OpenAI-совместимый API)"""
    from openai import OpenAI
    return OpenAI


@dataclass
class PollinationsClient(AbstractLLMClient):
    """Pollinations-specific implementation of LLM client.
    
    Uses OpenAI-compatible API at https://text.pollinations.ai/openai
    No API key required - free and open access.
    
    This class contains ONLY Pollinations API-specific logic:
    - Request parameter preparation
    - Stream creation
    - Response parsing (chunks, usage, rate limits)
    """

    # Pollinations-specific state
    _client: Optional[object] = field(default=None, init=False)

    # === API-specific methods (формирование запросов и парсинг ответов) ===

    def _prepare_api_params(self, user_input: Optional[str] = None) -> dict:
        """Подготовка параметров для Pollinations API запроса.
        
        Args:
            user_input: Пользовательский ввод (добавляется в историю сообщений)
            
        Returns:
            dict: Параметры для передачи в OpenAI SDK (OpenAI-compatible format)
        """
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        # Pollinations использует OpenAI-совместимый формат
        api_params = {
            "model": self.llm_config.model,
            "messages": self.messages,
            "stream": True,
        }

        # ВАЖНО: Некоторые модели Pollinations (например, "openai") не поддерживают
        # кастомные значения temperature, top_p и других параметров.
        # Они работают только со значениями по умолчанию.
        # Для таких моделей мы не добавляем эти параметры.
        
        # Список моделей с ограничениями (могут не поддерживать кастомные параметры)
        restricted_models = {"openai", "gpt-5-nano"}
        
        model_name = self.llm_config.model.lower()
        is_restricted = any(restricted in model_name for restricted in restricted_models)
        
        if not is_restricted:
            # Для моделей без ограничений добавляем все параметры
            if self.llm_config.temperature and self.llm_config.temperature != 1.0:
                api_params["temperature"] = self.llm_config.temperature

            if self.llm_config.max_tokens and self.llm_config.max_tokens > 0:
                api_params["max_tokens"] = self.llm_config.max_tokens

            if self.llm_config.top_p and self.llm_config.top_p != 1.0:
                api_params["top_p"] = self.llm_config.top_p
        else:
            # Для ограниченных моделей добавляем только max_tokens (обычно поддерживается)
            if self.llm_config.max_tokens and self.llm_config.max_tokens > 0:
                api_params["max_tokens"] = self.llm_config.max_tokens

        return api_params

    @property
    def client(self):
        """Lazy initialization Pollinations client (OpenAI-compatible SDK)."""
        if self._client is None:
            OpenAI = get_openai_client()
            # Pollinations использует OpenAI-совместимый endpoint и НЕ требует API ключа
            # Используем placeholder для api_key т.к. SDK требует его, но Pollinations игнорирует
            # Base URL должен указывать на /openai, т.к. SDK добавит /chat/completions
            self._client = OpenAI(
                api_key="not-needed",  # Pollinations не требует ключа
                base_url="https://text.pollinations.ai/openai"  # Pollinations OpenAI-compatible endpoint
            )
        return self._client

    def _create_stream(self, api_params: dict):
        """Создание потока для Pollinations API.
        
        Args:
            api_params: Параметры запроса (из _prepare_api_params)
            
        Returns:
            Stream object от OpenAI SDK (Pollinations совместим с OpenAI)
        """
        return self.client.chat.completions.create(**api_params)

    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Извлечение текстового контента из чанка.
        
        Pollinations использует OpenAI-совместимый формат:
        chunk.choices[0].delta.content
        
        Args:
            chunk: Чанк от stream
            
        Returns:
            str или None: Текст из чанка или None если пусто
        """
        if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'content'):
                return delta.content
        return None

    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Извлечение статистики использования токенов из чанка.
        
        Pollinations может не предоставлять usage stats в каждом чанке.
        Формат (если есть): chunk.usage с полями prompt_tokens, completion_tokens
        
        Args:
            chunk: Чанк от stream
            
        Returns:
            dict или None: {'prompt_tokens': int, 'completion_tokens': int} или None
        """
        if hasattr(chunk, 'usage') and chunk.usage:
            return {
                'prompt_tokens': getattr(chunk.usage, 'prompt_tokens', 0),
                'completion_tokens': getattr(chunk.usage, 'completion_tokens', 0)
            }
        return None

    def _extract_rate_limits(self, headers: dict) -> dict:
        """Извлечение rate limits из заголовков ответа.
        
        Pollinations может не предоставлять rate limit информацию,
        т.к. это бесплатный сервис без ограничений по ключу.
        
        Args:
            headers: HTTP заголовки ответа
            
        Returns:
            dict: Словарь с rate limit данными (может быть пустым)
        """
        # Pollinations скорее всего не возвращает rate limits
        # Возвращаем пустой dict, т.к. это бесплатный сервис
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


