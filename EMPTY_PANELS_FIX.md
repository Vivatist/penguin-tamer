# Решение проблемы пустых панелей в Textual Menu

## Дата: 6 октября 2025 г.

## Проблема
Окно показывало 2 пустые панели - вкладки были видны, но содержимое (таблицы, поля ввода) не отображалось.

## Причина
Проблемные CSS свойства блокировали отображение содержимого:
1. `height: 100%` на контейнерах `#left-panel` и `#right-panel`
2. `height: 100%` на `TabbedContent`
3. `min-height: 40` на `TabPane` (критично!)
4. Фиксированная `height` на `DataTable` вместо `min-height/max-height`

## Решение

### Изменения в CSS:

#### 1. Убрали `height: 100%` с панелей
```css
/* Было */
#left-panel {
    width: 65%;
    height: 100%;  /* ПРОБЛЕМА! */
}

/* Стало */
#left-panel {
    width: 65%;    /* height: auto по умолчанию */
}
```

#### 2. Упростили TabPane
```css
/* Было */
TabPane {
    padding: 2;
    overflow-y: auto;
    min-height: 40;  /* ПРОБЛЕМА! */
}

/* Стало */
TabPane {
    padding: 1;      /* Просто padding, без height */
}
```

#### 3. Убрали TabbedContent height
```css
/* Было */
TabbedContent {
    height: 100%;
    width: 100%;
}

/* Стало */
TabbedContent {
    width: 100%;     /* Убрали height */
}
```

#### 4. Упростили DataTable
```css
/* Было */
DataTable {
    min-height: 15;
    max-height: 20;
}

/* Стало */
DataTable {
    margin-bottom: 1;
    border: solid $primary;
}
```

### Изменения в коде:

#### Исправили создание таблиц
**Было** (неправильно - add_columns до yield):
```python
table = DataTable(id="llm-selector-table")
table.add_columns("✓", "Название", "Модель")
yield table
```

**Стало** (правильно - add_columns в update_llm_tables):
```python
yield DataTable(id="llm-selector-table", show_header=True, cursor_type="row")

# В update_llm_tables():
selector_table.clear(columns=True)
selector_table.add_columns("✓", "Название", "Модель")
```

## Результат

✅ **Все содержимое отображается корректно:**
- ✅ Таблицы с LLM видны и заполнены данными
- ✅ Заголовки вкладок отображаются
- ✅ Статус-панель справа работает
- ✅ Кнопки видны и доступны
- ✅ Уведомления показываются
- ✅ Текущая выбранная LLM отображается

## Ключевой урок

**В Textual:**
- ❌ НЕ используйте `height: 100%` на контейнерах с динамическим содержимым
- ❌ НЕ используйте `min-height` на `TabPane` - это блокирует layout
- ✅ Позволяйте Textual автоматически рассчитывать высоту
- ✅ Используйте `min-height` / `max-height` для конкретных виджетов (если нужно)
- ✅ Добавляйте столбцы в DataTable через `clear(columns=True)` + `add_columns()`

## Тестирование

```bash
cd /c/Users/Andrey/Coding/penguin-tamer
python src/penguin_tamer/textual_config_menu.py
```

Теперь все работает без эмодзи и с правильным отображением содержимого!
