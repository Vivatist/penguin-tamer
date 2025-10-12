"""
Demo Timing Configuration - centralized timing settings for demo modes.

All delays, pauses, and timing-related settings in one place.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class RobotTimingConfig:
    """
    Timing configuration for robot mode presentation.

    All values in seconds unless noted otherwise.
    """

    # === Typing simulation ===
    typing_speed_range: Tuple[float, float] = (0.05, 0.12)
    """Min/max delay per character when typing (seconds)"""

    space_delay_range: Tuple[float, float] = (0.05, 0.15)
    """Delay range for space character"""

    punctuation_delay_range: Tuple[float, float] = (0.15, 0.3)
    """Delay range for punctuation marks (.,!?;:)"""

    uppercase_delay_range: Tuple[float, float] = (0.08, 0.18)
    """Delay range for uppercase letters"""

    thinking_pause_chance: float = 0.05
    """Chance of random 'thinking' pause while typing (0.0-1.0)"""

    thinking_pause_range: Tuple[float, float] = (0.2, 0.5)
    """Duration of random thinking pauses"""

    # === Action pauses ===
    first_action_pause: float = 1.0
    """Pause before first action (seconds)"""

    between_actions_range: Tuple[float, float] = (3.0, 4.0)
    """Pause before subsequent actions (seconds)"""

    code_block_pause: float = 1.5
    """Pause before pressing Enter for code blocks"""

    after_enter_pause: float = 0.3
    """Pause after pressing Enter"""

    # === Spinner timing ===
    spinner_total_time: float = 4.0
    """Total spinner display time (seconds)"""

    spinner_connecting_ratio: float = 0.4
    """Fraction of time to show 'Connecting...' (0.0-1.0)"""

    spinner_thinking_ratio: float = 0.6
    """Fraction of time to show 'Ai thinking...' (0.0-1.0)"""

    # === Streaming ===
    chunk_delay: float = 0.01
    """Delay between streaming chunks (seconds)"""

    refresh_per_second: int = 10
    """Rich Live refresh rate (Hz)"""


@dataclass
class PlaybackTimingConfig:
    """
    Timing configuration for simple/streaming playback modes.
    """

    chunk_delay: float = 0.01
    """Delay between chunks when streaming (seconds)"""

    refresh_per_second: int = 10
    """Rich Live refresh rate (Hz)"""


# === Default instances ===

DEFAULT_ROBOT_TIMING = RobotTimingConfig()
"""Default robot mode timing configuration"""

DEFAULT_PLAYBACK_TIMING = PlaybackTimingConfig()
"""Default playback timing configuration"""


# === Preset configurations ===

FAST_ROBOT_TIMING = RobotTimingConfig(
    typing_speed_range=(0.02, 0.05),
    space_delay_range=(0.02, 0.08),
    punctuation_delay_range=(0.08, 0.15),
    uppercase_delay_range=(0.03, 0.08),
    first_action_pause=0.5,
    between_actions_range=(1.0, 1.5),
    code_block_pause=0.8,
    after_enter_pause=0.2,
    spinner_total_time=0.5,
    chunk_delay=0.005,
)
"""Fast robot mode - for quick demos"""

SLOW_ROBOT_TIMING = RobotTimingConfig(
    typing_speed_range=(0.08, 0.15),
    space_delay_range=(0.08, 0.2),
    punctuation_delay_range=(0.2, 0.4),
    uppercase_delay_range=(0.12, 0.22),
    first_action_pause=2.0,
    between_actions_range=(5.0, 7.0),
    code_block_pause=2.5,
    after_enter_pause=0.5,
    spinner_total_time=2.0,
    chunk_delay=0.02,
)
"""Slow robot mode - for presentations"""

INSTANT_PLAYBACK_TIMING = PlaybackTimingConfig(
    chunk_delay=0.0,
    refresh_per_second=30,
)
"""Instant playback - no delays"""


def get_robot_timing(preset: str = 'default') -> RobotTimingConfig:
    """
    Get robot timing configuration by preset name.

    Args:
        preset: 'default', 'fast', or 'slow'

    Returns:
        RobotTimingConfig instance
    """
    presets = {
        'default': DEFAULT_ROBOT_TIMING,
        'fast': FAST_ROBOT_TIMING,
        'slow': SLOW_ROBOT_TIMING,
    }
    return presets.get(preset, DEFAULT_ROBOT_TIMING)


def get_playback_timing(preset: str = 'default') -> PlaybackTimingConfig:
    """
    Get playback timing configuration by preset name.

    Args:
        preset: 'default' or 'instant'

    Returns:
        PlaybackTimingConfig instance
    """
    presets = {
        'default': DEFAULT_PLAYBACK_TIMING,
        'instant': INSTANT_PLAYBACK_TIMING,
    }
    return presets.get(preset, DEFAULT_PLAYBACK_TIMING)
