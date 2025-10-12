"""
Playback strategies for demo system.

Implements Strategy Pattern - different algorithms for playing demos.
Each strategy is independent and interchangeable.
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Optional
from rich.console import Console

from .models import DemoResponse, DemoSession, PlaybackState


class PlaybackStrategy(ABC):
    """
    Abstract base class for playback strategies.

    Defines the interface that all playback strategies must implement.
    Follows Open/Closed Principle - open for extension, closed for modification.
    """

    def __init__(self, session: DemoSession, console: Optional[Console] = None):
        """
        Initialize strategy with session and console.

        Args:
            session: Demo session to play
            console: Rich console for output
        """
        self.session = session
        self.console = console
        self.state = PlaybackState()

    @abstractmethod
    def play_response(self, response: DemoResponse) -> None:
        """
        Play a single response.

        Args:
            response: Response to play
        """
        pass

    @abstractmethod
    def get_next_action(self) -> Optional[dict]:
        """
        Get next user action.

        Returns:
            Action dictionary or None if no more actions
        """
        pass

    def reset(self) -> None:
        """Reset playback state."""
        self.state.reset()

    def has_more_responses(self) -> bool:
        """Check if there are more responses to play."""
        return self.state.current_response_index < len(self.session.responses)


class SimplePlaybackStrategy(PlaybackStrategy):
    """
    Simple playback - just returns responses one by one.

    No special effects, just straightforward playback.
    Good for testing and basic demo playback.
    """

    def play_response(self, response: DemoResponse) -> None:
        """Simply return the response content."""
        if self.console and response.has_response_content():
            self.console.print(response.response)

    def get_next_action(self) -> Optional[dict]:
        """Get next action sequentially."""
        if not self.has_more_responses():
            return None

        response = self.session.responses[self.state.current_response_index]

        if not response.user_actions:
            self.state.advance_response()
            return None

        if self.state.current_action_index >= len(response.user_actions):
            self.state.advance_response()
            return self.get_next_action()

        action = response.user_actions[self.state.current_action_index]
        self.state.advance_action()

        return action


class StreamingPlaybackStrategy(PlaybackStrategy):
    """
    Streaming playback with chunk-by-chunk display.

    Simulates real-time LLM response streaming.
    """

    def __init__(self, session: DemoSession, console: Optional[Console] = None,
                 chunk_delay: float = 0.01):
        """
        Initialize with chunk delay.

        Args:
            session: Demo session
            console: Rich console
            chunk_delay: Delay between chunks in seconds
        """
        super().__init__(session, console)
        self.chunk_delay = chunk_delay

    def play_response(self, response: DemoResponse) -> None:
        """Play response with streaming effect."""
        if not self.console or not response.has_response_content():
            return

        for chunk in response.chunks:
            self.console.print(chunk, end='', markup=False)
            if self.chunk_delay > 0:
                time.sleep(self.chunk_delay)

        self.console.print()  # New line after response

    def get_next_action(self) -> Optional[dict]:
        """Get next action (same as simple strategy)."""
        return SimplePlaybackStrategy.get_next_action(self)


class RobotPlaybackStrategy(PlaybackStrategy):
    """
    Robot mode - fully automated playback with human-like typing.

    Simulates human interaction: types queries, waits, shows responses.
    Most realistic demo mode.
    """

    def __init__(self, session: DemoSession, console: Optional[Console] = None,
                 typing_speed_range: tuple = (0.05, 0.12),
                 pause_range: tuple = (1.0, 3.0)):
        """
        Initialize robot mode.

        Args:
            session: Demo session
            console: Rich console
            typing_speed_range: (min, max) delay per character in seconds
            pause_range: (min, max) pause between actions in seconds
        """
        super().__init__(session, console)
        self.typing_speed_range = typing_speed_range
        self.pause_range = pause_range

    def simulate_typing(self, text: str, style: Optional[str] = None) -> None:
        """
        Simulate human typing with realistic delays.

        Args:
            text: Text to type
            style: Rich style for text
        """
        if not self.console:
            return

        for char in text:
            # Print character with style
            if style:
                self.console.print(f"[{style}]{char}[/{style}]", end='', highlight=False)
            else:
                self.console.print(char, end='', highlight=False)

            # Variable typing speed
            if char == ' ':
                delay = random.uniform(0.05, 0.15)
            elif char in '.,!?;:':
                delay = random.uniform(0.15, 0.3)
            elif char.isupper():
                delay = random.uniform(0.08, 0.18)
            else:
                delay = random.uniform(*self.typing_speed_range)

            # Random "thinking" pauses
            if random.random() < 0.05:
                delay += random.uniform(0.2, 0.5)

            time.sleep(delay)

    def play_response(self, response: DemoResponse) -> None:
        """Play response with streaming effect (no typing simulation for responses)."""
        if not self.console or not response.has_response_content():
            return

        # For robot mode, we'll handle response display in the main loop
        # This is just a placeholder
        pass

    def get_next_action(self) -> Optional[dict]:
        """Get next action with state management."""
        while self.state.current_response_index < len(self.session.responses):
            response = self.session.responses[self.state.current_response_index]

            if not response.user_actions:
                self.state.advance_response()
                continue

            while self.state.current_action_index < len(response.user_actions):
                action = response.user_actions[self.state.current_action_index]

                if action['type'] in ('command', 'code_block', 'query'):
                    self.state.advance_action()
                    return action

                self.state.current_action_index += 1

            self.state.advance_response()

        return None

    def wait_between_actions(self, action_type: str) -> None:
        """
        Add realistic pause between actions.

        Args:
            action_type: Type of action ('query', 'code_block', etc.)
        """
        if action_type == 'code_block':
            # Shorter pause for code block execution
            time.sleep(random.uniform(1.0, 2.0))
        else:
            # Longer pause between queries
            time.sleep(random.uniform(*self.pause_range))


class RecordStrategy:
    """
    Strategy for recording demo sessions.

    Not a playback strategy, but uses similar pattern for consistency.
    Handles all recording logic.
    """

    def __init__(self):
        """Initialize recording strategy."""
        self.session = DemoSession()
        self.pending_actions: list = []

    def add_user_action(self, action_type: str, value: str) -> None:
        """
        Add user action to pending list.

        Args:
            action_type: Type of action
            value: Action value
        """
        from .models import UserAction

        if action_type == 'query':
            action = UserAction.create_query(value)
        elif action_type == 'command':
            action = UserAction.create_command(value)
        elif action_type == 'code_block':
            action = UserAction.create_code_block(value)
        else:
            return

        self.pending_actions.append(action.to_dict())

    def record_response(self, user_query: str, response: str, chunks: list,
                       metadata: dict) -> None:
        """
        Record a complete response with pending actions.

        Args:
            user_query: User's query
            response: LLM response
            chunks: Response chunks
            metadata: Additional metadata
        """
        from datetime import datetime

        demo_response = DemoResponse(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            response=response,
            chunks=chunks,
            metadata=metadata,
            user_actions=self.pending_actions.copy()
        )

        self.session.add_response(demo_response)
        self.pending_actions.clear()

    def record_action_only(self, action_type: str, value: str, context: str = "") -> None:
        """
        Record action without LLM response.

        Args:
            action_type: Type of action
            value: Action value
            context: Additional context
        """
        from datetime import datetime
        from .models import UserAction

        if action_type == 'code_block':
            action = UserAction.create_code_block(value)
        elif action_type == 'command':
            action = UserAction.create_command(value)
        else:
            return

        demo_response = DemoResponse(
            timestamp=datetime.now().isoformat(),
            user_query="",
            response="",
            chunks=[],
            metadata={'action_only': True, 'context': context},
            user_actions=[action.to_dict()]
        )

        self.session.add_response(demo_response)

    def clear(self) -> None:
        """Clear all recorded data."""
        self.session.clear()
        self.pending_actions.clear()

    def get_session(self) -> DemoSession:
        """Get the recorded session."""
        return self.session
