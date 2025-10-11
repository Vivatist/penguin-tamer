# Запись Действий Пользователя в Demo Mode

## Обзор

Начиная с последней версии, система Demo Mode записывает не только ответы LLM, но и все действия пользователя, включая:
- Команды через точку (`.ls`, `.help`, и т.д.)
- Выбор блоков кода по номерам (1, 2, 3, и т.д.)
- Обычные запросы к LLM

Это позволяет воспроизводить полный контекст сессии при просмотре записей.

## Типы Записей

### 1. Запись с ответом LLM

Обычная запись, когда пользователь делает запрос к LLM:

```json
{
  "timestamp": "2025-10-11T20:32:00",
  "user_query": "Как проверить диск?",
  "response": "Используйте df -h...",
  "chunks": ["Используйте", "..."],
  "metadata": {...},
  "user_actions": [
    {
      "type": "query",
      "value": "Как проверить диск?",
      "timestamp": "2025-10-11T20:32:00"
    }
  ]
}
```

### 2. Запись только действия (NEW!)

Когда пользователь выполняет команду или блок кода БЕЗ запроса к LLM:

```json
{
  "timestamp": "2025-10-11T20:30:00",
  "user_query": "",
  "response": "",
  "chunks": [],
  "metadata": {
    "action_only": true,
    "context": "Exit code: 0, Success: True"
  },
  "user_actions": [
    {
      "type": "code_block",
      "value": "1",
      "timestamp": "2025-10-11T20:30:00"
    }
  ]
}
```

Это гарантирует, что **все действия пользователя записываются**, даже если после них не было запроса к LLM.

## Типы Действий Пользователя

### 1. `command` - Прямые команды через точку

Когда пользователь вводит команду, начинающуюся с точки:

```bash
> .ls -la
> .echo "Hello"
> .pwd
```

Записывается как:
```json
{
  "type": "command",
  "value": ".ls -la",
  "timestamp": "2025-10-11T20:30:45.123456"
}
```

### 2. `code_block` - Выбор блока кода по номеру

Когда пользователь выбирает блок кода для выполнения:

```bash
> 1
> 2
> 3
```

Записывается как:
```json
{
  "type": "code_block",
  "value": "1",
  "timestamp": "2025-10-11T20:31:12.789012"
}
```

### 3. `query` - Запрос к LLM

Когда пользователь задаёт вопрос или даёт инструкцию LLM:

```bash
> Как проверить использование диска?
> Объясни эту команду
> Создай скрипт для архивации
```

Записывается как:
```json
{
  "type": "query",
  "value": "Как проверить использование диска?",
  "timestamp": "2025-10-11T20:32:00.345678"
}
```

## Структура Записи

Каждая запись в demo-файле теперь содержит поле `user_actions`:

```json
{
  "timestamp": "2025-10-11T20:32:00.345678",
  "user_query": "Как проверить использование диска?",
  "response": "Используйте команду `df -h`...",
  "chunks": ["Используйте", " команду", "..."],
  "metadata": {
    "model": "gpt-4.1-mini",
    "temperature": 0.8
  },
  "user_actions": [
    {
      "type": "command",
      "value": ".ls",
      "timestamp": "2025-10-11T20:30:00.000000"
    },
    {
      "type": "code_block",
      "value": "1",
      "timestamp": "2025-10-11T20:31:00.000000"
    },
    {
      "type": "query",
      "value": "Как проверить использование диска?",
      "timestamp": "2025-10-11T20:32:00.000000"
    }
  ]
}
```

## Пример Сессии

### Интерактивная сессия пользователя:

```
> .ls
(выполняется команда ls)

> Что такое файл README.md?
LLM: README.md - это файл с описанием проекта...
[Code #1]
```bash
cat README.md
```

> 1
(выполняется блок #1)

> Покажи содержимое config файла
LLM: Вот пример конфигурации...
```

### Как это записывается:

```json
[
  {
    "timestamp": "2025-10-11T20:00:01",
    "user_query": "Что такое файл README.md?",
    "response": "README.md - это файл с описанием проекта...",
    "chunks": [...],
    "metadata": {...},
    "user_actions": [
      {
        "type": "command",
        "value": ".ls",
        "timestamp": "2025-10-11T20:00:00"
      },
      {
        "type": "query",
        "value": "Что такое файл README.md?",
        "timestamp": "2025-10-11T20:00:01"
      }
    ]
  },
  {
    "timestamp": "2025-10-11T20:01:00",
    "user_query": "Покажи содержимое config файла",
    "response": "Вот пример конфигурации...",
    "chunks": [...],
    "metadata": {...},
    "user_actions": [
      {
        "type": "code_block",
        "value": "1",
        "timestamp": "2025-10-11T20:00:30"
      },
      {
        "type": "query",
        "value": "Покажи содержимое config файла",
        "timestamp": "2025-10-11T20:01:00"
      }
    ]
  }
]
```

