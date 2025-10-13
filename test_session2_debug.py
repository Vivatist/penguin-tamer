#!/usr/bin/env python3
"""Debug first action in robot mode with session_2.json."""

import sys
sys.path.insert(0, 'c:/Users/Andrey/Coding/penguin-tamer/src')

from pathlib import Path
from rich.console import Console
from penguin_tamer.demo import DemoManager
from penguin_tamer.demo.robot_presenter import RobotPresenter

def t(x):
    """Translation stub."""
    return x

def test_session_2():
    """Test with session_2.json."""
    console = Console()
    
    session_file = Path(r"c:\Users\Andrey\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\Local\penguin-tamer\penguin-tamer\demo_sessions\session_2.json")
    
    if not session_file.exists():
        print(f"❌ File not found: {session_file}")
        return
    
    print(f"✅ Loading: {session_file}")
    print()
    
    # Create demo manager
    manager = DemoManager(mode='robot', demo_file=str(session_file), console=console)
    
    # Create presenter
    presenter = RobotPresenter(console, manager, t)
    
    print(f"Timing config spinner_total_time: {presenter.timing.spinner_total_time}s")
    print()
    
    # Get first action
    action = manager.get_next_user_action()
    if not action:
        print("❌ No action found!")
        return
    
    print(f"First action:")
    print(f"  Type: {action.get('type')}")
    print(f"  Value: {action.get('value')}")
    print()
    
    # Check if response exists
    response = manager.play_next_response(advance_index=False)
    print(f"Response data exists: {response is not None}")
    if response:
        print(f"  Response length: {len(response.response)} chars")
        print(f"  Chunks count: {len(response.chunks)}")
    print()
    
    # Present the action
    print("Presenting first action (should show 10-second spinner)...")
    import time
    start = time.time()
    
    action_type, code_blocks = presenter.present_action(
        action,
        has_code_blocks=False,
        skip_user_input=True  # Skip first query input
    )
    
    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.2f}s")
    print(f"Action type: {action_type}")
    print(f"Code blocks found: {len(code_blocks)}")
    
    if elapsed >= 9.5:
        print("✅ Timing is correct!")
    else:
        print(f"❌ Too fast! Expected ~10s + streaming time")


if __name__ == '__main__':
    test_session_2()
