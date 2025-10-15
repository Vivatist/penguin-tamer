"""
Тест для проверки записи команд с временными метками.
"""

import json
import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402
from penguin_tamer.command_executor import execute_and_handle_result  # noqa: E402


def test_command_recording():
    """Тест записи команды с временными метками."""
    console = Console()

    # Создаём demo manager в режиме записи
    config_dir = Path(__file__).parent / "test_demo_output"
    config_dir.mkdir(exist_ok=True)

    demo_manager = create_demo_manager(
        mode="record",
        console=console,
        config_dir=config_dir
    )

    # Записываем пользовательский ввод
    demo_manager.record_user_input(".echo test command")

    # Запускаем команду с записью чанков
    command = "echo Line 1\necho Line 2\necho Line 3"
    demo_manager.start_command_recording(command)

    _ = execute_and_handle_result(console, command, demo_manager)

    demo_manager.finalize_command_output()

    # Сохраняем
    demo_manager.finalize()

    # Проверяем что файл создан
    demo_files = list((config_dir / "demo").glob("*.json"))
    assert len(demo_files) > 0, "Demo file should be created"

    # Читаем и проверяем содержимое
    with open(demo_files[0], 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n=== Recorded Demo Session ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Проверяем структуру
    assert data['version'] == '2.0'
    assert len(data['events']) == 2  # input + command

    # Проверяем событие команды
    cmd_event = data['events'][1]
    assert cmd_event['type'] == 'command'
    assert 'chunks' in cmd_event, "Command should have chunks with timing"
    assert len(cmd_event['chunks']) > 0, "Should have recorded chunks"

    # Проверяем что чанки имеют текст и задержки
    for chunk in cmd_event['chunks']:
        assert 'text' in chunk
        assert 'delay' in chunk
        print(f"Chunk: {repr(chunk['text'][:30])} at {chunk['delay']:.3f}s")

    print("\n✓ Test passed! Commands are recorded with timing.")


if __name__ == "__main__":
    test_command_recording()

