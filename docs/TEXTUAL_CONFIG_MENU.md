# Textual Configuration Menu

Современное графическое меню конфигурации для Penguin Tamer с использованием Textual TUI.

## Возможности

### 🎨 Визуальный интерфейс
- **Табы для навигации**: Логически разделенные секции настроек
- **Живой статус**: Реал-тайм отображение текущей конфигурации
- **Подсказки**: Описание каждого параметра прямо в интерфейсе
- **Цветовое кодирование**: Легко читаемый интерфейс с подсветкой

### ⚙️ Управление LLM
- Таблица со всеми добавленными моделями
- Добавление/редактирование/удаление LLM
- Выбор текущей активной модели
- Отображение API ключей в безопасном формате

### 📝 Редактор контента
- Многострочный редактор с TextArea
- Сохранение/сброс пользовательского контента
- Превью в панели статуса

### 🔧 Параметры генерации
- Temperature (0.0 - 2.0) с подсказками
- Max Tokens с поддержкой unlimited
- Top P, Frequency/Presence Penalty
- Seed для детерминированной генерации
- Валидация всех значений

### 🌐 Системные настройки
- Выбор языка (EN/RU)
- Выбор темы подсветки кода
- Debug mode toggle
- Stream delay и refresh rate

## Установка

```bash
# Textual требуется для работы
pip install textual

# Или добавьте в requirements.txt
echo "textual>=0.47.0" >> requirements.txt
pip install -r requirements.txt
```

## Запуск

### Через командную строку
```bash
# Прямой запуск
python -m penguin_tamer.textual_config_menu

# Или через модуль
cd src
python penguin_tamer/textual_config_menu.py
```

### Интеграция в CLI
Добавьте в `cli.py`:
```python
elif args.config_textual:
    from penguin_tamer.textual_config_menu import main as textual_menu
    textual_menu()
```

## Использование

### Навигация

| Клавиша | Действие |
|---------|----------|
| **Tab** / **Shift+Tab** | Переключение между элементами |
| **←** / **→** | Переключение вкладок |
| **↑** / **↓** | Навигация по таблице/меню |
| **Enter** | Активировать кнопку/поле |
| **Q** / **Ctrl+C** | Выход |
| **F1** | Помощь |

### Вкладки

#### 🤖 LLMs
1. **Просмотр**: Таблица со всеми LLM (✓ отмечает текущую)
2. **Добавить**: Кнопка "➕ Add LLM"
   - Введите название, модель, URL, API ключ
3. **Редактировать**: Выберите в таблице → "✏️ Edit Selected"
4. **Установить текущей**: "✅ Set as Current"
5. **Удалить**: "🗑️ Delete" (текущую удалить нельзя)

#### ⚙️ Generation
Параметры генерации текста:
- **Temperature**: Креативность (0.0 = строго, 2.0 = очень креативно)
- **Max Tokens**: Максимальная длина ответа
- **Top P**: Nucleus sampling
- **Frequency Penalty**: Снижение повторов слов
- **Presence Penalty**: Снижение повторов тем
- **Seed**: Для одинаковых ответов

#### 📝 Content
- **Многострочный редактор**: TextArea для ввода
- **Подсказки**: Инструкции по использованию
- **Сохранение**: Кнопка "💾 Save Content"
- **Сброс**: Очистка всего контента

#### 🔧 System
- **Language**: EN / RU
- **Theme**: Default, Monokai, Dracula, Nord, etc.
- **Debug Mode**: Switch (ON/OFF)
- **Stream Settings**: Задержка и частота обновлений

### Панель статуса (правая)
Отображает в реальном времени:
- 🤖 Текущая LLM и её параметры
- ⚙️ Параметры генерации
- 📝 Превью пользовательского контента
- 🔧 Системные настройки

## Архитектура

### Компоненты

```
ConfigMenuApp (главное приложение)
├── Header / Footer
├── Left Panel (60% ширины)
│   ├── Tabs (навигация)
│   └── Tab Content
│       ├── LLMManagementTab
│       ├── GenerationParamsTab
│       ├── UserContentTab
│       └── SystemSettingsTab
└── Right Panel (40% ширины)
    └── StatusPanel (живой статус)
```

### Модальные окна

**ConfirmDialog**:
- Подтверждение действий (удаление, сброс)
- Yes/No кнопки

**InputDialog**:
- Одностроч

ный/многострочный ввод
- Support для TextArea
- OK/Cancel кнопки

### Стилизация
CSS-подобная система через атрибут `CSS`:
- Responsive layout (горизонтальное разделение)
- Цветовые темы через переменные Textual
- Адаптивные размеры и отступы

## Отличия от Inquirer-версии

