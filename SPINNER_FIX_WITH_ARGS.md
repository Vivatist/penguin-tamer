# Исправлено: Спиннер сразу закрывался при запуске с аргументами

## Проблема

При запуске в robot mode:
- **Без аргументов**: Спиннер показывается 10 секунд ✅
- **С аргументами** (с промптом): Спиннер сразу закрывается ❌

## Причина

При запуске с аргументами (например, `python -m penguin_tamer "текст промпта"`), этот промпт передавался как `initial_user_prompt` в `run_dialog_mode()`.

**Проблема в порядке выполнения:**

```python
# БЫЛО:
def run_dialog_mode(chat_client, console, initial_user_prompt=None):
    # 1. Обработать initial_user_prompt (если есть)
    last_code_blocks = _process_initial_prompt(chat_client, console, initial_user_prompt)

    # 2. Потом проверить robot mode
    is_robot_mode, robot_presenter = _setup_robot_presenter(chat_client, console)
```

### Что происходило:

1. **В robot mode с аргументами**:
   - `initial_user_prompt` не пустой (текст из командной строки)
   - Вызывается `_process_initial_prompt()`
   - Внутри вызывается `_process_ai_query()` с **обычным** спиннером (не robot)
   - Обычный спиннер быстро закрывается
   - Ответ обрабатывается в обычном режиме

2. **После этого**:
   - Создается `robot_presenter`
   - Но первый query уже обработан обычным способом!
   - Robot mode начинается со второго действия из файла

### Почему без аргументов работало:

- `initial_user_prompt = None`
- `_process_initial_prompt()` ничего не делает
- Robot mode начинается с первого действия из файла
- Используется robot presenter с 10-секундным спиннером

## Решение

Проверяем robot mode **ДО** обработки initial_prompt и пропускаем его в robot mode:

```python
# СТАЛО:
def run_dialog_mode(chat_client, console, initial_user_prompt=None):
    # 1. Проверить robot mode ПЕРВЫМ делом
    is_robot_mode_check = chat_client.demo_manager and chat_client.demo_manager.is_robot_mode()

    # 2. Обработать initial_prompt ТОЛЬКО если НЕ robot mode
    if not is_robot_mode_check:
        last_code_blocks = _process_initial_prompt(chat_client, console, initial_user_prompt)
    else:
        last_code_blocks = []  # В robot mode все действия из файла

    # 3. Создать robot presenter
    is_robot_mode, robot_presenter = _setup_robot_presenter(chat_client, console)
```

### Логика:

- **В обычном режиме**: `initial_user_prompt` обрабатывается как обычно
- **В robot mode**: `initial_user_prompt` **игнорируется**, все действия берутся из файла демо

## Результат

✅ **Теперь работает правильно:**

```bash
# Запуск без аргументов
python -m penguin_tamer --demo-mode robot --demo-file session_2.json
# → Спиннер 10 секунд ✅

# Запуск с аргументами (любыми)
python -m penguin_tamer --demo-mode robot --demo-file session_2.json "какой-то текст"
# → Спиннер 10 секунд ✅ (аргумент игнорируется в robot mode)
```

## Тесты

Все 118 тестов проходят ✅

## Почему это правильно

В **robot mode** весь сценарий определяется содержимым demo файла:
- Все действия пользователя (queries, commands, code blocks)
- Все ответы LLM
- Вся последовательность взаимодействия

Передача `initial_user_prompt` через аргументы командной строки не имеет смысла в robot mode - это режим **воспроизведения записанной сессии**, а не интерактивный режим.

## Дополнительно

Если нужно передать начальный промпт в **record mode**, это работает как и раньше:

```bash
# Record mode с начальным промптом - работает
python -m penguin_tamer --demo-mode record --demo-file new.json "Привет, как дела?"
# → Сразу отправляет запрос "Привет, как дела?" в LLM и записывает в new.json
```
