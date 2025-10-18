# Сравнение Pollinations и Mistral клиентов

## Обзор

Оба клиента используют **SSE (Server-Sent Events) streaming** через `sseclient-py`, но работают с разными API и имеют существенные различия в реализации.

---

## 🎯 Основные различия

| Характеристика | PollinationsClient | MistralClient |
|----------------|-------------------|---------------|
| **API URL** | `https://text.pollinations.ai/openai` | `https://api.mistral.ai/v1/chat/completions` |
| **API ключ** | ❌ Не требуется (бесплатный) | ✅ Требуется (платный сервис) |
| **Авторизация** | Отсутствует | `Authorization: Bearer {api_key}` |
| **Endpoint** | Кастомный `/openai` | Стандартный `/chat/completions` |
| **Язык кода** | Русские комментарии | Английские комментарии |
| **Rate limits** | Не предоставляет | Предоставляет в headers |

---

## ⚙️ Различия в параметрах API

### `_prepare_api_params()` - Подготовка параметров запроса

#### Общие параметры (оба клиента):
- ✅ `model` - ID модели
- ✅ `messages` - История сообщений
- ✅ `stream: True` - Включение потокового режима
- ✅ `temperature` - Творческость (если != 1.0)
- ✅ `max_tokens` - Максимум токенов в ответе
- ✅ `top_p` - Nucleus sampling (если != 1.0)

#### Pollinations специфичные:
```python
if self.seed is not None:
    api_params["seed"] = self.seed  # ✅ Стандартное поле
```

**НЕ поддерживает:**
- ❌ `frequency_penalty`
- ❌ `presence_penalty`
- ❌ `stop` sequences

#### Mistral специфичные:
```python
if self.seed is not None:
    api_params["random_seed"] = self.seed  # ⚠️ Отличается от стандарта!

if self.stop is not None:
    api_params["stop"] = self.stop  # ✅ Поддерживает stop sequences
```

**НЕ поддерживает:**
- ❌ `frequency_penalty` (не документировано)
- ❌ `presence_penalty` (не документировано)

---

## 🔌 Создание потока - `_create_stream()`

### Pollinations:
```python
url = "https://text.pollinations.ai/openai"

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
    # ❌ БЕЗ Authorization
}
```

### Mistral:
```python
url = f"{self.api_url}/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    "Authorization": f"Bearer {self.api_key}"  # ✅ Требует авторизацию
}
```

**Общее:**
- Оба используют `requests.post(..., stream=True)`
- Оба создают `sseclient.SSEClient(response)`
- Таймаут: 30 секунд

---

## 📊 Извлечение данных из SSE событий

### `_extract_chunk_content()` - Извлечение текста
✅ **ИДЕНТИЧНО** в обоих клиентах:
```python
parsed = json.loads(chunk.data)
content = parsed.get('choices', [{}])[0].get('delta', {}).get('content')
```

Оба проверяют маркер `[DONE]` для завершения потока.

### `_extract_usage_stats()` - Статистика токенов
✅ **ИДЕНТИЧНО** в обоих клиентах:
```python
usage = parsed.get('usage')
if usage:
    return {
        'prompt_tokens': usage.get('prompt_tokens', 0),
        'completion_tokens': usage.get('completion_tokens', 0)
    }
```

### `_extract_rate_limits()` - Лимиты API
❌ **РАЗЛИЧАЮТСЯ**:

**Pollinations:**
```python
def _extract_rate_limits(self, stream) -> dict:
    return {}  # Не предоставляет информацию о лимитах
```

**Mistral:**
```python
def _extract_rate_limits(self, stream) -> None:
    # Извлекает из headers:
    # - x-ratelimit-limit-requests
    # - x-ratelimit-limit-tokens
    # - x-ratelimit-remaining-requests
    # - x-ratelimit-remaining-tokens
    if hasattr(stream, 'resp') and hasattr(stream.resp, 'headers'):
        headers = stream.resp.headers
        # ... извлечение значений
```

---

## 📚 Получение списка моделей - `fetch_models()`

### Pollinations:
```python
models_url = "https://text.pollinations.ai/models"
# ❌ НЕ требует API ключ

# Возвращает массив: [{name, description, tier, ...}]
# Фильтрует только tier="anonymous" (бесплатные модели)

# Формирование имени:
display_name = f"{model_id} ({model_description})"

# Fallback при ошибке:
return [{"id": "openai", "name": "OpenAI (GPT-5 Nano)"}]
```

