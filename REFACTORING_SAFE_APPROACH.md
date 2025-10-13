# План упрощенного рефакторинга (Safe Approach)

## Проблема с исходным планом
- Полная переписка StreamProcessor слишком рискованна
- Много интегрированного кода (error handling, spinner, Live display)
- Сложно тестировать большие изменения

## ✅ Безопасный подход (итеративный)

### Фаза 1: Минимальные изменения для развязки

#### 1.1 Вынести demo_manager наружу OpenRouterClient
**Цель:** demo_manager создается в cli.py, не в OpenRouterClient

**Изменения:**
```python
# Было:
class OpenRouterClient:
    def __post_init__(self):
        demo_mode = config.get(...)
        self._demo_manager = DemoManager(...)  # ❌

# Стало:
class OpenRouterClient:
    def __post_init__(self):
        pass  # Ничего не создаем

# В cli.py:
demo_manager = create_demo_manager_if_needed()  # ✅
chat_client = OpenRouterClient(...)
chat_client.demo_manager = demo_manager  # Внешнее присвоение
```

**Плюсы:**
- Минимальные изменения (2-3 строки)
- Все тесты продолжают работать
- Разделение ответственности

---

#### 1.2 Добавить demo_manager в конструктор (опционально)
```python
@dataclass
class OpenRouterClient:
    console: object
    system_message: List[Dict[str, str]]
    llm_config: LLMConfig
    demo_manager: Optional['DemoManager'] = None  # Новое поле
```

**Плюсы:**
- Явная зависимость
- Легко мокировать в тестах
- Backward compatible (опциональный параметр)

---

### Фаза 2: Убрать импорт demo из llm_client

#### 2.1 Использовать Duck Typing вместо импорта
**Было:**
```python
from penguin_tamer.demo import DemoManager, DemoResponse  # ❌

class DemoStreamProcessor(StreamProcessor):
    def __init__(self, client, demo_manager: DemoManager):  # ❌ Тип demo
        ...
```

**Стало:**
```python
# НЕТ импорта! ✅

class DemoStreamProcessor(StreamProcessor):
    def __init__(self, client, demo_manager):  # ✅ Без типа (duck typing)
        ...
```

**Плюсы:**
- Убирается circular dependency
- llm_client не зависит от demo модуля
- Python поддерживает duck typing из коробки

---

#### 2.2 Использовать Protocol для типизации (опционально)
```python
from typing import Protocol

class DemoManagerProtocol(Protocol):
    """Интерфейс для demo manager (без импорта конкретного класса)."""
    def has_more_responses(self) -> bool: ...
    def play_next_response(self, advance_index: bool): ...
```

**Плюсы:**
- Сохраняется типизация
- Нет зависимости от конкретной реализации
- Совместимо с mypy

---

### Фаза 3: Упростить cli.py (постепенно)

#### 3.1 Создать helper функцию для обработки demo
```python
def _handle_demo_or_llm_query(chat_client, console, prompt, demo_manager):
    """Единая функция для обработки запросов."""
    if demo_manager and demo_manager.is_playing():
        # Demo режим - ответ уже есть в записи
        # Не вызываем ask_stream, сразу получаем из demo
        return _process_demo_query(demo_manager, console)
    else:
        # Обычный режим
        return _process_ai_query(chat_client, console, prompt)
```

**Плюсы:**
- Явное разделение demo/normal логики
- Меньше флагов и проверок
- Легко тестировать отдельно

---

#### 3.2 Упростить параметры через dict
**Было:**
```python
def _handle_robot_action(robot_presenter, action, last_code_blocks,
                        console, chat_client, is_first_query=False):  # 6 параметров!
```

**Стало:**
```python
def _handle_robot_action(state: dict):  # 1 параметр!
    robot_presenter = state['robot_presenter']
    action = state['action']
    # ...
```

Или еще лучше - SimpleNamespace:
```python
from types import SimpleNamespace

state = SimpleNamespace(
    robot_presenter=...,
    action=...,
    code_blocks=[],
    console=...,
    chat_client=...,
    is_first_query=False
)

def _handle_robot_action(state):
    # Доступ как state.action, state.code_blocks
```

**Плюсы:**
- 1 параметр вместо 6
- Легко добавлять новые поля
- Читаемый код (state.action вместо state['action'])

---

## 🎯 Порядок выполнения (по приоритету)

### 🔥 Сейчас (критично):
1. ✅ Вынести создание demo_manager из OpenRouterClient.__post_init__ в cli.py
2. ✅ Добавить demo_manager как параметр конструктора
3. ✅ Убрать импорт DemoManager из llm_client.py (использовать duck typing)

### ⚠️ Скоро (важно):
4. Упростить параметры cli функций (dict или SimpleNamespace)
5. Создать helper для demo/normal разделения

### 💡 Потом (улучшения):
6. Добавить Protocol для типизации
7. ResponseProvider интерфейс (если потребуется)
8. Дальнейшая оптимизация

---

## 📊 Ожидаемый результат (после Фазы 1-2)

**Метрики:**
- ❌ `from penguin_tamer.demo import ...` в llm_client.py
- ✅ demo_manager создается в cli.py
- ✅ OpenRouterClient получает demo_manager извне
- ✅ Все 118 тестов проходят
- ✅ Нет circular dependency

**Строки кода:**
- llm_client.py: -10 строк (убрать импорт, убрать создание)
- cli.py: +5 строк (создание demo_manager)
- Итого: -5 строк, +0 сложности

**Риски:**
- 🟢 Низкий (минимальные изменения)
- 🟢 Все тесты остаются валидными
- 🟢 Backward compatible

