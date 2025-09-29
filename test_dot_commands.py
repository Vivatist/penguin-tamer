#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aiebash.script_executor import execute_and_handle_result
from rich.console import Console

def test_dot_command_functionality():
    """Тест функционала выполнения команд с точкой"""
    
    console = Console()
    
    print("Тестирование функционала команд с точкой...")
    print("=" * 50)
    
    # Имитируем ввод пользователя в диалоговом режиме
    test_inputs = [
        ".echo Привет из команды с точкой!",
        ".dir",
        ".echo Текущее время: %TIME%",
        ".",  # Пустая команда после точки
        ".echo Многострочный\\nтест",
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        console.print(f"[bold blue]Тест {i}: Ввод пользователя '[green]{user_input}[/green]'[/bold blue]")
        
        # Проверяем, начинается ли с точки
        if user_input.startswith('.'):
            command_to_execute = user_input[1:].strip()  # Убираем точку и пробелы
            if command_to_execute:  # Выполняем только если есть команда после точки
                console.print(f"[dim]>>> Executing command:[/dim] {command_to_execute}")
                execute_and_handle_result(console, command_to_execute)
            else:
                console.print("[dim]Empty command after '.' - skipping.[/dim]")
        else:
            console.print("[dim]Not a dot command - would be sent to AI[/dim]")
        
        console.print()  # Пустая строка для разделения
    
    console.print("[bold green]✅ Тестирование завершено![/bold green]")

if __name__ == "__main__":
    test_dot_command_functionality()