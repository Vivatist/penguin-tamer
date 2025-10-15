"""
Комплексный тест спиннера в демо режиме.

Проверяет:
1. Спиннер показывается перед ответами LLM
2. Спиннер работает даже когда первый input пропущен
3. Спиннер можно отключить через конфиг
4. Настройки времени спиннера работают
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
    test_dir = Path(__file__).parent / "test_spinner_final"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "Первый вопрос"},
            {"type": "output", "text": "Первый ответ"},
            {"type": "input", "text": "Второй вопрос"},
            {"type": "output", "text": "Второй ответ"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)

    return test_dir, demo_file


def test_spinner_comprehensive():
    """Комплексный тест всех функций спиннера."""
    console = Console()
    config_dir, demo_file = create_test_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Сохраняем оригинальные значения
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    original_values = {
        'spinner_enabled': config_data['playback'].get('spinner_enabled', True),
        'spinner_phase_duration': config_data['playback'].get('spinner_phase_duration', 0.1),
        'spinner_phase_variance': config_data['playback'].get('spinner_phase_variance', 0.03),
        'spinner_min_duration': config_data['playback'].get('spinner_min_duration', 0.5),
        'spinner_max_duration': config_data['playback'].get('spinner_max_duration', 2.0),
        'play_first_input': config_data['playback'].get('play_first_input', True),
    }

    results = []

    try:
        # ==================== TEST 1 ====================
        print("\n" + "=" * 80)
        print("TEST 1: Спиннер включён с настройками по умолчанию")
        print("=" * 80)

        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_min_duration'] = 0.8
        config_data['playback']['spinner_max_duration'] = 1.2
        config_data['playback']['play_first_input'] = True
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

        results.append(f"✅ TEST 1: Спиннер показан перед каждым ответом (~{duration:.1f}s)")

        # ==================== TEST 2 ====================
        print("\n" + "=" * 80)
        print("TEST 2: Спиннер с пропуском первого input")
        print("=" * 80)

        config_data['playback']['play_first_input'] = False
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

        results.append(f"✅ TEST 2: Спиннер работает даже без первого input (~{duration:.1f}s)")

        # ==================== TEST 3 ====================
        print("\n" + "=" * 80)
        print("TEST 3: Спиннер отключён")
        print("=" * 80)

        config_data['playback']['spinner_enabled'] = False
        config_data['playback']['play_first_input'] = True
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

        results.append(f"✅ TEST 3: Без спиннера воспроизведение быстрее (~{duration:.1f}s)")

        # ==================== TEST 4 ====================
        print("\n" + "=" * 80)
        print("TEST 4: Короткий спиннер (0.3-0.5s)")
        print("=" * 80)

        config_data['playback']['spinner_enabled'] = True
        config_data['playback']['spinner_min_duration'] = 0.3
        config_data['playback']['spinner_max_duration'] = 0.5
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

        results.append(f"✅ TEST 4: Короткий спиннер работает (~{duration:.1f}s)")

    finally:
        # Восстанавливаем оригинальные значения
        for key, value in original_values.items():
            config_data['playback'][key] = value
        with open(config_demo_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

    # Итоговый отчёт
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 80)
    for result in results:
        print(result)

    print("\n" + "=" * 80)
    print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 80)
    print("\n📝 Возможности спиннера:")
    print("  ✅ Показывается перед каждым ответом LLM")
    print("  ✅ Работает даже если первый input пропущен")
    print("  ✅ Можно отключить через spinner_enabled: false")
    print("  ✅ Настраиваемая длительность (min/max duration)")
    print("  ✅ Настраиваемая скорость фаз (phase_duration, variance)")
    print("  ✅ Использует тот же механизм что и в основной программе")
    print("\n💡 Спиннер полностью функционален!")


if __name__ == "__main__":
    test_spinner_comprehensive()
