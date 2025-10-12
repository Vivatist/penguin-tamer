"""
Demo session player.

Handles playback of recorded demo sessions using different strategies.
"""

from typing import Optional
from rich.console import Console

from .models import DemoSession, DemoResponse
from .storage import DemoStorage
from .strategies import (
    PlaybackStrategy,
    SimplePlaybackStrategy,
    StreamingPlaybackStrategy,
    RobotPlaybackStrategy
)


class DemoPlayer:
    """
    Plays back recorded demo sessions.

    Uses Strategy Pattern to support different playback modes.
    Delegates actual playback behavior to strategy objects.
    """

    def __init__(
        self,
        demo_file: Optional[str] = None,
        strategy: Optional[PlaybackStrategy] = None,
        console: Optional[Console] = None
    ):
        """
        Initialize player.

        Args:
            demo_file: Path to demo file to load
            strategy: Playback strategy (will use SimplePlaybackStrategy if not provided)
            console: Rich console for output
        """
        self.demo_file = demo_file
        self.storage = DemoStorage()
        self.session: Optional[DemoSession] = None
        self.strategy = strategy
        self.console = console or Console()

        if demo_file:
            self.load(demo_file)

    def load(self, demo_file: str) -> bool:
        """
        Load demo session from file.

        Args:
            demo_file: Path to demo file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            self.session = self.storage.load_session(demo_file)
            self.demo_file = demo_file

            # Update strategy if already set, otherwise create default
            if self.strategy:
                self.strategy.session = self.session
                self.strategy.state.reset()
            else:
                # Set default strategy if none was provided
                self.strategy = SimplePlaybackStrategy(self.session, self.console)

            return True
        except Exception:
            return False

    def set_strategy(self, strategy: PlaybackStrategy) -> None:
        """
        Set playback strategy.

        Args:
            strategy: New playback strategy
        """
        self.strategy = strategy

        if self.session:
            self.strategy.session = self.session
            self.strategy.state.reset()

    def is_loaded(self) -> bool:
        """Check if a demo session is loaded."""
        return self.session is not None

    def has_more_responses(self) -> bool:
        """Check if there are more responses to play."""
        if not self.strategy or not self.session:
            return False

        return self.strategy.has_more_responses()

    def play_next_response(self, advance_index: bool = True) -> Optional[DemoResponse]:
        """
        Play next response using current strategy.

        Args:
            advance_index: Whether to advance response index after playing

        Returns:
            The response that was played, or None if no more responses
        """
        if not self.strategy or not self.session:
            return None

        if not self.strategy.has_more_responses():
            return None

        response = self.session.responses[self.strategy.state.current_response_index]

        # Play the response
        self.strategy.play_response(response)

        # Advance index if requested
        if advance_index:
            self.strategy.state.advance_response()

        return response

    def get_next_user_action(self) -> Optional[dict]:
        """
        Get next user action from current strategy.

        Returns:
            Action dictionary or None if no more actions
        """
        if not self.strategy:
            return None

        return self.strategy.get_next_action()

    def reset(self) -> None:
        """Reset playback to beginning."""
        if self.strategy:
            self.strategy.reset()

    def get_current_response_index(self) -> int:
        """Get current response index."""
        if not self.strategy:
            return 0

        return self.strategy.state.current_response_index

    def get_total_responses(self) -> int:
        """Get total number of responses in session."""
        if not self.session:
            return 0

        return len(self.session.responses)

    def get_progress(self) -> tuple:
        """
        Get playback progress.

        Returns:
            Tuple of (current_index, total_responses)
        """
        return (self.get_current_response_index(), self.get_total_responses())


class PlayerFactory:
    """
    Factory for creating players with different strategies.

    Simplifies player creation with pre-configured strategies.
    """

    @staticmethod
    def create_simple_player(
        demo_file: str,
        console: Optional[Console] = None
    ) -> DemoPlayer:
        """
        Create player with simple playback strategy.

        Args:
            demo_file: Path to demo file
            console: Rich console

        Returns:
            Configured DemoPlayer
        """
        player = DemoPlayer(demo_file=demo_file, console=console)

        if player.session:
            strategy = SimplePlaybackStrategy(player.session, console)
            player.set_strategy(strategy)

        return player

    @staticmethod
    def create_streaming_player(
        demo_file: str,
        console: Optional[Console] = None,
        chunk_delay: float = 0.01
    ) -> DemoPlayer:
        """
        Create player with streaming playback strategy.

        Args:
            demo_file: Path to demo file
            console: Rich console
            chunk_delay: Delay between chunks

        Returns:
            Configured DemoPlayer
        """
        player = DemoPlayer(demo_file=demo_file, console=console)

        if player.session:
            strategy = StreamingPlaybackStrategy(
                player.session,
                console,
                chunk_delay=chunk_delay
            )
            player.set_strategy(strategy)

        return player

    @staticmethod
    def create_robot_player(
        demo_file: str,
        console: Optional[Console] = None,
        typing_speed_range: tuple = (0.05, 0.12),
        pause_range: tuple = (1.0, 3.0)
    ) -> DemoPlayer:
        """
        Create player with robot playback strategy.

        Args:
            demo_file: Path to demo file
            console: Rich console
            typing_speed_range: (min, max) delay per character
            pause_range: (min, max) pause between actions

        Returns:
            Configured DemoPlayer
        """
        player = DemoPlayer(demo_file=demo_file, console=console)

        if player.session:
            strategy = RobotPlaybackStrategy(
                player.session,
                console,
                typing_speed_range=typing_speed_range,
                pause_range=pause_range
            )
            player.set_strategy(strategy)

        return player
