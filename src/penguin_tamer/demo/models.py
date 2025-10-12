"""
Data models for demo system.

Contains all data structures used in demo recording/playback.
Follows Single Responsibility Principle - each class has one clear purpose.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class UserAction:
    """Represents a single user action during a demo session."""

    type: str  # 'query', 'command', 'code_block'
    value: str
    timestamp: str

    @classmethod
    def create_query(cls, value: str) -> 'UserAction':
        """Factory method for query actions."""
        return cls(
            type='query',
            value=value,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def create_command(cls, value: str) -> 'UserAction':
        """Factory method for command actions."""
        return cls(
            type='command',
            value=value,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def create_code_block(cls, value: str) -> 'UserAction':
        """Factory method for code block actions."""
        return cls(
            type='code_block',
            value=value,
            timestamp=datetime.now().isoformat()
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            'type': self.type,
            'value': self.value,
            'timestamp': self.timestamp
        }


@dataclass
class DemoResponse:
    """
    Represents a recorded LLM response with all associated data.

    This is a Value Object - immutable after creation,
    representing a complete response snapshot.
    """

    timestamp: str
    user_query: str
    response: str
    chunks: List[str]
    metadata: Dict[str, Any]
    user_actions: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            'timestamp': self.timestamp,
            'user_query': self.user_query,
            'response': self.response,
            'chunks': self.chunks,
            'metadata': self.metadata,
            'user_actions': self.user_actions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemoResponse':
        """
        Create DemoResponse from dictionary.

        Args:
            data: Dictionary with response data

        Returns:
            DemoResponse instance
        """
        return cls(
            timestamp=data.get('timestamp', ''),
            user_query=data.get('user_query', ''),
            response=data.get('response', ''),
            chunks=data.get('chunks', []),
            metadata=data.get('metadata', {}),
            user_actions=data.get('user_actions', [])
        )

    def has_response_content(self) -> bool:
        """Check if response has actual content."""
        return bool(self.response and self.chunks)

    def is_action_only(self) -> bool:
        """Check if this is an action-only entry (no LLM response)."""
        return self.metadata.get('action_only', False)


@dataclass
class DemoSession:
    """
    Represents a complete demo session.

    Aggregates multiple responses into a coherent session.
    """

    responses: List[DemoResponse] = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)

    def add_response(self, response: DemoResponse) -> None:
        """Add a response to the session."""
        self.responses.append(response)

    def get_response_count(self) -> int:
        """Get total number of responses."""
        return len(self.responses)

    def clear(self) -> None:
        """Clear all responses."""
        self.responses.clear()

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert session to list of dicts for JSON."""
        return [response.to_dict() for response in self.responses]

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> 'DemoSession':
        """Create session from list of dicts."""
        session = cls()
        for item in data:
            session.add_response(DemoResponse.from_dict(item))
        return session


@dataclass
class PlaybackState:
    """
    Maintains state during playback.

    Follows State pattern - encapsulates playback state.
    """

    current_response_index: int = 0
    current_action_index: int = 0
    is_playing: bool = False
    is_paused: bool = False

    def advance_response(self) -> None:
        """Move to next response."""
        self.current_response_index += 1
        self.current_action_index = 0

    def advance_action(self) -> None:
        """Move to next action within current response."""
        self.current_action_index += 1

    def reset(self) -> None:
        """Reset to initial state."""
        self.current_response_index = 0
        self.current_action_index = 0
        self.is_playing = False
        self.is_paused = False

    def start(self) -> None:
        """Start playback."""
        self.is_playing = True
        self.is_paused = False

    def pause(self) -> None:
        """Pause playback."""
        self.is_paused = True

    def resume(self) -> None:
        """Resume playback."""
        self.is_paused = False

    def stop(self) -> None:
        """Stop playback."""
        self.is_playing = False
        self.is_paused = False
