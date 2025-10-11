#!/usr/bin/env python3
"""
Textual-based configuration menu for Penguin Tamer.
Provides a modern TUI interface with tabs, tables, and live status updates.
"""

import sys
import traceback
from pathlib import Path

# Add src directory to path for direct execution
if __name__ == "__main__":
    # Файл находится в src/penguin_tamer/menu/config_menu.py
    # Нужно подняться на 3 уровня до src/
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Select,
    Static,
    Switch,
    TabbedContent,
    TabPane,
    TextArea,
)

from penguin_tamer.config_manager import config
from penguin_tamer.i18n import translator
from penguin_tamer.arguments import __version__
from penguin_tamer.text_utils import format_api_key_display

# Import modular components
if __name__ == "__main__":
    # При прямом запуске используем абсолютные импорты
    from penguin_tamer.menu.widgets import DoubleClickDataTable, ResponsiveButtonRow
    from penguin_tamer.menu.dialogs import LLMEditDialog, ConfirmDialog, ApiKeyMissingDialog
    from penguin_tamer.menu.info_panel import InfoPanel
    from penguin_tamer.menu.intro_screen import show_intro
    from penguin_tamer.menu.locales.menu_i18n import menu_translator, t
else:
    # При импорте как модуль используем относительные импорты
    from .widgets import DoubleClickDataTable, ResponsiveButtonRow
    from .dialogs import LLMEditDialog, ConfirmDialog, ApiKeyMissingDialog
    from .info_panel import InfoPanel
    from .intro_screen import show_intro
    from .locales.menu_i18n import menu_translator, t

# Initialize menu translator with current language BEFORE class definition
current_lang = getattr(config, "language", "en")
menu_translator.set_language(current_lang)


