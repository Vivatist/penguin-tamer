"""
Information panel widget for displaying help and documentation.
"""

import re
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Markdown

from .locales.menu_i18n import menu_translator


class InfoPanel(VerticalScroll):
    """Information panel showing detailed help for current tab and widgets with Markdown support."""

    content_text = reactive("")

    def compose(self) -> ComposeResult:
        """Create markdown viewer."""
        yield Markdown(id="info-markdown")

    def on_mount(self) -> None:
        """Panel mounted - will show help when first tab is activated."""

    def watch_content_text(self, new_text: str) -> None:
        """Update display when content changes."""
        try:
            md_widget = self.query_one("#info-markdown", Markdown)
            # Convert Rich markup to Markdown
            markdown_text = self._rich_to_markdown(new_text)
            md_widget.update(markdown_text)
        except Exception:
            pass

    def _rich_to_markdown(self, rich_text: str) -> str:
        """Convert Rich markup to Markdown."""
        # Replace Rich bold cyan headers with Markdown headers
        text = rich_text.replace("[bold cyan]", "## ").replace("[/bold cyan]", "")
        # Replace Rich bold with Markdown bold
        text = text.replace("[bold]", "**").replace("[/bold]", "**")
        # Replace Rich dim with Markdown italic
        text = text.replace("[dim]", "*").replace("[/dim]", "*")
        # Remove other Rich tags
        text = re.sub(r'\[/?[^\]]+\]', '', text)
        return text

    def show_tab_help(self, tab_id: str) -> None:
        """Show general help for a tab."""
        tab_help, _ = menu_translator.get_help_content()
        content = tab_help.get(
            tab_id,
            f"# Help for {tab_id}\n\nHelp not found."
        )
        self.content_text = content

    def show_help(self, widget_id: str) -> None:
        """Show detailed help for specific widget."""
        _, widget_help = menu_translator.get_help_content()
        content = widget_help.get(
            widget_id,
            f"[bold yellow]Help for {widget_id} not found[/bold yellow]"
        )
        self.content_text = content
