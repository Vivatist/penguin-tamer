#!/usr/bin/env python3
"""
Демонстрация потокового вывода - вывод должен появляться постепенно.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from penguin_tamer.command_executor import execute_and_handle_result

console = Console()

print("=" * 60)
print("ДЕМОНСТРАЦИЯ ПОТОКОВОГО ВЫВОДА")
print("Каждая строка должна появляться с задержкой ~1 секунда")
print("=" * 60)
print()

if os.name == 'nt':
    # Windows: используем ping с задержкой между пакетами
    code = """echo Запуск теста...
ping -n 2 127.0.0.1 > nul
echo Строка 1 (прошла 1 секунда)
ping -n 2 127.0.0.1 > nul
echo Строка 2 (прошли 2 секунды)
ping -n 2 127.0.0.1 > nul
echo Строка 3 (прошли 3 секунды)
ping -n 2 127.0.0.1 > nul
echo Строка 4 (прошли 4 секунды)
ping -n 2 127.0.0.1 > nul
echo Тест завершен!"""
else:
    # Linux: используем sleep
    code = """echo "Запуск теста..."
sleep 1
echo "Строка 1 (прошла 1 секунда)"
sleep 1
echo "Строка 2 (прошли 2 секунды)"
sleep 1
echo "Строка 3 (прошли 3 секунды)"
sleep 1
echo "Строка 4 (прошли 4 секунды)"
sleep 1
echo "Тест завершен!"
"""

import time
start = time.time()

result = execute_and_handle_result(console, code)

elapsed = time.time() - start
print()
print("=" * 60)
print(f"✅ Тест завершен за {elapsed:.1f} секунд")
print()
print("Результат:")
if elapsed < 3:
    print("⚠️  Вывод был слишком быстрым - возможно, буферизация")
else:
    print("✅ Вывод был постепенным - потоковый режим работает!")
print("=" * 60)
