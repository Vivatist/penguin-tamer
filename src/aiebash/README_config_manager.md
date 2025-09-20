# Новый менеджер конфигурации (new_config_manager.py)

## Обзор

`new_config_manager.py` - это современный, удобный менеджер конфигурации для приложения ai-ebash. Он автоматически управляет файлами `config.yaml` (текущие настройки) и `default_config.yaml` (настройки по умолчанию).

## Основные возможности

### 🚀 Автоматическое создание конфигурации
- При первом запуске автоматически копирует `default_config.yaml` в `config.yaml`
- Не требует ручной настройки файлов конфигурации

### 📖 Простой доступ к настройкам
```python
from new_config_manager import config

# Чтение основных настроек
current_llm = config.current_llm
temperature = config.temperature
stream_mode = config.stream_mode
user_content = config.user_content
```

### ✏️ Удобное изменение настроек
```python
# Изменение настроек через свойства
config.temperature = 0.7
config.stream_mode = True
config.user_content = "Новый контент для всех LLM"
config.console_log_level = "DEBUG"
```

### 🤖 Управление LLM
```python
# Получение списка доступных LLM
available_llms = config.get_available_llms()

# Получение конфигурации текущей LLM
current_config = config.get_current_llm_config()

# Добавление новой LLM
config.add_llm("My LLM", "gpt-4", "https://api.example.com/v1", "api-key")

# Обновление существующей LLM
config.update_llm("My LLM", model="gpt-4-turbo")

# Удаление LLM
config.remove_llm("My LLM")
```

### 🔧 Продвинутые возможности
```python
# Универсальные методы get/set
value = config.get("global", "temperature")
config.set("global", "temperature", 0.8)

# Сброс к настройкам по умолчанию
config.reset_to_defaults()

# Перезагрузка конфигурации из файла
config.reload()

# Сохранение изменений
config.save()
```

## Структура конфигурации

```yaml
global:
  user_content: "Контекст для всех LLM"
  current_LLM: "OpenAI over Proxy"
  temperature: 0.2
  stream_output_mode: false
  json_mode: false

logging:
  console_level: "CRITICAL"
  file_level: "DEBUG"

supported_LLMs:
  "OpenAI over Proxy":
    model: "gpt-4o-mini"
    api_url: "https://openai-proxy.andrey-bch-1976.workers.dev/v1"
    api_key: ""
```

## Преимущества

✅ **Автоматическая инициализация** - не нужно вручную создавать файлы конфигурации  
✅ **Простой API** - удобные свойства для основных настроек  
✅ **Безопасность** - автоматическое резервное копирование и восстановление  
✅ **Гибкость** - поддержка произвольных настроек через универсальные методы  
✅ **Надежность** - обработка ошибок и валидация данных  

## Использование в коде

```python
from new_config_manager import config

# Использование глобального экземпляра (рекомендуется)
temperature = config.temperature
config.temperature = 0.5

# Или создание собственного экземпляра
from new_config_manager import ConfigManager
my_config = ConfigManager()
current_llm = my_config.current_llm
```</content>
<parameter name="filePath">c:\Users\Andrey\Coding\ai-bash\src\aiebash\README_config_manager.md