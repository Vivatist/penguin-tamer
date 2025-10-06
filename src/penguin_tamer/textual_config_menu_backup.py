#!/usr/bin/env python3
"""
Textual-based configuration menu for Penguin Tamer.
Provides a modern TUI interface with tabs, tables, and live status updates.
"""

import sys
from pathlib import Path

# Add src directory to path for direct execution
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Static,
    Switch,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.reactive import reactive

from penguin_tamer.config_manager import config
from penguin_tamer.i18n import translator


def format_api_key_display(key: str) -> str:
    """Format API key for display (show only last 4 chars)."""
    if not key or len(key) < 8:
        return "***" if key else "пусто"
    return f"...{key[-4:]}"


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation prompts."""

    def __init__(self, message: str, title: str = "Подтверждение", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.title_text = title
        self.result = False

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="dialog-title"),
            Static(self.message, classes="dialog-message"),
            Horizontal(
                Button("Да", variant="success", id="yes-btn"),
                Button("Нет", variant="error", id="no-btn"),
                classes="dialog-buttons",
            ),
            classes="dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.result = True
        self.dismiss(self.result)


class InputDialog(ModalScreen):
    """Modal dialog for text input with validation."""

    def __init__(
        self,
        prompt: str,
        title: str = "Ввод",
        default: str = "",
        validator=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.prompt = prompt
        self.title_text = title
        self.default = default
        self.validator = validator
        self.result = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="input-dialog-title"),
            Static(self.prompt, classes="input-dialog-prompt"),
            Input(value=self.default, id="input-field"),
            Horizontal(
                Button("OK", variant="success", id="ok-btn"),
                Button("Отмена", variant="error", id="cancel-btn"),
                classes="input-dialog-buttons",
            ),
            classes="input-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            input_field = self.query_one("#input-field", Input)
            value = input_field.value
            if self.validator and not self.validator(value):
                self.notify("❌ Неверный формат ввода", severity="error")
                return
            self.result = value
        self.dismiss(self.result)


class StatusPanel(Static):
    """Live status panel showing current configuration."""

    def on_mount(self) -> None:
        """Update content when mounted."""
        self.update_content()

    def update_content(self) -> None:
        """Update the status display."""
        try:
            current_llm = config.current_llm or "Не выбран"
            llm_info = ""
            if current_llm != "Не выбран":
                cfg = config.get_llm_config(current_llm) or {}
                model = cfg.get("model", "N/A")
                llm_info = f" [dim](модель: {model})[/dim]"

            content_preview = (
                config.user_content[:100] + "..."
                if len(config.user_content) > 100
                else config.user_content
            )
            if not content_preview.strip():
                content_preview = "[dim italic]Пусто[/dim italic]"

            # Получаем информацию о языке и теме
            current_lang = getattr(config, "language", "en")
            lang_display = "English" if current_lang == "en" else "Русский"

            current_theme = getattr(config, "theme", "default")
            theme_names = {
                "default": "Классический",
                "monokai": "Monokai",
                "dracula": "Dracula",
                "nord": "Nord",
            }
            theme_display = theme_names.get(current_theme, current_theme)

            content = f"""[bold cyan]📊 ТЕКУЩАЯ КОНФИГУРАЦИЯ[/bold cyan]

[bold]🤖 Текущая LLM:[/bold] {current_llm}{llm_info}
[dim]Выбранная модель для генерации[/dim]

[bold]⚙️  Температура:[/bold] {config.temperature}
[dim]Креативность (0.0-2.0)[/dim]

[bold]📏 Максимум токенов:[/bold] {config.max_tokens or 'Без ограничений'}
[dim]Длина ответа[/dim]

[bold]🎯 Top P:[/bold] {config.top_p}
[dim]Nucleus sampling (0.0-1.0)[/dim]

[bold]🔄 Штраф частоты:[/bold] {config.frequency_penalty}
[dim]Снижает повторения (-2.0 до 2.0)[/dim]

