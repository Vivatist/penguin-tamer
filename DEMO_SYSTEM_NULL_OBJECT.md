# Demo System - Интеграция без if-проверок

## 🎯 Null Object Pattern

Реализован паттерн **Null Object** для бесшовной интеграции без проверок `if demo_manager:`.

### Как это работает

```python
from penguin_tamer.demo_system import create_demo_manager

# Создаем manager - возвращает либо активный, либо Null-объект
demo_manager = create_demo_manager(
    mode=config.get("global", "demo_mode", "off"),
    console=console,
    config_dir=config.user_config_dir,
    demo_file=config.get("global", "demo_file")
)

# Используем БЕЗ проверок - работает всегда!
demo_manager.record_user_input("Hello")  # Запишет если mode="record", ничего не сделает если mode="off"
demo_manager.record_llm_chunk("chunk")   # То же самое
```

### Преимущества

1. **Чистый код** - нет if-проверок по всему коду
2. **Меньше ошибок** - невозможно забыть проверку
3. **Единообразие** - одинаковый код для всех режимов
4. **Производительность** - пустые вызовы очень быстрые

---

## 📝 Примеры интеграции в cli.py

### 1. Инициализация (один раз)

```python
from penguin_tamer.demo_system import create_demo_manager

def main():
    # ... инициализация конфига, console и т.д.

    # Создаем demo manager (БЕЗ if!)
    demo_manager = create_demo_manager(
        mode=config.get("global", "demo_mode", "off"),
        console=console,
        config_dir=config.user_config_dir,
        demo_file=config.get("global", "demo_file")
    )

    # Если play режим - воспроизвести и выйти
    if demo_manager.is_playing():
        demo_manager.play()
        return

    # Дальше работаем с demo_manager БЕЗ if-проверок!
    run_dialog_mode(chat_client, console, demo_manager)
```

### 2. Использование в коде (без if!)

```python
def run_dialog_mode(chat_client, console, demo_manager):
    """Основной цикл диалога."""

    while True:
        # Записываем промпт - работает всегда, нет if!
        demo_manager.record_prompt(has_code_blocks=bool(last_code_blocks))

        # Получаем ввод
        user_prompt = input_formatter.get_input(console)

        # Записываем ввод - работает всегда!
        demo_manager.record_user_input(user_prompt, input_type="query")

        # Обрабатываем команду
        if user_prompt.startswith('.'):
            result = execute_command(user_prompt)
            # Записываем результат - работает всегда!
            demo_manager.record_command_output(
                command=user_prompt,
                output=result.output,
                exit_code=result.exit_code,
                success=result.success
            )
            continue

        # LLM запрос
        demo_manager.record_llm_response_start("AI thinking...")

        for chunk in stream_chat(user_prompt):
            demo_manager.record_llm_chunk(chunk)
            console.print(chunk, end='')

        demo_manager.record_llm_response_end()

    # Завершение
    demo_manager.finalize()
```

### 3. Полная интеграция

```python
# В начале файла
from penguin_tamer.demo_system import create_demo_manager

# В run_dialog_mode()
def run_dialog_mode(chat_client: OpenRouterClient, console, initial_user_prompt: str = None):
    """Interactive dialog mode."""

    # Создаем demo manager
    demo_manager = create_demo_manager(
        mode=config.get("global", "demo_mode", "off"),
        console=console,
        config_dir=config.user_config_dir,
        demo_file=config.get("global", "demo_file")
    )

    # Play режим - воспроизвести и выйти
    if demo_manager.is_playing():
        demo_manager.play()
        return

    # Setup
    history_file_path = config.user_config_dir / "cmd_history"
    input_formatter = DialogInputFormatter(history_file_path)
    educational_prompt = get_educational_prompt()
    chat_client.init_dialog_mode(educational_prompt)

    last_code_blocks = []

    # Main loop
    while True:
        try:
            # === PROMPT ===
            demo_manager.record_prompt(has_code_blocks=bool(last_code_blocks))

            # === USER INPUT ===
            user_prompt = input_formatter.get_input(console, bool(last_code_blocks), t)

            # Определяем тип ввода
            if user_prompt.startswith('.'):
                input_type = "command"
            elif user_prompt.isdigit():
                input_type = "code_block"
            else:
                input_type = "query"

            demo_manager.record_user_input(user_prompt, input_type)

            # === EXIT CHECK ===
            if _is_exit_command(user_prompt):
                break

            # === COMMAND ===
            if _handle_direct_command(console, chat_client, user_prompt):
                # Внутри _handle_direct_command:
                # result = execute_command(...)
                # demo_manager.record_command_output(cmd, result.output, result.exit_code, result.success)
                continue

            # === CODE BLOCK ===
            if _handle_code_block_execution(console, chat_client, user_prompt, last_code_blocks):
                # Внутри _handle_code_block_execution:
                # result = execute_code_block(...)
                # demo_manager.record_code_block_output(num, code, result.output, result.exit_code, result.success)
                continue

            # === LLM QUERY ===
            demo_manager.record_llm_response_start("AI thinking...")

            # Стриминг с записью чанков
            for chunk in chat_client.stream_chat(user_prompt):
                demo_manager.record_llm_chunk(chunk)
                console.print(chunk, end='')

            demo_manager.record_llm_response_end()

        except KeyboardInterrupt:
            break

    # Финализация
    demo_manager.finalize()
```

