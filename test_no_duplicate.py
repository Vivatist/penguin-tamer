#!/usr/bin/env python3
"""Test that first LLM message is shown only once in robot mode."""

import sys
import os
from io import StringIO
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from penguin_tamer.demo import DemoManager, RobotPresenter, RobotTimingConfig
from rich.console import Console

def test_no_duplicate():
    """Test that first response is shown only once."""
    
    # Create test session file
    test_file = Path(__file__).parent / "test_session_simple.json"
    test_file.write_text("""
{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant", 
      "content": "This is the first response. It should appear ONLY ONCE."
    },
    {
      "role": "user",
      "content": "2"
    },
    {
      "role": "assistant",
      "content": "This is the second response."
    }
  ],
  "actions": [
    {
      "type": "query",
      "value": "Hello",
      "note": "First query"
    },
    {
      "type": "code_block",
      "value": "2",
      "note": "Code block"
    }
  ]
}
""", encoding='utf-8')
    
    # Capture output
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    
    # Setup demo manager in robot mode
    manager = DemoManager(mode='robot', demo_file=str(test_file))
    
    # Create timing config with very short times for testing
    timing = RobotTimingConfig(
        spinner_total_time=0.1,
        chunk_delay=0.0,
        first_action_pause=0.0,
        between_actions_range=(0.0, 0.0)
    )
    
    # Create presenter
    presenter = RobotPresenter(manager, console, timing)
    
    # Get first action
    action = manager.get_next_user_action()
    print(f"First action: {action}")
    
    # Present first action with skip_user_input=True
    action_type, code_blocks = presenter.present_action(
        action,
        has_code_blocks=False,
        skip_user_input=True
    )
    
    # Get output
    result = output.getvalue()
    
    # Count occurrences of the response text
    response_text = "This is the first response. It should appear ONLY ONCE."
    count = result.count(response_text)
    
    print(f"\n--- Captured Output ---")
    print(result)
    print(f"\n--- Analysis ---")
    print(f"Response text: '{response_text}'")
    print(f"Occurrences: {count}")
    
    if count == 1:
        print("\n✅ TEST PASSED: Response shown exactly once")
        return True
    else:
        print(f"\n❌ TEST FAILED: Response shown {count} times instead of 1")
        return False

if __name__ == '__main__':
    success = test_no_duplicate()
    sys.exit(0 if success else 1)
