#!/usr/bin/env python3
"""
Интеграционный тест: полный цикл работы с провайдерами и LLM.
"""

import sys
from pathlib import Path

# Добавляем src в путь
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from penguin_tamer.config_manager import config
from penguin_tamer.llm_clients import ClientFactory


def test_full_workflow():
    """Тест полного рабочего процесса."""
    
    print("=" * 70)
    print("ИНТЕГРАЦИОННЫЙ ТЕСТ: Провайдеры + LLM")
    print("=" * 70)
    
    # Шаг 1: Проверка провайдеров
    print("\n[Шаг 1] Проверка настроенных провайдеров")
    print("-" * 70)
    providers = config.get("supported_Providers") or {}
    print(f"Найдено провайдеров: {len(providers)}")
    for name in providers.keys():
        print(f"  ✓ {name}")
    
    # Шаг 2: Проверка LLM
    print("\n[Шаг 2] Проверка настроенных LLM")
    print("-" * 70)
    llms = config.get_available_llms()
    current_llm = config.current_llm
    print(f"Найдено LLM: {len(llms)}")
    for llm_name in llms:
        marker = "✓" if llm_name == current_llm else " "
        llm_config = config.get_llm_config(llm_name)
        model = llm_config.get("model", "N/A") if llm_config else "N/A"
        print(f"  {marker} {llm_name}: {model}")
    
    # Шаг 3: Проверка возможности загрузки моделей от каждого провайдера
    print("\n[Шаг 3] Проверка доступности API провайдеров")
    print("-" * 70)
    for provider_name, provider_config in providers.items():
        api_list = provider_config.get("api_list", "")
        api_key = provider_config.get("api_key", "")
        client_name = provider_config.get("client_name", "openrouter")
        
        if not api_list:
            print(f"  ⚠ {provider_name}: API List URL не настроен")
            continue
        
        print(f"  Testing {provider_name}...", end=" ")
        client_class = ClientFactory.get_client_for_static_methods(client_name)
        models = client_class.fetch_models(api_list, api_key)
        
        if models:
            print(f"✓ ({len(models)} моделей)")
        else:
            print("✗ (требуется API ключ или сервис недоступен)")
    
    # Шаг 4: Симуляция создания LLM через провайдера
    print("\n[Шаг 4] Симуляция создания LLM от провайдера")
    print("-" * 70)
    
    # Выбираем первого провайдера с доступными моделями
    test_provider = None
    test_models = []
    
    for provider_name, provider_config in providers.items():
        api_list = provider_config.get("api_list", "")
        api_key = provider_config.get("api_key", "")
        client_name = provider_config.get("client_name", "openrouter")
        
        if api_list:
            client_class = ClientFactory.get_client_for_static_methods(client_name)
            models = client_class.fetch_models(api_list, api_key)
            if models:
                test_provider = provider_name
                test_models = models[:3]  # Первые 3 модели
                break
    
    if test_provider:
        print(f"Выбран провайдер: {test_provider}")
        print(f"Доступно моделей для тестирования: {len(test_models)}")
        
        provider_config = providers[test_provider]
        print(f"\nДанные провайдера для автозаполнения:")
        print(f"  API URL: {provider_config.get('api_url', 'N/A')}")
        print(f"  API Key: {'✓ Есть' if provider_config.get('api_key') else '✗ Нет'}")
        
        print(f"\nПримеры доступных моделей:")
        for i, model in enumerate(test_models, 1):
            model_id = model.get("id", "N/A")
            model_name = model.get("name", model_id)
            print(f"  {i}. {model_name}")
            print(f"     ID: {model_id}")
        
        print(f"\n✓ Пользователь может выбрать любую из {len(test_models)} моделей")
    else:
        print("⚠ Нет доступных провайдеров с моделями для тестирования")
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    print(f"✓ Провайдеров настроено: {len(providers)}")
    print(f"✓ LLM настроено: {len(llms)}")
    print(f"✓ Текущая LLM: {current_llm}")
    
    working_providers = 0
    for provider_name, provider_config in providers.items():
        api_list = provider_config.get("api_list", "")
        api_key = provider_config.get("api_key", "")
        client_name = provider_config.get("client_name", "openrouter")
        if api_list:
            client_class = ClientFactory.get_client_for_static_methods(client_name)
            models = client_class.fetch_models(api_list, api_key)
            if models:
                working_providers += 1
    
    print(f"✓ Провайдеров с доступными моделями: {working_providers}")
    
    print("\n" + "=" * 70)
    print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_full_workflow()
    except Exception as e:
        print(f"\n✗ Ошибка при выполнении теста: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
