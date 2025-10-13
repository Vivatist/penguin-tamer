# Пошаговый план рефакторинга

## ✅ Сделано

1. ✅ Создан `response_provider.py` с интерфейсом ResponseProvider
2. ✅ Созданы реализации: LLMResponseProvider, DemoResponseProvider, MockResponseProvider

## 🔄 Следующие шаги (по порядку)

### Шаг 1: Обновить StreamProcessor для работы с ResponseProvider
**Файл:** `llm_client.py`
**Изменения:**
- StreamProcessor принимает ResponseProvider вместо прямого доступа к API
- Убрать логику выбора между demo/normal mode из `process()`
- Упростить `_connect_and_wait()` - теперь просто вызывает provider

**Преимущества:**
- StreamProcessor становится агностичным к источнику данных
- Можно тестировать с MockResponseProvider
- Убирается одна точка связанности

---

### Шаг 2: Удалить DemoStreamProcessor (больше не нужен)
**Файл:** `llm_client.py`
**Изменения:**
- Удалить класс DemoStreamProcessor (заменен DemoResponseProvider)
- Убрать специальную логику для demo mode из StreamProcessor

**Преимущества:**
- -100 строк кода
- Убирается наследование
- Упрощается иерархия классов

---

### Шаг 3: Убрать _demo_manager из OpenRouterClient
**Файл:** `llm_client.py`
**Изменения:**
- Удалить поле `_demo_manager`
- Удалить создание DemoManager из `__post_init__()`
- Убрать проверки `if self._demo_manager and ...` из `ask_stream()`
- Создавать ResponseProvider в `ask_stream()` на основе параметра

**Преимущества:**
- OpenRouterClient больше не зависит от demo
- Убирается circular dependency
- Клиент делает только одну вещь - общается с LLM

---

### Шаг 4: Передавать demo_manager через внешний интерфейс
**Файлы:** `cli.py`, `llm_client.py`
**Изменения:**
- Создавать DemoManager в `cli.py` (или main)
- Передавать его в функции, которые создают ResponseProvider
- OpenRouterClient получает уже готовый provider

**Код (примерно):**
```python
# cli.py
demo_manager = DemoManager(...) if demo_mode else None

# Создаем provider на основе режима
if demo_manager and demo_manager.is_playing():
    provider = DemoResponseProvider(demo_manager)
else:
    provider = LLMResponseProvider(client.client, params)

# Клиент работает через provider
response = client.ask_with_provider(user_input, provider)
```

**Преимущества:**
- Разделение ответственности
- cli владеет demo логикой
- llm_client агностичен к demo

---

### Шаг 5: Упростить ask_stream()
**Файл:** `llm_client.py`
**Изменения:**
```python
def ask_stream(self, user_input: str, provider: ResponseProvider = None) -> str:
    """Потоковый режим с провайдером ответов."""

    # Если provider не передан, используем LLM
    if provider is None:
        provider = LLMResponseProvider(self.client, self._prepare_api_params())

    # Обработка через единый StreamProcessor
    processor = StreamProcessor(self, provider)
    return processor.process(user_input)
```

**Преимущества:**
- 1 ветка кода вместо 3
- Нет проверок demo_manager
- Провайдер инжектится извне

---

### Шаг 6: Обновить вызовы в cli.py
**Файл:** `cli.py`
**Изменения:**
- В `_process_ai_query()` создавать provider
- Передавать provider в `ask_stream()`
- Убрать доступ к `chat_client.demo_manager`

**Код (примерно):**
```python
def _process_ai_query(chat_client, console, prompt, demo_manager=None):
    # Создаем provider
    if demo_manager and demo_manager.is_playing():
        provider = DemoResponseProvider(demo_manager)
    else:
        provider = None  # Будет использован LLM по умолчанию

    # Отправляем запрос
    reply = chat_client.ask_stream(prompt, provider=provider)
    ...
```

---

### Шаг 7: Упростить передачу demo_manager в cli.py
**Файл:** `cli.py`
**Изменения:**
- Создать класс `DialogContext` для хранения состояния:
  ```python
  @dataclass
  class DialogContext:
      console: Console
      chat_client: OpenRouterClient
      demo_manager: Optional[DemoManager]
      code_blocks: list = field(default_factory=list)
  ```
- Заменить 6-7 параметров функций на один `context`

**Преимущества:**
- Функции с 1-2 параметрами вместо 6-7
- Легко добавлять новые поля
- Явное состояние диалога

---

### Шаг 8: Удалить импорт demo из llm_client.py
**Файл:** `llm_client.py`
**Изменения:**
- Удалить `from penguin_tamer.demo import DemoManager, DemoResponse`
- Убрать все упоминания DemoManager из файла

**Результат:**
- ✅ Полная развязка llm_client ↔ demo
- ✅ Нет circular dependencies
- ✅ llm_client можно использовать без demo модуля

---

## 📊 Прогресс

```
[✅] ResponseProvider интерфейс
[ ] StreamProcessor с provider
[ ] Удалить DemoStreamProcessor
[ ] Убрать _demo_manager из OpenRouterClient
[ ] Передача demo_manager извне
[ ] Упростить ask_stream()
[ ] Обновить cli.py
[ ] DialogContext
[ ] Удалить импорт demo
```

## 🎯 Метрики после завершения

- **Связанность llm_client ↔ demo:** 0 (было 15+)
- **Параметров в функциях:** 2-3 (было 6-7)
- **Строк в llm_client.py:** ~450 (было 620, -27%)
- **Тестируемость:** Высокая (можно мокировать provider)

