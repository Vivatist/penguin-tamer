# Demo System - Краткая справка

## 🎯 Использование

### 1. Импорт

```python
from penguin_tamer.demo_system import create_demo_manager
```

### 2. Создание (один раз при запуске)

```python
demo_manager = create_demo_manager(
    mode=config.get("global", "demo_mode", "off"),  # "off", "record", "play"
    console=console,
    config_dir=config.user_config_dir,
    demo_file=config.get("global", "demo_file")
)
```

### 3. Play режим (если нужно)

```python
if demo_manager.is_playing():
    demo_manager.play()  # Воспроизводит и завершается
    return
```

### 4. Запись событий (БЕЗ if!)

```python
# Промпт
demo_manager.record_prompt(has_code_blocks=False)

# Ввод пользователя
demo_manager.record_user_input("Hello", input_type="query")  # "query", "command", "code_block"

# LLM ответ
demo_manager.record_llm_response_start("AI thinking...")
demo_manager.record_llm_chunk("Hello ")
demo_manager.record_llm_chunk("world")
demo_manager.record_llm_response_end()

# Команда
demo_manager.record_command_output(".ping 8.8.8.8", "pong", 0, True)

# Блок кода
demo_manager.record_code_block_output(1, "echo test", "test", 0, True)

# Завершение
demo_manager.finalize()
```

## 🔑 Ключевые моменты

1. **Null Object Pattern** - вызывайте методы БЕЗ `if demo_manager:` проверок
2. **create_demo_manager()** - возвращает активный или Null-объект
3. **Автоматическая нумерация** - файлы `demo_session_001.json`, `demo_session_002.json`
4. **Настраиваемость** - все задержки в `config_demo.yaml`

## 📝 Конфигурация

### default_config.yaml

```yaml
global:
  demo_mode: "off"  # off, record, play
  demo_file: null   # Путь к файлу или null (последний)
```

### config_demo.yaml

```yaml
playback:
  typing_delay_per_char: 0.03  # Скорость печати
  chunk_delay: 0.01            # Скорость LLM
  spinner_duration: 2.0         # Длительность спиннера
```

## 🚀 Быстрый старт

### Запись

```bash
# В config.yaml: demo_mode: "record"
python -m penguin_tamer
# Работайте как обычно
# Файл сохранится в <config_dir>/demo/demo_session_001.json
```

### Воспроизведение

```bash
# В config.yaml: demo_mode: "play"
python -m penguin_tamer
# Программа воспроизведет и завершится
```

## 📚 Полная документация

- `src/penguin_tamer/demo_system/README.md` - подробная документация
- `DEMO_SYSTEM_NULL_OBJECT.md` - примеры интеграции без if
- `DEMO_SYSTEM_IMPLEMENTATION.md` - детали реализации
