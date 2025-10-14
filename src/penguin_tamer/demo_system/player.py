"""
Simplified demo player - plays back recorded sessions with realistic timing.
"""

import json
import time
import random
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

from .models import DemoSession


class DemoPlayer:
    """Plays back recorded demo sessions with realistic timing."""

    def __init__(self, console: Console, config_path: Optional[Path] = None):
        """
        Initialize player.

        Args:
            console: Rich console for output
            config_path: Path to config_demo.yaml (if None, looks for it in demo_system/)
        """
        self.console = console
        self.session: Optional[DemoSession] = None

        # If no config path provided, use default location in demo_system/
        if config_path is None:
            config_path = Path(__file__).parent / "config_demo.yaml"

        self.config = self._load_config(config_path)
        self.is_playing = False

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load playback configuration."""
        default_config = {
            "playback": {
                "typing_delay_per_char": 0.03,
                "typing_delay_variance": 0.02,
                "pause_after_input": 0.5,
                "output_delay": 1.0,
                "char_delay": 0.01
            }
        }

        if config_path and config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        return loaded
            except Exception:
                pass

        return default_config

    def load_session(self, session_file: Path) -> bool:
        """
        Load demo session from file.

        Args:
            session_file: Path to session JSON file

        Returns:
            True if loaded successfully
        """
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.session = DemoSession.from_dict(data)
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to load session: {e}[/red]")
            return False

    def play_session(self):
        """Play loaded session with realistic timing."""
        if not self.session:
            self.console.print("[red]No session loaded[/red]")
            return

        self.is_playing = True

        try:
            for event in self.session.events:
                if not self.is_playing:
                    break

                self._play_event(event)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Playback interrupted[/yellow]")
        finally:
            self.is_playing = False

    def stop(self):
        """Stop playback."""
        self.is_playing = False

    def _play_event(self, event: Dict[str, Any]):
        """Play single event with appropriate timing and effects."""
        event_type = event.get("type")
        config = self.config.get("playback", {})

        if event_type == "input":
            self._play_user_input(event, config)
        elif event_type == "output":
            self._play_llm_output(event, config)
        elif event_type == "command":
            self._play_command_output(event, config)

    def _play_user_input(self, event: Dict[str, Any], config: Dict[str, Any]):
        """Play user input with typing simulation."""
        text = event.get("text", "")

        # Show prompt
        self.console.print("[bold #e07333]>>> [/bold #e07333]", end='')

        # Simulate typing with realistic delays
        base_delay = config.get("typing_delay_per_char", 0.03)
        variance = config.get("typing_delay_variance", 0.02)

        for char in text:
            self.console.print(char, end='', highlight=False)
            # Add variance to make it look more human
            delay = base_delay + random.uniform(-variance, variance)
            time.sleep(delay)

        # Press Enter
        self.console.print()
        time.sleep(config.get("pause_after_input", 0.5))

    def _play_llm_output(self, event: Dict[str, Any], config: Dict[str, Any]):
        """Play LLM output with realistic streaming effect and markdown rendering."""
        text = event.get("text", "")

        # Brief delay before response (thinking time)
        time.sleep(config.get("output_delay", 1.0))

        # Stream output with realistic variable-sized chunks
        base_chunk_delay = config.get("chunk_delay", 0.05)
        
        # Use Live display for progressive markdown rendering
        accumulated_text = ""
        i = 0
        
        with Live(console=self.console, auto_refresh=False) as live:
            while i < len(text):
                # Generate realistic chunk size (1-10 characters, weighted towards smaller)
                # This simulates real LLM streaming where chunks vary in size
                chunk_size = random.choices(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    weights=[5, 10, 15, 20, 15, 10, 8, 5, 2, 1]
                )[0]
                
                # Extract chunk
                chunk = text[i:i + chunk_size]
                accumulated_text += chunk
                i += chunk_size
                
                # Render accumulated text as markdown
                md = Markdown(accumulated_text)
                live.update(md)
                live.refresh()
                
                # Highly variable delay between chunks (realistic LLM behavior)
                # Sometimes fast bursts, sometimes slower processing
                delay_type = random.choices(
                    ['fast', 'normal', 'slow', 'pause'],
                    weights=[40, 35, 20, 5]
                )[0]
                
                if delay_type == 'fast':
                    # Fast burst (0.01-0.03s)
                    delay = random.uniform(0.01, 0.03)
                elif delay_type == 'normal':
                    # Normal speed (base_chunk_delay ± 30%)
                    delay = base_chunk_delay + random.uniform(-base_chunk_delay * 0.3, base_chunk_delay * 0.3)
                elif delay_type == 'slow':
                    # Slower processing (2-3x base)
                    delay = base_chunk_delay * random.uniform(2.0, 3.0)
                else:  # pause
                    # Brief thinking pause (4-6x base)
                    delay = base_chunk_delay * random.uniform(4.0, 6.0)
                
                time.sleep(max(0.01, delay))
        
        self.console.print()  # Extra newline for spacing

    def _play_command_output(self, event: Dict[str, Any], config: Dict[str, Any]):
        """Play command execution output."""
        command = event.get("command", "")
        output = event.get("output", "")

        time.sleep(0.5)

        # Show command
        self.console.print(f"[dim]>>> Executing command:[/dim] {command}")

        # Show output
        if output:
            self.console.print(output, highlight=False)

        self.console.print()
