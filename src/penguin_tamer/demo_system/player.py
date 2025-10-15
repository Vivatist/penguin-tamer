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

    def __init__(self, console: Console, config_path: Optional[Path] = None, play_first_input: bool = True):
        """
        Initialize player.

        Args:
            console: Rich console for output
            config_path: Path to config_demo.yaml (if None, looks for it in demo_system/)
            play_first_input: Show first user input during playback (default: True)
        """
        self.console = console
        self.session: Optional[DemoSession] = None
        self.play_first_input = play_first_input

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
        play_first_input = self.play_first_input  # Use instance variable instead of config
        first_input_skipped = False
        previous_event_type = None
        last_output_text = None  # Track last LLM output for placeholder logic

        try:
            for event in self.session.events:
                if not self.is_playing:
                    break

                event_type = event.get("type")

                # Track last output text
                if event_type == "output":
                    last_output_text = event.get("text", "")

                # Skip first input event if play_first_input is False
                if not play_first_input and not first_input_skipped and event_type == "input":
                    first_input_skipped = True
                    # Set previous_event_type to 'input' even though we skipped it
                    # so spinner shows before first output
                    previous_event_type = "input"
                    continue

                # Show spinner before LLM output if previous event was input or if first input was skipped
                if event_type == "output":
                    # Show spinner after input or at the start if first input was skipped
                    if (previous_event_type == "input" or
                            (not play_first_input and not first_input_skipped and
                             previous_event_type is None)):
                        self._show_spinner()

                self._play_event(event, last_output_text)
                previous_event_type = event_type
            
            # Show final prompt with placeholder after all events
            if self.is_playing:
                self._show_final_prompt(last_output_text)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Playback interrupted[/yellow]")
        finally:
            self.is_playing = False

    def stop(self):
        """Stop playback."""
        self.is_playing = False

    def _show_spinner(self):
        """Show two-phase spinner before LLM output (Connecting... → Thinking...)."""
        config = self.config.get("playback", {})

        if not config.get("spinner_enabled", True):
            return

        phase_duration = config.get("spinner_phase_duration", 0.1)
        phase_variance = config.get("spinner_phase_variance", 0.03)

        # Phase 1: "Connecting..."
        phase1_text = config.get("spinner_phase1_text", "Connecting...")
        phase1_min = config.get("spinner_phase1_min_duration", 0.3)
        phase1_max = config.get("spinner_phase1_max_duration", 0.8)
        phase1_duration = random.uniform(phase1_min, phase1_max)

        # Phase 2: "Thinking..."
        phase2_text = config.get("spinner_phase2_text", "Thinking...")
        phase2_min = config.get("spinner_phase2_min_duration", 0.5)
        phase2_max = config.get("spinner_phase2_max_duration", 2.0)
        phase2_duration = random.uniform(phase2_min, phase2_max)

        try:
            # Используем один status для обеих фаз
            with self.console.status(f"[dim]{phase1_text}[/dim]",
                                     spinner="dots",
                                     spinner_style="dim") as status:
                # Phase 1: Connecting
                start_time = time.time()
                while time.time() - start_time < phase1_duration:
                    delay = phase_duration + random.uniform(-phase_variance, phase_variance)
                    delay = max(0.01, delay)
                    time.sleep(delay)

                # Phase 2: Thinking - обновляем сообщение на той же строке
                status.update(f"[dim]{phase2_text}[/dim]")
                start_time = time.time()
                while time.time() - start_time < phase2_duration:
                    delay = phase_duration + random.uniform(-phase_variance, phase_variance)
                    delay = max(0.01, delay)
                    time.sleep(delay)
        except KeyboardInterrupt:
            pass

    def _play_event(self, event: Dict[str, Any], last_output_text: str = None):
        """Play single event with appropriate timing and effects."""
        event_type = event.get("type")
        config = self.config.get("playback", {})

        if event_type == "input":
            self._play_user_input(event, config, last_output_text)
        elif event_type == "output":
            self._play_llm_output(event, config)
        elif event_type == "command":
            self._play_command_output(event, config)

    def _play_user_input(self, event: Dict[str, Any], config: Dict[str, Any],
                         last_output_text: str = None):
        """Play user input with typing simulation."""
        text = event.get("text", "")

        # Show prompt
        self.console.print("[bold #e07333]>>> [/bold #e07333]", end='')

        # Check if last output has code blocks (look for [Code #N] pattern)
        has_code_blocks = False
        if last_output_text:
            import re
            has_code_blocks = bool(re.search(r'\[Code #\d+\]', last_output_text))

        # Show placeholder
        if has_code_blocks:
            placeholder = (
                "Number of the code block to execute or "
                "the next question... Ctrl+C - exit"
            )
        else:
            placeholder = "Your question... Ctrl+C - exit"

        # Print placeholder, then move cursor back to start position
        self.console.print(f"[dim italic]{placeholder}[/dim italic]", end='')
        # Move cursor back to beginning of line, then forward 4 chars (past ">>> ")
        # \r - return to start, \033[4C - move cursor forward 4 positions
        print('\r\033[4C', end='', flush=True)

        # Pause before typing (simulating user reading/thinking)
        pause_before = config.get("pause_before_input", 0.5)
        time.sleep(pause_before)
        
        # Clear line and show prompt atomically to avoid cursor jump
        import sys
        from io import StringIO
        # Capture Rich output to string
        buffer = StringIO()
        temp_console = Console(file=buffer, force_terminal=True, width=200)
        temp_console.print("[bold #e07333]>>> [/bold #e07333]", end='')
        rendered = buffer.getvalue()
        # Atomic operation: clear line + print colored prompt
        sys.stdout.write('\r\033[K' + rendered)
        sys.stdout.flush()

        # Simulate typing with realistic delays
        base_delay = config.get("typing_delay_per_char", 0.03)
        variance = config.get("typing_delay_variance", 0.02)

        # Check if it's a dot command for special formatting
        if text.startswith('.'):
            # Type the dot in gray (dim)
            self.console.print('.', end='', style='dim', highlight=False)
            delay = base_delay + random.uniform(-variance, variance)
            time.sleep(delay)

            # Type the rest in teal color (#007c6e)
            for char in text[1:]:
                self.console.print(char, end='', style='#007c6e', highlight=False)
                delay = base_delay + random.uniform(-variance, variance)
                time.sleep(delay)
        else:
            # Normal text - no special formatting
            for char in text:
                self.console.print(char, end='', highlight=False)
                delay = base_delay + random.uniform(-variance, variance)
                time.sleep(delay)

        # Pause then press Enter
        time.sleep(config.get("pause_after_input", 0.5))
        self.console.print()

    def _show_final_prompt(self, last_output_text: str = None):
        """Show final prompt with placeholder, wait, then type 'quit'."""
        config = self.config.get("playback", {})

        # Show prompt
        self.console.print("[bold #e07333]>>> [/bold #e07333]", end='')

        # Check if last output has code blocks
        has_code_blocks = False
        if last_output_text:
            import re
            has_code_blocks = bool(re.search(r'\[Code #\d+\]', last_output_text))

        # Show placeholder
        if has_code_blocks:
            placeholder = (
                "Number of the code block to execute or "
                "the next question... Ctrl+C - exit"
            )
        else:
            placeholder = "Your question... Ctrl+C - exit"

        # Print placeholder, cursor stays at start
        self.console.print(f"[dim italic]{placeholder}[/dim italic]", end='')
        # Move cursor back to beginning of line, then forward 4 chars (past ">>> ")
        # \r - return to start, \033[4C - move cursor forward 4 positions
        print('\r\033[4C', end='', flush=True)

        # Pause at final prompt
        final_pause = config.get("final_prompt_pause", 4.0)
        time.sleep(final_pause)
        
        # Clear line and show prompt atomically to avoid cursor jump
        import sys
        from io import StringIO
        # Capture Rich output to string
        buffer = StringIO()
        temp_console = Console(file=buffer, force_terminal=True, width=200)
        temp_console.print("[bold #e07333]>>> [/bold #e07333]", end='')
        rendered = buffer.getvalue()
        # Atomic operation: clear line + print colored prompt
        sys.stdout.write('\r\033[K' + rendered)
        sys.stdout.flush()

        # Type 'quit' as whole word
        self.console.print("quit", highlight=False)

    def _play_llm_output(self, event: Dict[str, Any], config: Dict[str, Any]):
        """Play LLM output with realistic streaming effect and markdown rendering."""
        text = event.get("text", "")

        # Note: Spinner is shown before this method is called in play_session()
        # No additional delay needed here

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
        """Play command execution output with proper formatting and recorded timing."""
        command = event.get("command", "")
        block_number = event.get("block_number")
        exit_code = event.get("exit_code", 0)
        stderr = event.get("stderr", "")
        interrupted = event.get("interrupted", False)

        time.sleep(0.3)

        # Show header (Running block or Executing command)
        if block_number is not None:
            self.console.print(f"[dim]>>> Running block #{block_number}:[/dim]")
            self.console.print(command)
        else:
            self.console.print(f"[dim]>>> Executing command:[/dim] {command}")

        # Show "Result:" header
        self.console.print("[dim]>>> Result:[/dim]")

        # Check if we have chunks with timing or just plain output
        chunks = event.get("chunks")
        output = event.get("output")

        if chunks:
            # Replay stdout with recorded timing
            last_delay = 0.0
            for chunk_data in chunks:
                chunk_text = chunk_data.get("text", "")
                chunk_delay = chunk_data.get("delay", 0.0)

                # Wait for the time difference between this chunk and previous
                delay_diff = chunk_delay - last_delay
                if delay_diff > 0:
                    time.sleep(delay_diff)

                # Print chunk without newline (already included in chunk)
                print(chunk_text, end='', flush=True)
                last_delay = chunk_delay
        elif output:
            # Show output exactly as it was
            self.console.print(output, highlight=False)

        # Show exit code
        self.console.print(f"[dim]>>> Exit code: {exit_code}[/dim]")

        # Show stderr if present
        if stderr and not interrupted:
            self.console.print("[dim italic]>>> Error:[/dim italic]")
            self.console.print(f"[dim italic]{stderr}[/dim italic]")

        # Show interruption message
        if interrupted:
            self.console.print("[dim]>>> Command interrupted by user (Ctrl+C)[/dim]")

        self.console.print()  # Empty line after command output
