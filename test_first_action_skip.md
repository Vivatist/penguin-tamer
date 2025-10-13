# Тест: Пропуск первого пользовательского запроса (query) в robot mode

## Изменения

### 1. `robot_presenter.py`
Добавлен параметр `skip_user_input` в метод `present_action()`:
- Если `skip_user_input=True`, пропускаются фазы 1-5 (показ промпта, печать, пауза)
- Сразу показывается спиннер и ответ LLM (фаза 6)
- Первое сообщение пользователя остаётся в JSON, но не выводится на экран
- **ВАЖНО**: `action_count` инкрементируется только при показе ввода пользователя

### 2. `cli.py`
Добавлена логика отслеживания первого **query** действия:
- Переменная `skip_first_query` инициализируется как `True` при старте robot mode
- Передаётся в `_get_user_input()` → `_handle_robot_action()` → `present_action()`
- **КРИТИЧНО**: Пропускается только первый **query**, НЕ command или code_block!
- После первого query устанавливается в `False`

## Результат

Для вашего `session_2.json`:

**До изменений:**
```
>>> Проверка режима Робот
[спиннер]
[Code #1]...

>>> 1
[выполняется код]

>>> .ping 8.8.8.8
[выполняется команда]
```

**После изменений:**
```
[спиннер]
[Code #1]...           ← Сразу показывается ответ на первый query

>>> 1                  ← Показывается ввод номера блока!
[выполняется код]

>>> .ping 8.8.8.8      ← Показывается команда!
[выполняется команда]
```

## Исправление бага #2: code_block и command тоже пропускались

**Проблема**: Первоначально `is_first_robot_action` применялся ко ВСЕМ типам действий (query, command, code_block).

**Решение**: 
1. Переименовал `is_first_robot_action` → `skip_first_query`
2. В `_handle_robot_action()` добавлена проверка типа:
   ```python
   action_type = action.get('type')
   skip_input = is_first_query and action_type == 'query'
   ```
3. Теперь пропускается только первый `query`, все остальные действия показываются

## Логика работы

```python
# В _handle_robot_action()
action_type = action.get('type')

# Skip input only for first query, not for commands or code blocks
skip_input = is_first_query and action_type == 'query'
```

**Типы действий:**
- `query` - вопрос к LLM (первый пропускается)
- `code_block` - выполнение блока кода (всегда показывается)
- `command` - прямая команда (всегда показывается)

## Тесты

Все 118 тестов проходят ✅

## Как протестировать с session_2.json

```bash
# Воспроизвести в robot mode
python -m penguin_tamer --demo-mode robot --demo-file session_2.json

# Ожидаемый результат:
# 1. [спиннер] → [Code #1] echo "..." (без показа "Проверка режима Робот")
# 2. >>> 1 (показывается ввод номера блока)
#    [выполняется команда echo]
# 3. >>> .ping 8.8.8.8 (показывается команда ping)
#    [выполняется ping]
```

## Структура session_2.json

1. **Action 1** (query): "Проверка режима Робот" → ПРОПУСКАЕТСЯ ввод
2. **Action 2** (code_block): "1" → ПОКАЗЫВАЕТСЯ ввод
3. **Action 3** (command): ".ping 8.8.8.8" → ПОКАЗЫВАЕТСЯ ввод
