"""
Тест для проверки записи LLM ответов.
"""

import json
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_llm_recording():
    """Тест записи LLM ответов из реального файла."""

    # Проверяем существующий файл demo_session_005.json
    demo_file = Path(__file__).parent / "penguin-tamer" / "penguin-tamer" / "demo" / "demo_session_005.json"

    if not demo_file.exists():
        # Пробуем альтернативный путь
        demo_file = (Path.home() / "AppData" / "Local" / "Packages" /
                     "PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0" / "LocalCache" /
                     "Local" / "penguin-tamer" / "penguin-tamer" / "demo" / "demo_session_005.json")

    if not demo_file.exists():
        print("❌ Demo file demo_session_005.json not found.")
        print(f"   Looked in: {demo_file}")
        return

    # Читаем файл
    with open(demo_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\n=== Analyzing demo_session_005.json ===")
    print(f"Version: {data['version']}")
    print(f"Total events: {len(data['events'])}")

    # Подсчитываем типы событий
    event_types = {}
    for event in data['events']:
        event_type = event.get('type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1

    print("\nEvent types:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")

    # Проверяем наличие LLM ответов
    if 'output' in event_types:
        print("\n✓ LLM outputs are recorded!")

        # Показываем примеры
        output_events = [e for e in data['events'] if e.get('type') == 'output']
        for i, event in enumerate(output_events[:2]):  # Первые 2
            text_preview = event.get('text', '')[:80].replace('\n', '\\n')
            print(f"\n  Output #{i+1}: {repr(text_preview)}...")
    else:
        print("\n❌ No LLM outputs found!")
        print("   Only found:", list(event_types.keys()))


if __name__ == "__main__":
    test_llm_recording()
