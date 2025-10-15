"""
Визуальный тест спиннера - с паузами чтобы было видно анимацию.
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
    """Создаёт демо-файл для визуального теста."""
    test_dir = Path(__file__).parent / "test_spinner_visual"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Как дела?"},
            {"type": "output", "text": "Отлично! Спасибо что спросили."},
            {"type": "input", "text": "Расскажи анекдот"},
            {"type": "output", "text": "Программист - это машина для превращения кофе в код! ☕➡️💻"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def visual_test():
    """Визуальный тест спиннера с длинными задержками."""
    console = Console()
    config_dir, demo_file = create_test_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальные значения
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_values = {
        'spinner_enabled': config_data['playback'].get('spinner_enabled', True),
        'spinner_min_duration': config_data['playback'].get('spinner_min_duration', 0.5),
        'spinner_max_duration': config_data['playback'].get('spinner_max_duration', 2.0),
        'play_first_input': config_data['playback'].get('play_first_input', True),
    }

    try:
        print("\n" + "=" * 80)
        print("ВИЗУАЛЬНЫЙ ТЕСТ СПИННЕРА")
        print("=" * 80)
        print("Спиннер будет показываться 2-3 секунды перед каждым ответом LLM")
        print("Вы увидите анимацию 'Thinking...' с крутящимися точками")
        print("-" * 80)
        input("Нажмите Enter чтобы начать...")

        # Настраиваем длинный спиннер чтобы было видно
        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_min_duration'] = 2.0
        config_data['playback']['spinner_max_duration'] = 3.0
        config_data['playback']['play_first_input'] = True
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        print("\n🎬 Начинаем демо...")
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager.play()

        print("\n" + "=" * 80)
        print("✅ Тест завершён!")
        print("=" * 80)
        print("\n💡 Вы должны были увидеть спиннер перед каждым ответом LLM!")

    finally:
        # Восстанавливаем оригинальные значения
        for key, value in original_values.items():
            config_data['playback'][key] = value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    visual_test()
