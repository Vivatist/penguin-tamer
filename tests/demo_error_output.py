#!/usr/bin/env python3
"""
Демонстрация исправления вывода ошибок команд.

Показывает разницу между старым и новым поведением.

Связанные файлы:
- test_command_output.py - автоматические тесты для проверки вывода команд
- TEST_COMMAND_OUTPUT.md - документация по тестам
"""

import sys
from pathlib import Path

# Добавляем путь к src для импорта модулей
# tests/demo_error_output.py -> tests/ -> project_root/ -> src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from penguin_tamer.command_executor import execute_and_handle_result
from rich.console import Console

console = Console()

console.print("=" * 70)
console.print("ДЕМОНСТРАЦИЯ: Вывод ошибок команд")
console.print("=" * 70)
console.print()

# Тест 1: Недопустимая опция
console.print("[bold cyan]Тест 1: Команда с неверным параметром[/]")
console.print("[dim]Команда: dir /invalid_option[/]")
console.print()
result1 = execute_and_handle_result(console, 'dir /invalid_option')
console.print()
console.print("[green]Результат структуры данных:[/]")
console.print(f"  success: {result1['success']}")
console.print(f"  exit_code: {result1['exit_code']}")
console.print(f"  stdout: '{result1['stdout'][:50]}...' ({len(result1['stdout'])} символов)")
console.print(f"  stderr: '{result1['stderr'][:50]}...' ({len(result1['stderr'])} символов)")
console.print()

# Тест 2: Несуществующий файл
console.print("-" * 70)
console.print("[bold cyan]Тест 2: Попытка открыть несуществующий файл[/]")
console.print("[dim]Команда: type nonexistent_file.txt[/]")
console.print()
result2 = execute_and_handle_result(console, 'type nonexistent_file.txt')
console.print()
console.print("[green]Результат структуры данных:[/]")
console.print(f"  success: {result2['success']}")
console.print(f"  exit_code: {result2['exit_code']}")
console.print(f"  stdout: '{result2['stdout'][:50]}...' ({len(result2['stdout'])} символов)")
console.print(f"  stderr: '{result2['stderr'][:50]}...' ({len(result2['stderr'])} символов)")
console.print()

# Тест 3: ping недоступного хоста
console.print("-" * 70)
console.print("[bold cyan]Тест 3: ping недоступного хоста[/]")
console.print("[dim]Команда: ping -n 1 999.999.999.999[/]")
console.print()
result3 = execute_and_handle_result(console, 'ping -n 1 999.999.999.999')
console.print()
console.print("[green]Результат структуры данных:[/]")
console.print(f"  success: {result3['success']}")
console.print(f"  exit_code: {result3['exit_code']}")
console.print(f"  stdout: '{result3['stdout'][:80]}...' ({len(result3['stdout'])} символов)")
console.print(f"  stderr: '{result3['stderr'][:80]}...' ({len(result3['stderr'])} символов)")
console.print()

# Тест 4: Успешная команда для сравнения
console.print("-" * 70)
console.print("[bold cyan]Тест 4: Успешная команда (для сравнения)[/]")
console.print("[dim]Команда: echo Hello World[/]")
console.print()
result4 = execute_and_handle_result(console, 'echo Hello World')
console.print()
console.print("[green]Результат структуры данных:[/]")
console.print(f"  success: {result4['success']}")
console.print(f"  exit_code: {result4['exit_code']}")
console.print(f"  stdout: '{result4['stdout']}'")
console.print(f"  stderr: '{result4['stderr']}'")
console.print()

console.print("=" * 70)
console.print("[bold green]✅ ИТОГ:[/]")
console.print("  1. Все ошибки теперь выводятся полностью")
console.print("  2. Код завершения всегда показывается")
console.print("  3. stderr корректно захватывается и отображается")
console.print("  4. Информация доступна для добавления в контекст AI")
console.print("=" * 70)
