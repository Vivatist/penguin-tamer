#!/usr/bin/env python3
"""
Простой скрипт для измерения времени запуска ai-bash без зависимостей
"""
import time
import sys
import os
from pathlib import Path

# Импорт декоратора логирования
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[0] / "src"))
    from aiebash.logger import log_execution_time
except ImportError:
    # Если не можем импортировать, создаем заглушку
    def log_execution_time(func):
        return func

@log_execution_time
def measure_startup_time():
    """Измеряет время различных этапов запуска"""

    print("=== Измерение времени запуска ai-bash ===\n")

    # Этап 1: Импорт базовых модулей
    start_time = time.time()

    import json
    import argparse
    from pathlib import Path

    import_time = time.time()
    print(f"[DEBUG] Время импорта базовых модулей: {import_time - start_time:.3f} сек")
    
    # Этап 2: Импорт системных модулей
    import subprocess
    import platform

    system_import_time = time.time()
    print(f"[DEBUG] Время импорта системных модулей: {system_import_time - import_time:.3f} сек")
    
    # Этап 3: Импорт Rich (если установлен)
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        rich_import_time = time.time()
        print(f"[DEBUG] Время импорта Rich: {rich_import_time - system_import_time:.3f} сек")
    except ImportError:
        print("Rich не установлен, пропускаем...")
        rich_import_time = time.time()

    # Этап 4: Импорт aiebash модулей
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        from aiebash.config_manager import config_manager
        from aiebash.logger import configure_logger

        aiebash_import_time = time.time()
        print(f"[DEBUG] Время импорта aiebash модулей: {aiebash_import_time - rich_import_time:.3f} сек")
        
        # Этап 5: Загрузка конфигурации
        logging_config = config_manager.get_logging_config()
        logger = configure_logger(logging_config)

        config_time = time.time()
        print(f"[DEBUG] Время загрузки конфигурации: {config_time - aiebash_import_time:.3f} сек")
        
        # Этап 6: Чтение настроек
        CONTEXT = config_manager.get_value("global", "context", "")
        CURRENT_LLM = config_manager.get_value("global", "current_LLM", "openai_over_proxy")
        TEMPERATURE = config_manager.get_value("global","temperature", 0.7)

        MODEL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("model", "")
        API_URL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_url", "")
        API_KEY = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_key", "")

        settings_time = time.time()
        print(f"[DEBUG] Время чтения настроек: {settings_time - config_time:.3f} сек")
        
        # Этап 7: Инициализация консоли
        console = Console()
        console_init_time = time.time()
        print(f"[DEBUG] Время инициализации консоли: {console_init_time - settings_time:.3f} сек")
        
        total_time = console_init_time - start_time
        print(f"[DEBUG] Общее время запуска: {total_time:.3f} сек")
        
        print("\n=== Детальный анализ ===")
        print(f"Импорт базовых модулей: {import_time - start_time:.3f} сек")
        print(f"Импорт системных модулей: {system_import_time - import_time:.3f} сек")
        print(f"Импорт Rich: {rich_import_time - system_import_time:.3f} сек")
        print(f"Импорт aiebash: {aiebash_import_time - rich_import_time:.3f} сек")
        print(f"Загрузка конфигурации: {config_time - aiebash_import_time:.3f} сек")
        print(f"Чтение настроек: {settings_time - config_time:.3f} сек")
        print(f"Инициализация консоли: {console_init_time - settings_time:.3f} сек")

        if total_time > 2.0:
            print("\n⚠️  Время запуска превышает 2 секунды!")
            print("Рекомендации по оптимизации:")
            print("- Проверьте скорость загрузки конфигурационных файлов")
            print("- Рассмотрите кэширование часто используемых данных")
            print("- Оптимизируйте импорт модулей (используйте ленивый импорт)")
        else:
            print("\n✅ Время запуска в пределах нормы!")

    except ImportError as e:
        print(f"❌ Ошибка импорта aiebash модулей: {e}")
        print("Убедитесь, что находитесь в корневой директории проекта")
        return

if __name__ == "__main__":
    measure_startup_time()