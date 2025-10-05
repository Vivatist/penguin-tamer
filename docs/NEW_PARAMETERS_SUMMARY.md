# 🎉 Реализация поддержки дополнительных параметров LLM API

## ✅ Что реализовано

### 1. Новые параметры в конфигурации

Добавлено **6 новых параметров** в `default_config.yaml`:

```yaml
global:
  # === LLM Generation Parameters ===
  temperature: 0.8              # Температура (0.0-2.0)
  max_tokens: null              # Максимум токенов в ответе
  top_p: 0.95                   # Nucleus sampling (0.0-1.0)
  frequency_penalty: 0.0        # Штраф за повторы (-2.0 до 2.0)
  presence_penalty: 0.0         # Штраф за упоминание (-2.0 до 2.0)
  stop: null                    # Стоп-последовательности
  seed: null                    # Seed для детерминизма
```

### 2. Расширен класс OpenRouterClient

**Обновлён конструктор:**
```python
def __init__(self, console, api_key: str, api_url: str, model: str,
             system_message: dict[str, str],
             temperature: float = 0.7,
             max_tokens: int = None,
             top_p: float = 0.95,
             frequency_penalty: float = 0.0,
             presence_penalty: float = 0.0,
             stop: list = None,
             seed: int = None)
```

**Умная передача параметров:**
- Опциональные параметры передаются только если заданы
- Избегает передачи значений по умолчанию
- Совместимость со всеми OpenAI-compatible API

### 3. Обновлена функция debug_print_messages()

**Новые возможности:**
- 🎨 Отдельная панель с параметрами генерации
- 📊 Цветовая индикация параметров
- 🔍 Показывает только ненулевые значения
- 📏 Иконки для каждого параметра

**Пример вывода:**
```
================================================================================
🔍 LLM Request Debug | Model: microsoft/mai-ds-r1:free
================================================================================

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃            Generation Parameters                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 🌡️  Temperature: 0.8                             │
│ 📏 Max Tokens: 2000                              │
│ 🎯 Top P: 0.95                                   │
│ 🔁 Frequency Penalty: 0.3                        │
│ 💭 Presence Penalty: 0.2                         │
└───────────────────────────────────────────────────┘
```

### 4. Автоматическая интеграция

**В `cli.py`:**
- Автоматическое чтение всех параметров из конфига
- Передача в OpenRouterClient при создании
- Нет необходимости вручную обновлять код

### 5. Обновлённые тесты

Файл `test_debug_messages.py` теперь показывает:
- Использование различных комбинаций параметров
- Примеры для разных сценариев
- Демонстрацию всех новых возможностей

### 6. Документация

Созданы **3 файла документации**:

1. **`LLM_PARAMETERS_GUIDE.md`** - Полное руководство (12 разделов)
   - Описание каждого параметра
   - Диапазоны и рекомендуемые значения
   - 5 готовых конфигураций
   - Best practices
   - Примеры использования

2. **`LLM_PARAMS_QUICK.md`** - Краткая шпаргалка
   - Таблица всех параметров
   - Готовые конфигурации
   - Быстрые команды

3. **Обновлён `DEBUG_GUIDE.md`**
   - Добавлена информация о новых параметрах
   - Примеры отладки

---

## 🚀 Использование

### Базовая настройка

Отредактируйте `config.yaml`:

```yaml
global:
  temperature: 0.7
  max_tokens: 2000
  top_p: 0.95
  frequency_penalty: 0.3
  presence_penalty: 0.2
```

### Готовые конфигурации

#### 🎯 Точные технические команды
```yaml
temperature: 0.2
max_tokens: 500
frequency_penalty: 0.1
presence_penalty: 0.0
```

#### 💡 Креативный brainstorming
```yaml
temperature: 1.2
max_tokens: null
frequency_penalty: 0.5
presence_penalty: 0.6
```

#### 📝 Краткие ответы
```yaml
temperature: 0.5
max_tokens: 300
stop: ["\n\n\n"]
```

#### 🧪 Воспроизводимые тесты
```yaml
temperature: 0.7
max_tokens: 1000
seed: 42
```

### Проверка параметров

```bash
# Включить debug mode
export PT_DEBUG=1
pt "ваш запрос"

# Или в конфиге
# debug_mode: true
```

### Тестирование

```bash
# Запустить тесты
cd src/penguin_tamer/tests
python test_debug_messages.py
```

---

## 📊 Сравнение ДО и ПОСЛЕ

### ДО

