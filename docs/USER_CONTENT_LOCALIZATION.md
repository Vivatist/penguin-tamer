# Автоматическая локализация user_content

## Обзор

В Penguin Tamer реализована система автоматической локализации параметра `user_content` (системного промпта для LLM). Эта система автоматически переводит `user_content` при смене языка интерфейса, но сохраняет пользовательские изменения.

## Возможности

- ✅ **Автоматическая локализация**: При создании конфигурации `user_content` устанавливается на языке системы
- ✅ **Умное переключение**: При смене языка `user_content` обновляется автоматически
- ✅ **Защита изменений**: Если пользователь изменил `user_content`, изменения сохраняются при смене языка
- ✅ **Поддержка языков**: Английский (en) и Русский (ru)

## Как это работает

### 1. При создании конфигурации

Когда пользователь запускает приложение впервые:

```python
# Определяется язык системы
system_language = detect_system_language(["en", "ru"])  # например, "ru"

# user_content устанавливается на этом языке
user_content = get_default_user_content(system_language)
```

### 2. При смене языка в меню

Когда пользователь переключает язык в меню настроек:

```python
# Вызывается метод
config.set_language("en")

# Внутри происходит проверка
if is_default_user_content(current_user_content):
    # user_content не изменён пользователем - переводим
    config.user_content = get_default_user_content("en")
else:
    # user_content изменён - сохраняем как есть
    pass
```

### 3. Определение изменений

Система проверяет, совпадает ли текущий `user_content` с дефолтным значением для любого языка:

```python
# Эти тексты считаются дефолтными
DEFAULT_USER_CONTENT = {
    "en": "You are a professional in Linux and Windows...",
    "ru": "Ты - профессионал в Linux и Windows..."
}

# Проверка
is_default = is_default_user_content(current_content)
# True - если совпадает с любым дефолтным
# False - если текст был изменён
```

## Примеры использования

### Пример 1: Обычное переключение языка

```python
from penguin_tamer.config_manager import config

# Изначально на русском
config.set_language("ru")
print(config.user_content)
# "Ты - профессионал в Linux и Windows..."

# Переключаемся на английский
config.set_language("en")
print(config.user_content)
# "You are a professional in Linux and Windows..."
```

### Пример 2: С пользовательскими изменениями

```python
from penguin_tamer.config_manager import config

# Устанавливаем кастомный промпт
config.user_content = "You are my custom AI assistant"

# Переключаем язык - кастомный текст сохраняется
config.set_language("ru")
print(config.user_content)
# "You are my custom AI assistant"  ← не изменился!
```

### Пример 3: Проверка, является ли контент дефолтным

```python
from penguin_tamer.i18n_content import is_default_user_content

# Проверка текущего контента
if is_default_user_content(config.user_content):
    print("Используется дефолтный текст")
else:
    print("Пользователь изменил текст")
```

## Архитектура

### Модуль `i18n_content.py`

Содержит:
- `DEFAULT_USER_CONTENT` - словарь с переводами для каждого языка
- `get_default_user_content(language)` - получение дефолтного текста для языка
- `is_default_user_content(content, language=None)` - проверка, является ли текст дефолтным

### Модуль `config_manager.py`

Содержит:
- `set_language(new_language)` - метод для смены языка с умной локализацией
- `_ensure_config_exists()` - устанавливает локализованный `user_content` при создании конфига

### Модуль `config_menu.py`

Обновлён метод `set_language()` для использования `config.set_language()`.

## Добавление нового языка

Чтобы добавить поддержку нового языка:

1. Добавьте перевод в `i18n_content.py`:

```python
DEFAULT_USER_CONTENT = {
    "en": "You are a professional...",
    "ru": "Ты - профессионал...",
    "de": "Sie sind ein Profi...",  # Новый язык
}
```

2. Обновите список поддерживаемых языков в `i18n.py`:

```python
supported_languages = ["en", "ru", "de"]
```

3. Готово! Система автоматически начнёт использовать новый перевод.

## Тестирование

Система покрыта тестами:

```bash
# Тесты модуля i18n_content
pytest tests/test_i18n_content.py -v

# Интеграционные тесты
pytest tests/test_config_language_switch.py -v
```

Всего 12 тестов проверяют:
- ✅ Получение дефолтного контента для разных языков
- ✅ Определение изменённого контента
- ✅ Автоматическое переключение при смене языка
- ✅ Сохранение пользовательских изменений
- ✅ Обработку пробелов и форматирования

## Технические детали

### Почему не используется простое сравнение строк?

Система использует `strip()` при сравнении, чтобы игнорировать различия в пробелах и переносах строк:

```python
content.strip() == default.strip()
```

Это позволяет корректно определять дефолтный контент даже если YAML добавил дополнительные пробелы.

### Что происходит при частичном изменении?

Любое изменение дефолтного текста защищает его от автоперевода:

```python
# Дефолтный текст + дополнение
modified = DEFAULT_USER_CONTENT["en"] + "\nP.S. Be helpful!"

# Считается изменённым
is_default_user_content(modified)  # False
```

### Безопасность данных

- Все проверки происходят локально
- Пользовательский контент никогда не отправляется никуда
- При неоднозначности система сохраняет текущий контент (безопасное поведение)

## Заключение

Система автоматической локализации `user_content` обеспечивает удобство использования для пользователей на разных языках, при этом уважая их кастомизации. Это достигается через умную проверку изменений и безопасное поведение по умолчанию.
