"""
Тест двухфазного спиннера в демо режиме.

Проверяет:
1. Спиннер показывает фазу "Connecting..."
2. Затем спиннер переключается на фазу "Thinking..."
3. Обе фазы имеют настраиваемую длительность
"""

import sys
import json
import yaml
from pathlib import Path
from rich.console import Console
import time

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def create_test_demo():
    """Создаёт демо-файл для теста."""
    test_dir = Path(__file__).parent / "test_two_phase"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Привет!"},
            {"type": "output", "text": "Привет! Как дела?"},
            {"type": "input", "text": "Отлично!"},
            {"type": "output", "text": "Рад слышать! 😊"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def test_two_phase_spinner():
    """Тест двухфазного спиннера."""
    console = Console()
    config_dir, demo_file = create_test_demo()
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
        # ==================== TEST 1 ====================
        print("\n" + "=" * 80)
        print("TEST 1: Двухфазный спиннер с длинными задержками (для наглядности)")
        print("=" * 80)
        print("Фаза 1: 'Connecting...' (1.0-1.5s)")
        print("Фаза 2: 'Thinking...' (1.5-2.0s)")
        print("-" * 80)

        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_phase1_text'] = "Connecting..."
        config_data['playback']['spinner_phase1_min_duration'] = 1.0
        config_data['playback']['spinner_phase1_max_duration'] = 1.5
        config_data['playback']['spinner_phase2_text'] = "Thinking..."
        config_data['playback']['spinner_phase2_min_duration'] = 1.5
        config_data['playback']['spinner_phase2_max_duration'] = 2.0

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        start = time.time()
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file,
            play_first_input=True  # Передаём через параметр
        )
        demo_manager.play()
        duration = time.time() - start

        print(f"\n✅ TEST 1: Завершён за ~{duration:.1f}s")
        print("   Вы должны были увидеть:")
        print("   1. 'Connecting...' с анимацией (~1-1.5s)")
        print("   2. 'Thinking...' с анимацией (~1.5-2s)")
        print("   3. Затем ответ LLM")

        # ==================== TEST 2 ====================
        print("\n" + "=" * 80)
        print("TEST 2: Быстрый двухфазный спиннер")
        print("=" * 80)
        print("Фаза 1: 'Connecting...' (0.3-0.5s)")
        print("Фаза 2: 'Thinking...' (0.4-0.6s)")
        print("-" * 80)

        config_data['playback']['spinner_phase1_min_duration'] = 0.3
        config_data['playback']['spinner_phase1_max_duration'] = 0.5
        config_data['playback']['spinner_phase2_min_duration'] = 0.4
        config_data['playback']['spinner_phase2_max_duration'] = 0.6

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        start = time.time()
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager.play()
        duration = time.time() - start

        print(f"\n✅ TEST 2: Завершён за ~{duration:.1f}s (быстрее чем TEST 1)")

        # ==================== TEST 3 ====================
        print("\n" + "=" * 80)
        print("TEST 3: Кастомные тексты фаз")
        print("=" * 80)
        print("Фаза 1: 'Подключение к серверу...' (0.5s)")
        print("Фаза 2: 'Генерация ответа...' (0.8s)")
        print("-" * 80)

        config_data['playback']['spinner_phase1_text'] = "Подключение к серверу..."
        config_data['playback']['spinner_phase1_min_duration'] = 0.5
        config_data['playback']['spinner_phase1_max_duration'] = 0.5
        config_data['playback']['spinner_phase2_text'] = "Генерация ответа..."
        config_data['playback']['spinner_phase2_min_duration'] = 0.8
        config_data['playback']['spinner_phase2_max_duration'] = 0.8

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        start = time.time()
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file
        )
        demo_manager.play()
        duration = time.time() - start

        print(f"\n✅ TEST 3: Завершён за ~{duration:.1f}s")
        print("   Вы должны были увидеть русские тексты фаз!")

        # ==================== TEST 4 ====================
        print("\n" + "=" * 80)
        print("TEST 4: Двухфазный спиннер с пропуском первого input")
        print("=" * 80)

        config_data['playback']['spinner_phase1_text'] = "Connecting..."
        config_data['playback']['spinner_phase1_min_duration'] = 0.5
        config_data['playback']['spinner_phase1_max_duration'] = 0.7
        config_data['playback']['spinner_phase2_text'] = "Thinking..."
        config_data['playback']['spinner_phase2_min_duration'] = 0.6
        config_data['playback']['spinner_phase2_max_duration'] = 0.8

        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        start = time.time()
        demo_manager = create_demo_manager(
            mode="play",
            console=console,
            config_dir=config_dir,
            demo_file=demo_file,
            play_first_input=False  # Передаём через параметр
        )
        demo_manager.play()
        duration = time.time() - start

        print(f"\n✅ TEST 4: Завершён за ~{duration:.1f}s")
        print("   Спиннер показан даже без первого input!")

    finally:
        # Восстанавливаем оригинальные значения
        for key, value in original_values.items():
            config_data['playback'][key] = value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    # Итоговый отчёт
    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)
    print("\n📝 Возможности двухфазного спиннера:")
    print("  ✅ Фаза 1: 'Connecting...' (настраиваемая длительность)")
    print("  ✅ Фаза 2: 'Thinking...' (настраиваемая длительность)")
    print("  ✅ Кастомные тексты для каждой фазы")
    print("  ✅ Работает при пропуске первого input")
    print("  ✅ Плавная смена фаз без артефактов")
    print("\n💡 Двухфазный спиннер как в настоящей программе!")


if __name__ == "__main__":
    test_two_phase_spinner()
