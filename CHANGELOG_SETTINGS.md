# Changelog: Settings Menu Enhancement

## Добавлены новые настройки в меню

### 1. Режим отладки (Debug Mode)

**Местоположение:** Главное меню настроек → Debug mode

**Функциональность:**
- Включение/выключение режима отладки
- Показывает детальную информацию о запросах и ответах LLM
- Отображает все параметры генерации, заголовки запросов, время выполнения
- Полезно для диагностики проблем с API или тонкой настройки параметров

**Использование:**
```bash
pt --settings
# Выберите "Debug mode" в меню
# Подтвердите включение/выключение
```

**Программный доступ:**
```python
from penguin_tamer.config_manager import config

# Проверка статуса
is_debug = config.debug

# Включить отладку
config.debug = True

# Выключить отладку
config.debug = False
```

**Хранение:** `config.yaml` → `global` → `debug`

---

### 2. Выбор темы оформления (Theme Selection)

**Местоположение:** Главное меню настроек → Theme

**Доступные темы:**
1. **Default (Classic)** - Классическая тема с cyan заголовками и желтым кодом
2. **Monokai (Dark)** - Популярная темная тема Monokai
3. **Dracula (Dark Purple)** - Знаменитая Dracula тема с фиолетовыми акцентами
4. **Nord (Cold Blue)** - Холодная скандинавская Nord палитра
5. **Solarized Dark** - Профессиональная Solarized Dark схема
6. **GitHub (Light)** - Светлая тема в стиле GitHub
7. **Matrix (Green)** - Зеленая Matrix тема для хакеров
8. **Minimal (B&W)** - Минималистичная черно-белая тема

**Функциональность:**
- Изменяет цветовую схему Markdown разметки
- Изменяет тему подсветки синтаксиса в блоках кода
- Применяется при следующем запуске приложения
- Затрагивает: заголовки, код, ссылки, списки, цитаты

**Использование:**
```bash
pt --settings
# Выберите "Theme" в меню
# Выберите желаемую тему из списка
```

**Программный доступ:**
```python
from penguin_tamer.config_manager import config
from penguin_tamer.themes import get_available_themes, get_theme

# Получить список доступных тем
themes = get_available_themes()
# ['default', 'monokai', 'dracula', 'nord', ...]

# Получить текущую тему
current_theme = config.theme

# Установить новую тему
config.theme = 'dracula'

# Получить Theme объект для Rich
theme_obj = get_theme('dracula')
```

**Хранение:** `config.yaml` → `global` → `theme`

---

## Технические детали

### Изменённые файлы:

1. **config_manager.py**
   - Добавлены свойства `debug` и `theme`
   - Оба хранятся в секции `global`
   - Автоматическое сохранение в `config.yaml`

2. **config_menu.py**
   - Добавлен пункт "Theme" в главное меню
   - Добавлен пункт "Debug mode" в главное меню
   - Функция `set_theme()` - выбор темы с красивыми названиями
   - Функция `toggle_debug_mode()` - включение/выключение отладки

3. **locales/ru.json**
   - Добавлены переводы: "Theme", "Select theme", "Debug mode", etc.

4. **locales/template_locale.json**
   - Добавлены шаблоны переводов для других языков

### Значения по умолчанию:

```yaml
global:
  debug: false
  theme: default
```

### Интеграция с themes.py:

Модуль `themes.py` предоставляет:
- `THEMES` - словарь со всеми темами
- `CODE_THEMES` - соответствие темам подсветки синтаксиса
- `get_theme(name)` - получить Theme объект Rich
- `get_code_theme(name)` - получить название темы для Syntax
- `get_available_themes()` - список доступных тем

### Примеры использования:

**Включить отладку и установить тему Dracula:**
```bash
pt --settings
# 1. Выбрать "Debug mode" → Yes
# 2. Выбрать "Theme" → Dracula (Dark Purple)
# 3. Exit
```

**Программная настройка:**
```python
from penguin_tamer.config_manager import config

config.debug = True
config.theme = 'matrix'
config.save()
```

**Проверка конфигурации:**
```bash
pt --settings
# Выбрать "Show current settings"
# Увидите: Debug mode, Theme и другие параметры
```

---

## Roadmap для будущих улучшений:

- [ ] Предпросмотр темы в реальном времени
- [ ] Кастомные темы пользователя
- [ ] Экспорт/импорт тем
- [ ] Автоматический выбор темы по времени суток
- [ ] Уровни отладки (minimal, normal, verbose)
- [ ] Логирование debug информации в файл

---

## Совместимость:

- ✅ Windows (протестировано)
- ✅ Linux (протестировано)
- ✅ macOS (должно работать)
- ✅ Обратная совместимость: старые конфиги без debug/theme работают корректно

## Зависимости:

Никаких новых зависимостей не требуется. Используются существующие:
- `rich` - для тем и отображения
- `inquirer` - для меню
- `yaml` - для конфигурации
