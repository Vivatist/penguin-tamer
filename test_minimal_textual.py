#!/usr/bin/env python3
"""
Минимальный тест Textual - проверка отображения вкладок.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, DataTable, Button

class MinimalTestApp(App):
    """Минимальное тестовое приложение для проверки вкладок."""

    CSS = """
    Screen {
        layout: vertical;
    }

    TabbedContent {
        height: 100%;
    }

    TabPane {
        padding: 1;
    }

    DataTable {
        height: 10;
        margin-bottom: 1;
    }

    .info {
        padding: 1;
        background: $boost;
        margin-bottom: 1;
    }
    """

    BINDINGS = [("q", "quit", "Выход")]

    def compose(self) -> ComposeResult:
        yield Header()
        
        with TabbedContent():
            with TabPane("📋 Вкладка 1"):
                yield Static("Это первая вкладка с текстом", classes="info")
                table = DataTable()
                table.add_columns("Колонка 1", "Колонка 2", "Колонка 3")
                table.add_row("Строка 1-1", "Строка 1-2", "Строка 1-3")
                table.add_row("Строка 2-1", "Строка 2-2", "Строка 2-3")
                table.add_row("Строка 3-1", "Строка 3-2", "Строка 3-3")
                yield table
                yield Button("Тестовая кнопка", variant="success")

            with TabPane("📊 Вкладка 2"):
                yield Static("Это вторая вкладка с другими данными", classes="info")
                table = DataTable()
                table.add_columns("Имя", "Значение")
                table.add_row("Параметр 1", "Значение 1")
                table.add_row("Параметр 2", "Значение 2")
                yield table

            with TabPane("🔧 Вкладка 3"):
                yield Static("Это третья вкладка", classes="info")
                yield Static("Здесь просто текст без таблиц")
                yield Button("Другая кнопка", variant="primary")

        yield Footer()

    def on_mount(self) -> None:
        self.notify("✅ Тестовое приложение загружено")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.notify(f"Кнопка нажата: {event.button.label}")


if __name__ == "__main__":
    app = MinimalTestApp()
    app.run()
