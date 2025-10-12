# Demo Package Architecture

Полностью независимая система записи и воспроизведения LLM-сессий.

## Структура

```
demo/
├── __init__.py          # Публичные экспорты
├── models.py            # Модели данных (DemoResponse, DemoSession, etc.)
├── storage.py           # Repository для хранения (JSON файлы)
├── strategies.py        # Strategy Pattern - режимы воспроизведения
├── recorder.py          # Запись сессий
├── player.py            # Воспроизведение сессий
└── manager.py           # Facade - единый интерфейс
```

## Паттерны проектирования

### 1. **Facade Pattern** (`manager.py`)
`DemoManager` предоставляет простой интерфейс к сложной подсистеме:

```python
# Простое использование
manager = DemoManager(mode='record', demo_file='demo.json')
manager.record_response(query, response)
manager.stop()
```

### 2. **Strategy Pattern** (`strategies.py`)
Разные алгоритмы воспроизведения:

- `SimplePlaybackStrategy` - простое воспроизведение
- `StreamingPlaybackStrategy` - с эффектом потоковой передачи
- `RobotPlaybackStrategy` - с имитацией печати

```python
# Легко добавлять новые стратегии
class CustomStrategy(PlaybackStrategy):
    def play_response(self, response):
        # Своя логика
        pass
```

### 3. **Repository Pattern** (`storage.py`)
Абстракция для хранения данных:

```python
storage = DemoStorage()
storage.save_session(session, 'demo.json')
session = storage.load_session('demo.json')
```

### 4. **Factory Pattern** (`player.py`)
Удобное создание плееров с нужными стратегиями:

```python
player = PlayerFactory.create_robot_player('demo.json')
```

### 5. **State Pattern** (`models.py`)
`PlaybackState` управляет состоянием воспроизведения:

```python
state = PlaybackState()
state.advance_response()
state.advance_action()
```

## Принципы SOLID

### Single Responsibility
- `DemoRecorder` - только запись
- `DemoPlayer` - только воспроизведение
- `DemoStorage` - только хранение
- `PlaybackStrategy` - только алгоритм воспроизведения

### Open/Closed
- Новые стратегии воспроизведения добавляются без изменения существующего кода
- Новые форматы хранения - через новые Repository

### Liskov Substitution
- Все стратегии взаимозаменяемы через базовый класс `PlaybackStrategy`

### Interface Segregation
- Recorder и Player имеют разные, несвязанные интерфейсы
- Strategies определяют только нужные методы

### Dependency Inversion
- Главная программа зависит от `DemoManager` (абстракция)
- `DemoManager` зависит от интерфейсов, а не реализаций

## Использование

### Базовое

```python
from penguin_tamer.demo import DemoManager

# Запись
manager = DemoManager(mode='record', demo_file='demo.json')
manager.record_response(query, response, chunks, metadata)
manager.stop()

# Воспроизведение
manager = DemoManager(mode='play', demo_file='demo.json')
while manager.has_more_responses():
    response = manager.play_next_response()

# Робот-режим
manager = DemoManager(mode='robot', demo_file='demo.json')
while manager.has_more_responses():
    action = manager.get_next_user_action()
    # Обработка действия
```

### С context manager

```python
from penguin_tamer.demo import create_demo_context

with create_demo_context('record', 'demo.json') as manager:
    manager.record_response(query, response)
    # Автоматическое сохранение при выходе
```

### Расширенное

```python
from penguin_tamer.demo import (
    DemoPlayer,
    PlayerFactory,
    RobotPlaybackStrategy
)

# Создание кастомного плеера
player = DemoPlayer(demo_file='demo.json')
strategy = RobotPlaybackStrategy(
    player.session,
    typing_speed_range=(0.03, 0.08),  # Быстрая печать
    pause_range=(0.5, 1.5)            # Короткие паузы
)
player.set_strategy(strategy)
```

## Преимущества новой архитектуры

### 1. **Полное разделение**
- Demo система полностью независима от LLM клиента
- Можно тестировать изолированно
- Легко переиспользовать в других проектах

### 2. **Расширяемость**
- Новые режимы воспроизведения - через новые стратегии
- Новые форматы хранения - через новые Repository
- Новая логика записи - через наследование Recorder

### 3. **Тестируемость**
- Каждый компонент можно тестировать отдельно
- Mock-объекты легко создавать
- Интеграционные тесты проще

### 4. **Простота использования**
- `DemoManager` скрывает сложность
- Простой API для 90% случаев
- Доступ к деталям при необходимости

### 5. **Поддерживаемость**
- Четкая структура
- Каждый модуль отвечает за одну вещь
- Легко найти и исправить баги

## Миграция со старого demo_recorder.py

### Было (монолитная структура):
```python
from penguin_tamer.demo_recorder import DemoManager

manager = DemoManager()
manager.start_recording('demo.json')
manager.record_response(...)
```

### Стало (модульная структура):
```python
from penguin_tamer.demo import DemoManager

manager = DemoManager(mode='record', demo_file='demo.json')
manager.record_response(...)
```

### Изменения в коде:
1. `from penguin_tamer.demo_recorder` → `from penguin_tamer.demo`
2. `start_recording()` убран - передается в `__init__`
3. Все основные методы сохранены

## Тестирование

```python
import pytest
from penguin_tamer.demo import (
    DemoManager,
    DemoRecorder,
    DemoPlayer,
    SimplePlaybackStrategy
)

def test_recording():
    manager = DemoManager(mode='record', demo_file='test.json')
    manager.record_response('Hello', 'Hi there!')
    assert manager.stop()

def test_playback():
    manager = DemoManager(mode='play', demo_file='test.json')
    response = manager.play_next_response()
    assert response.user_query == 'Hello'

def test_custom_strategy():
    # Тестирование собственной стратегии
    class MockStrategy(SimplePlaybackStrategy):
        def play_response(self, response):
            self.played_count = getattr(self, 'played_count', 0) + 1

    player = DemoPlayer()
    strategy = MockStrategy(player.session)
    player.set_strategy(strategy)
```

## Дальнейшее развитие

Потенциальные улучшения:

1. **Новые стратегии**:
   - `DebugStrategy` - с выводом метаинформации
   - `InteractiveStrategy` - с паузами и ручным управлением

2. **Новые форматы хранения**:
   - YAML вместо JSON
   - База данных (SQLite)
   - Облачное хранилище

3. **Дополнительные функции**:
   - Сжатие демо-файлов
   - Шифрование чувствительных данных
   - Версионирование формата

4. **Аналитика**:
   - Статистика по демо-сессиям
   - Визуализация взаимодействий
   - Экспорт в разные форматы
