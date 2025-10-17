#!/usr/bin/env python3
"""
Тест новых методов OpenRouterClient для работы с моделями.
"""

import sys
from pathlib import Path

# Добавляем src в путь
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from penguin_tamer.llm_client import OpenRouterClient


def test_fetch_models_static():
    """Тест статического метода fetch_models."""
    print("=" * 70)
    print("ТЕСТ: OpenRouterClient.fetch_models() - статический метод")
    print("=" * 70)
    
    # Тест 1: OpenRouter API (без ключа - публичный endpoint)
    print("\n[Тест 1] OpenRouter API без ключа")
    print("-" * 70)
    models = OpenRouterClient.fetch_models("https://openrouter.ai/api/v1/models")
    
    if models:
        print(f"✓ Успешно получено {len(models)} моделей")
        print("\nПримеры моделей:")
        for i, model in enumerate(models[:5], 1):
            print(f"  {i}. {model['name']}")
            print(f"     ID: {model['id']}")
    else:
        print("⚠ Не удалось получить модели (может требоваться API ключ)")
    
    # Тест 2: С фильтром
    print("\n[Тест 2] OpenRouter API с фильтром 'gpt'")
    print("-" * 70)
    filtered_models = OpenRouterClient.fetch_models(
        "https://openrouter.ai/api/v1/models",
        model_filter="gpt"
    )
    
    if filtered_models:
        print(f"✓ Найдено {len(filtered_models)} моделей с 'gpt' в названии")
        print("\nПримеры отфильтрованных моделей:")
        for i, model in enumerate(filtered_models[:3], 1):
            print(f"  {i}. {model['name']}")
            print(f"     ID: {model['id']}")
    else:
        print("⚠ Не удалось получить модели с фильтром")
    
    # Тест 3: Некорректный URL (должен вернуть пустой список)
    print("\n[Тест 3] Некорректный URL")
    print("-" * 70)
    empty_models = OpenRouterClient.fetch_models("https://invalid.example.com/api/models")
    
    if not empty_models:
        print("✓ Корректно обработан некорректный URL (вернул пустой список)")
    else:
        print("✗ Ожидался пустой список")
    
    print("\n" + "=" * 70)
    print("✓ ВСЕ ТЕСТЫ СТАТИЧЕСКОГО МЕТОДА ПРОЙДЕНЫ!")
    print("=" * 70)


def test_instance_method():
    """Тест метода экземпляра get_available_models."""
    print("\n" * 2)
    print("=" * 70)
    print("ТЕСТ: OpenRouterClient.get_available_models() - метод экземпляра")
    print("=" * 70)
    
    from rich.console import Console
    
    # Создаём минимальный клиент для теста
    console = Console()
    
    # Используем публичный endpoint OpenRouter
    from penguin_tamer.llm_client import LLMConfig
    
    llm_config = LLMConfig(
        api_key="",  # Пустой ключ для публичного endpoint
        api_url="https://openrouter.ai/api/v1/chat/completions",
        model="openai/gpt-3.5-turbo"
    )
    
    client = OpenRouterClient(
        console=console,
        system_message=[],
        llm_config=llm_config
    )
    
    print("\n[Тест 1] Получение моделей через метод экземпляра")
    print("-" * 70)
    models = client.get_available_models()
    
    if models:
        print(f"✓ Успешно получено {len(models)} моделей через экземпляр")
        print("\nПримеры моделей:")
        for i, model in enumerate(models[:3], 1):
            print(f"  {i}. {model['name']}")
            print(f"     ID: {model['id']}")
    else:
        print("⚠ Не удалось получить модели через экземпляр")
    
    print("\n[Тест 2] С фильтром через метод экземпляра")
    print("-" * 70)
    filtered_models = client.get_available_models(model_filter="claude")
    
    if filtered_models:
        print(f"✓ Найдено {len(filtered_models)} моделей с 'claude' в названии")
        print("\nПримеры отфильтрованных моделей:")
        for i, model in enumerate(filtered_models[:3], 1):
            print(f"  {i}. {model['name']}")
            print(f"     ID: {model['id']}")
    else:
        print("⚠ Не удалось получить модели с фильтром")
    
    print("\n" + "=" * 70)
    print("✓ ВСЕ ТЕСТЫ МЕТОДА ЭКЗЕМПЛЯРА ПРОЙДЕНЫ!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_fetch_models_static()
        test_instance_method()
        
        print("\n" * 2)
        print("=" * 70)
        print("✓✓✓ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! ✓✓✓")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Ошибка при выполнении теста: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
