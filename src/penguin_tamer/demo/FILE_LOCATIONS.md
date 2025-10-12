# Где хранятся demo-файлы?

## 📁 Расположение файлов

Demo-файлы сохраняются в **системной директории конфигурации пользователя**.

### Windows:
```
C:\Users\<Username>\AppData\Local\penguin-tamer\penguin-tamer\
```

### Linux:
```
~/.config/penguin-tamer/
```

### macOS:
```
~/Library/Application Support/penguin-tamer/
```

## 🔍 Как узнать точный путь?

### 1. Посмотреть при записи

При завершении записи программа выводит путь к сохраненному файлу:

```bash
python -m penguin_tamer --demo-mode record --demo-file my_demo.json
# ... работа с программой ...
# При выходе:
Demo recording saved to: C:\Users\Andrey\AppData\Local\penguin-tamer\penguin-tamer\my_demo.json
```

### 2. Через Python

```python
from platformdirs import user_config_dir
print(user_config_dir('penguin-tamer'))
```

### 3. Через API

```python
from penguin_tamer.demo import DemoStorage

storage = DemoStorage()
print("Config directory:", storage.config_dir)
```

## 📝 Именование файлов

### Относительные пути

Если указать относительный путь, файл сохранится в config directory:

```bash
python -m penguin_tamer --demo-mode record --demo-file demo.json
# Сохранится в: C:\Users\...\AppData\Local\penguin-tamer\penguin-tamer\demo.json
```

### Абсолютные пути

Если указать абсолютный путь, файл сохранится там:

```bash
python -m penguin_tamer --demo-mode record --demo-file C:\Temp\demo.json
# Сохранится в: C:\Temp\demo.json
```

### Автоматическая нумерация

Если файл уже существует, добавляется порядковый номер:

```
demo.json       # Первый файл
demo_1.json     # Второй (если demo.json уже есть)
demo_2.json     # Третий
...
```

## 🗂️ Структура demo-файла

Файл сохраняется в формате JSON:

```json
[
  {
    "timestamp": "2024-01-01T12:00:00",
    "user_query": "What is Python?",
    "response": "Python is a programming language...",
    "chunks": ["Python ", "is a ", "programming language..."],
    "metadata": {
      "model": "gpt-4",
      "temperature": 0.7
    },
    "user_actions": [
      {
        "type": "query",
        "value": "What is Python?"
      }
    ]
  }
]
```

## 📋 Примеры использования

### Запись с указанием директории

```bash
# В текущей директории
python -m penguin_tamer --demo-mode record --demo-file ./demo.json

# В произвольной директории
python -m penguin_tamer --demo-mode record --demo-file ~/demos/session_1.json
```

### Воспроизведение

```bash
# Из config directory
python -m penguin_tamer --demo-mode play --demo-file demo.json

# Абсолютный путь
python -m penguin_tamer --demo-mode play --demo-file C:\Demos\demo.json
```

### Список всех demo-файлов

```python
from penguin_tamer.demo import DemoStorage

storage = DemoStorage()
demos = storage.list_sessions()
for demo in demos:
    print(demo)
```

## 🔧 Управление файлами

### Через API

```python
from penguin_tamer.demo import DemoStorage

storage = DemoStorage()

# Список файлов
demos = storage.list_sessions()

# Удаление
storage.delete_session('demo.json')

# Получение уникального имени
unique_path = storage.get_unique_path('demo.json')
```

### Через файловую систему

Можно просто открыть папку:

**Windows:**
```cmd
explorer %LOCALAPPDATA%\penguin-tamer\penguin-tamer
```

**Linux:**
```bash
cd ~/.config/penguin-tamer
```

**macOS:**
```bash
open ~/Library/Application\ Support/penguin-tamer/
```

## 💡 Советы

### 1. Использовать описательные имена

```bash
--demo-file tutorial_basics.json
--demo-file debug_session_2024_01_15.json
--demo-file error_reproduction.json
```

### 2. Организация в поддиректории

```bash
--demo-file tutorials/lesson_1.json
--demo-file bugs/issue_123.json
--demo-file examples/advanced_usage.json
```

### 3. Резервные копии

Рекомендуется сохранять важные demo-файлы вне config directory:

```bash
--demo-file ~/Documents/penguin-demos/important_session.json
```

### 4. Очистка старых файлов

```python
from penguin_tamer.demo import DemoStorage
from pathlib import Path
import time

storage = DemoStorage()
demos = storage.list_sessions()

# Удалить файлы старше 30 дней
for demo in demos:
    path = Path(demo)
    age_days = (time.time() - path.stat().st_mtime) / 86400
    if age_days > 30:
        storage.delete_session(demo)
        print(f"Deleted old demo: {demo}")
```

## ⚙️ Изменение директории по умолчанию

Если нужно изменить директорию по умолчанию, можно создать DemoStorage с другим app_name:

```python
from penguin_tamer.demo import DemoStorage

# Использовать другую директорию
storage = DemoStorage(app_name="my-custom-app")
print(storage.config_dir)
# Windows: C:\Users\...\AppData\Local\my-custom-app\my-custom-app
```

Или указывать абсолютные пути для всех операций.

## 🐛 Troubleshooting

### Не могу найти файл

1. Проверьте, что используете правильный режим:
   ```bash
   --demo-mode record  # Для записи
   --demo-mode play    # Для воспроизведения
   ```

2. Проверьте путь:
   ```python
   from platformdirs import user_config_dir
   print(user_config_dir('penguin-tamer'))
   ```

3. Посмотрите список всех файлов:
   ```python
   from penguin_tamer.demo import DemoStorage
   storage = DemoStorage()
   print(storage.list_sessions())
   ```

### Файл не сохраняется

1. Убедитесь, что есть записанные данные (хотя бы один ответ)
2. Проверьте права доступа к директории
3. Проверьте место на диске

### Старый файл перезаписывается

Это не должно происходить - DemoStorage автоматически добавляет `_1`, `_2` и т.д.
Если это происходит, возможно:
- Используется `auto_sequence=False` в коде
- Файл удаляется между запусками

## 📚 Дополнительно

См. также:
- [API.md](API.md) - Полный API reference
- [README.md](README.md) - Архитектура системы
- [MIGRATION.md](MIGRATION.md) - Миграция со старой версии
