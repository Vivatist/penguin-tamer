"""
Simplified demo recorder - records only actual input/output data.
"""

import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import DemoSession


class DemoRecorder:
    """Records console session with simplified events."""

    def __init__(self, config_dir: Path):
        """
        Initialize recorder.

        Args:
            config_dir: Directory where config is stored (demo/ will be created inside)
        """
        self.config_dir = config_dir
        self.demo_dir = config_dir / "demo"
        self.demo_dir.mkdir(parents=True, exist_ok=True)

        self.session: Optional[DemoSession] = None
        self.current_file: Optional[Path] = None
        self.is_recording = False
        self._current_output = []  # Accumulate LLM output chunks
        self._current_command_chunks: List[Dict[str, Any]] = []  # Accumulate command output chunks
        self._command_start_time: Optional[float] = None  # Track command start time

    def start_recording(self) -> Path:
        """
        Start new recording session.

        Returns:
            Path to the recording file
        """
        self.session = DemoSession()
        self.current_file = self._get_next_filename()
        self.is_recording = True

        return self.current_file

    def stop_recording(self, auto_save: bool = True):
        """
        Stop recording and optionally save.

        Args:
            auto_save: If True, automatically save session
        """
        if auto_save and self.session:
            self.save_session()

        self.is_recording = False

    def record_user_input(self, text: str):
        """
        Record user input.

        Args:
            text: User input text
        """
        if not self.is_recording or not self.session:
            return

        self.session.add_user_input(text)

    def record_llm_chunk(self, chunk: str):
        """
        Accumulate LLM output chunk.

        Args:
            chunk: Single chunk of LLM output
        """
        if not self.is_recording:
            return

        self._current_output.append(chunk)

    def finalize_llm_output(self):
        """Finalize accumulated LLM output and add to session."""
        if not self.is_recording or not self.session:
            return

        if self._current_output:
            full_output = "".join(self._current_output)
            self.session.add_llm_output(full_output)
            self._current_output = []

    def record_command_output(self, command: str, output: str):
        """
        Record command execution output (simple version without timing).

        Args:
            command: Command that was executed
            output: Command output
        """
        if not self.is_recording or not self.session:
            return

        self.session.add_command_output(command, output=output)

    def start_command_recording(self, command: str):
        """
        Start recording command output with timing.

        Args:
            command: Command being executed
        """
        if not self.is_recording:
            return

        self._current_command_chunks = []
        self._command_start_time = time.time()
        self._current_command = command

    def record_command_chunk(self, chunk: str):
        """
        Record a chunk of command output with timestamp.

        Args:
            chunk: Output chunk (typically a line)
        """
        if not self.is_recording or self._command_start_time is None:
            return

        elapsed = time.time() - self._command_start_time
        self._current_command_chunks.append({
            "text": chunk,
            "delay": elapsed
        })

    def finalize_command_output(self):
        """Finalize accumulated command output chunks and add to session."""
        if not self.is_recording or not self.session:
            return

        if self._current_command_chunks and hasattr(self, '_current_command'):
            self.session.add_command_output(
                self._current_command,
                chunks=self._current_command_chunks
            )
            self._current_command_chunks = []
            self._command_start_time = None

    def save_session(self) -> Optional[Path]:
        """
        Save current session to file.

        Returns:
            Path to saved file or None if no session
        """
        if not self.session or not self.current_file:
            return None

        # Finalize any pending output
        self.finalize_llm_output()

        # Save to JSON
        with open(self.current_file, 'w', encoding='utf-8') as f:
            json.dump(self.session.to_dict(), f, ensure_ascii=False, indent=2)

        return self.current_file

    def _get_next_filename(self) -> Path:
        """
        Get next available filename with sequence number.

        Returns:
            Path to next demo file
        """
        # Find existing files
        existing_files = list(self.demo_dir.glob("demo_session_*.json"))

        if not existing_files:
            next_num = 1
        else:
            # Extract numbers from filenames
            numbers = []
            for f in existing_files:
                try:
                    # demo_session_001.json -> 001
                    num_str = f.stem.split('_')[-1]
                    numbers.append(int(num_str))
                except (ValueError, IndexError):
                    continue

            next_num = max(numbers, default=0) + 1

        # Create filename with padded number
        filename = f"demo_session_{next_num:03d}.json"
        return self.demo_dir / filename

    def get_last_recording(self) -> Optional[Path]:
        """
        Get path to the last recorded session.

        Returns:
            Path to last demo file or None if no recordings exist
        """
        existing_files = sorted(self.demo_dir.glob("demo_session_*.json"))

        if not existing_files:
            return None

        return existing_files[-1]
