# Анализ связанности demo и llm_client

## 🔴 Критические проблемы

### 1. **Circular Dependency: llm_client ↔ demo**

**llm_client.py:**
```python
from penguin_tamer.demo import DemoManager, DemoResponse  # Line 18
```

**Проблема:** OpenRouterClient импортирует DemoManager, но DemoManager НЕ должен знать о llm_client.

---

### 2. **OpenRouterClient владеет demo_manager (нарушение SRP)**

```python
class OpenRouterClient:
    _demo_manager: Optional[DemoManager] = field(default=None, init=False)
    
    def __post_init__(self):
        demo_mode = config.get("global", "demo_mode", "off")
        if demo_mode != "off":
            self._demo_manager = DemoManager(...)  # Line 374-379
```

**Проблема:** LLM клиент отвечает за создание demo manager. Это нарушает принцип единственной ответственности.

---

### 3. **DemoStreamProcessor наследует StreamProcessor**

```python
class DemoStreamProcessor(StreamProcessor):
    def __init__(self, client: 'OpenRouterClient', demo_manager: DemoManager):
        super().__init__(client)
        self.demo_manager = demo_manager
```

**Проблема:** Demo функциональность вшита в иерархию StreamProcessor, усложняя тестирование и замену.

---

### 4. **cli.py передает chat_client в demo функции**

```python
def _handle_robot_action(robot_presenter, action, last_code_blocks, 
                        console, chat_client, is_first_query=False):
    # ...
    _handle_direct_command(console, chat_client, user_prompt)
```

**Проблема:** 6 параметров! Demo логика требует доступа к chat_client для выполнения команд.

---

### 5. **RobotPresenter требует перевод функцию `t`**

```python
def __init__(self, console: Console, demo_manager: DemoManager, 
             t: Callable[[str], str], timing: Optional[RobotTimingConfig] = None):
```

**Проблема:** Presenter связан с системой i18n через параметр `t`, вместо того чтобы импортировать её напрямую.

---

### 6. **Множественные флаги и состояния**

```python
# cli.py
is_robot_mode = True/False
skip_first_query = True/False
is_first_query = True/False

# llm_client.py
if self._demo_manager and self._demo_manager.is_playing():
    processor = DemoStreamProcessor(...)
else:
    processor = StreamProcessor(...)
    if self._demo_manager and self._demo_manager.is_recording():
        self._demo_manager.record_response(...)
```

**Проблема:** Логика размазана по файлам, состояние управляется флагами.

---

## 📊 Метрики связанности

### llm_client.py
- **Строк:** 620
- **Зависимостей от demo:** 3 прямых импорта
- **Классов связанных с demo:** 2 (DemoStreamProcessor, OpenRouterClient)
- **Точек взаимодействия:** ~15

### cli.py
- **Функций с demo логикой:** 3 (_setup_robot_presenter, _handle_robot_action, _get_user_input)
- **Параметров в функциях:** 6-7 (слишком много!)
- **Точек проверки demo_manager:** 5+

### demo/
- **Модулей:** 9
- **Классов:** 12+
- **Обратных зависимостей на llm_client:** 0 (хорошо!)
- **Зависимостей на cli:** 0 (хорошо!)

---

## 🎯 Целевая архитектура

### Принципы:
1. **Dependency Inversion:** demo не знает о llm_client, cli не владеет demo
2. **Interface Segregation:** Минимальные интерфейсы между модулями
3. **Single Responsibility:** Каждый модуль делает одну вещь хорошо
4. **Composition over Inheritance:** Вместо DemoStreamProcessor - делегирование

---

## 🔧 План рефакторинга

### Phase 1: Развязать llm_client ↔ demo

**Текущее:**
```python
# llm_client.py
from penguin_tamer.demo import DemoManager

class OpenRouterClient:
    _demo_manager: Optional[DemoManager] = ...
```

**Целевое:**
```python
# llm_client.py
# NO demo imports!

class OpenRouterClient:
    # NO _demo_manager field
    # NO demo logic
```

**Как:** Использовать Strategy Pattern с интерфейсом `ResponseProvider`

---

### Phase 2: Упростить StreamProcessor

**Текущее:**
```python
class StreamProcessor: ...
class DemoStreamProcessor(StreamProcessor): ...

# В ask_stream():
if self._demo_manager and self._demo_manager.is_playing():
    processor = DemoStreamProcessor(...)
else:
    processor = StreamProcessor(...)
```

**Целевое:**
```python
class StreamProcessor:
    def __init__(self, client, response_provider: ResponseProvider):
        self.response_provider = response_provider
    
    def process(self, user_input):
        # Единый код для обоих режимов
        response = self.response_provider.get_response(user_input)
        # ...
```

**Как:** 
- Создать интерфейс `ResponseProvider` с методом `get_response()`
- Реализации: `LLMResponseProvider`, `DemoResponseProvider`
- Внедрять через конструктор

---

### Phase 3: Упростить cli.py

**Текущее:**
```python
def _handle_robot_action(robot_presenter, action, last_code_blocks, 
                        console, chat_client, is_first_query=False):
    # 6 параметров!
```

**Целевое:**
```python
class DialogSession:
    def __init__(self, console, chat_client):
        self.console = console
        self.chat_client = chat_client
        self.code_blocks = []
        self.is_first = True
    
    def handle_action(self, action):
        # 1 параметр!
```

**Как:** Создать класс DialogSession для хранения состояния

---

### Phase 4: Убрать demo_manager из OpenRouterClient

**Текущее:**
```python
def __post_init__(self):
    if demo_mode != "off":
        self._demo_manager = DemoManager(...)  # ❌ Клиент создает manager
```

**Целевое:**
```python
# main.py или cli.py
demo_manager = DemoManager(...) if demo_mode else None
chat_client = OpenRouterClient(...)  # Не знает о demo
```

**Как:** Создавать demo_manager в точке входа, передавать через ResponseProvider

---

### Phase 5: Упростить RobotPresenter

**Текущее:**
```python
def __init__(self, console, demo_manager, t, timing=None):
    # 4 параметра
```

**Целевое:**
```python
def __init__(self, console, timing=None):
    # 2 параметра
    self.t = t  # import напрямую
```

**Как:** 
- Импортировать `t` напрямую из i18n
- Получать данные через методы, а не хранить demo_manager

---

## 📈 Ожидаемые улучшения

### Метрики:
- ✅ **Связанность:** llm_client ↔ demo: 15 → 0 точек взаимодействия
- ✅ **Параметры функций:** 6-7 → 2-3 параметров
- ✅ **Флаги:** 5+ → 0-1 флагов
- ✅ **Тестируемость:** Низкая → Высокая (мокируемые интерфейсы)
- ✅ **Сложность:** O(N²) → O(N) (линейная зависимость)

### Качество:
- 🎯 Каждый модуль можно тестировать изолированно
- 🎯 Можно заменить demo систему без изменения llm_client
- 🎯 Можно заменить LLM провайдера без изменения demo
- 🎯 Функции с < 4 параметров
- 🎯 Нет circular dependencies

---

## 🚀 Приоритеты

### 🔥 Критично (делать сейчас):
1. **Убрать DemoManager из OpenRouterClient.__post_init__**
2. **Создать ResponseProvider интерфейс**
3. **Убрать DemoStreamProcessor наследование**

### ⚠️ Важно (делать скоро):
4. **Создать DialogSession класс**
5. **Упростить параметры в cli.py**

### 💡 Улучшения (можно потом):
6. **Упростить RobotPresenter**
7. **Добавить интерфейсные тесты**

