# Проблема: "Первый спиннер почти сразу закрывается"

## Диагностика

### ✅ Код работает правильно
Тестирование показало, что спиннер действительно показывается 10 секунд:
- `test_spinner_timing.py`: 10.01s ✅
- `test_session2_debug.py`: 10.31s ✅

### ❓ Возможные причины проблемы

#### 1. Кэшированный .pyc файл
Найдены два файла:
- `timing.cpython-311.pyc` (Python 3.11)
- `timing.cpython-313.pyc` (Python 3.13)

**Решение**: Удалил кэш
```bash
rm -f src/penguin_tamer/demo/__pycache__/timing.cpython-*.pyc
```

#### 2. Разные версии Python
Если вы запускаете через virtual environment с Python 3.11, а тестируете с Python 3.13, может быть несоответствие.

**Проверка**:
```bash
# Какую версию использует ваше приложение?
python -m penguin_tamer --version

# Или
which python
python --version
```

#### 3. Установлен пакет через pip
Если penguin-tamer установлен через `pip install -e .`, нужно переустановить:
```bash
pip uninstall penguin-tamer
pip install -e .
```

#### 4. Импортируется из другого места
Проверьте, откуда импортируется модуль:
```bash
python -c "import penguin_tamer.demo.timing; print(penguin_tamer.demo.timing.__file__)"
```

Должно быть:
```
c:\Users\Andrey\Coding\penguin-tamer\src\penguin_tamer\demo\timing.py
```

## Как проверить

### Тест 1: Проверка значения напрямую
```bash
cd /c/Users/Andrey/Coding/penguin-tamer
python -c "from penguin_tamer.demo.timing import DEFAULT_ROBOT_TIMING; print('spinner_total_time:', DEFAULT_ROBOT_TIMING.spinner_total_time)"
```

Должно вывести: `spinner_total_time: 10.0`

### Тест 2: Запуск с session_2.json
```bash
python test_session2_debug.py
```

Должен показать: `Total time: ~10.3s` и `✅ Timing is correct!`

### Тест 3: Реальный запуск
```bash
python -m penguin_tamer --demo-mode robot --demo-file "путь/к/session_2.json"
```

## Что делать дальше

1. **Очистите весь кэш Python**:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

2. **Переустановите в editable mode** (если используется):
   ```bash
   pip uninstall penguin-tamer
   pip install -e .
   ```

3. **Запустите тест** и покажите результат:
   ```bash
   python test_session2_debug.py
   ```

4. **Если тест работает, но CLI нет**, проверьте:
   - Запускаете ли через правильный Python?
   - Нет ли алиаса или обертки над командой?
   - Используете ли virtual environment?

## Дополнительная отладка

Добавьте вывод в начало `robot_presenter.py::_show_spinner()`:
```python
def _show_spinner(self) -> None:
    """Show spinner before AI response."""
    total_time = self.timing.spinner_total_time
    print(f"DEBUG: spinner_total_time = {total_time}")  # ← Добавить
    connecting_time = total_time * self.timing.spinner_connecting_ratio
    thinking_time = total_time * self.timing.spinner_thinking_ratio
    # ...
```

Затем запустите robot mode и посмотрите, что выводится.
