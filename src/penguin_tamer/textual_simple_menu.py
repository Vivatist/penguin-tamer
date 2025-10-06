#!/usr/bin/env python3
"""
Упрощённое Textual меню с гарантированным отображением контента.
"""

import sys
from pathlib import Path

# Add src directory to path
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Static,
    TabbedContent,
    TabPane,
)

from penguin_tamer.config_manager import config


class SimpleConfigMenu(App):
    """Упрощённое меню конфигурации."""

    CSS = """
    TabbedContent {
        height: 100%;
    }

    TabPane {
        padding: 2;
    }

    Static {
        margin-bottom: 1;
    }

    DataTable {
        height: 15;
        margin-bottom: 2;
        border: solid green;
    }

    Button {
        margin: 0 1 1 0;
    }

    Input {
        margin-bottom: 1;
        width: 40;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Выход"),
        Binding("ctrl+c", "quit", "Выход"),
    ]

    TITLE = "🐧 Penguin Tamer - Простое меню"

    def compose(self) -> ComposeResult:
        yield Header()

        with TabbedContent():
            # Tab 1: LLM список
            with TabPane("🤖 LLM"):
                yield Static(
                    "[bold cyan]Список доступных LLM[/bold cyan]",
                    classes="header",
                )

                table = DataTable(id="llm-table", zebra_stripes=True)
                table.add_columns("✓", "Название", "Модель")
                yield table

                with Horizontal():
                    yield Button("Выбрать", id="select-btn", variant="success")
                    yield Button("Обновить", id="refresh-btn")

            # Tab 2: Параметры
            with TabPane("⚙️ Параметры"):
                yield Static("[bold cyan]Параметры генерации[/bold cyan]")

                yield Static(f"Температура: [green]{config.temperature}[/green]")
                with Horizontal():
                    yield Input(value=str(config.temperature), id="temp-input")
                    yield Button("Установить", id="set-temp-btn")

                yield Static(
                    f"Max tokens: [green]{config.max_tokens or 'неограниченно'}[/green]"
                )
                max_tokens_str = (
                    str(config.max_tokens) if config.max_tokens else "неограниченно"
                )
                with Horizontal():
                    yield Input(value=max_tokens_str, id="tokens-input")
                    yield Button("Установить", id="set-tokens-btn")

                yield Static(f"Top P: [green]{config.top_p}[/green]")
                with Horizontal():
                    yield Input(value=str(config.top_p), id="topp-input")
                    yield Button("Установить", id="set-topp-btn")

            # Tab 3: Информация
            with TabPane("📊 Инфо"):
                yield Static("[bold cyan]Текущая конфигурация[/bold cyan]")
                yield Static(
                    f"Текущая LLM: [green]{config.current_llm or 'Не выбрана'}[/green]"
                )
                yield Static(f"Температура: [green]{config.temperature}[/green]")
                yield Static(
                    f"Max tokens: [green]{config.max_tokens or 'неограниченно'}[/green]"
                )
                yield Static(f"Top P: [green]{config.top_p}[/green]")
                yield Static(
                    f"Frequency penalty: [green]{config.frequency_penalty}[/green]"
                )
                yield Static(
                    f"Presence penalty: [green]{config.presence_penalty}[/green]"
                )
                yield Button("🔄 Обновить", id="refresh-info-btn", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize."""
        self.update_llm_table()
        self.notify("✅ Загружено")

    def update_llm_table(self) -> None:
        """Update LLM table."""
        table = self.query_one("#llm-table", DataTable)
        table.clear()

        current = config.current_llm
        llms = config.get_available_llms()

        for llm_name in llms:
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            table.add_row(is_current, llm_name, cfg.get("model", "N/A"))

        self.notify(f"Загружено {len(llms)} LLM")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "select-btn":
            table = self.query_one("#llm-table", DataTable)
            if table.cursor_row >= 0:
                row = table.get_row_at(table.cursor_row)
                llm_name = str(row[1])
                config.current_llm = llm_name
                self.update_llm_table()
                self.notify(f"✅ Выбрана: {llm_name}")
            else:
                self.notify("⚠️ Выберите LLM", severity="warning")

        elif btn_id == "refresh-btn":
            self.update_llm_table()

        elif btn_id == "set-temp-btn":
            input_field = self.query_one("#temp-input", Input)
            try:
                value = float(input_field.value.replace(",", "."))
                if 0.0 <= value <= 2.0:
                    config.temperature = value
                    self.notify(f"✅ Температура: {value}")
                else:
                    self.notify("❌ Должно быть 0.0-2.0", severity="error")
            except ValueError:
                self.notify("❌ Неверный формат", severity="error")

        elif btn_id == "set-tokens-btn":
            input_field = self.query_one("#tokens-input", Input)
            value = input_field.value.strip().lower()
            if value in ["null", "none", "", "неограниченно"]:
                config.max_tokens = None
                self.notify("✅ Max tokens: неограниченно")
            else:
                try:
                    num = int(value)
                    if num > 0:
                        config.max_tokens = num
                        self.notify(f"✅ Max tokens: {num}")
                    else:
                        self.notify("❌ Должно быть > 0", severity="error")
                except ValueError:
                    self.notify("❌ Неверный формат", severity="error")

        elif btn_id == "set-topp-btn":
            input_field = self.query_one("#topp-input", Input)
            try:
                value = float(input_field.value.replace(",", "."))
                if 0.0 <= value <= 1.0:
                    config.top_p = value
                    self.notify(f"✅ Top P: {value}")
                else:
                    self.notify("❌ Должно быть 0.0-1.0", severity="error")
            except ValueError:
                self.notify("❌ Неверный формат", severity="error")

        elif btn_id == "refresh-info-btn":
            self.notify("✅ Информация обновлена")
            self.refresh()


if __name__ == "__main__":
    app = SimpleConfigMenu()
    app.run()
