# Миграция настройки play_first_input

## 📋 Что изменилось

Настройка `play_first_input` **перенесена** из `config_demo.yaml` в основной конфиг `config.yaml` и **переименована** в `demo_play_first_input`.

## 🔄 Было → Стало

### Раньше (старый API)
```yaml
# src/penguin_tamer/demo_system/config_demo.yaml
playback:
  play_first_input: true  # ❌ Больше не используется
```

### Теперь (новый API)
```yaml
# config.yaml
global:
  demo_play_first_input: true  # ✅ Новое расположение
```

## 💡 Причина изменения

1. **Логичное расположение**: Настройка управляет поведением приложения, а не техническими параметрами воспроизведения (как timing)
2. **Согласованность**: Другие настройки демо (`demo_mode`, `demo_file`) уже находятся в основном конфиге
3. **Удобство**: Не нужно редактировать внутренний файл `config_demo.yaml`

## 🔧 Как использовать

### В config.yaml
```yaml
global:
  demo_mode: play
  demo_file: demo_session_001.json
  demo_play_first_input: true  # true = показывать первый ввод, false = пропустить
```

### В коде (через API)
```python
from penguin_tamer.demo_system import create_demo_manager

demo_manager = create_demo_manager(
    mode="play",
    console=console,
    config_dir=config_dir,
    demo_file=demo_file,
    play_first_input=True  # ✅ Передаём напрямую
)
```

### В CLI (автоматически)
```python
# В cli.py настройка читается из config.yaml автоматически
demo_manager = create_demo_manager(
    mode=config.get("global", "demo_mode", "off"),
    console=console,
    config_dir=config.user_config_dir,
    demo_file=config.get("global", "demo_file"),
    play_first_input=config.get("global", "demo_play_first_input", True)
)
```

## 📦 API изменения

### create_demo_manager()
```python
# Новая сигнатура
def create_demo_manager(
    mode: str,
    console: Console,
    config_dir: Path,
    demo_file: Optional[Path] = None,
    play_first_input: bool = True  # ✅ Новый параметр
) -> Union[DemoSystemManager, NullDemoManager]:
```

### DemoSystemManager.__init__()
```python
# Новая сигнатура
def __init__(
    self,
    mode: str,
    console: Console,
    config_dir: Path,
    demo_file: Optional[Path] = None,
    play_first_input: bool = True  # ✅ Новый параметр
):
```

### DemoPlayer.__init__()
```python
# Новая сигнатура
def __init__(
    self,
    console: Console,
    config_path: Optional[Path] = None,
    play_first_input: bool = True  # ✅ Новый параметр
):
```

## 🔄 Обратная совместимость

### Значение по умолчанию
Все функции имеют `play_first_input=True` по умолчанию, поэтому старый код продолжит работать:

```python
# Старый код - работает!
demo_manager = create_demo_manager(
    mode="play",
    console=console,
    config_dir=config_dir,
    demo_file=demo_file
    # play_first_input не указан → используется True
)
```

### Миграция тестов
Старые тесты которые модифицировали `config_demo.yaml`:

```python
# ❌ Старый способ
config_data['playback']['play_first_input'] = False
with open(config_demo_path, 'w') as f:
    yaml.dump(config_data, f)
demo_manager = create_demo_manager(...)
```

Новые тесты передают параметр напрямую:

```python
# ✅ Новый способ
demo_manager = create_demo_manager(
    ...,
    play_first_input=False  # Передаём напрямую
)
```

## 📁 Изменённые файлы

### Код
- ✅ `src/penguin_tamer/demo_system/manager.py` - добавлен параметр `play_first_input`
- ✅ `src/penguin_tamer/demo_system/player.py` - добавлен параметр `play_first_input`
- ✅ `src/penguin_tamer/cli.py` - читает `demo_play_first_input` из config.yaml
- ✅ `src/penguin_tamer/demo_system/config_demo.yaml` - удалена строка `play_first_input`

### Конфиги
- ✅ `config.yaml` - добавлена настройка `demo_play_first_input: true`

### Тесты (обновлены)
- ✅ `test_play_first_input_final.py` - использует новый API
- ✅ `test_two_phase_spinner.py` - использует новый API

## ✅ Проверка

### Тест 1: Новый API
```bash
python test_play_first_input_final.py
```
Ожидаемый результат:
- TEST 1: Показывает первый ввод
- TEST 2: Пропускает первый ввод

### Тест 2: Импорт
```bash
python -c "from penguin_tamer.demo_system import create_demo_manager; print('OK')"
```
Ожидаемый результат: `OK`

### Тест 3: Основная программа
```bash
# Отредактируйте config.yaml:
# demo_play_first_input: false

python -m penguin_tamer
```
Ожидаемый результат: демо начинается сразу с ответа LLM

## 💡 Рекомендации

1. **Для разработки**: Используйте `demo_play_first_input: true` для полного контекста
2. **Для презентаций**: Используйте `demo_play_first_input: false` для быстрого старта
3. **Для тестов**: Передавайте параметр напрямую в `create_demo_manager()`

## 📚 Связанные документы

- `docs/DEMO_TWO_PHASE_SPINNER.md` - документация спиннера
- `SPINNER_SUMMARY.md` - итоговая сводка по спиннеру
- `src/penguin_tamer/demo_system/config_demo.yaml` - конфигурация воспроизведения (timing)

---

**Дата изменения**: Октябрь 2025
**Версия**: 2.1
