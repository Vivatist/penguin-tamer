"""
Reusable UI widgets for the configuration menu.
"""

import time
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.widgets import Button, DataTable


class DoubleClickDataTable(DataTable):
    """DataTable with double-click support."""

    class DoubleClicked(Message):
        """Message sent when table is double-clicked."""
        def __init__(self, row: int) -> None:
            self.row = row
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_click_time = 0
        self._last_clicked_row = -1
        self._double_click_threshold = 0.5

    def on_click(self, event) -> None:
        """Handle click to detect double-click."""
        current_time = time.time()
        current_row = self.cursor_row

        # Check for double-click
        is_double_click = (
            current_row == self._last_clicked_row and
            current_time - self._last_click_time < self._double_click_threshold
        )
        if is_double_click:
            # Double-click detected!
            if current_row >= 0:
                self.post_message(self.DoubleClicked(current_row))
            # Reset
            self._last_click_time = 0
            self._last_clicked_row = -1
        else:
            # First click
            self._last_click_time = current_time
            self._last_clicked_row = current_row


class ResponsiveButtonRow(Container):
    """Container that adapts button layout based on available width."""

    def __init__(self, buttons_data: list, **kwargs):
        super().__init__(**kwargs)
        self.buttons_data = buttons_data  # List of (text, id, variant)
        self._current_layout = 4  # How many buttons fit in first row

    def compose(self) -> ComposeResult:
        """Create layout with all buttons in one row aligned to the right."""
        with Horizontal(classes="adaptive-button-row"):
            for text, btn_id, variant in self.buttons_data:
                yield Button(text, id=btn_id, variant=variant)

    def on_resize(self, event) -> None:
        """Handle container resize to adapt layout."""
        container_width = self.size.width

        # Calculate how many buttons fit: each button ~19 chars (17 content + 2 margins)
        button_width = 19
        buttons_per_row = max(1, container_width // button_width)
        buttons_per_row = min(buttons_per_row, len(self.buttons_data))

        # Only rebuild if layout changed
        if buttons_per_row != self._current_layout:
            self._current_layout = buttons_per_row
            self._rebuild_layout()

    def _rebuild_layout(self):
        """Rebuild button layout based on how many buttons fit per row."""
        # Remove all children first
        try:
            for child in list(self.children):
                child.remove()
        except Exception:
            pass

        buttons_per_row = self._current_layout
        total_buttons = len(self.buttons_data)

        # Create rows dynamically
        current_index = 0
        while current_index < total_buttons:
            # Create a new row with spacing between rows
            row_classes = "adaptive-button-row"

            row = Horizontal(classes=row_classes)
            self.mount(row)

            # Calculate how many buttons in this row
            end_index = min(current_index + buttons_per_row, total_buttons)

            # Add buttons to this row
            for text, btn_id, variant in self.buttons_data[current_index:end_index]:
                row.mount(Button(text, id=btn_id, variant=variant))

            current_index = end_index
