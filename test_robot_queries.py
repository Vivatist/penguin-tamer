#!/usr/bin/env python3
"""Тест для проверки, что robot mode воспроизводит все запросы."""
import json
from pathlib import Path

# Загружаем сессию
session_file = Path("C:/Users/Andrey/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/Local/penguin-tamer/penguin-tamer/demo_sessions/session_1.json")
with open(session_file, 'r', encoding='utf-8') as f:
    session_data = json.load(f)

# Извлекаем все действия типа 'query'
query_actions = []
for entry in session_data:
    if 'user_actions' in entry:
        for action in entry['user_actions']:
            if action['type'] == 'query':
                query_actions.append(action['value'])

print(f"Всего найдено {len(query_actions)} query действий:")
for i, query in enumerate(query_actions, 1):
    print(f"{i}. {query}")

# Ожидаемые запросы
expected_queries = [
    "Как посмотреть логфайл",
    "ssh",
    "как проверить интернет",
    "что это значит",
    "что это значит"
]

print(f"\nОжидается {len(expected_queries)} запросов")
print(f"Найдено {len(query_actions)} запросов")

if query_actions == expected_queries:
    print("\n✅ Все запросы на месте!")
else:
    print("\n❌ Не совпадает:")
    print(f"Ожидалось: {expected_queries}")
    print(f"Получено: {query_actions}")
