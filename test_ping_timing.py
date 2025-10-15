"""
Тест для проверки записи команды с реальными паузами (ping).
"""

import json
import sys
from pathlib import Path
from rich.console import Console

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))

from penguin_tamer.demo_system import create_demo_manager  # noqa: E402
from penguin_tamer.command_executor import execute_and_handle_result  # noqa: E402


def test_ping_recording():
    """Тест записи команды ping с реальными паузами."""
    console = Console()

    # Создаём demo manager в режиме записи
    config_dir = Path(__file__).parent / "test_demo_output_ping"
    config_dir.mkdir(exist_ok=True)

    demo_manager = create_demo_manager(
        mode="record",
        console=console,
        config_dir=config_dir
    )

    # Записываем пользовательский ввод
    demo_manager.record_user_input(".ping 8.8.8.8")

    # Запускаем команду ping (только 3 пакета для скорости)
    command = "ping -n 3 8.8.8.8"
    demo_manager.start_command_recording(command)

    print("\n=== Executing ping command ===")
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
    print(f"Total events: {len(data['events'])}")

    # Проверяем событие команды
    cmd_event = data['events'][1]
    assert cmd_event['type'] == 'command'
    assert 'chunks' in cmd_event, "Command should have chunks with timing"

    print(f"Total chunks: {len(cmd_event['chunks'])}")
    print("\nTiming between chunks:")

    prev_delay = 0.0
    for i, chunk in enumerate(cmd_event['chunks']):
        delay_diff = chunk['delay'] - prev_delay
        text_preview = chunk['text'].replace('\n', '\\n')[:40]
        print(f"  #{i+1}: +{delay_diff:.3f}s -> {repr(text_preview)}")
        prev_delay = chunk['delay']

    print("\n✓ Test passed! Ping command recorded with realistic timing.")


if __name__ == "__main__":
    test_ping_recording()
