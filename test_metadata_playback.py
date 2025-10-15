"""
Тест воспроизведения команд с полными метаданными.
"""

import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402


def test_playback_with_metadata():
    """Тест воспроизведения команд с exit code и stderr."""
    console = Console()

    # Используем записанный файл из предыдущего теста
    config_dir = Path(__file__).parent / "test_demo_metadata"
    demo_file = config_dir / "demo" / "demo_session_001.json"

    if not demo_file.exists():
        print("❌ Demo file not found. Run test_command_metadata.py first.")
        return

    # Создаём demo manager в режиме воспроизведения
    demo_manager = create_demo_manager(
        mode="play",
        console=console,
        config_dir=config_dir,
        demo_file=demo_file
    )

    print("\n=== Playing Demo with Metadata ===")
    print("Watch how output includes:")
    print("  - 'Running block #N:' for code blocks")
    print("  - 'Result:' header")
    print("  - Exit codes")
    print("  - Error messages\n")

    # Воспроизводим
    demo_manager.play()

    print("\n✓ Playback completed! Did you see the complete output?")


if __name__ == "__main__":
    test_playback_with_metadata()
