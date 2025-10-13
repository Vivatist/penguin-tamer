#!/usr/bin/env python3
"""Test spinner timing in robot presenter."""

import sys
import time
from unittest.mock import Mock
from rich.console import Console

# Add src to path
sys.path.insert(0, 'c:/Users/Andrey/Coding/penguin-tamer/src')

from penguin_tamer.demo.robot_presenter import RobotPresenter
from penguin_tamer.demo.timing import DEFAULT_ROBOT_TIMING


def test_spinner_timing():
    """Test that spinner shows for correct duration."""
    
    # Create mock objects
    console = Console()
    demo_manager = Mock()
    t = lambda x: x
    
    # Create presenter with default timing
    presenter = RobotPresenter(console, demo_manager, t)
    
    print(f"Timing config spinner_total_time: {presenter.timing.spinner_total_time}")
    print(f"Expected connecting time: {presenter.timing.spinner_total_time * presenter.timing.spinner_connecting_ratio}")
    print(f"Expected thinking time: {presenter.timing.spinner_total_time * presenter.timing.spinner_thinking_ratio}")
    print(f"Total expected time: {presenter.timing.spinner_total_time}")
    print()
    
    # Test the actual spinner
    print("Testing spinner (should take 10 seconds)...")
    start = time.time()
    presenter._show_spinner()
    elapsed = time.time() - start
    
    print(f"\nActual spinner duration: {elapsed:.2f} seconds")
    
    if elapsed >= 9.5:  # Allow small timing variance
        print("✅ Spinner timing is correct!")
    else:
        print(f"❌ Spinner too fast! Expected ~10s, got {elapsed:.2f}s")


if __name__ == '__main__':
    test_spinner_timing()
