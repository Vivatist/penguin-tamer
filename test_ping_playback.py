"""
Тест воспроизведения команды ping с реальными паузами.
"""

import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def test_ping_playback():
    """Тест воспроизведения ping с записанными паузами."""
    console = Console()

    # Используем записанный файл из предыдущего теста
    config_dir = Path(__file__).parent / "test_demo_output_ping"
    demo_file = config_dir / "demo" / "demo_session_001.json"

    if not demo_file.exists():
        print("❌ Demo file not found. Run test_ping_timing.py first.")
        return

    # Создаём demo manager в режиме воспроизведения
    demo_manager = create_demo_manager(
        mode="play",
        console=console,
        config_dir=config_dir,
        demo_file=demo_file
    )

    print("\n=== Playing Ping Demo ===")
    print("Watch how output appears with ~1 second delays between pings...\n")

    # Воспроизводим
    demo_manager.play()

    print("\n✓ Playback completed! Did you see the realistic ~1s delays?")


if __name__ == "__main__":
    test_ping_playback()
