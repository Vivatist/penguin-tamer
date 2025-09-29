#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест обработки Ctrl+C во время выполнения команд
"""

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ctrl_c_handling():
    """Тест обработки Ctrl+C"""
    
    from rich.console import Console
    console = Console()
    
    console.print("[bold cyan]🛑 Тест обработки Ctrl+C[/bold cyan]")
    console.print()
    
    try:
        from aiebash.script_executor import execute_and_handle_result
        
        console.print("🔍 Тест команд, которые можно прервать:")
        console.print("- На Windows: ping будет пинговать бесконечно")
        console.print("- Нажмите [red]Ctrl+C[/red] чтобы прервать команду")
        console.print("- Программа должна вернуться в диалог, а не завершиться")
        console.print()
        
        # Тест длительной команды
        if os.name == 'nt':  # Windows
            test_command = "ping -t 8.8.8.8"  # Бесконечный ping на Windows
        else:  # Linux/Unix
            test_command = "ping 8.8.8.8"  # Обычный ping (4 пакета по умолчанию)
        
        console.print(f"[dim]Выполняем:[/dim] {test_command}")
        console.print("[yellow]Нажмите Ctrl+C для прерывания...[/yellow]")
        console.print()
        
        # Выполняем команду
        execute_and_handle_result(console, test_command)
        
        console.print()
        console.print("✅ Команда завершена. Программа продолжает работу!")
        console.print("🔄 Это означает, что обработка Ctrl+C работает корректно")
        
    except KeyboardInterrupt:
        console.print("\n❌ KeyboardInterrupt не был перехвачен!")
        console.print("Это означает, что Ctrl+C все еще прерывает всю программу")
        return False
    except Exception as e:
        console.print(f"❌ Ошибка: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = test_ctrl_c_handling()
    if success:
        print("\n🎯 Тест успешен!")
    else:
        print("\n💥 Тест провален!")
        sys.exit(1)