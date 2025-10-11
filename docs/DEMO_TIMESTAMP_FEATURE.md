# Автоматическая нумерация демо-файлов

## Обзор

При записи демо-сессий автоматически добавляется порядковый номер к имени файла, что позволяет сохранять все записи без перезаписи.

## Формат нумерации

Формат: `basename_N.ext`, где N - порядковый номер (1, 2, 3, ...)

Пример: `session_1.json`, `session_2.json`, `session_3.json`

## Как это работает

### Режим записи (record)

Когда `demo_mode: "record"`, при создании `DemoRecorder`:

1. Берётся путь из конфигурации: `demo_sessions/session.json`
2. Разрешается в директорию конфига: `%LOCALAPPDATA%\penguin-tamer\demo_sessions\session.json`
3. Находится следующий свободный номер, проверяя существующие файлы
4. Итоговый путь: `%LOCALAPPDATA%\penguin-tamer\demo_sessions\session_1.json` (или 2, 3, и т.д.)

### Алгоритм нумерации

```python
def _add_sequence_number_to_filename(filepath: Path) -> Path:
    stem = filepath.stem
    suffix = filepath.suffix
    parent = filepath.parent

    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
```

Функция проверяет существование файлов с номерами 1, 2, 3, ... и возвращает первый свободный номер.

### Режим воспроизведения (play)

Для воспроизведения укажите полное имя файла с номером:

```yaml
global:
  demo_mode: "play"
  demo_file: "demo_sessions/session_1.json"
```

## Примеры

### Пример 1: Базовое использование

**Конфигурация:**
```yaml
global:
  demo_mode: "record"
  demo_file: "demo_sessions/session.json"
```

**Запуск №1:**
- Создаётся: `session_1.json`

**Запуск №2:**
- Создаётся: `session_2.json`

**Запуск №3:**
- Создаётся: `session_3.json`

**Результат:** Все три записи сохранены с последовательными номерами!

### Пример 2: Организация по типам

```yaml
# Учебные демо
demo_file: "tutorials/lesson1.json"
# → tutorials/lesson1_1.json, lesson1_2.json, lesson1_3.json, ...

# Презентации
demo_file: "presentations/conference.json"
# → presentations/conference_1.json, conference_2.json, conference_3.json, ...

# Тестовые записи
demo_file: "tests/test_session.json"
# → tests/test_session_1.json, test_session_2.json, test_session_3.json, ...
```

### Пример 3: Абсолютные пути

```yaml
demo_file: "C:/Demos/important.json"
# → C:/Demos/important_1.json, important_2.json, important_3.json, ...
```

## Просмотр созданных файлов

### Windows
```cmd
dir %LOCALAPPDATA%\penguin-tamer\demo_sessions
```

### Linux/macOS
```bash
ls -lt ~/.config/penguin-tamer/demo_sessions/
```

## Воспроизведение конкретной записи

1. Найдите нужный файл в директории demo_sessions
2. Скопируйте его полное имя (с номером)
3. Укажите в конфигурации:

```yaml
global:
  demo_mode: "play"
  demo_file: "demo_sessions/session_3.json"  # Третья запись
```

## Технические детали

### Функция `_add_sequence_number_to_filename`

```python
def _add_sequence_number_to_filename(filepath: Path) -> Path:
    """
    Добавляет порядковый номер к имени файла перед расширением.
    Находит следующий свободный номер, проверяя существующие файлы.

    Args:
        filepath: Путь к файлу

    Returns:
        Path: Путь с добавленным порядковым номером

    Example:
        demo.json -> demo_1.json (если demo_1.json не существует)
        demo.json -> demo_2.json (если demo_1.json уже существует)
    """
    stem = filepath.stem
    suffix = filepath.suffix
    parent = filepath.parent

    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
        # Защита от бесконечного цикла (на случай 10000+ файлов)
        if counter > 10000:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{stem}_{timestamp}{suffix}"
            return parent / new_name
```

### Место вызова

Функция вызывается автоматически в `DemoRecorder.__init__()`:

```python
def __init__(self, demo_file: str):
    # Добавляем порядковый номер к имени файла
    base_path = _resolve_demo_path(demo_file)
    self.demo_file = _add_sequence_number_to_filename(base_path)
    self.responses: List[DemoResponse] = []
```

## Преимущества

✅ **Простота** - Короткие и понятные имена файлов (session_1, session_2)
✅ **Не теряются данные** - Каждая запись сохраняется в отдельный файл
✅ **Последовательность** - Легко понять порядок записей
✅ **Компактность** - Не занимают много места в имени файла
✅ **Удобство** - Легко ссылаться на конкретную запись ("session_5")

## Миграция со старой версии

Если у вас есть демо-файлы с временными метками:

1. Они будут продолжать работать в режиме воспроизведения
2. Новые записи будут создаваться с порядковыми номерами
3. При необходимости переименуйте старые файлы вручную:
   - `session_2025-10-11_20-01-28.json` → `session_1.json`
   - `session_2025-10-11_20-12-51.json` → `session_2.json`

## Часто задаваемые вопросы

**Q: Что если я удалю session_2.json? Следующая запись станет session_2 или session_4?**
A: Станет session_2, так как функция ищет первый свободный номер.

**Q: Могу ли я вручную создать session_100.json?**
A: Да, но следующая автоматическая запись получит номер 101.

**Q: Что если у меня уже есть 10000 файлов?**
A: Алгоритм автоматически переключится на временные метки для защиты от бесконечного цикла.

**Q: Можно ли использовать старые файлы с временными метками?**
A: Да, для воспроизведения можно использовать любые файлы, независимо от их имени.

**Q: Сколько места занимают демо-файлы?**
A: Обычно несколько килобайт на сессию. Периодически очищайте старые записи.

## См. также

- [DEMO_MODE.md](DEMO_MODE.md) - Полная документация по Demo Mode
- [DEMO_MODE_QUICKSTART.md](DEMO_MODE_QUICKSTART.md) - Быстрый старт
