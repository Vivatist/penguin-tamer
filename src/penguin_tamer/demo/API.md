# Demo Package API Reference

Быстрая справка по новому API демо-системы.

## Основной интерфейс: DemoManager

### Инициализация

```python
from penguin_tamer.demo import DemoManager

# Запись
manager = DemoManager(mode='record', demo_file='demo.json')

# Воспроизведение
manager = DemoManager(mode='play', demo_file='demo.json')

# Робот-режим
manager = DemoManager(mode='robot', demo_file='demo.json')

# Без демо
manager = DemoManager(mode='off')
```

### Методы для записи

| Метод | Описание | Пример |
|-------|----------|--------|
| `is_recording()` | Проверка режима записи | `if manager.is_recording():` |
| `add_user_action(type, value)` | Добавить действие пользователя | `manager.add_user_action('query', 'Hello')` |
| `record_response(query, response, chunks, metadata)` | Записать ответ LLM | `manager.record_response(q, r, chunks)` |
| `record_action_only(type, value, context)` | Записать действие без LLM | `manager.record_action_only('command', 'ls')` |
| `stop_recording()` | Остановить и сохранить | `manager.stop_recording()` |

### Методы для воспроизведения

| Метод | Описание | Пример |
|-------|----------|--------|
| `is_playing()` | Проверка режима воспроизведения | `if manager.is_playing():` |
| `is_robot_mode()` | Проверка робот-режима | `if manager.is_robot_mode():` |
| `has_more_responses()` | Есть ли еще ответы | `while manager.has_more_responses():` |
| `play_next_response(advance_index)` | Воспроизвести следующий | `response = manager.play_next_response()` |
| `get_next_user_action()` | Получить следующее действие | `action = manager.get_next_user_action()` |
| `reset_playback()` | Сбросить к началу | `manager.reset_playback()` |
| `get_progress()` | Получить прогресс | `current, total = manager.get_progress()` |

### Вспомогательные методы

| Метод | Описание | Пример |
|-------|----------|--------|
| `stop()` | Остановить запись/воспроизведение | `manager.stop()` |
| `is_loaded()` | Проверка загрузки демо-файла | `if manager.is_loaded():` |
| `list_demos(directory)` | Список доступных демо | `demos = manager.list_demos()` |
| `get_session()` | Получить текущую сессию | `session = manager.get_session()` |

## Модели данных

### DemoResponse

```python
from penguin_tamer.demo import DemoResponse

response = DemoResponse(
    timestamp='2024-01-01T12:00:00',
    user_query='Hello',
    response='Hi there!',
    chunks=['Hi ', 'there!'],
    metadata={'model': 'gpt-4'},
    user_actions=[{'type': 'query', 'value': 'Hello'}]
)

# Методы
response.has_response_content()  # Есть ли содержимое ответа
response.is_action_only()        # Только действие (без ответа)
response.to_dict()               # Конвертация в dict
DemoResponse.from_dict(data)     # Создание из dict
```

### UserAction

```python
from penguin_tamer.demo import UserAction

# Фабричные методы
action = UserAction.create_query('What is Python?')
action = UserAction.create_command('ls -la')
action = UserAction.create_code_block('print("Hello")')

# Доступ к данным
action.type     # 'query', 'command', 'code_block'
action.value    # Значение действия
```

### DemoSession

```python
from penguin_tamer.demo import DemoSession

session = DemoSession()
session.add_response(response)
session.clear()

# Свойства
session.responses  # List[DemoResponse]
len(session.responses)
```

### PlaybackState

```python
from penguin_tamer.demo import PlaybackState

state = PlaybackState()
state.advance_response()  # Следующий ответ
state.advance_action()    # Следующее действие
state.reset()             # К началу

# Свойства
state.current_response_index
state.current_action_index
```

## Стратегии воспроизведения

### SimplePlaybackStrategy

Простое последовательное воспроизведение.

```python
from penguin_tamer.demo import SimplePlaybackStrategy

strategy = SimplePlaybackStrategy(session, console)
```

### StreamingPlaybackStrategy

С эффектом потоковой передачи (chunk-by-chunk).

```python
from penguin_tamer.demo import StreamingPlaybackStrategy

strategy = StreamingPlaybackStrategy(
    session,
    console,
    chunk_delay=0.01  # Задержка между чанками
)
```

### RobotPlaybackStrategy

Полная автоматизация с имитацией печати.

```python
from penguin_tamer.demo import RobotPlaybackStrategy

strategy = RobotPlaybackStrategy(
    session,
    console,
    typing_speed_range=(0.05, 0.12),  # Скорость печати
    pause_range=(1.0, 3.0)             # Паузы между действиями
)
```

