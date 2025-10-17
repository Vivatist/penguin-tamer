#!/usr/bin/env python3
"""
Простой функциональный тест PollinationsClient
"""

import sys
sys.path.insert(0, 'src')


def test_models_filtering():
    """Тест: Проверка фильтрации только anonymous моделей"""
    print("=" * 60)
    print("ТЕСТ: Фильтрация моделей (только tier=anonymous)")
    print("=" * 60)
    
    from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
    
    # Получаем модели
    models = PollinationsClient.fetch_models(
        api_list_url="",
        api_key="",
        model_filter=None
    )
    
    print(f"\nПолучено моделей: {len(models)}")
    
    if len(models) == 0:
        print("❌ ОШИБКА: Нет моделей!")
        return False
    
    # Проверяем каждую модель
    import requests
    response = requests.get("https://text.pollinations.ai/models", timeout=10)
    all_models = response.json()
    
    # Создаём lookup по имени
    models_by_name = {m.get('name'): m for m in all_models}
    
    all_anonymous = True
    for model in models:
        model_id = model['id']
        if model_id in models_by_name:
            tier = models_by_name[model_id].get('tier', 'unknown')
            status = "✓" if tier == 'anonymous' else "✗"
            print(f"  {status} {model_id:20} tier={tier}")
            if tier != 'anonymous':
                all_anonymous = False
        else:
            print(f"  ? {model_id:20} НЕ НАЙДЕНА В API")
            all_anonymous = False
    
    print()
    if all_anonymous:
        print("✅ УСПЕШНО: Все модели имеют tier=anonymous")
        return True
    else:
        print("❌ ОШИБКА: Найдены модели с другими tier!")
        return False


def test_client_creation():
    """Тест: Создание клиента с правильными параметрами"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Создание PollinationsClient")
    print("=" * 60)
    
    try:
        from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
        from penguin_tamer.llm_clients.base import LLMConfig
        from rich.console import Console
        
        config = LLMConfig(
            api_url="https://text.pollinations.ai",
            api_key="",
            model="openai",
            temperature=0.7,
            max_tokens=100
        )
        
        console = Console()
        system_message = [{"role": "system", "content": "You are a helpful assistant."}]
        
        client = PollinationsClient(
            console=console,
            system_message=system_message,
            llm_config=config
        )
        
        print(f"\n✓ Клиент создан")
        print(f"  Модель: {client.model}")
        print(f"  API URL: {client.api_url}")
        print(f"  Temperature: {client.temperature}")
        print(f"  Max tokens: {client.max_tokens}")
        
        print("\n✅ УСПЕШНО: Клиент создан корректно")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_key_check_bypass():
    """Тест: Проверка пропуска API ключа для Pollinations в cli.py"""
    print("\n" + "=" * 60)
    print("ТЕСТ: Проверка пропуска API ключа для Pollinations")
    print("=" * 60)
    
    # Проверяем, что в cli.py есть логика для pollinations
    try:
        with open('src/penguin_tamer/cli.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем строку с проверкой client_name
        if 'client_name != "pollinations"' in content or 'client_name == "pollinations"' in content:
            print("\n✓ Найдена логика проверки client_name для Pollinations")
            
            # Проверяем, что код не закомментирован
            if '# Check if API key exists' in content and not '# ВРЕМЕННО ОТКЛЮЧЕНО' in content:
                print("✓ Проверка API ключа активна")
                print("\n✅ УСПЕШНО: Логика пропуска API ключа реализована")
                return True
            else:
                print("✗ Проверка API ключа закомментирована или отсутствует")
                return False
        else:
            print("\n✗ Не найдена логика проверки Pollinations")
            return False
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("ФУНКЦИОНАЛЬНОЕ ТЕСТИРОВАНИЕ POLLINATIONS")
    print("=" * 60 + "\n")
    
    results = {
        "Фильтрация моделей": test_models_filtering(),
        "Создание клиента": test_client_creation(),
        "Пропуск API ключа": test_api_key_check_bypass()
    }
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nПройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print(f"\n⚠️  Провалено тестов: {total - passed}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
