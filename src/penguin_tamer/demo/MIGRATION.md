# Migration Guide: Old demo_recorder.py → New demo package

Руководство по миграции со старой монолитной системы на новую модульную архитектуру.

## Что изменилось

### Структура

**Было:**
```
src/penguin_tamer/
  demo_recorder.py  (503 строки - всё в одном файле)
```

**Стало:**
```
src/penguin_tamer/demo/
  __init__.py       # Публичные экспорты
  models.py         # Модели данных
  storage.py        # Repository для хранения
  strategies.py     # Strategy Pattern - режимы воспроизведения
  recorder.py       # Запись сессий
  player.py         # Воспроизведение сессий
  manager.py        # Facade - единый интерфейс
  README.md         # Документация архитектуры
  API.md            # Справка по API
```

### Импорты

**Было:**
```python
from penguin_tamer.demo_recorder import DemoManager, DemoResponse
```

**Стало:**
```python
from penguin_tamer.demo import DemoManager, DemoResponse
```

### API Changes

#### 1. Создание DemoManager

**Было:**
```python
demo_manager = DemoManager(
    demo_mode='record',
    demo_file='demo.json',
    demo_spinner_sec=1.0
)
```

**Стало:**
```python
demo_manager = DemoManager(
    mode='record',          # было: demo_mode
    demo_file='demo.json',
    console=console         # НОВОЕ: передается console
)
# demo_spinner_sec убран - берется из config
```

#### 2. Методы больше не возвращают внутренние объекты

**Было:**
```python
recorder = demo_manager.get_recorder()
recorder.record_response(...)

player = demo_manager.get_player()
response = player.play_next_response()
```

**Стало:**
```python
# Прямое использование DemoManager (Facade Pattern)
demo_manager.record_response(...)
response = demo_manager.play_next_response()
```

#### 3. User Actions упрощены

**Было:**
```python
demo_manager.add_user_action('query', 'Hello')
# Затем при записи:
user_actions = demo_manager.get_and_clear_user_actions()
recorder.record_response(..., user_actions=user_actions)
```

**Стало:**
```python
# Действия добавляются и автоматически включаются в запись
demo_manager.add_user_action('query', 'Hello')
demo_manager.record_response(...)  # user_actions уже внутри
```

#### 4. record_user_action_only → record_action_only

**Было:**
```python
recorder = demo_manager.get_recorder()
recorder.record_user_action_only('command', 'ls', context)
```

**Стало:**
```python
demo_manager.record_action_only('command', 'ls', context)
```

## Пошаговая миграция

### Шаг 1: Обновить импорты

Найти и заменить во всех файлах:
```bash
# В cli.py, llm_client.py, и других
sed -i 's/from penguin_tamer.demo_recorder import/from penguin_tamer.demo import/g' src/penguin_tamer/*.py
```

### Шаг 2: Обновить создание DemoManager

**cli.py:**
```python
# БЫЛО:
from penguin_tamer.demo_recorder import DemoManager
demo_manager = DemoManager(
    demo_mode=args.demo_mode,
    demo_file=args.demo_file
)

# СТАЛО:
from penguin_tamer.demo import DemoManager
demo_manager = DemoManager(
    mode=args.demo_mode,
    demo_file=args.demo_file,
    console=console
)
```

### Шаг 3: Убрать get_recorder() и get_player()

**Было:**
```python
if chat_client.demo_manager and chat_client.demo_manager.is_recording():
    recorder = chat_client.demo_manager.get_recorder()
    if recorder:
        context = f"Exit code: {result.get('exit_code', -1)}"
        recorder.record_user_action_only('command', prompt, context)
```

**Стало:**
```python
if chat_client.demo_manager and chat_client.demo_manager.is_recording():
    context = f"Exit code: {result.get('exit_code', -1)}"
    chat_client.demo_manager.record_action_only('command', prompt, context)
```

### Шаг 4: Упростить запись ответов

**llm_client.py:**

**Было:**
```python
if self._demo_manager and self._demo_manager.is_recording():
    recorder = self._demo_manager.get_recorder()
    if recorder and hasattr(processor, 'recorded_chunks'):
        metadata = {...}
        user_actions = self._demo_manager.get_and_clear_user_actions()

        recorder.record_response(
            user_query=user_input,
            response=response,
            chunks=processor.recorded_chunks,
            metadata=metadata,
            user_actions=user_actions
        )
```

**Стало:**
```python
if self._demo_manager and self._demo_manager.is_recording():
    if hasattr(processor, 'recorded_chunks'):
        metadata = {...}

        # user_actions уже добавлены через add_user_action()
        self._demo_manager.record_response(
            user_query=user_input,
            response=response,
            chunks=processor.recorded_chunks,
            metadata=metadata
        )
```

