"""
Простой тест для наглядной демонстрации play_first_input.
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
    test_dir = Path(__file__).parent / "test_play_first"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "FIRST USER INPUT"},
            {"type": "output", "text": "First LLM response"},
            {"type": "input", "text": "SECOND USER INPUT"},
            {"type": "output", "text": "Second LLM response"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2)

    return test_dir, demo_file


def test_setting():
    """Тест настройки play_first_input."""
    console = Console()

    # Создаём тестовый демо-файл
    config_dir, demo_file = create_test_demo()

    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    print("\n" + "=" * 70)
    print("DEMO DATA:")
    print("=" * 70)
    print("  Event 1: [input] FIRST USER INPUT")
    print("  Event 2: [output] First LLM response")
    print("  Event 3: [input] SECOND USER INPUT")
    print("  Event 4: [output] Second LLM response")

    print("\n" + "=" * 70)
    print("TEST 1: play_first_input = true")
    print("=" * 70)
    print("Expected: Shows ALL events\n")

    demo_manager1 = create_demo_manager(
        mode="play",
        console=console,
        config_dir=config_dir,
        demo_file=demo_file
    )
    demo_manager1.play()

    print("\n" + "=" * 70)
    print("TEST 2: play_first_input = false")
    print("=" * 70)
    print("Expected: SKIPS first user input, starts from first LLM response\n")

    # Изменяем настройку
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_value = config_data['playback'].get('play_first_input', True)
    config_data['playback']['play_first_input'] = False

    with open(config_demo_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    try:
        demo_manager2 = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager2.play()
    finally:
        # Восстанавливаем
        config_data['playback']['play_first_input'] = original_value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    print("\n" + "=" * 70)
    print("✓ Difference visible? First test shows 'FIRST USER INPUT', second doesn't")
    print("=" * 70)


if __name__ == "__main__":
    test_setting()
