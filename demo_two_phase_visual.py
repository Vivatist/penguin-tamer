"""
Визуальная демонстрация двухфазного спиннера.

Показывает:
- Фазу 1: "Connecting..." (~2-3 секунды)
- Фазу 2: "Thinking..." (~2-3 секунды)
- Плавный переход между фазами
"""

import sys
import json
import yaml
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def create_demo():
    """Создаёт простой демо-файл."""
    test_dir = Path(__file__).parent / "test_visual_phases"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Расскажи что-нибудь интересное"},
            {"type": "output", "text": "Знаете ли вы, что осьминоги имеют три сердца? 🐙"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def visual_demo():
    """Визуальная демонстрация двухфазного спиннера."""
    console = Console()
    config_dir, demo_file = create_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальные значения
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_values = {
        'spinner_enabled': config_data['playback'].get('spinner_enabled', True),
        'spinner_phase1_text': config_data['playback'].get('spinner_phase1_text', 'Connecting...'),
        'spinner_phase1_min_duration': config_data['playback'].get('spinner_phase1_min_duration', 0.3),
        'spinner_phase1_max_duration': config_data['playback'].get('spinner_phase1_max_duration', 0.8),
        'spinner_phase2_text': config_data['playback'].get('spinner_phase2_text', 'Thinking...'),
        'spinner_phase2_min_duration': config_data['playback'].get('spinner_phase2_min_duration', 0.5),
        'spinner_phase2_max_duration': config_data['playback'].get('spinner_phase2_max_duration', 2.0),
    }

    try:
        print("\n" + "=" * 80)
        print("🎬 ВИЗУАЛЬНАЯ ДЕМОНСТРАЦИЯ ДВУХФАЗНОГО СПИННЕРА")
        print("=" * 80)
        print("\nСейчас вы увидите:")
        print("  1️⃣  Пользователь вводит вопрос")
        print("  2️⃣  Спиннер фаза 1: 'Connecting...' (~2-3 секунды)")
        print("  3️⃣  Спиннер фаза 2: 'Thinking...' (~2-3 секунды)")
        print("  4️⃣  Вывод ответа LLM с анимацией")
        print("\n" + "-" * 80)
        input("Нажмите Enter чтобы начать демонстрацию...")

        # Настраиваем очень длинные фазы для наглядности
        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_phase1_text'] = "Connecting..."
        config_data['playback']['spinner_phase1_min_duration'] = 2.0
        config_data['playback']['spinner_phase1_max_duration'] = 3.0
        config_data['playback']['spinner_phase2_text'] = "Thinking..."
        config_data['playback']['spinner_phase2_min_duration'] = 2.0
        config_data['playback']['spinner_phase2_max_duration'] = 3.0

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        print("\n🚀 Демонстрация началась...\n")
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager.play()

        print("\n" + "=" * 80)
        print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 80)
        print("\n🎯 Вы видели:")
        print("  ✅ Фазу 'Connecting...' с крутящейся анимацией")
        print("  ✅ Плавный переход на фазу 'Thinking...'")
        print("  ✅ Продолжение анимации во второй фазе")
        print("  ✅ Затем вывод ответа LLM")
        print("\n💡 Это точно имитирует поведение настоящей программы!")

    finally:
        # Восстанавливаем оригинальные значения
        for key, value in original_values.items():
            config_data['playback'][key] = value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    visual_demo()
