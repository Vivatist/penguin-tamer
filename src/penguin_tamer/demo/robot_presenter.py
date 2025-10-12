"""
Robot Mode Presenter - handles visual presentation of robot mode playback.

Separates robot mode UI logic from main CLI code.
"""

import sys
import time
import random
from typing import Optional, Callable
from rich.console import Console
from rich.text import Text
from rich.live import Live

from ..config_manager import config
from .manager import DemoManager
from .timing import RobotTimingConfig, DEFAULT_ROBOT_TIMING


class RobotPresenter:
    """
    Handles visual presentation of robot mode.

    Responsibilities:
    - Display typing simulation
    - Show spinner before AI responses
    - Stream response chunks with markdown
    - Manage timing and pauses
    """

    def __init__(
        self,
        console: Console,
        demo_manager: DemoManager,
        t: Callable[[str], str],
        timing: Optional[RobotTimingConfig] = None
    ):
        """
        Initialize robot presenter.

        Args:
            console: Rich console for output
            demo_manager: Demo manager instance
            t: Translation function
            timing: Timing configuration (uses default if not provided)
        """
        self.console = console
        self.demo_manager = demo_manager
        self.t = t
        self.timing = timing or DEFAULT_ROBOT_TIMING
        self.action_count = 0

    def present_action(
        self,
        action: dict,
        has_code_blocks: bool
    ) -> tuple[Optional[str], list]:
        """
        Present a single robot action.

        Args:
            action: Action dictionary from demo
            has_code_blocks: Whether code blocks are available

        Returns:
            Tuple of (action_type, code_blocks)
            action_type can be: 'query', 'command', 'code_block'
        """
        self.action_count += 1
        user_prompt = action['value']
        action_type = action.get('type')

        # Phase 1: Show prompt and placeholder
        self._show_prompt_with_placeholder(has_code_blocks)

        # Phase 2: Pause before typing
        self._pause_before_typing()

        # Phase 3: Clear and show typing
        self._clear_and_type(user_prompt)

        # Phase 4: Pause before Enter (for code blocks)
        if action_type == 'code_block':
            time.sleep(self.timing.code_block_pause)

        # Phase 5: Press Enter
        self.console.print()
        time.sleep(self.timing.after_enter_pause)

        # Phase 6: Handle response based on action type
        code_blocks = []
        if action_type == 'query':
            code_blocks = self._present_query_response()

        return action_type, code_blocks

    def _show_prompt_with_placeholder(self, has_code_blocks: bool) -> None:
        """Show prompt symbol with placeholder text."""
        self.console.print("[bold #e07333]>>> [/bold #e07333]", end='')

        if has_code_blocks:
            placeholder_text = self.t(
                "Number of the code block to execute or "
                "the next question... Ctrl+C - exit"
            )
        else:
            placeholder_text = self.t("Your question... Ctrl+C - exit")

        placeholder_obj = Text(placeholder_text, style="dim italic")
        self.console.print(placeholder_obj, end='')

        # Return cursor after prompt
        sys.stdout.write('\r')
        sys.stdout.flush()
        sys.stdout.write('\033[4C')  # Move 4 chars right (length of ">>> ")
        sys.stdout.flush()

    def _pause_before_typing(self) -> None:
        """Pause before starting to type."""
        if self.action_count == 1:
            time.sleep(self.timing.first_action_pause)
        else:
            pause = random.uniform(*self.timing.between_actions_range)
            time.sleep(pause)

    def _clear_and_type(self, user_prompt: str) -> None:
        """Clear placeholder and simulate typing."""
        # Clear placeholder
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

        # Show prompt again
        self.console.print("[bold #e07333]>>> [/bold #e07333]", end='')

        # Get typing strategy
        strategy = self.demo_manager.get_typing_strategy()

        if strategy and hasattr(strategy, 'simulate_typing'):
            # Check if command starts with dot for highlighting
            if user_prompt.startswith('.'):
                strategy.simulate_typing('.', style='dim')
                strategy.simulate_typing(user_prompt[1:], style='#007c6e')
            else:
                strategy.simulate_typing(user_prompt)
        else:
            # Fallback - just print text
            self.console.print(user_prompt, end='', highlight=False)

    def _present_query_response(self) -> list:
        """
        Present AI response for query action.

        Returns:
            List of code blocks extracted from response
        """
        # Get response without advancing index (get_next_user_action already did)
        response_data = self.demo_manager.play_next_response(advance_index=False)

        if not response_data:
            return []

        # Phase 1: Show spinner
        self._show_spinner()

        # Phase 2: Stream response
        self._stream_response(response_data)

        # Phase 3: Extract code blocks
        from ..text_utils import extract_labeled_code_blocks
        code_blocks = extract_labeled_code_blocks(response_data.response)

        return code_blocks

    def _show_spinner(self) -> None:
        """Show spinner before AI response."""
        total_time = self.timing.spinner_total_time
        connecting_time = total_time * self.timing.spinner_connecting_ratio
        thinking_time = total_time * self.timing.spinner_thinking_ratio

        with self.console.status(
            f"[dim]{self.t('Connecting...')}[/dim]",
            spinner="dots",
            spinner_style="dim"
        ) as status:
            time.sleep(connecting_time)
            status.update(f"[dim]{self.t('Ai thinking...')}[/dim]")
            time.sleep(thinking_time)

    def _stream_response(self, response_data) -> None:
        """Stream response chunks with markdown formatting."""
        from ..llm_client import _create_markdown

        theme_name = config.get("global", "markdown_theme", "default")

        with Live(
            console=self.console,
            refresh_per_second=self.timing.refresh_per_second,
            auto_refresh=True
        ) as live:
            accumulated_text = ""
            for chunk in response_data.chunks:
                accumulated_text += chunk
                markdown = _create_markdown(accumulated_text, theme_name)
                live.update(markdown)
                time.sleep(self.timing.chunk_delay)

        self.console.print()  # New line after response
