"""
Demo session recorder.

Handles recording of LLM interactions for later playback.
Completely decoupled from specific LLM client implementations.
"""

from typing import Optional

from .models import DemoSession
from .storage import DemoStorage
from .strategies import RecordStrategy


class DemoRecorder:
    """
    Records demo sessions for later playback.

    Uses RecordStrategy for recording logic and DemoStorage for persistence.
    Follows Single Responsibility Principle - only handles recording coordination.
    """

    def __init__(self, demo_file: Optional[str] = None):
        """
        Initialize recorder.

        Args:
            demo_file: Path to save demo file (optional, can be set later)
        """
        self.demo_file = demo_file
        self.storage = DemoStorage()
        self.strategy = RecordStrategy()
        self._is_recording = False
        self._saved_path: Optional[str] = None

    def start_recording(self, demo_file: Optional[str] = None) -> None:
        """
        Start recording session.

        Args:
            demo_file: Path to save demo file
        """
        if demo_file:
            self.demo_file = demo_file

        self._is_recording = True
        self.strategy.clear()

    def stop_recording(self) -> bool:
        """
        Stop recording and save to file.

        Returns:
            True if saved successfully, False otherwise
        """
        if not self._is_recording:
            return False

        self._is_recording = False

        if self.demo_file:
            return self.save()

        return False

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def add_user_action(self, action_type: str, value: str) -> None:
        """
        Add a user action to pending list.

        Action will be associated with the next LLM response.

        Args:
            action_type: Type of action ('query', 'command', 'code_block')
            value: Action value
        """
        if not self._is_recording:
            return

        self.strategy.add_user_action(action_type, value)

    def record_response(
        self,
        user_query: str,
        response: str,
        chunks: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Record a complete LLM response.

        Includes any pending user actions.

        Args:
            user_query: User's query that prompted the response
            response: Complete LLM response text
            chunks: List of response chunks (for streaming)
            metadata: Additional metadata
        """
        if not self._is_recording:
            return

        self.strategy.record_response(
            user_query=user_query,
            response=response,
            chunks=chunks or [],
            metadata=metadata or {}
        )

    def record_action_only(
        self,
        action_type: str,
        value: str,
        context: str = ""
    ) -> None:
        """
        Record a user action without LLM response.

        Used for actions like code block execution or commands
        that don't involve the LLM.

        Args:
            action_type: Type of action ('command', 'code_block')
            value: Action value
            context: Additional context
        """
        if not self._is_recording:
            return

        self.strategy.record_action_only(action_type, value, context)

    def save(self, demo_file: Optional[str] = None) -> bool:
        """
        Save recorded session to file.

        Args:
            demo_file: Path to save to (uses self.demo_file if not provided)

        Returns:
            True if saved successfully, False otherwise
        """
        file_to_save = demo_file or self.demo_file

        if not file_to_save:
            return False

        session = self.strategy.get_session()

        try:
            saved_path = self.storage.save_session(session, file_to_save)
            # Store the actual saved path for retrieval
            self._saved_path = str(saved_path)
            return True
        except Exception:
            return False

    def get_session(self) -> DemoSession:
        """Get the current recording session."""
        return self.strategy.get_session()

    def clear(self) -> None:
        """Clear all recorded data."""
        self.strategy.clear()

    def get_response_count(self) -> int:
        """Get number of recorded responses."""
        return len(self.strategy.get_session().responses)

    def get_saved_path(self) -> Optional[str]:
        """
        Get the path where the recording was saved.

        Returns:
            Absolute path to saved file, or None if not saved yet
        """
        return self._saved_path


class RecordingContext:
    """
    Context manager for recording sessions.

    Ensures proper start/stop of recording with automatic cleanup.

    Example:
        with RecordingContext(recorder, 'demo.json') as rec:
            rec.record_response('Hello', 'Hi there!')
    """

    def __init__(self, recorder: DemoRecorder, demo_file: str):
        """
        Initialize context.

        Args:
            recorder: Demo recorder instance
            demo_file: Path to save demo file
        """
        self.recorder = recorder
        self.demo_file = demo_file

    def __enter__(self) -> DemoRecorder:
        """Start recording."""
        self.recorder.start_recording(self.demo_file)
        return self.recorder

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Stop recording and save."""
        self.recorder.stop_recording()
        return False  # Don't suppress exceptions
