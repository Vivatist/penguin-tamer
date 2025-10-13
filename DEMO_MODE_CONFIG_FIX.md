# Исправление: Демо режим из конфига + корректное завершение

## ✅ Проблемы и решения

### Проблема 1: demo_mode из конфига не применялся
**Симптом:** При установке `demo_mode: robot` в config.yaml программа работала в обычном режиме.

**Причина:** Код проверял только аргументы командной строки:
```python
if hasattr(args, 'demo_mode') and args.demo_mode:  # ❌ Только args
    demo_manager = DemoManager(...)
```

**Решение:** Добавлена проверка конфига (строки 527-544):
```python
# Проверяем сначала аргументы командной строки
if hasattr(args, 'demo_mode') and args.demo_mode:
    demo_mode = args.demo_mode
    demo_file = args.demo_file
# Если в args нет, проверяем конфиг
elif config.get("global", "demo_mode") and config.get("global", "demo_mode") != "off":
    demo_mode = config.get("global", "demo_mode")
    demo_file = config.get("global", "demo_file", "demo_session.json")

# Создаем DemoManager если режим определен
if demo_mode:
    demo_manager = DemoManager(mode=demo_mode, demo_file=demo_file, console=console)
```

**Результат:** ✅ Демо режим теперь читается из конфига

---

### Проблема 2: Программа зависала после окончания robot mode
**Симптом:** После выполнения всех actions в robot mode программа не завершалась.

**Причина:** Код переключался в обычный режим и вызывал `input_formatter.get_input()`:
```python
else:
    # Нет больше действий - переходим в обычный режим ❌
    is_robot_mode = False
    robot_presenter = None

# Обычный режим - запрашиваем ввод у пользователя
user_prompt = input_formatter.get_input(...)  # ← Зависает здесь!
```

**Решение:** Возвращаем специальный маркер для выхода (строки 348-350):
```python
else:
    # Robot mode finished - no more actions
    # Return special marker to exit the dialog loop
    return None, False, None, last_code_blocks  # ✅ Маркер выхода
```

И обрабатываем его в main loop (строки 405-407):
```python
# Check if robot mode finished (no more actions)
if user_prompt is None and not is_robot_mode and robot_presenter is None:
    break  # ✅ Выход из цикла
```

**Результат:** ✅ Программа корректно завершается после robot mode

---

## 📊 Изменения по файлам

### cli.py (src/penguin_tamer/cli.py)

**1. Строки 527-544:** Чтение demo_mode из конфига
```python
# Было:
if hasattr(args, 'demo_mode') and args.demo_mode:
    demo_manager = DemoManager(...)

# Стало:
demo_mode = None
demo_file = None

if hasattr(args, 'demo_mode') and args.demo_mode:
    demo_mode = args.demo_mode
    demo_file = args.demo_file
elif config.get("global", "demo_mode") and config.get("global", "demo_mode") != "off":
    demo_mode = config.get("global", "demo_mode")
    demo_file = config.get("global", "demo_file", "demo_session.json")

if demo_mode:
    demo_manager = DemoManager(...)
```

**2. Строки 348-350:** Возврат маркера завершения robot mode
```python
# Было:
else:
    is_robot_mode = False
    robot_presenter = None

# Стало:
else:
    return None, False, None, last_code_blocks
```

**3. Строки 405-407:** Обработка завершения robot mode
```python
# Добавлено:
if user_prompt is None and not is_robot_mode and robot_presenter is None:
    break
```

---

## 🧪 Тестирование

### 1. Проверка чтения конфига
```bash
$ python -c "from penguin_tamer.config_manager import config; print(config.get('global', 'demo_mode'))"
robot
```

### 2. Запуск с конфигом
```bash
$ python -m penguin_tamer  # Без аргументов, использует config.yaml
[Code #1]
...
>>> .ping 8.8.8.8
...
>>> Exit code: 0

# Программа завершается автоматически ✅
```

### 3. Все тесты проходят
```bash
$ python -m pytest tests/ -v
====================== 118 passed, 4 warnings in 19.67s =======================
```

---

## 📝 Примечания

### Приоритет настроек
1. **Аргументы командной строки** (высший приоритет)
   ```bash
   python -m penguin_tamer --demo-mode play --demo-file session.json
   ```

2. **Конфиг config.yaml** (если args не указаны)
   ```yaml
   global:
     demo_mode: 'robot'
     demo_file: demo_session_1.json
   ```

3. **Значение по умолчанию** (demo_mode = 'off')

### Расположение файлов
- **Конфиг:** `C:/Users/Andrey/AppData/Local/penguin-tamer/penguin-tamer/config.yaml`
- **Demo файлы:** `C:/Users/Andrey/AppData/Local/penguin-tamer/penguin-tamer/`

Относительные пути в `demo_file` резолвятся относительно config директории.

---

## ✅ Итоги

- ✅ demo_mode читается из конфига
- ✅ Программа корректно завершается после robot mode
- ✅ Все 118 тестов проходят
- ✅ Backward compatible (args имеют приоритет над конфигом)
- ✅ Нет изменений в public API

**Статус:** ГОТОВО! 🚀