```python
# Только 3 параметра
stream = self.client.chat.completions.create(
    model=self.model,
    messages=self.messages,
    temperature=self.temperature,
    stream=True
)
```

### ПОСЛЕ

```python
# 7 параметров + умная передача
api_params = {
    "model": self.model,
    "messages": self.messages,
    "temperature": self.temperature,
    "stream": True
}

# Добавляем опциональные параметры
if self.max_tokens is not None:
    api_params["max_tokens"] = self.max_tokens
if self.top_p is not None and self.top_p != 1.0:
    api_params["top_p"] = self.top_p
if self.frequency_penalty != 0.0:
    api_params["frequency_penalty"] = self.frequency_penalty
if self.presence_penalty != 0.0:
    api_params["presence_penalty"] = self.presence_penalty
if self.stop is not None:
    api_params["stop"] = self.stop
if self.seed is not None:
    api_params["seed"] = self.seed

stream = self.client.chat.completions.create(**api_params)
```

---

## 🎓 Что дают новые параметры

### max_tokens
- ✅ Контроль длины ответа
- ✅ Экономия токенов API
- ✅ Быстрые короткие ответы

### top_p
- ✅ Альтернативный контроль креативности
- ✅ Более стабильные результаты
- ✅ Лучше для технических задач

### frequency_penalty
- ✅ Уменьшение повторов
- ✅ Более разнообразные ответы
- ✅ Избавление от зацикливания

### presence_penalty
- ✅ Новые темы в диалоге
- ✅ Более широкий охват
- ✅ Креативные решения

### stop
- ✅ Контроль формата вывода
- ✅ Точная остановка генерации
- ✅ Парсинг structured output

### seed
- ✅ Воспроизводимость
- ✅ Тестирование промптов
- ✅ A/B тестирование

---

## 📁 Изменённые файлы

### Обновлены:
1. ✅ `src/penguin_tamer/default_config.yaml`
2. ✅ `src/penguin_tamer/llm_client.py`
3. ✅ `src/penguin_tamer/cli.py`
4. ✅ `src/penguin_tamer/tests/test_debug_messages.py`

### Созданы:
5. ✅ `docs/LLM_PARAMETERS_GUIDE.md`
6. ✅ `docs/LLM_PARAMS_QUICK.md`

---

## 🎯 Примеры использования

### Пример 1: Точные команды Linux

```yaml
global:
  temperature: 0.2
  max_tokens: 500
  frequency_penalty: 0.1
```

```bash
pt "как создать файл в Linux?"
```

### Пример 2: Генерация скриптов

```yaml
global:
  temperature: 0.7
  max_tokens: 2000
  frequency_penalty: 0.3
```

```bash
pt "напиши скрипт для backup базы данных"
```

### Пример 3: Отладка промпта

```yaml
global:
  temperature: 0.7
  seed: 42
  debug_mode: true
```

```bash
pt "объясни docker compose"
# Каждый запуск будет одинаковым
```

### Пример 4: Краткие Q&A

```yaml
global:
  temperature: 0.5
  max_tokens: 200
  stop: ["\n\n"]
```

```bash
pt -d  # Диалоговый режим с короткими ответами
```

---

## 🔧 Для разработчиков

### Добавление нового параметра

1. Добавить в `default_config.yaml`
2. Добавить в `__init__` класса `OpenRouterClient`
3. Добавить в `api_params` в `ask_stream()`
4. Добавить в параметры `debug_print_messages()`
5. Обновить `_create_chat_client()` в `cli.py`
6. Обновить документацию

### Тестирование

```python
from penguin_tamer import debug_print_messages

messages = [{"role": "user", "content": "test"}]
debug_print_messages(
    messages,
    model="test-model",
    temperature=0.7,
    max_tokens=1000,
    seed=42
)
```

---

## 📚 Ресурсы

- 📖 [Полное руководство](docs/LLM_PARAMETERS_GUIDE.md)
- ⚡ [Краткая справка](docs/LLM_PARAMS_QUICK.md)
- 🔍 [Debug Guide](docs/DEBUG_GUIDE.md)
- 🧪 [Тесты](src/penguin_tamer/tests/test_debug_messages.py)

---

## ✨ Итого

**Добавлено:**
- ✅ 6 новых параметров API
- ✅ Умная передача параметров
- ✅ Расширенная отладка
- ✅ Полная документация
- ✅ Готовые конфигурации
- ✅ Обновлённые тесты

**Обратная совместимость:**
- ✅ Все старые конфиги работают
- ✅ Значения по умолчанию сохранены
- ✅ Опциональные параметры не обязательны

**Готово к использованию!** 🎉
