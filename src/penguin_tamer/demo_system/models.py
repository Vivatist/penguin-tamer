"""
Simplified data models for demo system - only actual input/output data.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class DemoSession:
    """Container for a demo session with simplified events."""
    version: str = "2.0"
    events: List[Dict[str, Any]] = field(default_factory=list)

    def add_user_input(self, text: str) -> None:
        """Add user input event."""
        self.events.append({
            "type": "input",
            "text": text
        })

    def add_llm_output(self, text: str) -> None:
        """Add LLM output event."""
        self.events.append({
            "type": "output",
            "text": text
        })

    def add_command_output(
        self,
        command: str,
        output: str = None,
        chunks: List[Dict[str, Any]] = None,
        exit_code: int = None,
        stderr: str = None,
        block_number: int = None,
        interrupted: bool = False
    ) -> None:
        """Add command output event.

        Args:
            command: Command that was executed
            output: Full output text (for simple recording)
            chunks: List of chunks with timestamps (for realistic playback)
            exit_code: Command exit code
            stderr: Error output if any
            block_number: Block number if executed as code block
            interrupted: Whether command was interrupted
        """
        event = {
            "type": "command",
            "command": command
        }

        # Add execution metadata
        if exit_code is not None:
            event["exit_code"] = exit_code
        if stderr:
            event["stderr"] = stderr
        if block_number is not None:
            event["block_number"] = block_number
        if interrupted:
            event["interrupted"] = interrupted

        # Add output data
        if chunks is not None:
            event["chunks"] = chunks
        elif output is not None:
            event["output"] = output

        self.events.append(event)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "events": self.events
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemoSession':
        """Create session from dictionary."""
        session = cls(version=data.get("version", "2.0"))
        session.events = data.get("events", [])
        return session