### Шаг 5: Обновить воспроизведение

**Было:**
```python
if is_robot_mode:
    player = chat_client.demo_manager.get_player()
    if player:
        action = player.get_next_user_action()
        response_data = player.play_next_response(advance_index=False)
```

**Стало:**
```python
if is_robot_mode:
    action = chat_client.demo_manager.get_next_user_action()
    response_data = chat_client.demo_manager.play_next_response(advance_index=False)
```

### Шаг 6: Убрать _simulate_human_typing

**Было:**
```python
from penguin_tamer.demo_recorder import _simulate_human_typing

if user_prompt.startswith('.'):
    _simulate_human_typing('.', console, style='dim')
    _simulate_human_typing(user_prompt[1:], console, style='#007c6e')
else:
    _simulate_human_typing(user_prompt, console)
```

**Стало:**
```python
# Используем стратегию из player
strategy = chat_client.demo_manager.player.strategy if chat_client.demo_manager.player else None
if strategy and hasattr(strategy, 'simulate_typing'):
    if user_prompt.startswith('.'):
        strategy.simulate_typing('.', style='dim')
        strategy.simulate_typing(user_prompt[1:], style='#007c6e')
    else:
        strategy.simulate_typing(user_prompt)
else:
    # Fallback
    console.print(user_prompt, end='', highlight=False)
```

## Проверка миграции

### 1. Запустить старые тесты
```bash
python -m pytest tests/test_demo_recorder.py -v
```
Должны пройти все тесты (они тестируют старую систему, которая пока еще есть).

### 2. Запустить новые тесты
```bash
python -m pytest tests/test_demo_new.py -v
```
Должны пройти все 24 теста новой системы.

### 3. Запустить все тесты
```bash
python -m pytest
```
Должны пройти все 118 тестов.

### 4. Ручное тестирование

#### Запись демо:
```bash
python -m penguin_tamer --demo-mode record --demo-file test_demo.json
```

#### Воспроизведение:
```bash
python -m penguin_tamer --demo-mode play --demo-file test_demo.json
```

#### Робот-режим:
```bash
python -m penguin_tamer --demo-mode robot --demo-file test_demo.json
```

## Удаление старого кода

После успешной миграции и тестирования:

### 1. Удалить старый файл
```bash
rm src/penguin_tamer/demo_recorder.py
```

### 2. Удалить старые тесты (опционально)
```bash
# Можно оставить для истории или удалить
rm tests/test_demo_recorder.py
```

### 3. Обновить документацию
- Обновить README.md с новыми импортами
- Обновить примеры в docs/

## Откат (если что-то пошло не так)

Если миграция вызвала проблемы:

```bash
# Откатить изменения в git
git checkout -- src/penguin_tamer/cli.py
git checkout -- src/penguin_tamer/llm_client.py

# Или полностью откатить коммит
git revert HEAD
```

Старая система остается в `demo_recorder.py` до тех пор, пока вы её не удалите.

## Преимущества новой системы

✅ **Модульность**: Каждый компонент имеет четкую ответственность
✅ **Тестируемость**: Легко тестировать отдельные части
✅ **Расширяемость**: Новые режимы через новые стратегии
✅ **Поддерживаемость**: Проще найти и исправить баги
✅ **Паттерны**: Strategy, Facade, Repository - стандартные решения
✅ **Документация**: README.md и API.md в пакете

## Дополнительные возможности

### Создание собственной стратегии

```python
from penguin_tamer.demo import PlaybackStrategy

class CustomStrategy(PlaybackStrategy):
    def play_response(self, response):
        # Ваша логика
        pass

    def get_next_action(self):
        # Ваша логика
        pass

# Использование
from penguin_tamer.demo import DemoPlayer
player = DemoPlayer('demo.json')
player.set_strategy(CustomStrategy(player.session, console))
```

### Context Manager

```python
from penguin_tamer.demo import create_demo_context

with create_demo_context('record', 'demo.json') as manager:
    manager.record_response(query, response)
    # Автоматическое сохранение при выходе
```

### Низкоуровневый доступ

```python
from penguin_tamer.demo import DemoManager

manager = DemoManager(mode='record', demo_file='demo.json')

# Доступ к внутренним компонентам (для продвинутых случаев)
recorder = manager.recorder  # DemoRecorder instance
player = manager.player      # DemoPlayer instance
storage = manager.storage    # DemoStorage instance
```

## Поддержка

Если возникли проблемы с миграцией:
1. Проверьте этот гайд
2. Посмотрите API.md в `src/penguin_tamer/demo/`
3. Посмотрите примеры в тестах `tests/test_demo_new.py`
4. Проверьте README.md в `src/penguin_tamer/demo/`