**Особенности:**
- Поле `name` в API = ID модели
- Добавляет `description` к отображаемому имени
- Возвращает fallback модель при ошибке

### Mistral:
```python
api_list_url = "https://api.mistral.ai/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}  # ✅ Требует ключ

# Возвращает объект: {"data": [{"id": "..."}, ...]}

# Формирование имени из ID:
# "mistral-large-latest" → "Mistral Large"
parts = model_id.replace('-latest', '').replace('-', ' ').split()
model_name = ' '.join(word.capitalize() for word in parts)

# Fallback при ошибке:
return []  # Пустой список
```

**Особенности:**
- Генерирует красивое имя из ID
- Удаляет суффикс `-latest`
- Возвращает пустой список при ошибке

---

## 🔍 Сравнение обработки ошибок

### Создание потока:

**Pollinations:**
```python
except Exception as e:
    raise RuntimeError(f"Pollinations API error: {e}")
```

**Mistral:**
```python
except Exception as e:
    raise RuntimeError(f"Mistral API error: {e}")
```
✅ Идентичная обработка

### Получение моделей:

**Pollinations:**
```python
except Exception:
    return [{"id": "openai", "name": "OpenAI (GPT-5 Nano)"}]
```
👍 Возвращает fallback модель для работоспособности

**Mistral:**
```python
except Exception:
    return []
```
👎 Возвращает пустой список (UI может сломаться)

---

## 📝 Различия в документации

### Pollinations:
- Русские комментарии
- Подробные docstrings на русском
- Упоминает "бесплатный доступ"

### Mistral:
- Английские комментарии
- Английские docstrings
- Упоминает требование API ключа
- Ссылается на https://docs.mistral.ai/

---

## 🎨 Стилистические различия

| Аспект | Pollinations | Mistral |
|--------|-------------|---------|
| Комментарии к секциям | Русские | Английские |
| Docstrings | Русские | Английские |
| Переменные | Английские | Английские |
| Сообщения об ошибках | Английские | Английские |

---

## 🧪 Совместимость с StreamProcessor

✅ **ОБА КЛИЕНТА ПОЛНОСТЬЮ СОВМЕСТИМЫ**

Оба используют:
```python
def ask_stream(self, user_input: str) -> str:
    from penguin_tamer.llm_clients.stream_processor import StreamProcessor
    processor = StreamProcessor(self)
    return processor.process(user_input)
```

StreamProcessor ожидает следующие методы (оба реализуют):
- `_prepare_api_params(user_input)` → dict
- `_create_stream(api_params)` → SSE iterator
- `_extract_chunk_content(chunk)` → Optional[str]
- `_extract_usage_stats(chunk)` → Optional[dict]
- `_extract_rate_limits(stream)` → None/dict

---

## 💡 Выводы

### Pollinations лучше для:
- ✅ Прототипирования без API ключей
- ✅ Бесплатного использования
- ✅ Простой настройки (нет авторизации)

### Mistral лучше для:
- ✅ Продакшн приложений с мощными моделями
- ✅ Отслеживания rate limits
- ✅ Использования stop sequences
- ✅ Больших контекстов (128k токенов)

### Технические отличия:
1. **Авторизация**: Pollinations - нет, Mistral - Bearer token
2. **Seed параметр**: Pollinations - `seed`, Mistral - `random_seed`
3. **Rate limits**: Pollinations не предоставляет, Mistral в headers
4. **Fallback модели**: Pollinations возвращает дефолт, Mistral пустой список
5. **Stop sequences**: Pollinations не поддерживает, Mistral поддерживает

### Общие черты:
- ✅ SSE streaming через sseclient
- ✅ OpenAI-совместимый формат сообщений
- ✅ Одинаковый парсинг chunks и usage
- ✅ Совместимость со StreamProcessor
- ✅ Поддержка temperature, max_tokens, top_p

---

## 🚀 Рекомендации

**Используйте Pollinations для:**
- Разработки и тестирования
- Демо приложений
- Обучающих проектов
- Когда бюджет ограничен

**Используйте Mistral для:**
- Продакшн приложений
- Когда нужны мощные модели
- Когда важна стабильность SLA
- Когда нужен контроль rate limits

**Можно использовать оба:**
- Pollinations для разработки
- Mistral для продакшн
- Переключение через `client_name` в конфиге