### RecordStrategy

Стратегия для записи (не для воспроизведения).

```python
from penguin_tamer.demo import RecordStrategy

strategy = RecordStrategy()
strategy.add_user_action('query', 'Hello')
strategy.record_response(query, response, chunks, metadata)
session = strategy.get_session()
```

## Recorder

Прямая работа с рекордером (низкоуровневый API).

```python
from penguin_tamer.demo import DemoRecorder, RecordingContext

# Обычное использование
recorder = DemoRecorder('demo.json')
recorder.start_recording()
recorder.record_response(query, response, chunks)
recorder.stop_recording()

# С context manager
with RecordingContext(recorder, 'demo.json') as rec:
    rec.record_response(query, response)
```

## Player

Прямая работа с плеером (низкоуровневый API).

```python
from penguin_tamer.demo import DemoPlayer, PlayerFactory

# Создание с фабрикой
player = PlayerFactory.create_simple_player('demo.json')
player = PlayerFactory.create_streaming_player('demo.json', chunk_delay=0.02)
player = PlayerFactory.create_robot_player('demo.json')

# Ручное создание
player = DemoPlayer(demo_file='demo.json')
player.load('demo.json')
player.set_strategy(strategy)

# Использование
while player.has_more_responses():
    response = player.play_next_response()
    action = player.get_next_user_action()

# Управление
player.reset()
current, total = player.get_progress()
```

## Storage

Низкоуровневая работа с хранилищем.

```python
from penguin_tamer.demo import DemoStorage

storage = DemoStorage()

# Сохранение
storage.save_session(session, 'demo.json')
storage.save_session(session, 'demo.json')  # Создаст demo_1.json

# Загрузка
session = storage.load_session('demo.json')

# Список файлов
demos = storage.list_sessions()
demos = storage.list_sessions('/custom/path')

# Удаление
storage.delete_session('demo.json')

# Вспомогательные методы
path = storage.resolve_path('demo.json')
unique_path = storage.get_unique_path('demo.json')
```

## Создание собственной стратегии

```python
from penguin_tamer.demo import PlaybackStrategy

class MyCustomStrategy(PlaybackStrategy):
    def play_response(self, response):
        # Ваша логика воспроизведения
        if self.console:
            self.console.print(f"[custom]{response.response}[/custom]")

    def get_next_action(self):
        # Ваша логика получения действий
        if not self.has_more_responses():
            return None

        response = self.session.responses[self.state.current_response_index]
        # ... логика ...
        return action

# Использование
player = DemoPlayer('demo.json')
strategy = MyCustomStrategy(player.session, console)
player.set_strategy(strategy)
```

## Context Managers

```python
from penguin_tamer.demo import create_demo_context

# Автоматическое управление жизненным циклом
with create_demo_context('record', 'demo.json') as manager:
    manager.record_response(query, response)
    # Автоматическое сохранение при выходе

# Для воспроизведения
with create_demo_context('play', 'demo.json') as manager:
    while manager.has_more_responses():
        response = manager.play_next_response()
```

## Типы и константы

```python
from penguin_tamer.demo import DemoMode

# DemoMode = Literal['record', 'play', 'robot', 'off']
mode: DemoMode = 'record'
```

## Обработка ошибок

```python
from penguin_tamer.demo import DemoManager

try:
    manager = DemoManager(mode='play', demo_file='missing.json')
    if not manager.is_loaded():
        print("Failed to load demo file")
except Exception as e:
    print(f"Error: {e}")
```

## Примеры интеграции

### В LLM клиенте

```python
class MyLLMClient:
    def __init__(self, demo_manager=None):
        self.demo_manager = demo_manager

    def query(self, prompt):
        if self.demo_manager and self.demo_manager.is_playing():
            # Воспроизведение
            response = self.demo_manager.play_next_response()
            return response.response

        # Реальный запрос к LLM
        response = self.actual_llm_call(prompt)

        if self.demo_manager and self.demo_manager.is_recording():
            # Запись
            self.demo_manager.record_response(prompt, response)

        return response
```

### В CLI

```python
def main():
    args = parse_args()

    # Создание demo manager
    demo_manager = None
    if args.demo_mode in ('record', 'play', 'robot'):
        demo_manager = DemoManager(
            mode=args.demo_mode,
            demo_file=args.demo_file
        )

    # Передача в клиент
    client = LLMClient(demo_manager=demo_manager)

    # Работа с client
    # ...

    # Остановка
    if demo_manager:
        demo_manager.stop()
```
