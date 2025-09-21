#!/usr/bin/env python3
"""
Тестовый запуск меню конфигурации
"""

import sys
import os

# Добавляем путь к текущей директории
sys.path.insert(0, os.path.dirname(__file__))

from config_menu import run_config_menu

if __name__ == "__main__":
    print("Запуск меню конфигурации...")
    print("Используйте клавиатуру для навигации")
    print("Нажмите Ctrl+C для выхода")
    print()

    try:
        run_config_menu()
    except KeyboardInterrupt:
        print("\nВыход из меню конфигурации")
    except Exception as e:
        print(f"Ошибка: {e}")