#!/usr/bin/env python3
"""
Тест потокового вывода команд в реальном времени.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from penguin_tamer.command_executor import execute_and_handle_result

console = Console()

print("=" * 60)
print("Тест 1: Команда с задержкой между выводами (ping)")
print("Ожидается: вывод появляется построчно в реальном времени")
print("=" * 60)

# Windows: ping с 4 пакетами (вывод с задержками)
# Linux: ping с 4 пакетами и таймаутом 1 сек между пакетами
if os.name == 'nt':
    code = "ping -n 4 127.0.0.1"
else:
    code = "ping -c 4 -i 1 127.0.0.1"

result = execute_and_handle_result(console, code)

print("\n" + "=" * 60)
print("Тест 2: Команда с выводом в stderr (несуществующий хост)")
print("Ожидается: сообщение об ошибке появляется сразу")
print("=" * 60)

if os.name == 'nt':
    code = "ping -n 1 999.999.999.999"
else:
    code = "ping -c 1 999.999.999.999"

result = execute_and_handle_result(console, code)

print("\n" + "=" * 60)
print("Тест 3: Последовательные команды с задержками")
print("Ожидается: каждая команда выводится сразу после выполнения")
print("=" * 60)

if os.name == 'nt':
    code = """echo Шаг 1: Начало теста
echo Шаг 2: Проверка системы
systeminfo | findstr /C:"OS Name"
echo Шаг 3: Завершение"""
else:
    code = """echo "Шаг 1: Начало теста"
sleep 1
echo "Шаг 2: Проверка системы"
uname -a
sleep 1
echo "Шаг 3: Завершение"
"""

result = execute_and_handle_result(console, code)

print("\n" + "=" * 60)
print("✅ Тестирование завершено!")
print("=" * 60)
print("\nПроверьте:")
print("1. Строки появляются постепенно, а не все разом в конце")
print("2. Ошибки отображаются корректно")
print("3. Код завершения показывается после каждой команды")
