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
    
    def add_command_output(self, command: str, output: str) -> None:
        """Add command output event."""
        self.events.append({
            "type": "command",
            "command": command,
            "output": output
        })
    
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
