"""
Тест для проверки записи команд с полными метаданными.
"""

import json
import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402
from penguin_tamer.command_executor import execute_and_handle_result  # noqa: E402


def test_command_with_error():
    """Тест записи команды с ошибкой."""
    console = Console()

    # Создаём demo manager в режиме записи
    config_dir = Path(__file__).parent / "test_demo_metadata"
    config_dir.mkdir(exist_ok=True)

    demo_manager = create_demo_manager(
        mode="record",
        console=console,
        config_dir=config_dir
    )

    print("\n=== Test 1: Successful command ===")
    demo_manager.record_user_input(".echo Success")
    command = "echo Success"
    demo_manager.start_command_recording(command)
    result = execute_and_handle_result(console, command, demo_manager)
    demo_manager.finalize_command_output(
        exit_code=result['exit_code'],
        stderr=result['stderr'],
        interrupted=result['interrupted']
    )

    print("\n=== Test 2: Command with error ===")
    demo_manager.record_user_input("2")
    error_command = "python nonexistent_file.py"
    demo_manager.start_command_recording(error_command, block_number=2)
    result = execute_and_handle_result(console, error_command, demo_manager)
    demo_manager.finalize_command_output(
        exit_code=result['exit_code'],
        stderr=result['stderr'],
        interrupted=result['interrupted']
    )

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
    command_events = [e for e in data['events'] if e.get('type') == 'command']
    assert len(command_events) == 2, "Should have 2 command events"

    # Проверяем первую команду (успешная)
    cmd1 = command_events[0]
    print("\n--- Command 1 ---")
    print(f"Command: {cmd1.get('command')}")
    print(f"Exit code: {cmd1.get('exit_code')}")
    print(f"Stderr: {cmd1.get('stderr', 'None')}")
    print(f"Block number: {cmd1.get('block_number', 'None')}")
    assert cmd1.get('exit_code') == 0, "First command should succeed"

    # Проверяем вторую команду (с ошибкой)
    cmd2 = command_events[1]
    print("\n--- Command 2 ---")
    print(f"Command: {cmd2.get('command')}")
    print(f"Exit code: {cmd2.get('exit_code')}")
    print(f"Block number: {cmd2.get('block_number')}")
    print(f"Has stderr: {bool(cmd2.get('stderr'))}")
    assert cmd2.get('exit_code') != 0, "Second command should fail"
    assert cmd2.get('block_number') == 2, "Should have block number"
    assert cmd2.get('stderr'), "Should have error message"

    print("\n✓ Test passed! Commands recorded with full metadata.")


if __name__ == "__main__":
    test_command_with_error()
