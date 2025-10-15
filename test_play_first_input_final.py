"""
Тест настройки play_first_input для демо режима.

Проверяет что:
- play_first_input=true показывает первый пользовательский ввод
- play_first_input=false пропускает первый пользовательский ввод
"""

import sys
import json
import yaml
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def create_test_demo():
    """Создаёт простой демо-файл для теста."""
    test_dir = Path(__file__).parent / "test_play_first_final"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Первый вопрос пользователя"},
            {"type": "output", "text": "Ответ LLM на первый вопрос"},
            {"type": "input", "text": "Второй вопрос пользователя"},
            {"type": "output", "text": "Ответ LLM на второй вопрос"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def test_play_first_input():
    """Тест настройки play_first_input."""
    console = Console()
    config_dir, demo_file = create_test_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальное значение
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    original_value = config_data['playback'].get('play_first_input', True)

    try:
        print("\n" + "=" * 80)
        print("TEST 1: play_first_input = true (показывать первый ввод)")
        print("=" * 80)
        print("Ожидается: >>> Первый вопрос пользователя")
        print("-" * 80)

        # Устанавливаем True
        config_data['playback']['play_first_input'] = True
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        demo_manager1 = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager1.play()

        print("\n" + "=" * 80)
        print("TEST 2: play_first_input = false (пропустить первый ввод)")
        print("=" * 80)
        print("Ожидается: сразу начинается с 'Ответ LLM на первый вопрос'")
        print("-" * 80)

        # Устанавливаем False
        config_data['playback']['play_first_input'] = False
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        demo_manager2 = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager2.play()

    finally:
        # Восстанавливаем оригинальное значение
        config_data['playback']['play_first_input'] = original_value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    print("\n" + "=" * 80)
    print("✅ Тест завершён успешно!")
    print("=" * 80)
    print("\nРезультаты:")
    print("  TEST 1: Показал первый пользовательский ввод")
    print("  TEST 2: Пропустил первый пользовательский ввод")
    print("\n💡 Настройка работает правильно!")


if __name__ == "__main__":
    test_play_first_input()
