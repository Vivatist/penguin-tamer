#!/usr/bin/env python3
"""
Быстрый запуск меню конфигурации ai-ebash
"""

import sys
import os

def main():
    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    try:
        from config_menu import run_config_menu
        run_config_menu()
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Убедитесь, что установлены зависимости: pip install textual")
    except KeyboardInterrupt:
        print("\nВыход из меню конфигурации")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()