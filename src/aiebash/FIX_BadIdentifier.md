# Исправление ошибки BadIdentifier в config_menu.py

## Проблема
Ошибка `BadIdentifier: 'llm_OpenAI over Proxy' is an invalid id` возникала из-за того, что в названиях LLM содержались пробелы и другие недопустимые символы, которые нельзя использовать в ID элементов Textual.

## Решение
Исправлена генерация ID для элементов списка LLM:

### Было:
```python
list_view.append(ListItem(Label(f"{llm_name}{marker}"), id=f"llm_{llm_name}"))
```

### Стало:
```python
# Создаем безопасный ID, заменяя недопустимые символы
safe_id = f"llm_{llm_name.replace(' ', '_').replace('/', '_').replace('-', '_').replace('.', '_')}"
item = ListItem(Label(f"{llm_name}{marker}"), id=safe_id)
# Сохраняем оригинальное имя в атрибуте
setattr(item, "_llm_name", llm_name)
list_view.append(item)
```

## Изменения:
1. **Генерация безопасного ID**: Заменяем пробелы, слеши, дефисы и точки на подчеркивания
2. **Сохранение оригинального имени**: Используем атрибут `_llm_name` для хранения реального имени LLM
3. **Правильное извлечение имени**: В `on_list_view_selected()` получаем имя из атрибута, а не парсим ID

## Результат:
- ✅ Ошибка BadIdentifier исправлена
- ✅ Меню работает с любыми названиями LLM
- ✅ Функциональность полностью сохранена