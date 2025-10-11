# Robot Mode - Полная автоматизация демо

## Описание

Robot mode - это режим полной автоматизации воспроизведения демо-сессий с эмуляцией ввода пользователя. В отличие от обычного режима `play`, который просто воспроизводит записанные ответы LLM, режим `robot` также автоматически вбивает команды пользователя с имитацией печати человека.

## Основные возможности

### 1. Автоматический ввод
- Последовательное воспроизведение всех действий пользователя из записи
- Побуквенная печать с реалистичными задержками
- Поддержка всех типов действий: запросы (query), команды (command), блоки кода (code_block)

### 2. Эмуляция человеческой печати
Robot mode использует функцию `_simulate_human_typing()` для реалистичной имитации набора текста:

```python
def _simulate_human_typing(text: str, console=None, style: str = None) -> None:
    """
    Имитирует постепенный ввод текста человеком с неравномерными задержками.
    
    Args:
        text: Текст для вывода
        console: Rich console для форматированного вывода (опционально)
        style: Стиль Rich для текста (например, 'bold', 'dim', '#007c6e')
    """
```

**Характеристики задержек:**
- Обычные символы: 0.05-0.12 секунды
- Пробелы: 0.05-0.15 секунды  
- Заглавные буквы: 0.08-0.18 секунды (дольше, как при удерживании Shift)
- Знаки препинания: 0.15-0.3 секунды (требуют больше внимания)
- Случайные "заминки": 5% шанс добавить паузу 0.2-0.5 секунды
- **Пауза между действиями: 3-4 секунды** (кроме первого действия)

**Визуальное оформление:**
- Приглашение: `>>>` (оранжевый цвет `#e07333`)
- Команды с точкой: `.` (серый) + `команда` (бирюзовый `#007c6e`)
- Обычный текст: стандартный цвет консоли### 3. Последовательное воспроизведение

Robot mode использует метод `get_next_user_action()` для последовательного извлечения действий:

```python
def get_next_user_action(self) -> Optional[Dict[str, str]]:
    """
    Получает следующее действие пользователя из записи.
    Отслеживает позицию в списке user_actions для возврата всех действий.

    Returns:
        Словарь с типом и значением действия, или None если действий больше нет
    """
```

**Принцип работы:**
1. Отслеживает текущую позицию в списке записей (`current_index`)
2. Отслеживает позицию внутри `user_actions` (`current_action_index`)
3. Последовательно возвращает все действия всех записей
4. Возвращает `None` когда действия закончились

## Использование

### Включение robot mode

В конфигурационном файле `config.yaml`:

```yaml
demo:
  mode: robot  # Режимы: record, play, robot, off
  file: session_1.json  # Файл с записью
```

### Создание записи для robot mode

Сначала создайте запись в режиме `record`:

```yaml
demo:
  mode: record
  file: my_demo.json
```

Взаимодействуйте с программой как обычно. Все ваши действия (запросы, команды, блоки кода) будут записаны в файл.

### Воспроизведение в robot mode

Переключите режим на `robot`:

```yaml
demo:
  mode: robot
  file: my_demo.json
```

Программа автоматически:
1. Извлечёт следующее действие из записи
2. **Выведет приглашение `>>>` сразу**
3. Выдержит паузу 3-4 секунды (кроме первого действия)
4. Симулирует печать этого действия побуквенно
5. "Нажмёт Enter" (пауза 0.3 сек)
6. Обработает действие как обычный пользовательский ввод
7. Повторит для всех действий в записи
8. После завершения записи переключится в обычный режим диалога

## Структура данных

### Формат записи

```json
[
  {
    "timestamp": "2025-01-01T12:00:00",
    "user_query": "Привет",
    "response": "Привет! Как дела?",
    "chunks": ["Привет! ", "Как ", "дела?"],
    "metadata": {},
    "user_actions": [
      {
        "type": "query",
        "value": "Привет",
        "timestamp": "2025-01-01T12:00:00"
      }
    ]
  },
  {
    "timestamp": "2025-01-01T12:00:10",
    "user_query": ".help",
    "response": "Доступные команды...",
    "chunks": ["Доступные ", "команды..."],
    "metadata": {},
    "user_actions": [
      {
        "type": "command",
        "value": ".help",
        "timestamp": "2025-01-01T12:00:10"
      }
    ]
  },
  {
    "timestamp": "2025-01-01T12:00:20",
    "user_query": "Покажи пример кода",
    "response": "Вот пример:\n```python\nprint('Hello')\n```",
    "chunks": ["Вот ", "пример:\n", "```python\n", "print('Hello')\n", "```"],
    "metadata": {},
    "user_actions": [
      {
        "type": "query",
        "value": "Покажи пример кода",
        "timestamp": "2025-01-01T12:00:20"
      },
      {
        "type": "code_block",
        "value": "1",
        "timestamp": "2025-01-01T12:00:25"
      }
    ]
  }
]
```

### Типы действий

- `query` - Обычный запрос к LLM
- `command` - Команда через точку (.help, .ls, .exit и т.д.)
- `code_block` - Выполнение блока кода по номеру (1, 2, 3 и т.д.)

## Интеграция с CLI

В `run_dialog_mode()` добавлена проверка robot mode:

```python
# Проверяем режим robot
is_robot_mode = chat_client.demo_manager and chat_client.demo_manager.is_robot_mode()

# Main dialog loop
while True:
    # В режиме robot автоматически получаем следующее действие
    if is_robot_mode:
        player = chat_client.demo_manager.get_player()
        if player:
            action = player.get_next_user_action()
            if action:
                user_prompt = action['value']
                console.print("[dim]>[/dim] ", end='')

                # Эмуляция печати
                from penguin_tamer.demo_recorder import _simulate_human_typing
                _simulate_human_typing(user_prompt, console)

                # Пауза перед "нажатием Enter"
                import time
                time.sleep(0.3)
            else:
                # Нет больше действий
                console.print("[dim]Demo завершено[/dim]")
                break
    else:
        # Обычный режим - запрос ввода у пользователя
        user_prompt = input_formatter.get_input(...)
```

## API

### DemoManager

```python
class DemoManager:
    def is_robot_mode(self) -> bool:
        """Проверяет, включен ли режим robot."""
        return self.demo_mode == 'robot'
```

### DemoPlayer

```python
class DemoPlayer:
    def get_next_user_action(self) -> Optional[Dict[str, str]]:
        """
        Получает следующее действие пользователя.

        Returns:
            {'type': 'query/command/code_block', 'value': '...', 'timestamp': '...'}
            или None
        """
```

### Вспомогательные функции

```python
def _simulate_human_typing(text: str, console=None) -> None:
    """
    Имитирует печать человека с неравномерными задержками.

    Args:
        text: Текст для печати
        console: Rich console (если None - используется print)
    """
```

## Примеры использования

### Пример 1: Простая демонстрация

```bash
# 1. Создание записи
penguin-tamer --demo-mode record --demo-file tutorial.json

# Введите:
# > Привет!
# > .help
# > Покажи пример Python

# 2. Воспроизведение
penguin-tamer --demo-mode robot --demo-file tutorial.json
```

### Пример 2: Программное использование

```python
from penguin_tamer.demo_recorder import DemoManager, _simulate_human_typing
from rich.console import Console

# Создание менеджера
demo_manager = DemoManager(
    demo_mode='robot',
    demo_file='my_demo.json'
)

# Получение плеера
player = demo_manager.get_player()

console = Console()

# Воспроизведение действий
while True:
    action = player.get_next_user_action()
    if not action:
        break

    # Эмуляция ввода
    console.print("> ", end='')
    _simulate_human_typing(action['value'], console)
    print()  # Перевод строки после "Enter"

    # Обработка действия
    # process_user_input(action['value'])
```

### Пример 3: Тестирование

```python
def test_robot_mode():
    """Тест полной автоматизации."""
    demo_manager = DemoManager(
        demo_mode='robot',
        demo_file='test_session.json'
    )

    player = demo_manager.get_player()
    actions = []

    while True:
        action = player.get_next_user_action()
        if not action:
            break
        actions.append(action)

    # Проверяем, что все действия получены
    assert len(actions) == 4
    assert actions[0]['type'] == 'query'
    assert actions[1]['type'] == 'command'
    assert actions[2]['type'] == 'query'
    assert actions[3]['type'] == 'code_block'
```

## Преимущества

1. **Реалистичность** - Эмуляция человеческой печати с паузами делает демонстрацию естественной
2. **Полная автоматизация** - Не требует участия оператора
3. **Воспроизводимость** - Всегда одинаковая последовательность действий
4. **Тестирование** - Идеально для автоматического тестирования UI
5. **Обучение** - Можно создавать обучающие демонстрации
6. **Продолжение работы** - После завершения записи программа переходит в обычный режим диалога

## Ограничения

1. **Фиксированная запись** - Нельзя отклониться от записанного сценария во время воспроизведения
2. **Время выполнения** - Задержки печати и паузы между действиями увеличивают время выполнения

## Отличия от режима play

| Аспект | Play Mode | Robot Mode |
|--------|-----------|------------|
| Ввод пользователя | Ручной | Автоматический |
| Эмуляция печати | Нет | Да, побуквенно |
| Паузы между действиями | Нет | 3-4 секунды |
| Ответы LLM | Из записи | Из записи |
| Продолжение после записи | Ручной ввод | Ручной ввод |
| Интерактивность | Да | Частичная |
| Применение | Ускорение разработки | Демонстрация, тестирование |

## Смотрите также

- [DEMO_MODE.md](DEMO_MODE.md) - Общая информация о demo mode
- [DEMO_USER_ACTIONS.md](DEMO_USER_ACTIONS.md) - Запись действий пользователя
- [DEMO_TIMESTAMP_FEATURE.md](DEMO_TIMESTAMP_FEATURE.md) - Нумерация файлов сессий

## История изменений

### v1.3.0 (2025-01-11)
- Приглашение `>>>` теперь выводится сразу, а пауза идет перед началом печати текста
- Улучшена реалистичность: видно что робот "думает" перед тем как начать печатать

### v1.2.0 (2025-01-11)
- Добавлено красивое приглашение `>>>` (оранжевый цвет) вместо простого `>`
- Команды с точкой теперь подсвечиваются: `.` (серый) + `команда` (бирюзовый)
- Функция `_simulate_human_typing()` теперь поддерживает параметр `style`

### v1.1.0 (2025-01-11)
- Добавлены паузы 3-4 секунды между действиями (кроме первого)
- После завершения записи программа остается в режиме диалога вместо выхода
- Удалено сообщение "Demo завершено"

### v1.0.0 (2025-01-10)
- Первая версия robot mode
- Реализована функция `_simulate_human_typing()`
- Добавлен метод `get_next_user_action()`
- Интеграция с `run_dialog_mode()`
- Документация и примеры