---

## 🔄 Сравнение

### До (с if-проверками)

```python
if demo_manager:
    demo_manager.record_prompt(has_code_blocks)

user_prompt = get_input()

if demo_manager:
    demo_manager.record_user_input(user_prompt)

if demo_manager:
    demo_manager.record_llm_response_start()

for chunk in stream:
    if demo_manager:
        demo_manager.record_llm_chunk(chunk)

if demo_manager:
    demo_manager.record_llm_response_end()
```

**Проблемы:**
- 5 if-проверок на одну операцию
- Можно забыть проверку
- Код загроможден

### После (Null Object)

```python
demo_manager.record_prompt(has_code_blocks)
user_prompt = get_input()
demo_manager.record_user_input(user_prompt)
demo_manager.record_llm_response_start()

for chunk in stream:
    demo_manager.record_llm_chunk(chunk)

demo_manager.record_llm_response_end()
```

**Преимущества:**
- Чистый код
- Невозможно забыть вызов
- Одинаково для всех режимов

---

## 🎨 Архитектура

```
┌─────────────────────────────────────────┐
│         cli.py (основной код)           │
│                                         │
│  demo_manager.record_user_input(...)   │ ◄── Всегда вызываем, нет if!
│  demo_manager.record_llm_chunk(...)    │
│  demo_manager.record_command_output()  │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────▼──────────────┐
      │  create_demo_manager()   │
      │     (factory)            │
      └───────────┬──────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼──────┐   ┌────────▼────────┐
│ mode="off"   │   │ mode="record"   │
│              │   │ mode="play"     │
│ Returns:     │   │                 │
│ NullDemo     │   │ Returns:        │
│ Manager      │   │ DemoSystem      │
│              │   │ Manager         │
│ (does        │   │                 │
│  nothing)    │   │ (records/plays) │
└──────────────┘   └─────────────────┘
```

---

## ✅ Чеклист интеграции

- [ ] Импортировать `create_demo_manager`
- [ ] Создать `demo_manager` при инициализации
- [ ] Добавить проверку `if demo_manager.is_playing(): demo_manager.play(); return`
- [ ] Добавить `demo_manager.record_prompt()` перед промптом
- [ ] Добавить `demo_manager.record_user_input()` после ввода
- [ ] Добавить `demo_manager.record_llm_response_start()` перед LLM
- [ ] Добавить `demo_manager.record_llm_chunk()` в цикле стриминга
- [ ] Добавить `demo_manager.record_llm_response_end()` после LLM
- [ ] Добавить `demo_manager.record_command_output()` после команд
- [ ] Добавить `demo_manager.record_code_block_output()` после блоков
- [ ] Добавить `demo_manager.finalize()` при завершении

**Важно:** Везде БЕЗ `if demo_manager:` проверок!

---

## 🚀 Готовность

✅ Null Object Pattern реализован
✅ Фабричная функция `create_demo_manager()`
✅ Интеграция без if-проверок
✅ Чистый и поддерживаемый код

**Статус:** Готово к интеграции! Просто вызывайте методы без проверок.
