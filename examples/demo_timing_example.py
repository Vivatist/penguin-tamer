"""
Example: Using different timing presets with RobotPresenter.

Shows how to use timing configuration for different scenarios.
"""

from rich.console import Console
from penguin_tamer.demo import (
    DemoManager,
    RobotPresenter,
    FAST_ROBOT_TIMING,
    SLOW_ROBOT_TIMING,
    RobotTimingConfig,
    get_robot_timing
)


def demo_with_fast_timing():
    """Quick demo for testing."""
    console = Console()
    manager = DemoManager(mode='robot', demo_file='demo.json', console=console)

    # Use fast timing preset
    presenter = RobotPresenter(console, manager, lambda x: x, timing=FAST_ROBOT_TIMING)

    print("Running with FAST timing...")
    # ... robot mode loop


def demo_with_slow_timing():
    """Presentation mode for audience."""
    console = Console()
    manager = DemoManager(mode='robot', demo_file='demo.json', console=console)

    # Use slow timing preset
    presenter = RobotPresenter(console, manager, lambda x: x, timing=SLOW_ROBOT_TIMING)

    print("Running with SLOW timing...")
    # ... robot mode loop


def demo_with_custom_timing():
    """Custom timing for specific needs."""
    console = Console()
    manager = DemoManager(mode='robot', demo_file='demo.json', console=console)

    # Create custom timing
    custom = RobotTimingConfig(
        typing_speed_range=(0.03, 0.06),    # Medium typing speed
        first_action_pause=0.5,              # Quick start
        between_actions_range=(2.0, 3.0),   # Medium pauses
        spinner_total_time=0.7,              # Medium spinner
        chunk_delay=0.008,                   # Medium streaming
    )

    presenter = RobotPresenter(console, manager, lambda x: x, timing=custom)

    print("Running with CUSTOM timing...")
    # ... robot mode loop


def demo_with_preset_by_name():
    """Get preset by name (useful for config-driven setup)."""
    console = Console()
    manager = DemoManager(mode='robot', demo_file='demo.json', console=console)

    # Get timing by name (from config or command line argument)
    preset_name = "fast"  # Could come from: args.timing_preset
    timing = get_robot_timing(preset_name)

    presenter = RobotPresenter(console, manager, lambda x: x, timing=timing)

    print(f"Running with {preset_name.upper()} timing...")
    # ... robot mode loop


if __name__ == '__main__':
    print("Demo timing examples")
    print("=" * 50)

    print("\n1. Fast timing (for quick demos):")
    print(f"   - Typing speed: {FAST_ROBOT_TIMING.typing_speed_range}")
    print(f"   - Between actions: {FAST_ROBOT_TIMING.between_actions_range}")
    print(f"   - Spinner time: {FAST_ROBOT_TIMING.spinner_total_time}s")

    print("\n2. Slow timing (for presentations):")
    print(f"   - Typing speed: {SLOW_ROBOT_TIMING.typing_speed_range}")
    print(f"   - Between actions: {SLOW_ROBOT_TIMING.between_actions_range}")
    print(f"   - Spinner time: {SLOW_ROBOT_TIMING.spinner_total_time}s")

    print("\n3. Available presets:")
    for name in ['default', 'fast', 'slow']:
        timing = get_robot_timing(name)
        print(f"   - {name}: typing {timing.typing_speed_range}, pauses {timing.between_actions_range}")
