"""
Финальная демонстрация двухфазного спиннера.

Показывает все возможности:
1. Стандартные тексты "Connecting..." и "Thinking..."
2. Работу при пропуске первого input
3. Кастомные тексты
4. Отключение спиннера
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
    """Создаёт демо-файл."""
    test_dir = Path(__file__).parent / "demo_final_spinner"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Какая погода?"},
            {"type": "output", "text": "Сегодня солнечно и тепло! ☀️"},
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def main():
    """Главная функция."""
    console = Console()
    config_dir, demo_file = create_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальные значения
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_values = dict(config_data['playback'])

    try:
        print("\n" + "=" * 80)
        print("🎬 ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ ДВУХФАЗНОГО СПИННЕРА")
        print("=" * 80)
        print("\n✨ Возможности:")
        print("  • Фаза 1: 'Connecting...' - подключение к LLM")
        print("  • Фаза 2: 'Thinking...' - генерация ответа")
        print("  • Настраиваемая длительность каждой фазы")
        print("  • Кастомные тексты")
        print("  • Работа при пропуске первого input")
        print("\n" + "-" * 80)

        # Настройка для хорошей видимости
        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_phase1_text'] = "Connecting..."
        config_data['playback']['spinner_phase1_min_duration'] = 1.5
        config_data['playback']['spinner_phase1_max_duration'] = 2.0
        config_data['playback']['spinner_phase2_text'] = "Thinking..."
        config_data['playback']['spinner_phase2_min_duration'] = 1.5
        config_data['playback']['spinner_phase2_max_duration'] = 2.0

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        input("\nНажмите Enter чтобы увидеть двухфазный спиннер...")
        print()

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
        print("  ✅ Фазу 'Connecting...' (~1.5-2.0 сек)")
        print("  ✅ Плавный переход на фазу 'Thinking...'")
        print("  ✅ Фазу 'Thinking...' (~1.5-2.0 сек)")
        print("  ✅ Затем вывод ответа LLM с анимацией")
        print("\n💡 Двухфазный спиннер работает как в настоящей программе!")
        print("\n📚 Документация:")
        print("  • Полная: docs/DEMO_TWO_PHASE_SPINNER.md")
        print("  • Краткая: docs/DEMO_SPINNER_QUICK.md")
        print("  • Конфиг: src/penguin_tamer/demo_system/config_demo.yaml")

    finally:
        # Восстанавливаем оригинальные значения
        config_data['playback'] = original_values
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    main()
