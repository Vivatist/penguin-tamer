#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aiebash.script_executor import execute_and_handle_result
from rich.console import Console

def test_execute_and_handle_result():
    """Тест нового публичного метода execute_and_handle_result"""
    
    console = Console()
    
    print("Тестирование метода execute_and_handle_result...")
    print("=" * 50)
    
    # Тест 1: Простая команда
    console.print("[bold blue]Тест 1: Простая команда echo[/bold blue]")
    execute_and_handle_result(console, 'echo "Привет из метода execute_and_handle_result!"')
    
    print()
    
    # Тест 2: Команда с несколькими строками
    console.print("[bold blue]Тест 2: Многострочная команда[/bold blue]")
    multi_line_code = """
echo "=== Тестирование нового метода ==="
echo "Текущее время: %TIME%"
echo "Имя пользователя: %USERNAME%"
echo "=============================="
"""
    execute_and_handle_result(console, multi_line_code.strip())
    
    print()
    
    # Тест 3: Bash скрипт (для демонстрации автоконвертации)
    console.print("[bold blue]Тест 3: Bash скрипт с конвертацией[/bold blue]")
    bash_code = """#!/bin/bash
echo "Информация о системе:"
echo "Пользователь: $(whoami)"
echo "Текущая папка: $(pwd)"
"""
    execute_and_handle_result(console, bash_code)
    
    print()
    console.print("[bold green]✅ Все тесты завершены![/bold green]")

if __name__ == "__main__":
    test_execute_and_handle_result()