| Особенность | Inquirer Menu | Textual Menu |
|-------------|---------------|--------------|
| **Интерфейс** | Последовательные промпты | Параллельное отображение |
| **Навигация** | Стрелки + Enter | Tabs + клик/клавиши |
| **Статус** | Отдельная команда | Живая панель справа |
| **Редактор** | `input()` с `\n` | Полноценная TextArea |
| **Визуальная обратная связь** | Текстовые сообщения | Нотификации + цвета |
| **Таблицы** | Текстовый вывод | Интерактивная DataTable |
| **Валидация** | После ввода | В реальном времени |

## Преимущества Textual версии

✅ **Наглядность**: Все настройки видны одновременно  
✅ **Живой статус**: Изменения видны сразу  
✅ **Подсказки**: Описание прямо в интерфейсе  
✅ **Многострочный ввод**: Нормальный текстовый редактор  
✅ **Валидация**: Проверка значений до сохранения  
✅ **UX**: Современный интерфейс с клавиатурой и мышью  
✅ **Цвета**: Подсветка текущих значений и статусов  
✅ **Таблицы**: Удобный просмотр списка LLM  

## Примеры использования

### Добавление новой LLM

```
1. Запустите меню
2. Вкладка "🤖 LLMs" (по умолчанию)
3. Нажмите "➕ Add LLM"
4. Заполните поля:
   - Name: GPT-4
   - Model: gpt-4-turbo
   - API URL: https://api.openai.com/v1
   - API Key: sk-...
5. Готово! LLM добавлена и видна в таблице
```

### Настройка параметров генерации

```
1. Вкладка "⚙️ Generation"
2. Видите все параметры с подсказками:
   - Temperature: 0.7 ← "Controls randomness..."
   - Max Tokens: 2000
   - ...
3. Измените значение в поле
4. Нажмите кнопку "Set [Parameter]"
5. Видите изменение в панели статуса справа →
```

### Редактирование контента

```
1. Вкладка "📝 Content"
2. Видите TextArea с текущим контентом
3. Редактируйте (многострочный ввод работает!)
4. Нажмите "💾 Save Content"
5. Превью обновилось в панели статуса
```

## Расширение

### Добавление нового параметра

```python
# В GenerationParamsTab.compose():
yield Static("\n[bold]New Parameter[/bold]", classes="param-label")
yield Static(
    "[dim]Description of what this parameter does[/dim]",
    classes="param-hint"
)
yield Input(value=str(config.new_param), id="new-param-input")
yield Button("Set New Parameter", id="set-new-param-btn", classes="param-btn")

# В GenerationParamsTab.on_button_pressed():
elif event.button.id == "set-new-param-btn":
    value = self.query_one("#new-param-input", Input).value
    config.new_param = value
    self.notify("✅ New parameter updated", severity="information")
```

### Добавление новой вкладки

```python
# 1. В ConfigMenuApp.compose():
with Tabs():
    # ... existing tabs ...
    yield Tab("🎨 New Tab", id="tab-new")

# 2. Создайте класс вкладки:
class NewTab(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield Static("[bold]🎨 New Feature[/bold]", classes="tab-header")
        # ... your widgets ...

# 3. Добавьте в compose():
yield NewTab(id="new-tab")

# 4. Обновите on_tabs_tab_activated():
elif event.tab.id == "tab-new":
    self.query_one("#new-tab").display = True
```

## Troubleshooting

### Textual не установлен
```bash
pip install textual>=0.47.0
```

### Ошибка импорта
Убедитесь, что запускаете из правильной директории:
```bash
# Из корня проекта
python -m penguin_tamer.textual_config_menu

# Или из src/
cd src
python -m penguin_tamer.textual_config_menu
```

### Неправильное отображение
Проверьте размер терминала (минимум 120x30 рекомендуется):
```bash
echo $COLUMNS x $LINES  # Unix
# Или просто разверните окно терминала
```

## См. также

- [config_menu.py](config_menu.py) - Оригинальная Inquirer версия
- [settings_overview.py](settings_overview.py) - Функция обзора настроек
- [Textual Documentation](https://textual.textualize.io/) - Официальная документация
- [config_manager.py](config_manager.py) - Менеджер конфигурации

## Roadmap

Планируемые улучшения:

- [ ] Поддержка мыши для всех элементов
- [ ] Горячие клавиши для быстрых действий
- [ ] История изменений (Undo/Redo)
- [ ] Импорт/экспорт конфигурации
- [ ] Визуальный редактор промптов
- [ ] Предпросмотр ответов LLM
- [ ] Встроенная валидация API ключей
- [ ] Темы оформления самого интерфейса

---

**Автор**: Penguin Tamer Team  
**Версия**: 1.0.0  
**Лицензия**: MIT
