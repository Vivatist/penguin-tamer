"""
Simplified Demo System Manager - unified interface for recording and playback.

Uses Null Object Pattern for seamless integration without if-checks.
"""

from pathlib import Path
from typing import Optional
from rich.console import Console

from .recorder import DemoRecorder
from .player import DemoPlayer


class NullDemoManager:
    """
    Null Object implementation - does nothing, allows calls without checks.

    Usage:
        demo_manager.record_user_input("text")  # No-op if mode is 'off'
    """

    def is_recording(self) -> bool:
        return False

    def is_playing(self) -> bool:
        return False

    def is_active(self) -> bool:
        return False

    def record_user_input(self, text: str):
        pass

    def record_llm_chunk(self, chunk: str):
        pass

    def finalize_llm_output(self):
        pass

    def record_command_output(self, command: str, output: str):
        pass

    def start_command_recording(self, command: str, block_number: int = None):
        pass

    def record_command_chunk(self, chunk: str):
        pass

    def finalize_command_output(self, exit_code: int = 0, stderr: str = None, interrupted: bool = False):
        pass

    def play(self):
        pass

    def stop_playback(self):
        pass

    def finalize(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class DemoSystemManager:
    """
    Unified manager for demo system with simplified events.

    Provides simple interface for cli.py integration.
    """

    def __init__(self, mode: str, console: Console, config_dir: Path, demo_file: Optional[Path] = None,
                 play_first_input: bool = True):
        """
        Initialize demo manager.

        Args:
            mode: Mode - 'off', 'record', or 'play'
            console: Rich console
            config_dir: Directory where config is stored
            demo_file: File to play (for 'play' mode, optional - uses last if not specified)
            play_first_input: Show first user input during playback (default: True)
        """
        self.mode = mode
        self.console = console
        self.config_dir = config_dir
        self.demo_file = demo_file
        self.play_first_input = play_first_input

        self.recorder: Optional[DemoRecorder] = None
        self.player: Optional[DemoPlayer] = None

        self._initialize()

    def _initialize(self):
        """Initialize recorder or player based on mode."""
        if self.mode == "record":
            self.recorder = DemoRecorder(self.config_dir)
            recording_file = self.recorder.start_recording()
            self.console.print(f"[yellow]📹 Demo recording started: {recording_file}[/yellow]")

        elif self.mode == "play":
            # config_demo.yaml is in the same directory as this file
            config_demo_path = Path(__file__).parent / "config_demo.yaml"
            self.player = DemoPlayer(self.console, config_demo_path, self.play_first_input)

            # Determine which file to play
            if self.demo_file:
                session_file = Path(self.demo_file)
                # If not absolute path, look in demo/ folder
                if not session_file.is_absolute():
                    session_file = self.config_dir / "demo" / self.demo_file
            else:
                # Use last recording
                temp_recorder = DemoRecorder(self.config_dir)
                session_file = temp_recorder.get_last_recording()

            if session_file and session_file.exists():
                if self.player.load_session(session_file):
                    self.console.print(f"[green]▶️  Playing demo: {session_file}[/green]")
                else:
                    self.console.print(f"[red]Failed to load demo file: {session_file}[/red]")
                    self.mode = "off"
            else:
                self.console.print(f"[red]No demo file found to play: {session_file}[/red]")
                self.mode = "off"

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.mode == "record" and self.recorder is not None

    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self.mode == "play" and self.player is not None

    def is_active(self) -> bool:
        """Check if demo system is active (recording or playing)."""
        return self.mode != "off"

    # === Recording methods ===

    def record_user_input(self, text: str):
        """
        Record user input.

        Args:
            text: User input text
        """
        if self.recorder:
            self.recorder.record_user_input(text)

    def record_llm_chunk(self, chunk: str):
        """Record LLM response chunk."""
        if self.recorder:
            self.recorder.record_llm_chunk(chunk)

    def finalize_llm_output(self):
        """Finalize accumulated LLM output."""
        if self.recorder:
            self.recorder.finalize_llm_output()

    def record_command_output(self, command: str, output: str):
        """Record command execution output."""
        if self.recorder:
            self.recorder.record_command_output(command, output)

    def start_command_recording(self, command: str, block_number: int = None):
        """Start recording command output with timing."""
        if self.recorder:
            self.recorder.start_command_recording(command, block_number)

    def record_command_chunk(self, chunk: str):
        """Record a chunk of command output with timestamp."""
        if self.recorder:
            self.recorder.record_command_chunk(chunk)

    def finalize_command_output(self, exit_code: int = 0, stderr: str = None, interrupted: bool = False):
        """Finalize accumulated command output chunks."""
        if self.recorder:
            self.recorder.finalize_command_output(exit_code, stderr, interrupted)

    # === Playback methods ===

    def play(self):
        """Start playback (blocks until finished)."""
        if self.player:
            self.player.play_session()

    def stop_playback(self):
        """Stop playback."""
        if self.player:
            self.player.stop()

    # === Lifecycle methods ===

    def finalize(self):
        """Finalize demo system (save recording if needed)."""
        if self.recorder:
            saved_file = self.recorder.save_session()
            if saved_file:
                self.console.print(f"[green]✓ Demo saved: {saved_file}[/green]")
            self.recorder.stop_recording()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finalize()


def create_demo_manager(mode: str, console: Console, config_dir: Path,
                        demo_file: Optional[Path] = None, play_first_input: bool = True):
    """
    Factory function to create appropriate demo manager.

    Returns NullDemoManager if mode is 'off', otherwise DemoSystemManager.
    This allows calling code to avoid if-checks.

    Args:
        mode: 'off', 'record', or 'play'
        console: Rich console
        config_dir: Config directory path
        demo_file: Demo file for playback (optional)
        play_first_input: Show first user input during playback (default: True)

    Returns:
        DemoSystemManager or NullDemoManager

    Example:
        # No if-checks needed!
        demo_manager = create_demo_manager(mode, console, config_dir)
        demo_manager.record_user_input("Hello")  # Works regardless of mode
    """
    if mode == "off":
        return NullDemoManager()
    else:
        return DemoSystemManager(mode, console, config_dir, demo_file, play_first_input)
