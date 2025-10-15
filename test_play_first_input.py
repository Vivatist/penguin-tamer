"""
Тест для проверки настройки play_first_input.
"""

import sys
import yaml
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def test_play_first_input():
    """Тест настройки play_first_input."""
    console = Console()

    # Используем существующий файл demo_session_009.json
    demo_file = (Path.home() / "AppData" / "Local" / "Packages" /
                 "PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0" / "LocalCache" /
                 "Local" / "penguin-tamer" / "penguin-tamer" / "demo" / "demo_session_009.json")

    if not demo_file.exists():
        print(f"❌ Demo file not found: {demo_file}")
        return

    config_dir = demo_file.parent.parent

    # Путь к config_demo.yaml
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    print("\n" + "=" * 70)
    print("TEST 1: play_first_input = true (default)")
    print("=" * 70)
    print("Should show first user input, then LLM response, then rest...\n")

    # Создаём demo manager с play_first_input = true
    demo_manager = create_demo_manager(
        mode="play",
        console=console,
        config_dir=config_dir,
        demo_file=demo_file
    )

    demo_manager.play()

    print("\n" + "=" * 70)
    print("TEST 2: play_first_input = false")
    print("=" * 70)
    print("Should START from LLM response (skip first user input)...\n")

    # Временно изменяем настройку
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_value = config_data['playback'].get('play_first_input', True)
    config_data['playback']['play_first_input'] = False

    with open(config_demo_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    try:
        # Создаём новый demo manager с обновлённой настройкой
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

    print("\n" + "=" * 70)
    print("✓ Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_play_first_input()
