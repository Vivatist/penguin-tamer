"""
Тест для проверки воспроизведения команд с записанными паузами.
"""

import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def test_command_playback():
    """Тест воспроизведения команды с записанными временными метками."""
    console = Console()

    # Используем записанный файл из предыдущего теста
    config_dir = Path(__file__).parent / "test_demo_output"
    demo_file = config_dir / "demo" / "demo_session_001.json"

    if not demo_file.exists():
        print("❌ Demo file not found. Run test_command_timing.py first.")
        return

    # Создаём demo manager в режиме воспроизведения
    demo_manager = create_demo_manager(
        mode="play",
        console=console,
        config_dir=config_dir,
        demo_file=demo_file
    )

    print("\n=== Playing Demo Session ===")
    print("Watch how output appears with recorded timing...\n")

    # Воспроизводим
    demo_manager.play()

    print("\n✓ Playback completed!")


if __name__ == "__main__":
    test_command_playback()
