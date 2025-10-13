#!/usr/bin/env python3
"""Integration test to verify no duplicate output in robot mode."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from penguin_tamer.demo import DemoManager
from penguin_tamer.cli import _handle_robot_action


def test_first_query_skips_reprocessing():
    """
    Test that first query with skip_input=True returns should_continue=True
    to prevent double processing in main loop.
    """
    print("Testing first query skip logic...")
    
    # Mock objects
    robot_presenter = Mock()
    robot_presenter.present_action.return_value = ('query', [])
    
    console = Mock()
    chat_client = Mock()
    
    # Test action
    action = {
        'type': 'query',
        'value': 'Test query'
    }
    
    # Call with is_first_query=True
    should_continue, code_blocks, user_prompt = _handle_robot_action(
        robot_presenter=robot_presenter,
        action=action,
        last_code_blocks=[],
        console=console,
        chat_client=chat_client,
        is_first_query=True
    )
    
    # Verify present_action was called with skip_user_input=True
    robot_presenter.present_action.assert_called_once_with(
        action,
        has_code_blocks=False,
        skip_user_input=True
    )
    
    # Verify should_continue=True (to skip _process_ai_query)
    assert should_continue is True, "should_continue must be True to skip reprocessing"
    assert user_prompt is None, "user_prompt must be None when skipping"
    
    print("✅ First query correctly returns should_continue=True")
    
    # Now test subsequent query (is_first_query=False)
    robot_presenter.reset_mock()
    
    should_continue, code_blocks, user_prompt = _handle_robot_action(
        robot_presenter=robot_presenter,
        action=action,
        last_code_blocks=[],
        console=console,
        chat_client=chat_client,
        is_first_query=False
    )
    
    # Verify present_action called with skip_user_input=False
    robot_presenter.present_action.assert_called_once_with(
        action,
        has_code_blocks=False,
        skip_user_input=False
    )
    
    # Verify should_continue=False (to process normally)
    assert should_continue is False, "should_continue must be False for subsequent queries"
    assert user_prompt == 'Test query', "user_prompt must be returned for processing"
    
    print("✅ Subsequent query correctly returns should_continue=False")
    print("\n✅ ALL TESTS PASSED")
    return True


if __name__ == '__main__':
    try:
        success = test_first_query_skips_reprocessing()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
