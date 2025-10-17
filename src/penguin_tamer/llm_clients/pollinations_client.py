"""
Pollinations Client - Реализация клиента для Pollinations API.

Использует GET запросы к https://text.pollinations.ai/{prompt}
API documentation: https://pollinations.ai/
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import urllib.parse

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.utils.lazy_import import lazy_import

# Ленивый импорт requests для работы с API
@lazy_import
def get_requests_module():
    """Ленивый импорт requests для API запросов"""
    import requests
    return requests


@dataclass
class PollinationsClient(AbstractLLMClient):
    """Pollinations-specific implementation of LLM client.
    
    Uses GET requests to https://text.pollinations.ai/{encoded_prompt}
    No API key required - free and open access.
    
    This class contains ONLY Pollinations API-specific logic:
    - Request parameter preparation (URL encoding)
    - Direct GET requests (no streaming)
    - Response parsing
    """

    # === API-specific methods (формирование запросов и парсинг ответов) ===

    def _prepare_prompt_url(self, user_input: str) -> tuple:
        """Подготовка URL и параметров для Pollinations API запроса.
        
        Pollinations использует формат: GET https://text.pollinations.ai/{encoded_prompt}?model=...&seed=...
        
        Для многооборотных диалогов формируем полный контекст в промпте.
        
        ВАЖНО: Параметр system вызывает ошибки Azure content filter,
        поэтому мы включаем system message прямо в промпт.
        
        Args:
            user_input: Пользовательский ввод
            
        Returns:
            tuple: (url, params) - URL с закодированным промптом и словарь параметров
        """
        # Формируем полный промпт из истории сообщений
        full_prompt_parts = []
        
        # Добавляем системное сообщение БЕЗ префикса "System:" (Azure content filter блокирует это слово)
        for msg in self.messages:
            if msg["role"] == "system":
                full_prompt_parts.append(msg['content'])
                break
        
        # Добавляем историю диалога
        for msg in self.messages:
            if msg["role"] == "user":
                full_prompt_parts.append(f"User: {msg['content']}")
            elif msg["role"] == "assistant":
                full_prompt_parts.append(f"Assistant: {msg['content']}")
        
        # Добавляем текущий запрос пользователя
        full_prompt_parts.append(f"User: {user_input}")
        full_prompt_parts.append("Assistant:")
        
        full_prompt = "\n\n".join(full_prompt_parts)
        
        # Кодируем промпт для URL
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Формируем URL
        base_url = self.api_url.rstrip('/')
        url = f"{base_url}/{encoded_prompt}"
        
        # Формируем параметры запроса
        # НЕ используем параметр system - он вызывает Azure content filter ошибки
        params = {
            "model": self.model,
            "seed": self.seed if self.seed is not None else 42,
        }
        
        return url, params

    def _create_stream(self, api_params: dict):
        """Создание "потока" для Pollinations API.
        
        На самом деле Pollinations не поддерживает настоящий streaming,
        поэтому мы делаем обычный GET запрос и возвращаем результат.
        
        Args:
            api_params: Параметры запроса (url, params)
            
        Returns:
            Ответ от API как текст
        """
        requests = get_requests_module()
        url = api_params['url']
        params = api_params['params']
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise RuntimeError(f"Pollinations API error: {e}")

    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Извлечение контента из "чанка".
        
        Для Pollinations весь ответ приходит целиком, поэтому
        chunk это просто полный текст ответа.
        
        Args:
            chunk: Текстовый ответ от API
            
        Returns:
            Полный текст ответа
        """
        # Pollinations возвращает весь ответ целиком
        if isinstance(chunk, str):
            return chunk
        return None

    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Извлечение статистики использования токенов.
        
        Pollinations не предоставляет статистику токенов в своём API.
        
        Args:
            chunk: Ответ от API
            
        Returns:
            None (статистика недоступна)
        """
        # Pollinations не возвращает usage stats
        return None

    def _extract_rate_limits(self, stream) -> dict:
        """Извлечение rate limits из ответа.
        
        Pollinations не предоставляет rate limit информацию,
        т.к. это бесплатный сервис без ограничений.
        
        Args:
            stream: Ответ от API
            
        Returns:
            Пустой dict
        """
        # Pollinations не возвращает rate limits
        return {}

    # === Основной метод генерации ===

    def ask_stream(self, user_input: str) -> str:
        """Основной метод для генерации с Pollinations.
        
        Примечание: Несмотря на название "stream", Pollinations не поддерживает
        настоящий streaming - весь ответ приходит целиком.
        
        Args:
            user_input: Запрос пользователя
            
        Returns:
            str: Полный ответ от LLM
        """
        from penguin_tamer.i18n import t
        from penguin_tamer.config_manager import config
        from penguin_tamer.error_handlers import ErrorHandler, ErrorContext, ErrorSeverity
        
        debug_mode = config.get("global", "debug", False)
        error_handler = ErrorHandler(console=self.console, debug_mode=debug_mode)
        
        # Показываем спиннер во время запроса
        with self._managed_spinner(t('Connecting to Pollinations...')) as status_message:
            try:
                # Подготавливаем URL и параметры
                url, params = self._prepare_prompt_url(user_input)
                
                status_message['text'] = t('Ai thinking...')
                
                # Делаем запрос
                api_params = {'url': url, 'params': params}
                response_text = self._create_stream(api_params)
                
                if not response_text or not response_text.strip():
                    warning = t('Warning: Empty response received from API.')
                    self.console.print(f"[dim italic]{warning}[/dim italic]")
                    return ""
                
                # Добавляем в контекст
                self.messages.append({"role": "user", "content": user_input})
                self.messages.append({"role": "assistant", "content": response_text})
                
                # Показываем ответ
                theme_name = config.get("global", "markdown_theme", "default")
                markdown = self._create_markdown(response_text, theme_name)
                self.console.print(markdown)
                
                # Debug output если включён
                self._debug_print_if_enabled("response")
                
                return response_text
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                context = ErrorContext(
                    operation="Pollinations API request",
                    severity=ErrorSeverity.ERROR,
                    recoverable=True
                )
                error_message = error_handler.handle(e, context)
                self.console.print(error_message)
                return ""

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


