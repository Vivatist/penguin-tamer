# 🔍 Debug Mode Quick Reference

## Включение режима отладки

### Способ 1: Переменная окружения (быстро)
```bash
# Linux/macOS
export PT_DEBUG=1
pt "ваш запрос"

# Windows PowerShell
$env:PT_DEBUG="1"
pt "ваш запрос"
```

### Способ 2: Конфиг (постоянно)
```bash
pt --settings
# Или вручную отредактируйте config.yaml:
# global:
#   debug_mode: true
```

## Что показывает

- 🎯 Все сообщения, отправляемые в LLM API
- 🎨 Цветовая кодировка по ролям (system/user/assistant)
- 📊 Статистика: количество сообщений и символов
- 🔢 Нумерация сообщений
- ✂️ Автообрезка длинных текстов (>500 символов)

## Пример вывода

```
================================================================================
🔍 LLM Request Debug | Model: microsoft/mai-ds-r1:free | Temp: 0.8
================================================================================

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⚙️ Message #1: SYSTEM             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Your name is Penguin Tamer...     │
└───────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 👤 Message #2: USER               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ALWAYS number code blocks...      │
└───────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 👤 Message #3: USER               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Как создать файл в Linux?         │
└───────────────────────────────────┘

Total messages: 3 | Total characters: 423
================================================================================
```

## Программное использование

```python
from penguin_tamer import debug_print_messages

messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
]

debug_print_messages(messages, model="gpt-4", temperature=0.7)
```

## Тестирование

```bash
cd src/penguin_tamer/tests
python test_debug_messages.py
```

## Отключение

```bash
unset PT_DEBUG          # Linux/macOS
Remove-Item Env:PT_DEBUG  # Windows PowerShell
```

📚 Полная документация: [DEBUG_GUIDE.md](DEBUG_GUIDE.md)