[bold]👁️  Штраф присутствия:[/bold] {config.presence_penalty}
[dim]Разнообразие тем (-2.0 до 2.0)[/dim]

[bold]🎲 Seed:[/bold] {config.seed or 'Случайный'}
[dim]Для воспроизводимости[/dim]

[bold]📝 Контент:[/bold]
[dim]{content_preview}[/dim]

[bold]🌐 Язык:[/bold] {lang_display}
[bold]🎨 Тема:[/bold] {theme_display}
[bold]🐛 Отладка:[/bold] {'Вкл' if getattr(config, 'debug', False) else 'Выкл'}
"""
            self.update(content)
        except Exception as e:
            self.update(f"[red]❌ Ошибка: {e}[/red]")


class ConfigMenuApp(App):
    """Main Textual configuration application."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #left-panel {
        width: 65%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }

    #right-panel {
        width: 35%;
        height: 100%;
        border: solid $secondary;
        padding: 1;
        margin-left: 1;
    }

    TabbedContent {
        height: 100%;
        width: 100%;
    }

    TabPane {
        padding: 2;
        overflow-y: auto;
    }

    .tab-header {
        padding: 1;
        margin-bottom: 1;
        background: $boost;
        border: solid $primary;
    }

    .setting-group {
        margin-bottom: 2;
        border: solid $primary-darken-3;
        padding: 1;
        background: $surface;
    }

    .param-label {
        margin-top: 1;
        color: $text;
        text-style: bold;
    }

    .param-description {
        margin-bottom: 1;
        color: $text-muted;
        text-style: italic;
    }

    .param-current {
        margin-bottom: 1;
        color: $success;
        text-style: bold;
        background: $success-darken-3;
        padding: 1;
    }

    DataTable {
        min-height: 15;
        max-height: 20;
        margin-bottom: 1;
        border: solid $primary;
    }

    .button-row {
        height: auto;
        margin-bottom: 1;
        margin-top: 1;
    }

    .button-row Button {
        margin: 0 1;
    }

    TextArea {
        min-height: 20;
        margin-bottom: 1;
        border: solid $primary;
    }

    Input {
        width: 1fr;
        margin-right: 1;
    }

    .setting-button {
        min-width: 12;
    }

    Container {
        height: auto;
    }

    Horizontal {
        height: auto;
    }

    /* Dialog styles */
    .dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .dialog-message {
        width: 100%;
        margin-bottom: 2;
        text-align: center;
    }

    .dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    .dialog-buttons Button {
        margin: 0 2;
        min-width: 10;
    }

    .input-dialog-container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .input-dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .input-dialog-prompt {
        width: 100%;
        margin-bottom: 1;
    }

    .input-dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    .input-dialog-buttons Button {
        margin: 0 2;
        min-width: 10;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Выход", priority=True),
        Binding("ctrl+c", "quit", "Выход"),
        Binding("f1", "help", "Помощь"),
        Binding("ctrl+r", "refresh_status", "Обновить"),
    ]

    TITLE = "🐧 Penguin Tamer - Конфигурация"
    SUB_TITLE = "Управление настройками ИИ"

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        with Horizontal():
            # Left panel with tabs
            with Vertical(id="left-panel"):
                with TabbedContent():
                    # Tab 1: LLM Selection
                    with TabPane("🤖 Выбор LLM", id="tab-llm-select"):
                        yield Static(
                            "[bold]🤖 ВЫБОР ТЕКУЩЕЙ LLM[/bold]\n"
                            "[dim]Выберите модель для генерации ответов[/dim]",
                            classes="tab-header",
                        )
                        current_llm = config.current_llm or "Не выбрана"
                        yield Static(
                            f"Текущая: [bold cyan]{current_llm}[/bold cyan]",
                            classes="param-current",
                        )
                        table = DataTable(id="llm-selector-table")
                        table.add_columns("✓", "Название", "Модель")
                        yield table
                        with Horizontal(classes="button-row"):
                            yield Button(
                                "✅ Выбрать",
                                id="select-llm-btn",
                                variant="success",
                            )
                            yield Button(
                                "🔄 Обновить", id="refresh-llm-btn", variant="default"
                            )

                    # Tab 2: LLM Management
                    with TabPane("⚙️ Управление LLM", id="tab-llm-manage"):
                        yield Static(
                            "[bold]⚙️ УПРАВЛЕНИЕ LLM[/bold]\n"
                            "[dim]Добавление, редактирование, удаление моделей[/dim]",
                            classes="tab-header",
                        )
                        table = DataTable(id="llm-management-table")
                        table.add_columns("✓", "Название", "Модель", "API URL")
                        yield table
                        with Horizontal(classes="button-row"):
                            yield Button("➕ Добавить", id="add-llm-btn", variant="success")
                            yield Button("✏️ Редактировать", id="edit-llm-btn")
                            yield Button("🗑️ Удалить", id="delete-llm-btn", variant="error")

                    # Tab 3: Generation Parameters
                    with TabPane("🎛️ Параметры", id="tab-params"):
                        yield Static(
                            "[bold]🎛️ ПАРАМЕТРЫ ГЕНЕРАЦИИ[/bold]\n"
                            "[dim]Настройка поведения ИИ[/dim]",
                            classes="tab-header",
                        )

                        # Temperature
                        with Container(classes="setting-group"):
                            yield Static("Температура", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{config.temperature}[/green]\n"
                                "Контролирует креативность (0.0-2.0)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(
                                    value=str(config.temperature), id="temp-input"
                                )
                                yield Button(
                                    "Установить",
                                    id="set-temp-btn",
                                    classes="setting-button",
                                )

                        # Max Tokens
                        with Container(classes="setting-group"):
                            max_tokens_str = (
                                str(config.max_tokens)
                                if config.max_tokens
                                else "неограниченно"
                            )
                            yield Static("Максимум токенов", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{max_tokens_str}[/green]\n"
                                "Ограничивает длину ответа",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(value=max_tokens_str, id="max-tokens-input")
                                yield Button(
                                    "Установить",
                                    id="set-max-tokens-btn",
                                    classes="setting-button",
                                )

                        # Top P
                        with Container(classes="setting-group"):
                            yield Static("Top P", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{config.top_p}[/green]\n"
                                "Nucleus sampling (0.0-1.0)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(value=str(config.top_p), id="top-p-input")
                                yield Button(
                                    "Установить",
                                    id="set-top-p-btn",
                                    classes="setting-button",
                                )

                        # Frequency Penalty
                        with Container(classes="setting-group"):
                            yield Static("Штраф частоты", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{config.frequency_penalty}[/green]\n"
                                "Снижает повторения (-2.0 до 2.0)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(
                                    value=str(config.frequency_penalty),
                                    id="freq-penalty-input",
                                )
                                yield Button(
                                    "Установить",
                                    id="set-freq-penalty-btn",
                                    classes="setting-button",
                                )

                        # Presence Penalty
                        with Container(classes="setting-group"):
                            yield Static("Штраф присутствия", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{config.presence_penalty}[/green]\n"
                                "Разнообразие тем (-2.0 до 2.0)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(
                                    value=str(config.presence_penalty),
                                    id="pres-penalty-input",
                                )
                                yield Button(
                                    "Установить",
                                    id="set-pres-penalty-btn",
                                    classes="setting-button",
                                )

                        # Seed
                        with Container(classes="setting-group"):
                            seed_str = str(config.seed) if config.seed else "случайный"
                            yield Static("Seed", classes="param-label")
                            yield Static(
                                f"Текущее: [green]{seed_str}[/green]\n"
                                "Для воспроизводимости результатов",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(value=seed_str, id="seed-input")
                                yield Button(
                                    "Установить",
                                    id="set-seed-btn",
                                    classes="setting-button",
                                )

                    # Tab 4: User Content
                    with TabPane("📝 Контент", id="tab-content"):
                        yield Static(
                            "[bold]📝 ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ[/bold]\n"
                            "[dim]Дополнительный контекст для всех запросов[/dim]",
                            classes="tab-header",
                        )
                        yield Static(
                            "Этот контент автоматически добавляется к каждому запросу.\n"
                            "Используйте для системных промптов и инструкций.",
                            classes="param-description",
                        )
                        yield TextArea(text=config.user_content, id="content-textarea")
                        with Horizontal(classes="button-row"):
                            yield Button(
                                "💾 Сохранить",
                                id="save-content-btn",
                                variant="success",
                            )
                            yield Button(
                                "🔄 Сбросить", id="reset-content-btn", variant="warning"
                            )

                    # Tab 5: System Settings
                    with TabPane("🔧 Система", id="tab-system"):
                        yield Static(
                            "[bold]🔧 СИСТЕМНЫЕ НАСТРОЙКИ[/bold]\n"
                            "[dim]Поведение приложения[/dim]",
                            classes="tab-header",
                        )

                        # Stream Delay
                        with Container(classes="setting-group"):
                            yield Static("Задержка стрима", classes="param-label")
                            stream_delay = config.get("global", "sleep_time", 0.01)
                            yield Static(
                                f"Текущее: [green]{stream_delay} сек[/green]\n"
                                "Пауза между частями текста (0.001-0.1)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(
                                    value=str(stream_delay), id="stream-delay-input"
                                )
                                yield Button(
                                    "Установить",
                                    id="set-stream-delay-btn",
                                    classes="setting-button",
                                )

                        # Refresh Rate
                        with Container(classes="setting-group"):
                            yield Static("Частота обновлений", classes="param-label")
                            refresh_rate = config.get("global", "refresh_per_second", 10)
                            yield Static(
                                f"Текущее: [green]{refresh_rate} Гц[/green]\n"
                                "Как часто обновляется интерфейс (1-60)",
                                classes="param-description",
                            )
                            with Horizontal():
                                yield Input(
                                    value=str(refresh_rate), id="refresh-rate-input"
                                )
                                yield Button(
                                    "Установить",
                                    id="set-refresh-rate-btn",
                                    classes="setting-button",
                                )

                        # Debug Mode
                        with Container(classes="setting-group"):
                            yield Static("Режим отладки", classes="param-label")
                            debug_status = (
                                "Включен"
                                if getattr(config, "debug", False)
                                else "Выключен"
                            )
                            yield Static(
                                f"Текущее: [green]{debug_status}[/green]\n"
                                "Подробная информация о запросах к API",
                                classes="param-description",
                            )
                            yield Switch(
                                value=getattr(config, "debug", False), id="debug-switch"
                            )

                    # Tab 6: Language & Theme
                    with TabPane("🌐 Язык/Тема", id="tab-appearance"):
                        yield Static(
                            "[bold]🌐 ЯЗЫК И ТЕМА[/bold]\n"
                            "[dim]Настройки интерфейса[/dim]",
                            classes="tab-header",
                        )

                        # Language
                        with Container(classes="setting-group"):
                            yield Static("Язык интерфейса", classes="param-label")
                            current_lang = getattr(config, "language", "en")
                            lang_display = (
                                "English" if current_lang == "en" else "Русский"
                            )
                            yield Static(
                                f"Текущий: [green]{lang_display}[/green]\n"
                                "Изменения вступят в силу после перезапуска",
                                classes="param-description",
                            )
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "🇺🇸 English",
                                    id="lang-en-btn",
                                    variant="primary"
                                    if current_lang == "en"
                                    else "default",
                                )
                                yield Button(
                                    "🇷🇺 Русский",
                                    id="lang-ru-btn",
                                    variant="primary"
                                    if current_lang == "ru"
                                    else "default",
                                )

                        # Theme
                        with Container(classes="setting-group"):
                            yield Static("Цветовая тема", classes="param-label")
                            current_theme = getattr(config, "theme", "default")
                            theme_names = {
                                "default": "Классический",
                                "monokai": "Monokai",
                                "dracula": "Dracula",
                                "nord": "Nord",
                            }
                            theme_display = theme_names.get(current_theme, current_theme)
                            yield Static(
                                f"Текущая: [green]{theme_display}[/green]\n"
                                "Изменения вступят в силу после перезапуска",
                                classes="param-description",
                            )
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "Классический",
                                    id="theme-default-btn",
                                    variant="primary"
                                    if current_theme == "default"
                                    else "default",
                                )
                                yield Button(
                                    "Monokai",
                                    id="theme-monokai-btn",
                                    variant="primary"
                                    if current_theme == "monokai"
                                    else "default",
                                )
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "Dracula",
                                    id="theme-dracula-btn",
                                    variant="primary"
                                    if current_theme == "dracula"
                                    else "default",
                                )
                                yield Button(
                                    "Nord",
                                    id="theme-nord-btn",
                                    variant="primary"
                                    if current_theme == "nord"
                                    else "default",
                                )

            # Right panel with status
            with Vertical(id="right-panel"):
                yield StatusPanel(id="status-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app."""
        self.notify("🔄 Загрузка данных...", severity="information")
        self.update_llm_tables()
        self.notify("✅ Приложение загружено", severity="information")
        
        # Диагностика
        try:
            selector_table = self.query_one("#llm-selector-table", DataTable)
            self.notify(f"📊 Селектор: {selector_table.row_count} строк", severity="information")
        except Exception as e:
            self.notify(f"❌ Ошибка селектора: {e}", severity="error")

    def update_llm_tables(self) -> None:
        """Update LLM tables with current data."""
        current = config.current_llm
        llms = config.get_available_llms()
        
        self.notify(f"🔍 Найдено LLM: {len(llms)}", severity="information")

        # Update selector table
        selector_table = self.query_one("#llm-selector-table", DataTable)
        selector_table.clear()
        for llm_name in llms:
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            selector_table.add_row(
                is_current, llm_name, cfg.get("model", "N/A")
            )
        self.notify(f"✅ Селектор обновлён: {selector_table.row_count} строк", severity="information")

        # Update management table
        management_table = self.query_one("#llm-management-table", DataTable)
        management_table.clear()
        for llm_name in llms:
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            management_table.add_row(
                is_current,
                llm_name,
                cfg.get("model", "N/A"),
                cfg.get("api_url", "N/A"),
            )
        self.notify(f"✅ Управление обновлено: {management_table.row_count} строк", severity="information")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        # LLM Selection
        if btn_id == "select-llm-btn":
            self.select_current_llm()
        elif btn_id == "refresh-llm-btn":
            self.update_llm_tables()
            self.notify("✅ Список обновлён", severity="information")

        # LLM Management
        elif btn_id == "add-llm-btn":
            self.add_llm()
        elif btn_id == "edit-llm-btn":
            self.edit_llm()
        elif btn_id == "delete-llm-btn":
            self.delete_llm()

        # Parameters
        elif btn_id == "set-temp-btn":
            self.set_temperature()
        elif btn_id == "set-max-tokens-btn":
            self.set_max_tokens()
        elif btn_id == "set-top-p-btn":
            self.set_top_p()
        elif btn_id == "set-freq-penalty-btn":
            self.set_frequency_penalty()
        elif btn_id == "set-pres-penalty-btn":
            self.set_presence_penalty()
        elif btn_id == "set-seed-btn":
            self.set_seed()

        # User Content
        elif btn_id == "save-content-btn":
            self.save_user_content()
        elif btn_id == "reset-content-btn":
            self.reset_user_content()

        # System Settings
        elif btn_id == "set-stream-delay-btn":
            self.set_stream_delay()
        elif btn_id == "set-refresh-rate-btn":
            self.set_refresh_rate()

        # Language & Theme
        elif btn_id == "lang-en-btn":
            self.set_language("en")
        elif btn_id == "lang-ru-btn":
            self.set_language("ru")
        elif btn_id in [
            "theme-default-btn",
            "theme-monokai-btn",
            "theme-dracula-btn",
            "theme-nord-btn",
        ]:
            theme = btn_id.replace("theme-", "").replace("-btn", "")
            self.set_theme(theme)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch changes."""
        if event.switch.id == "debug-switch":
            setattr(config, "debug", event.value)
            self.refresh_status()
            status = "включен" if event.value else "выключен"
            self.notify(f"✅ Режим отладки {status}", severity="information")

    # LLM Methods
    def select_current_llm(self) -> None:
        """Select current LLM from table."""
        table = self.query_one("#llm-selector-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Выберите LLM из списка", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])
        config.current_llm = llm_name
        self.update_llm_tables()
        self.refresh_status()
        self.notify(f"✅ Текущая LLM: {llm_name}", severity="information")

    def add_llm(self) -> None:
        """Add new LLM."""

        def handle_name(name):
            if not name:
                return

            def handle_model(model):
                if not model:
                    return

                def handle_url(api_url):
                    if not api_url:
                        return

                    def handle_key(api_key):
                        config.add_llm(name, model, api_url, api_key or "")
                        self.update_llm_tables()
                        self.refresh_status()
                        self.notify(f"✅ LLM '{name}' добавлена", severity="information")

                    self.push_screen(
                        InputDialog(
                            "API ключ (необязательно):",
                            title="Добавление LLM",
                            default="",
                        ),
                        handle_key,
                    )

                self.push_screen(
                    InputDialog("API URL:", title="Добавление LLM"), handle_url
                )

            self.push_screen(
                InputDialog("Модель:", title="Добавление LLM"), handle_model
            )

        self.push_screen(InputDialog("Название LLM:", title="Добавление LLM"), handle_name)

    def edit_llm(self) -> None:
        """Edit selected LLM."""
        table = self.query_one("#llm-management-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Выберите LLM для редактирования", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])
        cfg = config.get_llm_config(llm_name) or {}

        def handle_model(model):
            if model is not None:
                config.update_llm(llm_name, model=model)
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"✅ LLM '{llm_name}' обновлена", severity="information")

        self.push_screen(
            InputDialog(
                "Модель:",
                default=cfg.get("model", ""),
                title=f"Редактирование {llm_name}",
            ),
            handle_model,
        )

    def delete_llm(self) -> None:
        """Delete selected LLM."""
        table = self.query_one("#llm-management-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Выберите LLM для удаления", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])

        if llm_name == config.current_llm:
            self.notify("❌ Нельзя удалить текущую LLM", severity="error")
            return

        def handle_confirm(confirm):
            if confirm:
                config.remove_llm(llm_name)
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"✅ LLM '{llm_name}' удалена", severity="information")

        self.push_screen(
            ConfirmDialog(f"Удалить LLM '{llm_name}'?", title="Подтверждение"),
            handle_confirm,
        )

    # Parameter Methods
    def set_temperature(self) -> None:
        """Set temperature parameter."""
        input_field = self.query_one("#temp-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 2.0:
                config.temperature = value
                self.refresh_status()
                self.notify(f"✅ Температура: {value}", severity="information")
            else:
                self.notify("❌ Температура должна быть от 0.0 до 2.0", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    def set_max_tokens(self) -> None:
        """Set max tokens parameter."""
        input_field = self.query_one("#max-tokens-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.max_tokens = None
            self.refresh_status()
            self.notify("✅ Максимум токенов: без ограничений", severity="information")
        else:
            try:
                num_value = int(value)
                if num_value > 0:
                    config.max_tokens = num_value
                    self.refresh_status()
                    self.notify(f"✅ Максимум токенов: {num_value}", severity="information")
                else:
                    self.notify("❌ Должно быть положительным", severity="error")
            except ValueError:
                self.notify("❌ Неверный числовой формат", severity="error")

    def set_top_p(self) -> None:
        """Set top_p parameter."""
        input_field = self.query_one("#top-p-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 1.0:
                config.top_p = value
                self.refresh_status()
                self.notify(f"✅ Top P: {value}", severity="information")
            else:
                self.notify("❌ Top P должен быть от 0.0 до 1.0", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    def set_frequency_penalty(self) -> None:
        """Set frequency penalty."""
        input_field = self.query_one("#freq-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.frequency_penalty = value
                self.refresh_status()
                self.notify(f"✅ Штраф частоты: {value}", severity="information")
            else:
                self.notify("❌ Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    def set_presence_penalty(self) -> None:
        """Set presence penalty."""
        input_field = self.query_one("#pres-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.presence_penalty = value
                self.refresh_status()
                self.notify(f"✅ Штраф присутствия: {value}", severity="information")
            else:
                self.notify("❌ Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    def set_seed(self) -> None:
        """Set seed parameter."""
        input_field = self.query_one("#seed-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.seed = None
            self.refresh_status()
            self.notify("✅ Seed: случайный", severity="information")
        else:
            try:
                num_value = int(value)
                config.seed = num_value
                self.refresh_status()
                self.notify(f"✅ Seed: {num_value}", severity="information")
            except ValueError:
                self.notify("❌ Неверный числовой формат", severity="error")

    # User Content Methods
    def save_user_content(self) -> None:
        """Save user content."""
        text_area = self.query_one("#content-textarea", TextArea)
        config.user_content = text_area.text
        self.refresh_status()
        self.notify("✅ Контент сохранён", severity="information")

    def reset_user_content(self) -> None:
        """Reset user content."""

        def handle_confirm(confirm):
            if confirm:
                config.user_content = ""
                text_area = self.query_one("#content-textarea", TextArea)
                text_area.text = ""
                self.refresh_status()
                self.notify("✅ Контент сброшен", severity="information")

        self.push_screen(
            ConfirmDialog("Сбросить пользовательский контент?"), handle_confirm
        )

    # System Settings Methods
    def set_stream_delay(self) -> None:
        """Set stream delay."""
        input_field = self.query_one("#stream-delay-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.001 <= value <= 0.1:
                config.set("global", "sleep_time", value)
                self.refresh_status()
                self.notify(f"✅ Задержка стрима: {value} сек", severity="information")
            else:
                self.notify("❌ Должно быть от 0.001 до 0.1", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    def set_refresh_rate(self) -> None:
        """Set refresh rate."""
        input_field = self.query_one("#refresh-rate-input", Input)
        try:
            value = int(input_field.value)
            if 1 <= value <= 60:
                config.set("global", "refresh_per_second", value)
                self.refresh_status()
                self.notify(f"✅ Частота обновлений: {value} Гц", severity="information")
            else:
                self.notify("❌ Должно быть от 1 до 60", severity="error")
        except ValueError:
            self.notify("❌ Неверный числовой формат", severity="error")

    # Language & Theme Methods
    def set_language(self, lang: str) -> None:
        """Set interface language."""
        setattr(config, "language", lang)
        translator.set_language(lang)
        self.refresh_status()
        lang_name = "English" if lang == "en" else "Русский"
        self.notify(f"✅ Язык: {lang_name}", severity="information")

    def set_theme(self, theme: str) -> None:
        """Set interface theme."""
        setattr(config, "theme", theme)
        self.refresh_status()
        theme_names = {
            "default": "Классический",
            "monokai": "Monokai",
            "dracula": "Dracula",
            "nord": "Nord",
        }
        theme_name = theme_names.get(theme, theme)
        self.notify(f"✅ Тема: {theme_name}", severity="information")

    # Utility Methods
    def refresh_status(self) -> None:
        """Refresh status panel."""
        status_panel = self.query_one("#status-panel", StatusPanel)
        status_panel.update_content()

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Q или Ctrl+C - выход\n"
            "F1 - помощь\n"
            "Ctrl+R - обновить статус\n"
            "Все изменения сохраняются автоматически",
            title="Помощь",
            severity="information",
        )

    def action_refresh_status(self) -> None:
        """Refresh status action."""
        self.refresh_status()
        self.notify("✅ Статус обновлён", severity="information")


if __name__ == "__main__":
    app = ConfigMenuApp()
    app.run()
