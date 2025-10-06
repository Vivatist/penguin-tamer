#!/usr/bin/env python3
"""
Быстрый тест восстановления потокового вывода.
Запустите: python quick_test_streaming.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from penguin_tamer.command_executor import execute_and_handle_result

console = Console()

print("\n🔍 БЫСТРЫЙ ТЕСТ ПОТОКОВОГО ВЫВОДА\n")

# Команда с задержками для визуальной проверки
if os.name == 'nt':
    code = """echo Начало...
ping -n 2 127.0.0.1 > nul
echo Середина...
ping -n 2 127.0.0.1 > nul
echo Конец!"""
else:
    code = """echo "Начало..."
sleep 1
echo "Середина..."
sleep 1
echo "Конец!"
"""

print("Выполняем команду с задержками...")
print("Если строки появляются постепенно - потоковый вывод работает! ✅\n")

result = execute_and_handle_result(console, code)

print("\n✅ Тест завершен!")
print(f"Exit code: {result['exit_code']}")
print(f"Success: {result['success']}")
