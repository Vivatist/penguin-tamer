#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simulate_dialog_interaction():
    """Симуляция взаимодействия с диалоговым режимом"""
    
    from aiebash.script_executor import execute_and_handle_result
    from rich.console import Console
    
    console = Console()
    
    console.print("[bold blue]🚀 Демонстрация новой функции диалогового режима[/bold blue]")
    console.print("[dim]Команды, начинающиеся с точки (.), выполняются напрямую![/dim]")
    console.print()
    
    # Имитируем диалоговую сессию
    dialog_examples = [
        ("Обычный вопрос пользователя", False),
        (".echo Привет! Это прямая команда", True),
        ("123", False),  # Номер блока кода
        (".dir /w", True),  # Список файлов в широком формате
        (".systeminfo | findstr \"Processor\"", True),  # Информация о процессоре
        ("Как посмотреть версию Windows?", False),
        (".ver", True),  # Прямое выполнение команды для показа версии
    ]
    
    for i, (user_input, is_command) in enumerate(dialog_examples, 1):
        console.print(f"[green]>>> [/green]{user_input}")
        
        if is_command:
            # Обрабатываем команду с точкой
            if user_input.startswith('.'):
                command_to_execute = user_input[1:].strip()
                if command_to_execute:
                    console.print(f"[dim]>>> Executing command:[/dim] {command_to_execute}")
                    execute_and_handle_result(console, command_to_execute)
                else:
                    console.print("[dim]Empty command after '.' - skipping.[/dim]")
        else:
            # Имитируем обработку обычных запросов
            if user_input.isdigit():
                console.print(f"[dim]>>> Would execute code block #{user_input}[/dim]")
            else:
                console.print("[dim]>>> Would send to AI for processing...[/dim]")
        
        console.print()
    
    console.print("[bold green]✅ Демонстрация завершена![/bold green]")
    console.print("[dim]В реальном диалоговом режиме эти команды будут выполняться аналогично.[/dim]")

if __name__ == "__main__":
    simulate_dialog_interaction()