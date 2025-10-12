"""
Demo package - Recording and playback system for LLM interactions.

Provides a complete, decoupled system for recording and playing back
LLM interactions with support for multiple playback modes.

Architecture:
- models.py: Data models (DemoResponse, DemoSession, etc.)
- storage.py: Repository pattern for persistence
- strategies.py: Strategy pattern for playback modes
- recorder.py: Recording functionality
- player.py: Playback functionality
- manager.py: Facade for unified interface

Main entry point: DemoManager
"""

# Manager (Facade) - Main entry point
from .manager import DemoManager, create_demo_context, DemoMode

# Models - Data structures
from .models import (
    DemoResponse,
    DemoSession,
    PlaybackState,
    UserAction
)

# Storage - Persistence
from .storage import DemoStorage

# Recorder - Recording functionality
from .recorder import DemoRecorder, RecordingContext

# Player - Playback functionality
from .player import DemoPlayer, PlayerFactory

# Strategies - Playback modes
from .strategies import (
    PlaybackStrategy,
    SimplePlaybackStrategy,
    StreamingPlaybackStrategy,
    RobotPlaybackStrategy,
    RecordStrategy
)

__all__ = [
    # Manager
    'DemoManager',
    'create_demo_context',
    'DemoMode',

    # Models
    'DemoResponse',
    'DemoSession',
    'PlaybackState',
    'UserAction',

    # Storage
    'DemoStorage',

    # Recorder
    'DemoRecorder',
    'RecordingContext',

    # Player
    'DemoPlayer',
    'PlayerFactory',

    # Strategies
    'PlaybackStrategy',
    'SimplePlaybackStrategy',
    'StreamingPlaybackStrategy',
    'RobotPlaybackStrategy',
    'RecordStrategy',
]

