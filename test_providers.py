#!/usr/bin/env python3
"""
Тестовый скрипт для проверки управления провайдерами.
"""

import sys
from pathlib import Path

# Добавляем src в путь
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from penguin_tamer.config_manager import config

# Проверяем, что можем получить провайдеров
print("=== Текущие провайдеры ===")
providers = config.get("supported_Providers") or {}
for name, provider_config in providers.items():
    print(f"\nПровайдер: {name}")
    print(f"  API List: {provider_config.get('api_list', 'N/A')}")
    print(f"  API URL: {provider_config.get('api_url', 'N/A')}")
    print(f"  API Key: {'Установлен' if provider_config.get('api_key') else 'Не установлен'}")

print("\n=== Тест добавления провайдера ===")
providers["TestProvider"] = {
    "api_list": "https://test.example.com/api/v1/models",
    "api_url": "https://test.example.com/api/v1",
    "api_key": "test-key-12345"
}
config.update_section("supported_Providers", providers)
config.save()
print("Провайдер TestProvider добавлен")

print("\n=== Проверяем, что провайдер добавлен ===")
config.reload()
providers = config.get("supported_Providers") or {}
if "TestProvider" in providers:
    print("✓ Провайдер TestProvider найден в конфиге")
    print(f"  API List: {providers['TestProvider'].get('api_list')}")
else:
    print("✗ Провайдер TestProvider НЕ найден в конфиге")

print("\n=== Тест удаления провайдера ===")
del providers["TestProvider"]
config.update_section("supported_Providers", providers)
config.save()
print("Провайдер TestProvider удалён")

print("\n=== Проверяем, что провайдер удалён ===")
config.reload()
providers = config.get("supported_Providers") or {}
if "TestProvider" not in providers:
    print("✓ Провайдер TestProvider успешно удалён")
else:
    print("✗ Провайдер TestProvider всё ещё в конфиге")

print("\n=== Тест завершён ===")
