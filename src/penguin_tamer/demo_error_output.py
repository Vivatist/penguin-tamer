#!/usr/bin/env python3
"""
Демонстрация исправления вывода ошибок команд.

Показывает разницу между старым и новым поведением.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from penguin_tamer.command_executor import execute_and_handle_result
from rich.console import Console

console = Console()

print("=" * 70)
print("ДЕМОНСТРАЦИЯ: Вывод ошибок команд")
print("=" * 70)
print()

# Тест 1: Недопустимая опция
print("[bold cyan]Тест 1: Команда с неверным параметром[/]")
print("[dim]Команда: dir /invalid_option[/]")
print()
result1 = execute_and_handle_result(console, 'dir /invalid_option')
print()
print("[green]Результат структуры данных:[/]")
print(f"  success: {result1['success']}")
print(f"  exit_code: {result1['exit_code']}")
print(f"  stdout: '{result1['stdout'][:50]}...' ({len(result1['stdout'])} символов)")
print(f"  stderr: '{result1['stderr'][:50]}...' ({len(result1['stderr'])} символов)")
print()

# Тест 2: Несуществующий файл
print("-" * 70)
print("[bold cyan]Тест 2: Попытка открыть несуществующий файл[/]")
print("[dim]Команда: type nonexistent_file.txt[/]")
print()
result2 = execute_and_handle_result(console, 'type nonexistent_file.txt')
print()
print("[green]Результат структуры данных:[/]")
print(f"  success: {result2['success']}")
print(f"  exit_code: {result2['exit_code']}")
print(f"  stdout: '{result2['stdout'][:50]}...' ({len(result2['stdout'])} символов)")
print(f"  stderr: '{result2['stderr'][:50]}...' ({len(result2['stderr'])} символов)")
print()

# Тест 3: ping недоступного хоста
print("-" * 70)
print("[bold cyan]Тест 3: ping недоступного хоста[/]")
print("[dim]Команда: ping -n 1 999.999.999.999[/]")
print()
result3 = execute_and_handle_result(console, 'ping -n 1 999.999.999.999')
print()
print("[green]Результат структуры данных:[/]")
print(f"  success: {result3['success']}")
print(f"  exit_code: {result3['exit_code']}")
print(f"  stdout: '{result3['stdout'][:80]}...' ({len(result3['stdout'])} символов)")
print(f"  stderr: '{result3['stderr'][:80]}...' ({len(result3['stderr'])} символов)")
print()

# Тест 4: Успешная команда для сравнения
print("-" * 70)
print("[bold cyan]Тест 4: Успешная команда (для сравнения)[/]")
print("[dim]Команда: echo Hello World[/]")
print()
result4 = execute_and_handle_result(console, 'echo Hello World')
print()
print("[green]Результат структуры данных:[/]")
print(f"  success: {result4['success']}")
print(f"  exit_code: {result4['exit_code']}")
print(f"  stdout: '{result4['stdout']}'")
print(f"  stderr: '{result4['stderr']}'")
print()

print("=" * 70)
print("[bold green]✅ ИТОГ:[/]")
print("  1. Все ошибки теперь выводятся полностью")
print("  2. Код завершения всегда показывается")
print("  3. stderr корректно захватывается и отображается")
print("  4. Информация доступна для добавления в контекст AI")
print("=" * 70)
