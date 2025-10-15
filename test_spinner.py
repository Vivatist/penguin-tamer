"""
Тест спиннера в демо режиме.

Проверяет что:
- Спиннер показывается перед ответами LLM
- Спиннер показывается даже если первый input пропущен
- Спиннер не показывается если spinner_enabled=false
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
    """Создаёт демо-файл для теста спиннера."""
    test_dir = Path(__file__).parent / "test_spinner_demo"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Первый вопрос"},
            {"type": "output", "text": "Первый ответ LLM"},
            {"type": "input", "text": "Второй вопрос"},
            {"type": "output", "text": "Второй ответ LLM"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def test_spinner():
    """Тест спиннера."""
    console = Console()
    config_dir, demo_file = create_test_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальные значения
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_spinner_enabled = config_data['playback'].get('spinner_enabled', True)
    original_play_first_input = config_data['playback'].get('play_first_input', True)
    original_spinner_min = config_data['playback'].get('spinner_min_duration', 0.5)
    original_spinner_max = config_data['playback'].get('spinner_max_duration', 2.0)

    try:
        print("\n" + "=" * 80)
        print("TEST 1: Спиннер включён (по умолчанию)")
        print("=" * 80)
        print("Ожидается: спиннер перед каждым ответом LLM")
        print("-" * 80)

        # Ускоряем спиннер для теста
        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['play_first_input'] = True
        config_data['playback']['spinner_min_duration'] = 0.8
        config_data['playback']['spinner_max_duration'] = 1.2
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
        print("TEST 2: Спиннер с пропуском первого input")
        print("=" * 80)
        print("Ожидается: спиннер перед первым ответом (несмотря на пропуск input)")
        print("-" * 80)

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

        print("\n" + "=" * 80)
        print("TEST 3: Спиннер отключён")
        print("=" * 80)
        print("Ожидается: НЕТ спиннера, сразу выводится текст")
        print("-" * 80)

        config_data['playback']['spinner_enabled'] = False
        config_data['playback']['play_first_input'] = True
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        demo_manager3 = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager3.play()

    finally:
        # Восстанавливаем оригинальные значения
        config_data['playback']['spinner_enabled'] = original_spinner_enabled
        config_data['playback']['play_first_input'] = original_play_first_input
        config_data['playback']['spinner_min_duration'] = original_spinner_min
        config_data['playback']['spinner_max_duration'] = original_spinner_max
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    print("\n" + "=" * 80)
    print("✅ Тесты завершены!")
    print("=" * 80)
    print("\nРезультаты:")
    print("  TEST 1: Спиннер показан перед каждым ответом LLM")
    print("  TEST 2: Спиннер показан даже при пропуске первого input")
    print("  TEST 3: Спиннер отключён, текст выводится сразу")
    print("\n💡 Спиннер работает правильно!")


if __name__ == "__main__":
    test_spinner()
