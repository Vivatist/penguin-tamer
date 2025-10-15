"""
Отладочный тест для play_first_input.
"""

import sys
import json
import yaml
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))


def create_test_demo():
    """Создаёт простой демо-файл для теста."""
    test_dir = Path(__file__).parent / "test_debug"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "demo").mkdir(exist_ok=True)

    demo_data = {
        "version": "2.0",
        "events": [
            {"type": "input", "text": "===FIRST INPUT==="},
            {"type": "output", "text": "First LLM response"},
            {"type": "input", "text": "===SECOND INPUT==="},
            {"type": "output", "text": "Second LLM response"}
        ]
    }

    demo_file = test_dir / "demo" / "test.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2)

    return test_dir, demo_file


def patch_player_for_debug():
    """Патчит player.py для отладки."""
    from penguin_tamer.demo_system import player

    def debug_play_session(self):
        """Play loaded session with realistic timing + DEBUG."""
        if not self.session:
            self.console.print("[red]No session loaded[/red]")
            return

        self.is_playing = True
        play_first_input = self.config.get("playback", {}).get("play_first_input", True)
        first_input_skipped = False

        print(f"\n[DEBUG] play_first_input setting: {play_first_input}")
        print(f"[DEBUG] Total events: {len(self.session.events)}\n")

        try:
            for i, event in enumerate(self.session.events):
                if not self.is_playing:
                    break

                event_type = event.get("type")
                event_text = event.get("text", "")[:30]
                print(f"[DEBUG] Event {i + 1}: type={event_type}, text={event_text}...")

                # Skip first input event if play_first_input is False
                if not play_first_input and not first_input_skipped and event.get("type") == "input":
                    print("[DEBUG] -> SKIPPING first input (play_first_input=False)")
                    first_input_skipped = True
                    continue

                print("[DEBUG] -> PLAYING event")
                self._play_event(event)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Playback interrupted[/yellow]")
        finally:
            self.is_playing = False

    player.DemoPlayer.play_session = debug_play_session


def test_with_debug():
    """Тест с отладочными выводами."""
    from penguin_tamer.demo_system import create_demo_manager

    console = Console()
    config_dir, demo_file = create_test_demo()
    config_demo_path = Path(__file__).parent / "src" / "penguin_tamer" / "demo_system" / "config_demo.yaml"

    # Патчим для отладки
    patch_player_for_debug()

    # Сохраняем оригинальное значение
    with open(config_demo_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    original_value = config_data['playback'].get('play_first_input', True)

    try:
        print("\n" + "=" * 70)
        print("TEST 1: play_first_input = true")
        print("=" * 70)

        # Устанавливаем True для первого теста
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

        print("\n" + "=" * 70)
        print("TEST 2: play_first_input = false")
        print("=" * 70)

        # Изменяем настройку на False для второго теста
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

    print("\n" + "=" * 70)
    print("✓ Test completed")
    print("=" * 70)


if __name__ == "__main__":
    test_with_debug()
