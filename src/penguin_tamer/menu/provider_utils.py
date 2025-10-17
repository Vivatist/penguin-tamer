"""
UI utility functions for LLM provider menu.

Contains only UI-specific formatting functions.
Model fetching has been moved to LLM client classes (see llm_clients package).
"""

from typing import Dict


# def fetch_models_from_provider(api_list_url: str, api_key: str = "", model_filter: Optional[str] = None) -> List[Dict[str, str]]:
#     """
#     Запрашивает список моделей у провайдера.
    
#     Args:
#         api_list_url: URL для получения списка моделей
#         api_key: API ключ для аутентификации (опционально)
#         model_filter: Фильтр для моделей (опционально). Если указан, будут возвращены только модели,
#                      содержащие эту подстроку в id или name (регистронезависимо)
    
#     Returns:
#         Список словарей с информацией о моделях [{"id": "model-id", "name": "Model Name"}, ...]
#         В случае ошибки возвращает пустой список
#     """
#     try:
#         headers = {}
#         if api_key:
#             # Добавляем Authorization header если есть API ключ
#             headers["Authorization"] = f"Bearer {api_key}"
        
#         # Таймаут 10 секунд для запроса
#         response = requests.get(api_list_url, headers=headers, timeout=10)
#         response.raise_for_status()
        
#         data = response.json()
        
#         # Обрабатываем разные форматы ответа
#         models = []
        
#         # OpenAI/OpenRouter формат: {"data": [{"id": "...", "name": "..."}]}
#         if "data" in data and isinstance(data["data"], list):
#             for model in data["data"]:
#                 if isinstance(model, dict) and "id" in model:
#                     model_id = model["id"]
#                     # Используем name если есть, иначе id
#                     model_name = model.get("name", model_id)
#                     models.append({"id": model_id, "name": model_name})
        
#         # Альтернативный формат: {"models": [...]}
#         elif "models" in data and isinstance(data["models"], list):
#             for model in data["models"]:
#                 if isinstance(model, dict) and "id" in model:
#                     model_id = model["id"]
#                     model_name = model.get("name", model_id)
#                     models.append({"id": model_id, "name": model_name})
        
#         # Простой список строк
#         elif isinstance(data, list):
#             for item in data:
#                 if isinstance(item, str):
#                     models.append({"id": item, "name": item})
#                 elif isinstance(item, dict) and "id" in item:
#                     model_id = item["id"]
#                     model_name = item.get("name", model_id)
#                     models.append({"id": model_id, "name": model_name})
        
#         # Применяем фильтр если он указан
#         if model_filter:
#             filter_lower = model_filter.lower()
#             models = [
#                 model for model in models
#                 if filter_lower in model["id"].lower() or filter_lower in model["name"].lower()
#             ]
        
#         return models
    
#     except requests.exceptions.Timeout:
#         # Таймаут - провайдер не отвечает
#         return []
#     except requests.exceptions.RequestException:
#         # Другие ошибки сети
#         return []
#     except (KeyError, ValueError, TypeError):
#         # Ошибки парсинга JSON
#         return []
#     except Exception:
#         # Любые другие ошибки


def format_model_for_select(model: Dict[str, str]) -> tuple:
    """
    Форматирует модель для использования в Select виджете Textual.
    
    Args:
        model: Словарь с информацией о модели {"id": "...", "name": "..."}
    
    Returns:
        Кортеж (display_name, model_id) для Select виджета
    """
    model_id = model.get("id", "")
    model_name = model.get("name", model_id)
    
    # Если name и id одинаковые, показываем только одно
    if model_name == model_id:
        display_name = model_id
    else:
        # Показываем name (id)
        display_name = f"{model_name} ({model_id})"
    
    return (display_name, model_id)
