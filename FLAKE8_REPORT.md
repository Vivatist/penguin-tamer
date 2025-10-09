# Отчёт flake8: Анализ качества кода

**Дата:** 2025-10-09
**Проверено:** `src/` и `tests/`
**Всего проблем:** 567

---

## Сводка по категориям

### 🔴 Критические ошибки (требуют исправления)

| Код | Описание | Количество |
|-----|----------|------------|
| **E402** | Module level import not at top of file | 12 |
| **E501** | Line too long (>120 characters) | 19 |
| **F401** | Imported but unused | 16 |
| **F841** | Variable assigned but never used | 8 |
| **E722** | Bare 'except' without exception type | 5 |

**Итого критических:** 60

### 🟡 Форматирование (PEP 8)

| Код | Описание | Количество |
|-----|----------|------------|
| **W293** | Blank line contains whitespace | 432 |
| **W291** | Trailing whitespace | 44 |
| **E302** | Expected 2 blank lines, found 0/1 | 13 |
| **E303** | Too many blank lines | 3 |
| **E305** | Expected 2 blank lines after class/function | 3 |
| **W292** | No newline at end of file | 3 |

**Итого форматирование:** 498

### 🔵 Стиль кода

| Код | Описание | Количество |
|-----|----------|------------|
| **E128** | Continuation line under-indented | 2 |
| **E129** | Visually indented line with same indent | 1 |
| **E251** | Unexpected spaces around keyword equals | 2 |
| **E265** | Block comment should start with '# ' | 1 |
| **E306** | Expected 1 blank line before nested definition | 1 |
| **E731** | Don't assign lambda, use def | 1 |
| **F824** | Global unused | 1 |

**Итого стиль:** 9

---

## Детальная разбивка по файлам

### 📁 src/penguin_tamer/

#### Файлы с критическими ошибками:

1. **menu/help_content.py**
   - `E501` (4): Строки >120 символов
   - `W291` (4): Trailing whitespace

2. **settings_overview.py**
   - `F401` (1): Unused import `Text`
   - `E501` (2): Строки >120 символов
   - `W293` (6): Blank lines with whitespace

3. **system_info.py**
   - `E302` (1): Missing blank lines
   - `E305` (1): Missing blank lines after function
   - `E501` (1): Line too long

4. **text_utils.py**
   - `F401` (1): Unused import `platform`

5. **menu/widgets.py**
   - `E129` (1): Indentation issue
   - `W291` (1): Trailing whitespace

6. **themes.py**, **prompts.py**, **menu/info_panel.py**, **menu/intro_screen.py**
   - Множественные `W293`: Blank lines with whitespace
   - Множественные `W291`: Trailing whitespace

### 📁 tests/

#### Файлы с критическими ошибками:

1. **test_command_executor.py**
   - `E402` (2): Imports not at top (sys.path manipulation)
   - `E501` (2): Lines >120 characters
   - `W291` (1): Trailing whitespace
   - `W293` (48): Blank lines with whitespace

2. **test_llm_client.py**
   - `F841` (1): Unused variable `mock_request`
   - `E303` (1): Too many blank lines
   - `W293` (40): Blank lines with whitespace

3. **demo_error_output.py**
   - `F401` (1): Unused import `os`
   - `E402` (2): Imports not at top

4. **conftest.py**
   - `F401` (1): Unused import `os`

5. **run_tests.py**
   - `W293` (6): Blank lines with whitespace

---

## Приоритетные исправления

### 1. Критичные (требуют кода)

#### E402: Imports not at top of file
```python
# tests/test_command_executor.py, tests/demo_error_output.py
# Проблема: sys.path.insert() перед импортами

# ПЛОХО:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from rich.console import Console

# ХОРОШО:
import sys
from pathlib import Path

# Модификация sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Теперь импорты
from rich.console import Console
```

#### F401: Unused imports
```python
# Удалить:
from rich.text import Text  # settings_overview.py
import platform  # text_utils.py
import os  # conftest.py, demo_error_output.py
```

#### E501: Lines too long
```python
# Разбить длинные строки:
content_lines.append(
    f"{t('Max tokens')}: "
    f"[cyan]{config.max_tokens if config.max_tokens is not None else t('unlimited')}[/cyan]"
)
```

#### F841: Unused variables
```python
# tests/test_llm_client.py
# Удалить или использовать:
mock_request = Mock()  # Не используется
```

### 2. Форматирование (автоматически)

Запустить autopep8 или black для автоматического исправления:

```bash
# Автоматическое исправление W291, W293, E302, E303:
autopep8 --in-place --aggressive --aggressive --recursive src/ tests/

# Или использовать black:
black src/ tests/
```

---

## Рекомендации

### Немедленно исправить:
1. ✅ **E402**: Переместить `sys.path` перед импортами
2. ✅ **F401**: Удалить неиспользуемые импорты
3. ✅ **F841**: Удалить неиспользуемые переменные
4. ✅ **E501**: Разбить длинные строки

### Желательно исправить:
5. ⚠️ **W293/W291**: Удалить trailing whitespace (432+44 случая)
6. ⚠️ **E302/E303/E305**: Исправить пустые строки между определениями
7. ⚠️ **E722**: Заменить `except:` на `except Exception:`

### Опционально:
8. 💡 **E129**: Исправить отступы в продолжениях строк
9. 💡 **E731**: Заменить lambda на def где уместно

---

## Команды для исправления

### Автоматическое форматирование:
```bash
# Установить autopep8
pip install autopep8

# Исправить всё автоматически (кроме E501)
autopep8 --in-place --aggressive --aggressive \
  --exclude="*.pyc,__pycache__" \
  --recursive src/ tests/

# Исправить только trailing whitespace:
autopep8 --in-place --select=W291,W293 --recursive src/ tests/
```

### Проверка после исправлений:
```bash
# Повторная проверка
flake8 src/ tests/ --statistics --count

# Только критичные ошибки
flake8 src/ tests/ --select=E4,E5,E7,F --statistics
```

---

## Интеграция в CI/CD

Добавить в `.github/workflows/lint.yml`:

```yaml
- name: Lint with flake8
  run: |
    pip install flake8
    # Остановить сборку на критичных ошибках:
    flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source
    # Предупреждения для остальных:
    flake8 src/ tests/ --count --exit-zero --max-complexity=10 --statistics
```

---

## Метрики после исправлений (прогноз)

### Текущее состояние:
```
Всего проблем:     567
Критичных:          60
Форматирование:    498
Стиль:               9
```

### После автоисправлений:
```
Всего проблем:     ~60  (-89%)
Критичных:          60  (требуют ручного исправления)
Форматирование:      0  (-100%, autopep8)
Стиль:              ~9  (опционально)
```

### После ручных исправлений:
```
Всего проблем:      0
Критичных:          0
Форматирование:     0
Стиль:              0
```

---

**Статус:** 🟡 Требует внимания
**Приоритет:** Высокий (критичные ошибки)
**Время на исправление:** ~2-3 часа (автомат + ручное)
