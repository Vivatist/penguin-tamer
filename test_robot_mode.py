#!/usr/bin/env python3
"""Простой тест для проверки robot mode."""

import json
import sys
import time
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_recorder import DemoManager, _simulate_human_typing  # noqa: E402
from rich.console import Console  # noqa: E402


def test_robot_mode():
    """Тестирует robot mode с записью и воспроизведением."""
    console = Console()

    # 1. Создаем тестовый файл с записью
    test_file = Path(__file__).parent / "test_robot_session.json"

    # Создаем простую сессию с действиями пользователя
    demo_data = [
        {
            "timestamp": "2025-01-01T12:00:00",
            "user_query": "Привет",
            "response": "Привет! Как дела?",
            "chunks": ["Привет! ", "Как ", "дела?"],
            "metadata": {},
            "user_actions": [
                {
                    "type": "query",
                    "value": "Привет",
                    "timestamp": "2025-01-01T12:00:00"
                }
            ]
        },
        {
            "timestamp": "2025-01-01T12:00:10",
            "user_query": ".help",
            "response": "Доступные команды...",
            "chunks": ["Доступные ", "команды..."],
            "metadata": {},
            "user_actions": [
                {
                    "type": "command",
                    "value": ".help",
                    "timestamp": "2025-01-01T12:00:10"
                }
            ]
        },
        {
            "timestamp": "2025-01-01T12:00:20",
            "user_query": "Покажи пример кода",
            "response": "Вот пример:\n```python\nprint('Hello')\n```",
            "chunks": ["Вот пример:\n", "```python\n", "print('Hello')\n", "```"],
            "metadata": {},
            "user_actions": [
                {
                    "type": "query",
                    "value": "Покажи пример кода",
                    "timestamp": "2025-01-01T12:00:20"
                },
                {
                    "type": "code_block",
                    "value": "1",
                    "timestamp": "2025-01-01T12:00:25"
                }
            ]
        }
    ]

    # Сохраняем файл
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)

    console.print("[bold green]✓ Создан тестовый файл сессии[/bold green]")

    # 2. Создаем DemoManager в режиме robot
    demo_manager = DemoManager(demo_mode='robot', demo_file=str(test_file))

    console.print(f"[bold green]✓ DemoManager создан в режиме: {demo_manager.demo_mode}[/bold green]")
    console.print(f"[bold green]✓ is_robot_mode(): {demo_manager.is_robot_mode()}[/bold green]")
    console.print(f"[bold green]✓ is_playing(): {demo_manager.is_playing()}[/bold green]")

    # 3. Проверяем, что player создан
    player = demo_manager.get_player()
    if not player:
        console.print("[bold red]✗ Player не создан![/bold red]")
        return False

    console.print("[bold green]✓ Player успешно создан[/bold green]")

    # 4. Получаем и имитируем действия пользователя
    console.print("\n[bold cyan]--- Начало эмуляции robot mode ---[/bold cyan]\n")

    action_count = 0
    
    while True:
        action = player.get_next_user_action()
        if not action:
            break
        
        action_count += 1
        console.print(f"\n[bold yellow]Действие {action_count}:[/bold yellow] {action['type']}")
        console.print("[bold #e07333]>>> [/bold #e07333]", end='')
        
        # Пауза перед началом печати (кроме первого)
        if action_count > 1:
            import random
            pause = random.uniform(3.0, 4.0)
            console.print(f"[dim](пауза {pause:.2f} сек)[/dim] ", end='')
            time.sleep(pause)
        
        # Эмулируем печать с подсветкой команд
        if action['value'].startswith('.'):
            _simulate_human_typing('.', console, style='dim')
            _simulate_human_typing(action['value'][1:], console, style='#007c6e')
        else:
            _simulate_human_typing(action['value'], console)        # Перевод строки
        console.print()
        
        # Небольшая пауза после "нажатия Enter"
        time.sleep(0.3)
    
    console.print(f"\n[bold green]✓ Обработано действий: {action_count}[/bold green]")
    console.print("\n[bold cyan]--- Конец эмуляции robot mode ---[/bold cyan]\n")

    # 5. Очистка
    test_file.unlink()
    console.print("[bold green]✓ Тестовый файл удален[/bold green]")

    # Ожидаем 4 действия: "Привет", ".help", "Покажи пример кода", "1"
    return action_count == 4


if __name__ == "__main__":
    console = Console()

    console.print("[bold blue]Тестирование robot mode[/bold blue]\n")

    try:
        success = test_robot_mode()
        if success:
            console.print("\n[bold green]✓✓✓ Все тесты пройдены успешно! ✓✓✓[/bold green]")
            sys.exit(0)
        else:
            console.print("\n[bold red]✗✗✗ Тесты не прошли ✗✗✗[/bold red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Ошибка: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
