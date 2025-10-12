"""
Demo Manager - Unified facade for demo system.

Provides simple interface to complex demo recording/playback subsystem.
Implements Facade Pattern - hides complexity, provides high-level interface.
"""

from typing import Optional, Literal
from rich.console import Console

from .models import DemoSession, DemoResponse
from .storage import DemoStorage
from .recorder import DemoRecorder
from .player import DemoPlayer, PlayerFactory


DemoMode = Literal['record', 'play', 'robot', 'off']


class DemoManager:
    """
    Unified interface for demo recording and playback.

    Facade Pattern - provides simple API to complex subsystem.
    Main entry point for all demo-related operations.

    Example:
        # Recording
        manager = DemoManager(mode='record', demo_file='demo.json')
        manager.record_response(query, response)
        manager.stop()

        # Playback
        manager = DemoManager(mode='play', demo_file='demo.json')
        if manager.has_more():
            response = manager.play_next()

        # Robot mode
        manager = DemoManager(mode='robot', demo_file='demo.json')
        while manager.has_more():
            action = manager.get_next_action()
            # Process action...
    """

    def __init__(
        self,
        mode: DemoMode = 'off',
        demo_file: Optional[str] = None,
        console: Optional[Console] = None
    ):
        """
        Initialize demo manager.

        Args:
            mode: Demo mode ('record', 'play', 'robot', 'off')
            demo_file: Path to demo file
            console: Rich console for output
        """
        self.mode = mode
        self.demo_file = demo_file
        self.console = console or Console()

        # Components (lazy initialization)
        self._recorder: Optional[DemoRecorder] = None
        self._player: Optional[DemoPlayer] = None
        self._storage = DemoStorage()

        # Initialize based on mode
        if mode == 'record':
            self._init_recorder()
        elif mode in ('play', 'robot'):
            self._init_player()

    def _init_recorder(self) -> None:
        """Initialize recorder for recording mode."""
        self._recorder = DemoRecorder(self.demo_file)
        self._recorder.start_recording()

    def _init_player(self) -> None:
        """Initialize player based on mode."""
        if not self.demo_file:
            return

        if self.mode == 'robot':
            self._player = PlayerFactory.create_robot_player(
                self.demo_file,
                self.console
            )
        else:
            self._player = PlayerFactory.create_streaming_player(
                self.demo_file,
                self.console
            )

    # === Recording Methods ===

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recorder is not None and self._recorder.is_recording()

    def add_user_action(self, action_type: str, value: str) -> None:
        """
        Add user action to pending list.

        Args:
            action_type: Type of action
            value: Action value
        """
        if self._recorder:
            self._recorder.add_user_action(action_type, value)

    def record_response(
        self,
        user_query: str,
        response: str,
        chunks: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Record LLM response.

        Args:
            user_query: User's query
            response: LLM response
            chunks: Response chunks
            metadata: Additional metadata
        """
        if self._recorder:
            self._recorder.record_response(
                user_query,
                response,
                chunks,
                metadata
            )

    def record_action_only(
        self,
        action_type: str,
        value: str,
        context: str = ""
    ) -> None:
        """
        Record action without LLM response.

        Args:
            action_type: Type of action
            value: Action value
            context: Additional context
        """
        if self._recorder:
            self._recorder.record_action_only(action_type, value, context)

    def stop_recording(self) -> bool:
        """
        Stop recording and save.

        Returns:
            True if saved successfully
        """
        if self._recorder:
            return self._recorder.stop_recording()
        return False

    def get_saved_path(self) -> Optional[str]:
        """
        Get path where recording was saved.

        Returns:
            Absolute path to saved file, or None if not saved
        """
        if self._recorder:
            return self._recorder.get_saved_path()
        return None

    # === Playback Methods ===

    def is_playing(self) -> bool:
        """Check if in playback mode."""
        return self.mode in ('play', 'robot')

    def is_robot_mode(self) -> bool:
        """Check if in robot mode."""
        return self.mode == 'robot'

    def has_more_responses(self) -> bool:
        """Check if there are more responses to play."""
        if self._player:
            return self._player.has_more_responses()
        return False

    def play_next_response(self, advance_index: bool = True) -> Optional[DemoResponse]:
        """
        Play next response.

        Args:
            advance_index: Whether to advance response index

        Returns:
            The response that was played
        """
        if self._player:
            return self._player.play_next_response(advance_index)
        return None

    def get_next_user_action(self) -> Optional[dict]:
        """
        Get next user action.

        Returns:
            Action dictionary or None
        """
        if self._player:
            return self._player.get_next_user_action()
        return None

    def reset_playback(self) -> None:
        """Reset playback to beginning."""
        if self._player:
            self._player.reset()

    def get_progress(self) -> tuple:
        """
        Get playback progress.

        Returns:
            Tuple of (current_index, total_responses)
        """
        if self._player:
            return self._player.get_progress()
        return (0, 0)

    # === Utility Methods ===

    def stop(self) -> bool:
        """
        Stop current operation (recording or playback).

        Returns:
            True if successful
        """
        if self.is_recording():
            return self.stop_recording()

        if self._player:
            self._player.reset()

        return True

    def is_loaded(self) -> bool:
        """Check if demo file is loaded."""
        if self._player:
            return self._player.is_loaded()
        return False

    def list_demos(self, directory: Optional[str] = None) -> list:
        """
        List available demo files.

        Args:
            directory: Directory to search (uses default if not provided)

        Returns:
            List of demo file paths
        """
        return self._storage.list_sessions(directory)

    def get_session(self) -> Optional[DemoSession]:
        """
        Get current session.

        Returns:
            DemoSession for recorder or player, None otherwise
        """
        if self._recorder:
            return self._recorder.get_session()
        if self._player:
            return self._player.session
        return None

    def get_typing_strategy(self):
        """
        Get typing strategy for robot mode (if available).

        Returns strategy that has simulate_typing method, or None.
        Used in robot mode to simulate human typing.

        Returns:
            Strategy object with simulate_typing method, or None
        """
        if self._player and self._player.strategy:
            return self._player.strategy
        return None

    # === Context Manager Support ===

    def __enter__(self):
        """Enter context (for 'with' statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and cleanup."""
        self.stop()
        return False

    # === Convenience Properties ===

    @property
    def recorder(self) -> Optional[DemoRecorder]:
        """Get recorder instance (for advanced usage)."""
        return self._recorder

    @property
    def player(self) -> Optional[DemoPlayer]:
        """Get player instance (for advanced usage)."""
        return self._player

    @property
    def storage(self) -> DemoStorage:
        """Get storage instance (for advanced usage)."""
        return self._storage


def create_demo_context(
    mode: DemoMode,
    demo_file: str,
    console: Optional[Console] = None
) -> DemoManager:
    """
    Convenience function to create demo manager with context.

    Args:
        mode: Demo mode
        demo_file: Path to demo file
        console: Rich console

    Returns:
        Configured DemoManager

    Example:
        with create_demo_context('record', 'demo.json') as manager:
            manager.record_response(query, response)
    """
    return DemoManager(mode=mode, demo_file=demo_file, console=console)