class ConfigMenuApp(App):
    """Main Textual configuration application."""

    # Flag to prevent notifications during initialization
    _initialized = False

    # Load CSS from external file
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    ENABLE_COMMAND_PALETTE = False

    TITLE = "Penguin Tamer " + __version__
    SUB_TITLE = t("Configuration")

    BINDINGS = [
        Binding("q", "quit", t("Exit"), priority=True),
        Binding("ctrl+c", "quit", t("Exit")),
        Binding("f1", "help", t("Help")),
        Binding("ctrl+r", "refresh_status", t("Refresh")),
    ]

    def __init__(self, show_api_key_dialog: bool = False, *args, **kwargs):
        """Initialize app.

        Args:
            show_api_key_dialog: If True, shows API key missing dialog on mount
        """
        super().__init__(*args, **kwargs)
        self._show_api_key_dialog = show_api_key_dialog

    def get_css_variables(self) -> dict[str, str]:
        """Определяем кастомную цветовую палитру для Textual."""
        variables = super().get_css_variables()

        palette = {
            # Базовые цвета
            "background": "#1a2429",
            "surface": "#1e2a30",
            "surface-lighten-1": "#27353c",
            "surface-lighten-2": "#303f47",
            "surface-lighten-3": "#3a4b54",
            "surface-darken-1": "#162025",
            "panel": "#27353c",
            "panel-lighten-1": "#303f47",
            "panel-darken-1": "#1a2429",
            "border": "#2f3b41",
            "shadow": "rgba(0, 0, 0, 0.25)",

            # Основной акцент (оранжевый)
            "primary": "#e07333",
            "primary-lighten-1": "#2f3b41",
            "primary-lighten-2": "#004b41",
            "primary-lighten-3": "#006257",
            "primary-darken-1": "#c86529",
            "primary-darken-2": "#aa4f1e",
            "primary-darken-3": "#8c3e15",

            # Успех / основной вторичный цвет (бирюзовый)
            "secondary": "#007c6e",
            "secondary-lighten-1": "#239f90",
            "secondary-lighten-2": "#45c2b3",
            "secondary-lighten-3": "#7adcd0",
            # "secondary-darken-1": "#006257",
            # "secondary-darken-2": "#004b41",
            # "secondary-darken-3": "#00342d",
            "success": "#007c6e",
            "success-lighten-1": "#239f90",
            "success-darken-1": "#006257",

            # Мягкий акцент (песочный)
            "accent": "#e07333",
            "accent-lighten-1": "#ffe6cf",
            "accent-lighten-2": "#fff2e4",
            "accent-lighten-3": "#fffaf3",
            "accent-darken-1": "#f2bf94",
            "accent-darken-2": "#dba578",
            "accent-darken-3": "#c1895c",
            "warning": "#ff0909",
            "warning-darken-1": "#f2bf94",

            # Сообщения об ошибках
            "error": "#e07333",
            "error-darken-1": "#c86529",

            # Текстовые цвета
            "text": "#f4f7f7",
            "text-muted": "#a7b4b7",
            "text-disabled": "#6e7a7d",

            # Дополнительные элементы
            "boost": "#303f47",
            "foreground": "#f4f7f7",
            "muted": "#a7b4b7",
            "dark": "#1e2a30",
            "scrollbar-background": "#162025",
            "scrollbar-foreground": "#04004b",
            "scrollbar-hover": "#006257",
        }

        variables.update(palette)
        return variables

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header(show_clock=False, icon="")

        with Horizontal():
            # Left panel with tabs
            with Vertical(id="left-panel"):
                with TabbedContent():
                    # Tab 1: General Settings (Общие)
                    with TabPane(t("General"), id="tab-general"):
                        with VerticalScroll():
                            yield Static(
                                f"[bold]{t('GENERAL SETTINGS')}[/bold]\n"
                                f"[dim]{t('System information and LLM management')}[/dim]",
                                classes="tab-header",
                            )

                            # Language setting
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Language')}\n[dim]{t('Restart required')}[/dim]",
                                    classes="param-label"
                                )
                                current_lang_val = getattr(config, "language", "en")
                                yield Select(
                                    [("English", "en"), ("Русский", "ru")],
                                    value=current_lang_val,
                                    id="language-select",
                                    allow_blank=False,
                                    classes="param-control"
                                )

                            yield Static("")

                            # System Info
                            if hasattr(config, 'config_path'):
                                config_dir = Path(config.config_path).parent
                            else:
                                config_dir = Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
                            bin_path = Path(sys.executable).parent
                            current_llm = config.current_llm or t("Not selected")

                            yield Static(
                                f"[bold]{t('Current LLM:')}[/bold] [#e07333]{current_llm}[/#e07333]\n\n"
                                f"[bold]{t('Config folder:')}[/bold] {config_dir}\n"
                                f"[bold]{t('Binary folder:')}[/bold] {bin_path}",
                                classes="system-info-panel",
                                id="system-info-display"
                            )

                            yield Static("")
                            yield Static(
                                f"[bold]{t('Neural network setup')}[/bold]\n"
                                f"[dim]{t('Select the used neural network or add your own')}[/dim]"
                            )
                            llm_dt = DoubleClickDataTable(id="llm-table", show_header=True, cursor_type="row")
                            yield llm_dt
                            yield Static("")
                            yield ResponsiveButtonRow(
                                buttons_data=[
                                    (t("Add"), "add-llm-btn", "success"),
                                    (t("Settings"), "edit-llm-btn", "success"),
                                    (t("Delete"), "delete-llm-btn", "error"),
                                ],
                                classes="button-row"
                            )

                    # Tab 2: User Context
                    with TabPane(t("Context"), id="tab-content"):
                        with VerticalScroll():
                            yield Static(
                                f"[bold]{t('USER CONTEXT')}[/bold]\n"
                                f"[dim]{t('Shape the assistant character and communication style')}[/dim]",
                                classes="tab-header",
                            )
                            yield TextArea(text=config.user_content, id="content-textarea")
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    t("Save"),
                                    id="save-content-btn",
                                    variant="success",
                                )

                    # Tab 3: Generation Parameters
                    with TabPane(t("Generation"), id="tab-params"):
                        with VerticalScroll():
                            yield Static(
                                f"[bold]{t('GENERATION PARAMETERS')}[/bold]\n"
                                f"[dim]{t('AI behavior settings (press Enter to save)')}[/dim]",
                                classes="tab-header",
                            )

                            # Temperature
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Temperature')}\n[dim]{t('Creativity (0.0-2.0)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.temperature),
                                    id="temp-input",
                                    placeholder="0.0-2.0",
                                    classes="param-control"
                                )

                            # Max Tokens
                            max_tokens_str = (
                                str(config.max_tokens)
                                if config.max_tokens
                                else t("unlimited")
                            )
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Max Tokens')}\n[dim]{t('Response length')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=max_tokens_str,
                                    id="max-tokens-input",
                                    placeholder=t("number or 'null'"),
                                    classes="param-control"
                                )

                            # Top P
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Top P')}\n[dim]{t('Nucleus Sampling (0.0-1.0)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.top_p),
                                    id="top-p-input",
                                    placeholder="0.0-1.0",
                                    classes="param-control"
                                )

                            # Frequency Penalty
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Frequency Penalty')}\n[dim]{t('Reduces repetitions (-2.0 to 2.0)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.frequency_penalty),
                                    id="freq-penalty-input",
                                    placeholder=t("-2.0 to 2.0"),
                                    classes="param-control"
                                )

                            # Presence Penalty
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Presence Penalty')}\n[dim]{t('Topic diversity (-2.0 to 2.0)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.presence_penalty),
                                    id="pres-penalty-input",
                                    placeholder=t("-2.0 to 2.0"),
                                    classes="param-control"
                                )

                            # Seed
                            seed_str = str(config.seed) if config.seed else t("random")
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Seed')}\n[dim]{t('For reproducibility')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=seed_str,
                                    id="seed-input",
                                    placeholder=t("number or 'null'"),
                                    classes="param-control"
                                )

                    # Tab 4: System Settings

                    with TabPane(t("System"), id="tab-system"):
                        with VerticalScroll():
                            yield Static(
                                f"[bold]{t('SYSTEM SETTINGS')}[/bold]\n"
                                f"[dim]{t('Application behavior (press Enter to save)')}[/dim]",
                                classes="tab-header",
                            )

                            # Stream Delay
                            stream_delay = config.get("global", "sleep_time", 0.01)
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Stream delay')}\n"
                                    f"[dim]{t('Pause between displaying new chunks (0.001-0.1)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(stream_delay),
                                    id="stream-delay-input",
                                    placeholder="0.001-0.1",
                                    classes="param-control"
                                )

                            # Refresh Rate
                            refresh_rate = config.get("global", "refresh_per_second", 10)
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Refresh rate')}\n"
                                    f"[dim]{t('Terminal update during generation (1-60 Hz)')}[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(refresh_rate),
                                    id="refresh-rate-input",
                                    placeholder="1-60",
                                    classes="param-control"
                                )

                            # Debug Mode
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Debug mode')}\n[dim]{t('Detailed information about LLM requests')}[/dim]",
                                    classes="param-label"
                                )
                                with Container(classes="param-control"):
                                    yield Switch(
                                        value=getattr(config, "debug", False),
                                        id="debug-switch"
                                    )

                            # Reset Settings Button
                            yield Static("")
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    t("Reset settings"),
                                    id="reset-settings-btn",
                                    variant="error",
                                )

                            # Flexible spacer AFTER button to fill remaining space
                            yield Static("", classes="flexible-spacer")

                    # Tab 5: Interface

                    with TabPane(t("Interface"), id="tab-appearance"):
                        with VerticalScroll():
                            yield Static(
                                f"[bold]{t('INTERFACE SETTINGS')}[/bold]\n"
                                f"[dim]{t('Application appearance (changes save automatically)')}[/dim]",
                                classes="tab-header",
                            )

                            # Theme
                            current_theme = config.get("global", "markdown_theme", "default")
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    f"{t('Color scheme')}\n[dim]{t('Restart required')}[/dim]",
                                    classes="param-label"
                                )
                                yield Select(
                                    [
                                        (t("Classic"), "default"),
                                        ("Monokai", "monokai"),
                                        ("Dracula", "dracula"),
                                        ("Nord", "nord"),
                                        ("Solarized Dark", "solarized_dark"),
                                        ("GitHub Dark", "github"),
                                        ("Matrix", "matrix"),
                                        ("Minimal", "minimal"),
                                    ],
                                    value=current_theme,
                                    id="theme-select",
                                    allow_blank=False,
                                    classes="param-control"
                                )

            # Right panel with info
            with Vertical(id="right-panel"):
                with VerticalScroll():
                    yield InfoPanel(id="info-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app."""
        self._initialized = False
        # Перезагружаем конфигурацию из файла, чтобы подхватить любые внешние изменения
        config.reload()
        self.update_llm_tables()
        # Set flag after initialization to enable notifications and tab switching

        def finish_init():
            self._initialized = True
            # Обновляем все поля ввода актуальными значениями из конфига
            self.update_all_inputs()
            # Show help for first tab
            panel = self.query_one("#info-panel", InfoPanel)
            panel.show_tab_help("tab-general")

            # Show API key dialog if requested
            if self._show_api_key_dialog:
                self.show_api_key_missing_dialog()

        self.set_timer(0.2, finish_init)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab change to update info panel."""
        # Ensure we're initialized
        if not getattr(self, '_initialized', False):
            return

        try:
            panel = self.query_one("#info-panel", InfoPanel)
            # Extract actual tab ID from the event
            raw_id = event.tab.id

            # Format is "--content-tab-tab-system", we need "tab-system"
            # Remove "--content-" prefix first
            if raw_id and raw_id.startswith("--content-"):
                tab_id = raw_id[len("--content-"):]
                # If it has duplicate "tab-tab-", fix it
                if tab_id.startswith("tab-tab-"):
                    tab_id = tab_id[4:]  # Remove one "tab-"
            else:
                tab_id = raw_id

            panel.show_tab_help(tab_id)
        except Exception as e:
            self.notify(t("Error: {error}", error=str(e)), severity="error")

    def on_focus(self, event) -> None:
        """Show help when any widget gets focus."""
        widget = event.widget
        widget_id = getattr(widget, 'id', None)

        if widget_id and isinstance(widget, (Input, Select, Switch)):
            panel = self.query_one(InfoPanel)
            panel.show_help(widget_id)

    def on_blur(self, event) -> None:
        """Restore config when widget loses focus."""
        widget = event.widget

        if isinstance(widget, (Input, Select, Switch)):
            # Get current tab and show its help
            tabs = self.query_one(TabbedContent)
            current_tab = tabs.active
            panel = self.query_one(InfoPanel)
            panel.show_tab_help(current_tab)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch state changes."""
        if event.switch.id == "debug-switch":
            config.debug = event.value
            config.save()
            self.refresh_status()
            status = t("enabled") if event.value else t("disabled")
            self.notify(t("Debug mode {status}", status=status), severity="information")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        # Skip notifications during initialization
        if not self._initialized:
            return

        select_id = event.select.id

        if select_id == "language-select" and event.value != Select.BLANK:
            self.set_language(str(event.value))
        elif select_id == "theme-select" and event.value != Select.BLANK:
            self.set_theme(str(event.value))

    def update_llm_tables(self, keep_cursor_position: bool = False) -> None:
        """Update LLM table with current data.

        Args:
            keep_cursor_position: If True, try to keep cursor on the same row
        """
        current = config.current_llm
        llms = config.get_available_llms()

        # Update unified LLM table
        llm_table = self.query_one("#llm-table", DataTable)

        # Save cursor position
        old_cursor_row = llm_table.cursor_row if keep_cursor_position else -1
        old_llm_name = None
        if old_cursor_row >= 0:
            try:
                row = llm_table.get_row_at(old_cursor_row)
                old_llm_name = str(row[1])  # Название LLM
            except Exception:
                pass

        llm_table.clear(columns=True)
        llm_table.add_columns(t(""), t("Name"), t("Model ID"), t("API Key"), t("API URL"))

        new_cursor_row = 0
        for idx, llm_name in enumerate(llms):
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            llm_table.add_row(
                is_current,
                llm_name,
                cfg.get("model", "N/A"),
                format_api_key_display(cfg.get("api_key", "")),
                cfg.get("api_url", "N/A"),
            )
            # Запоминаем позицию для текущей LLM или старой LLM
            if keep_cursor_position and old_llm_name and llm_name == old_llm_name:
                new_cursor_row = idx
            elif not keep_cursor_position and llm_name == current:
                # При первой загрузке устанавливаем курсор на текущую LLM
                new_cursor_row = idx

        # Устанавливаем позицию курсора
        if len(llms) > 0:
            try:
                # Устанавливаем cursor_coordinate для правильного highlight
                llm_table.cursor_coordinate = (new_cursor_row, 0)
            except Exception:
                try:
                    # Альтернативный способ
                    llm_table.move_cursor(row=new_cursor_row, animate=False)
                except Exception:
                    pass

            # Force highlight event to trigger selection (only on first load)
            if not keep_cursor_position and new_cursor_row > 0:
                # Manually trigger row highlight to ensure visual feedback
                try:
                    llm_table.move_cursor(row=new_cursor_row, animate=False)
                except Exception:
                    pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        input_id = event.input.id

        # Parameters
        if input_id == "temp-input":
            self.set_temperature()
        elif input_id == "max-tokens-input":
            self.set_max_tokens()
        elif input_id == "top-p-input":
            self.set_top_p()
        elif input_id == "freq-penalty-input":
            self.set_frequency_penalty()
        elif input_id == "pres-penalty-input":
            self.set_presence_penalty()
        elif input_id == "seed-input":
            self.set_seed()
        # System
        elif input_id == "stream-delay-input":
            self.set_stream_delay()
        elif input_id == "refresh-rate-input":
            self.set_refresh_rate()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        # Reset Settings
        if btn_id == "reset-settings-btn":
            self.action_reset_settings()

        # LLM Management
        elif btn_id == "add-llm-btn":
            self.add_llm()
        elif btn_id == "edit-llm-btn":
            self.edit_llm()
        elif btn_id == "delete-llm-btn":
            self.delete_llm()

        # User Content
        elif btn_id == "save-content-btn":
            self.save_user_content()

    def on_double_click_data_table_double_clicked(self, event: DoubleClickDataTable.DoubleClicked) -> None:
        """Handle double-click on DataTable - open edit dialog."""
        self.edit_llm()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlight in DataTable - auto-select LLM."""
        # Only handle LLM table
        if event.data_table.id != "llm-table":
            return

        # Skip if not initialized to avoid notifications during setup
        if not self._initialized:
            return

        self.select_current_llm()

    # LLM Methods
    def select_current_llm(self) -> None:
        """Select current LLM from table (called automatically on cursor move)."""
        try:
            table = self.query_one("#llm-table", DataTable)
        except Exception:
            # Table not found (e.g., dialog is open)
            return

        if table.cursor_row < 0:
            return

        try:
            row = table.get_row_at(table.cursor_row)
            llm_name = str(row[1])  # Название во втором столбце (после галочки)

            # Only update if it's a different LLM
            if llm_name == config.current_llm:
                return

            config.current_llm = llm_name
            config.save()
            self.update_llm_tables(keep_cursor_position=True)  # Сохраняем позицию курсора

            # Update system info panel with new current LLM
            if hasattr(config, 'config_path'):
                config_dir = Path(config.config_path).parent
            else:
                config_dir = Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
            bin_path = Path(sys.executable).parent
            system_info_display = self.query_one("#system-info-display", Static)
            system_info_display.update(
                f"[bold]{t('Current LLM:')}[/bold] [#e07333]{llm_name}[/#e07333]\n\n"
                f"[bold]{t('Config folder:')}[/bold] {config_dir}\n"
                f"[bold]{t('Binary folder:')}[/bold] {bin_path}"
            )

            self.refresh_status()

            # Check if API key exists and show appropriate notification
            llm_config = config.get_llm_config(llm_name)
            api_key = llm_config.get("api_key", "").strip() if llm_config else ""

            if not api_key:
                # Warning: No API key
                self.notify(
                    t("LLM '{name}' selected. Warning: API key is missing!", name=llm_name),
                    severity="warning",
                    timeout=5
                )
            else:
                # Success: LLM selected with API key
                self.notify(
                    t("LLM '{name}' selected", name=llm_name),
                    severity="information",
                    timeout=3
                )
        except Exception:
            # Ignore errors during cursor movement
            pass

    def add_llm(self) -> None:
        """Add new LLM."""
        def handle_result(result):
            if result:
                config.add_llm(
                    result["name"],
                    result["model"],
                    result["api_url"],
                    result["api_key"]
                )
                self.update_llm_tables()
                self.refresh_status()
                self.notify(t("LLM '{name}' added", name=result['name']), severity="information")

        self.push_screen(
            LLMEditDialog(title=t("Add LLM")),
            handle_result
        )

    def edit_llm(self) -> None:
        """Edit selected LLM."""
        try:
            table = self.query_one("#llm-table", DataTable)
        except Exception:
            # Table not found (e.g., another dialog is open)
            return

        if table.cursor_row < 0:
            self.notify(t("Select LLM to edit"), severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)
        cfg = config.get_llm_config(llm_name) or {}

        def handle_result(result):
            if result:
                # Если API ключ не был изменен (пустой), оставляем старый
                api_key_to_save = result["api_key"] if result["api_key"] else cfg.get("api_key", "")
                config.update_llm(
                    llm_name,
                    model=result["model"],
                    api_url=result["api_url"],
                    api_key=api_key_to_save
                )
                self.update_llm_tables()
                self.refresh_status()
                self.notify(t("LLM '{name}' updated", name=llm_name), severity="information")

        self.push_screen(
            LLMEditDialog(
                title=t("Edit {name}", name=llm_name),
                name=llm_name,
                model=cfg.get("model", ""),
                api_url=cfg.get("api_url", ""),
                api_key=cfg.get("api_key", ""),
                name_editable=False  # При редактировании имя не меняется
            ),
            handle_result
        )

    def delete_llm(self) -> None:
        """Delete selected LLM."""
        try:
            table = self.query_one("#llm-table", DataTable)
        except Exception:
            # Table not found (e.g., another dialog is open)
            return

        if table.cursor_row < 0:
            self.notify(t("Select LLM to delete"), severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)

        if llm_name == config.current_llm:
            self.notify(t("Cannot delete current LLM"), severity="error")
            return

        def handle_confirm(confirm):
            if confirm:
                config.remove_llm(llm_name)
                self.update_llm_tables()
                self.refresh_status()
                self.notify(t("LLM '{name}' deleted", name=llm_name), severity="information")

        self.push_screen(
            ConfirmDialog(t("Delete LLM '{name}'?", name=llm_name), title=t("Confirmation")),
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
                config.save()
                self.refresh_status()
                self.notify(t("Temperature set to {value}", value=value), severity="information")
            else:
                self.notify(t("Error: Temperature must be between 0.0 and 2.0"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    def set_max_tokens(self) -> None:
        """Set max tokens parameter."""
        input_field = self.query_one("#max-tokens-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.max_tokens = None
            config.save()
            self.refresh_status()
            self.notify(t("Max tokens set to unlimited"), severity="information")
        else:
            try:
                num_value = int(value)
                if num_value > 0:
                    config.max_tokens = num_value
                    config.save()
                    self.refresh_status()
                    self.notify(t("Max tokens set to {value}", value=num_value), severity="information")
                else:
                    self.notify(t("Error: Must be positive"), severity="error")
            except ValueError:
                self.notify(t("Error: Invalid number format"), severity="error")

    def set_top_p(self) -> None:
        """Set top_p parameter."""
        input_field = self.query_one("#top-p-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 1.0:
                config.top_p = value
                config.save()
                self.refresh_status()
                self.notify(t("Top P set to {value}", value=value), severity="information")
            else:
                self.notify(t("Error: Top P must be between 0.0 and 1.0"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    def set_frequency_penalty(self) -> None:
        """Сет frequency penalty."""
        input_field = self.query_one("#freq-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.frequency_penalty = value
                config.save()
                self.refresh_status()
                self.notify(t("Frequency penalty set to {value}", value=value), severity="information")
            else:
                self.notify(t("Error: Must be between -2.0 and 2.0"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    def set_presence_penalty(self) -> None:
        """Set presence penalty."""
        input_field = self.query_one("#pres-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.presence_penalty = value
                config.save()
                self.refresh_status()
                self.notify(t("Presence penalty set to {value}", value=value), severity="information")
            else:
                self.notify(t("Error: Must be between -2.0 and 2.0"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    def set_seed(self) -> None:
        """Set seed parameter."""
        input_field = self.query_one("#seed-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.seed = None
            config.save()
            self.refresh_status()
            self.notify(t("Seed set to random"), severity="information")
        else:
            try:
                num_value = int(value)
                config.seed = num_value
                config.save()
                self.refresh_status()
                self.notify(t("Seed set to {value}", value=num_value), severity="information")
            except ValueError:
                self.notify(t("Error: Invalid number format"), severity="error")

    # User Content Methods
    def save_user_content(self) -> None:
        """Save user content."""
        text_area = self.query_one("#content-textarea", TextArea)
        config.user_content = text_area.text
        config.save()
        self.refresh_status()
        self.notify(t("User context saved"), severity="information")

    # System Settings Methods
    def set_stream_delay(self) -> None:
        """Set stream delay."""
        input_field = self.query_one("#stream-delay-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.001 <= value <= 0.1:
                config.set("global", "sleep_time", value)
                self.refresh_status()
                self.notify(t("Stream delay set to {value} sec", value=value), severity="information")
            else:
                self.notify(t("Error: Must be between 0.001 and 0.1"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    def set_refresh_rate(self) -> None:
        """Set refresh rate."""
        input_field = self.query_one("#refresh-rate-input", Input)
        try:
            value = int(input_field.value)
            if 1 <= value <= 60:
                config.set("global", "refresh_per_second", value)
                self.refresh_status()
                self.notify(t("Refresh rate set to {value} Hz", value=value), severity="information")
            else:
                self.notify(t("Error: Must be between 1 and 60"), severity="error")
        except ValueError:
            self.notify(t("Error: Invalid number format"), severity="error")

    # Language & Theme Methods
    def set_language(self, lang: str) -> None:
        """Set interface language and update user_content if not modified."""
        # Используем новый метод config.set_language() который автоматически
        # локализует user_content если он не был изменён пользователем
        config.set_language(lang)
        # Sync both translators
        translator.set_language(lang)
        menu_translator.set_language(lang)
        self.refresh_status()
        lang_name = t("English") if lang == "en" else t("Русский")
        self.notify(t("Language set to {lang}. Restart required.", lang=lang_name), severity="information")

    def set_theme(self, theme: str) -> None:
        """Set interface theme for Rich Markdown output."""
        # Сохраняем тему для Rich Markdown (используется в llm_client.py)
        config.set("global", "markdown_theme", theme)
        self.refresh_status()
        theme_names = {
            "default": t("Classic"),
            "monokai": "Monokai",
            "dracula": "Dracula",
            "nord": "Nord",
            "solarized_dark": "Solarized Dark",
            "github": "GitHub Dark",
            "matrix": "Matrix",
            "minimal": "Minimal",
        }
        theme_name = theme_names.get(theme, theme)
        self.notify(t("Theme set to {theme}", theme=theme_name), severity="information")

    # Utility Methods
    def refresh_status(self) -> None:
        """Refresh info panel to show current tab help."""
        tabs = self.query_one(TabbedContent)
        current_tab = tabs.active
        info_panel = self.query_one("#info-panel", InfoPanel)
        info_panel.show_tab_help(current_tab)

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            t("Help: Q or Ctrl+C to exit, F1 for help, Ctrl+R to refresh. All changes save automatically."),
            title=t("Help"),
            severity="information",
        )

    def show_api_key_missing_dialog(self) -> None:
        """Show modal dialog informing about missing API key."""
        dialog = ApiKeyMissingDialog(t)
        self.push_screen(dialog)

    def action_refresh_status(self) -> None:
        """Refresh status action."""
        self.refresh_status()
        self.notify(t("Status refreshed"), severity="information")

    def action_reset_settings(self) -> None:
        """Сброс настроек к значениям по умолчанию."""
        message = t("Warning! All settings, including API keys, will be reset to defaults. Continue?")

        def handle_confirm(result):
            if result:
                try:
                    # Загружаем default_config.yaml
                    default_config_path = Path(__file__).parent / "default_config.yaml"

                    if not default_config_path.exists():
                        self.notify(t("Error: default_config.yaml not found"), severity="error")
                        return

                    # Читаем содержимое default_config.yaml
                    with open(default_config_path, 'r', encoding='utf-8') as f:
                        default_content = f.read()

                    # Записываем в пользовательский конфиг
                    if hasattr(config, 'config_path'):
                        config_path = Path(config.config_path)
                    else:
                        config_path = (
                            Path.home() / ".config" / "penguin-tamer" / "penguin-tamer" / "config.yaml"
                        )

                    # Создаем директорию если не существует
                    config_path.parent.mkdir(parents=True, exist_ok=True)

                    # Записываем default конфиг
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)

                    # Перезагружаем конфигурацию
                    config.reload()

                    # Обновляем все отображаемые значения
                    self.update_all_inputs()
                    self.update_llm_tables()

                    self.notify(t("Settings successfully reset to defaults"), severity="information")

                except Exception as e:
                    self.notify(t("Error resetting settings: {error}", error=str(e)), severity="error")

        self.push_screen(ConfirmDialog(message, t("Reset Settings")), handle_confirm)

    def update_all_inputs(self) -> None:
        """Обновляет все поля ввода значениями из конфига."""
        try:
            # Обновляем параметры генерации
            temp_input = self.query_one("#temp-input", Input)
            temp_input.value = str(config.temperature)

            max_tokens_input = self.query_one("#max-tokens-input", Input)
            max_tokens_str = str(config.max_tokens) if config.max_tokens else "null"
            max_tokens_input.value = max_tokens_str

            top_p_input = self.query_one("#top-p-input", Input)
            top_p_input.value = str(config.top_p)

            freq_penalty_input = self.query_one("#freq-penalty-input", Input)
            freq_penalty_input.value = str(config.frequency_penalty)

            pres_penalty_input = self.query_one("#pres-penalty-input", Input)
            pres_penalty_input.value = str(config.presence_penalty)

            seed_input = self.query_one("#seed-input", Input)
            seed_str = str(config.seed) if config.seed else "null"
            seed_input.value = seed_str

            # Обновляем системные настройки
            stream_delay_input = self.query_one("#stream-delay-input", Input)
            stream_delay = config.get("global", "sleep_time", 0.01)
            stream_delay_input.value = str(stream_delay)

            refresh_rate_input = self.query_one("#refresh-rate-input", Input)
            refresh_rate = config.get("global", "refresh_per_second", 10)
            refresh_rate_input.value = str(refresh_rate)

            debug_switch = self.query_one("#debug-switch", Switch)
            debug_switch.value = getattr(config, "debug", False)

            # Обновляем контент
            content_textarea = self.query_one("#content-textarea", TextArea)
            content_textarea.text = config.user_content

            # Обновляем язык
            language_select = self.query_one("#language-select", Select)
            current_lang = getattr(config, "language", "en")
            language_select.value = current_lang

            # Обновляем тему
            theme_select = self.query_one("#theme-select", Select)
            current_theme = config.get("global", "markdown_theme", "default")
            theme_select.value = current_theme

            # Обновляем панель с системной информацией и текущей LLM
            if hasattr(config, 'config_path'):
                config_dir = Path(config.config_path).parent
            else:
                config_dir = Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
            bin_path = Path(sys.executable).parent
            current_llm = config.current_llm or t("Not selected")

            system_info_display = self.query_one("#system-info-display", Static)
            system_info_display.update(
                f"[bold]{t('Current LLM:')}[/bold] [#e07333]{current_llm}[/#e07333]\n\n"
                f"[bold]{t('Config folder:')}[/bold] {config_dir}\n"
                f"[bold]{t('Binary folder:')}[/bold] {bin_path}"

            )

        except Exception:
            # Некоторые виджеты могут быть не найдены, это нормально
            pass


def main_menu(show_api_key_dialog: bool = False):
    """Entry point for running the config menu.

    Args:
        show_api_key_dialog: If True, shows API key missing dialog on startup
    """
    try:
        # Показываем интро перед запуском меню
        show_intro()

        app = ConfigMenuApp(show_api_key_dialog=show_api_key_dialog)
        app.run()
    except Exception as e:
        print(f"Error starting settings menu: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_menu()