## Преимущества

✅ **Полный контекст**: Видно, что делал пользователь между запросами к LLM
✅ **Отладка**: Легко понять последовательность действий
✅ **Обучение**: Можно использовать для создания обучающих материалов
✅ **Аналитика**: Понимание паттернов использования приложения
✅ **Воспроизводимость**: Возможность точно повторить сессию пользователя

## Техническая Реализация

### В DemoManager

Добавлен буфер для накопления действий:

```python
class DemoManager:
    def __init__(self, ...):
        self.pending_user_actions: List[Dict[str, str]] = []

    def add_user_action(self, action_type: str, action_value: str) -> None:
        """Добавляет действие пользователя в буфер."""
        self.pending_user_actions.append({
            'type': action_type,
            'value': action_value,
            'timestamp': datetime.now().isoformat()
        })

    def get_and_clear_user_actions(self) -> List[Dict[str, str]]:
        """Получает накопленные действия и очищает буфер."""
        actions = self.pending_user_actions.copy()
        self.pending_user_actions.clear()
        return actions
```

### В DemoRecorder

Добавлен метод для записи действий без ответа LLM:

```python
class DemoRecorder:
    def record_user_action_only(
        self,
        action_type: str,
        action_value: str,
        context: str = ""
    ) -> None:
        """
        Записывает действие пользователя без ответа LLM.
        Используется для команд через точку и выбора блоков кода.
        """
        demo_response = DemoResponse(
            timestamp=datetime.now().isoformat(),
            user_query="",
            response="",
            chunks=[],
            metadata={'action_only': True, 'context': context},
            user_actions=[{
                'type': action_type,
                'value': action_value,
                'timestamp': datetime.now().isoformat()
            }]
        )
        self.responses.append(demo_response)
        self._save_responses()
```

### В cli.py

Действия записываются сразу после выполнения:

```python
# Блок кода по номеру
result = get_script_executor()(console, code_blocks, block_index)
if chat_client.demo_manager and chat_client.demo_manager.is_recording():
    recorder = chat_client.demo_manager.get_recorder()
    if recorder:
        context = f"Exit code: {result.get('exit_code', -1)}, Success: {result.get('success', False)}"
        recorder.record_user_action_only('code_block', prompt, context)

# Команда через точку
result = get_execute_handler()(console, command)
if chat_client.demo_manager and chat_client.demo_manager.is_recording():
    recorder = chat_client.demo_manager.get_recorder()
    if recorder:
        context = f"Exit code: {result.get('exit_code', -1)}, Success: {result.get('success', False)}"
        recorder.record_user_action_only('command', prompt, context)
```

### В llm_client.py

При записи ответа передаются накопленные действия:

```python
if self._demo_manager and self._demo_manager.is_recording():
    user_actions = self._demo_manager.get_and_clear_user_actions()
    recorder.record_response(
        user_query=user_input,
        response=response,
        chunks=processor.recorded_chunks,
        metadata=metadata,
        user_actions=user_actions
    )
```

## Обратная Совместимость

Старые demo-файлы без поля `user_actions` продолжают работать:

```python
@dataclass
class DemoResponse:
    user_actions: Optional[List[Dict[str, str]]] = None
```

При загрузке старых файлов `user_actions` будет `None` или пустой список.

## Использование в Анализе

### Пример скрипта для анализа действий:

```python
import json
from collections import Counter

with open('demo_sessions/recording.json', 'r') as f:
    data = json.load(f)

# Собираем статистику по типам действий
action_types = []
for entry in data:
    if entry.get('user_actions'):
        action_types.extend([a['type'] for a in entry['user_actions']])

stats = Counter(action_types)
print("Статистика действий:")
for action_type, count in stats.items():
    print(f"  {action_type}: {count}")

# Вывод:
# Статистика действий:
#   query: 15
#   command: 8
#   code_block: 5
```

## См. также

- [DEMO_MODE.md](DEMO_MODE.md) - Полная документация по Demo Mode
- [DEMO_MODE_QUICKSTART.md](DEMO_MODE_QUICKSTART.md) - Быстрый старт
- [DEMO_TIMESTAMP_FEATURE.md](DEMO_TIMESTAMP_FEATURE.md) - Автоматические временные метки
