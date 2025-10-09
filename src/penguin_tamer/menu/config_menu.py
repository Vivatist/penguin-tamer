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
    from penguin_tamer.menu.dialogs import LLMEditDialog, ConfirmDialog
    from penguin_tamer.menu.info_panel import InfoPanel
    from penguin_tamer.menu.intro_screen import show_intro
else:
    # При импорте как модуль используем относительные импорты
    from .widgets import DoubleClickDataTable, ResponsiveButtonRow
    from .dialogs import LLMEditDialog, ConfirmDialog
    from .info_panel import InfoPanel
    from .intro_screen import show_intro


class ConfigMenuApp(App):
    """Main Textual configuration application."""

    # Flag to prevent notifications during initialization
    _initialized = False

    # Load CSS from external file
    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Выход", priority=True),
        Binding("ctrl+c", "quit", "Выход"),
        Binding("f1", "help", "Помощь"),
        Binding("ctrl+r", "refresh_status", "Обновить"),
    ]

    ENABLE_COMMAND_PALETTE = False

    TITLE = "Penguin Tamer " + __version__
    SUB_TITLE = "Конфигурация"

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
            "warning": "#ffd8b9",
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
                    with TabPane("Общие", id="tab-general"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ОБЩИЕ НАСТРОЙКИ[/bold]\n"
                                "[dim]Системная информация и управление LLM[/dim]",
                                classes="tab-header",
                            )

                            # Language setting
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Language\n[dim]Требуется перезапуск[/dim]",
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
                            current_llm = config.current_llm or "Не выбрана"

                            yield Static(
                                f"[bold]Текущая LLM:[/bold] [#e07333]{current_llm}[/#e07333]\n\n"
                                f"[bold]Папка конфига:[/bold] {config_dir}\n"
                                f"[bold]Папка бинарника:[/bold] {bin_path}",
                                classes="system-info-panel",
                                id="system-info-display"
                            )

                            yield Static("")
                            yield Static(
                                "[bold]Добавленные нейросети[/bold]\n"
                                "[dim]Выберите какую нейросеть использовать, или добавьте свою[/dim]"
                            )
                            llm_dt = DoubleClickDataTable(id="llm-table", show_header=True, cursor_type="row")
                            yield llm_dt
                            yield Static("")
                            yield ResponsiveButtonRow(
                                buttons_data=[
                                    ("Выбрать", "select-llm-btn", "success"),
                                    ("Добавить", "add-llm-btn", "success"),
                                    ("Изменить", "edit-llm-btn", "success"),
                                    ("Удалить", "delete-llm-btn", "error"),
                                ],
                                classes="button-row"
                            )

                    # Tab 2: User Content
                    with TabPane("Контент", id="tab-content"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ[/bold]\n"
                                "[dim]Дополнительный контекст для всех запросов[/dim]",
                                classes="tab-header",
                            )
                            yield TextArea(text=config.user_content, id="content-textarea")
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "Сохранить",
                                    id="save-content-btn",
                                    variant="success",
                                )

                    # Tab 3: Generation Parameters
                    with TabPane("Генерация", id="tab-params"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ПАРАМЕТРЫ ГЕНЕРАЦИИ[/bold]\n"
                                "[dim]Настройка поведения ИИ (нажмите Enter для сохранения)[/dim]",
                                classes="tab-header",
                            )

                            # Temperature
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Температура\n[dim]Креативность (0.0-2.0)[/dim]",
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
                                else "неограниченно"
                            )
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Максимум токенов\n[dim]Длина ответа[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=max_tokens_str,
                                    id="max-tokens-input",
                                    placeholder="число или 'null'",
                                    classes="param-control"
                                )

                            # Top P
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Top P\n[dim]Ядерная выборка (0.0-1.0)[/dim]",
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
                                    "Штраф частоты\n[dim]Снижает повторения (-2.0 до 2.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.frequency_penalty),
                                    id="freq-penalty-input",
                                    placeholder="-2.0 до 2.0",
                                    classes="param-control"
                                )

                            # Presence Penalty
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Штраф присутствия\n[dim]Разнообразие тем (-2.0 до 2.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.presence_penalty),
                                    id="pres-penalty-input",
                                    placeholder="-2.0 до 2.0",
                                    classes="param-control"
                                )

                            # Seed
                            seed_str = str(config.seed) if config.seed else "случайный"
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Seed\n[dim]Для воспроизводимости[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=seed_str,
                                    id="seed-input",
                                    placeholder="число или 'null'",
                                    classes="param-control"
                                )

                    # Tab 4: System Settings

                    with TabPane("Система", id="tab-system"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]СИСТЕМНЫЕ НАСТРОЙКИ[/bold]\n"
                                "[dim]Поведение приложения (нажмите Enter для сохранения)[/dim]",
                                classes="tab-header",
                            )

                            # Stream Delay
                            stream_delay = config.get("global", "sleep_time", 0.01)
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Задержка стрима\n[dim]Пауза между частями (0.001-0.1)[/dim]",
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
                                    "Частота обновлений\n[dim]Обновление интерфейса (1-60 Гц)[/dim]",
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
                                    "Режим отладки\n[dim]Подробная информация о запросах[/dim]",
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
                                    "Сброс настроек",
                                    id="reset-settings-btn",
                                    variant="error",
                                )

                            # Flexible spacer AFTER button to fill remaining space
                            yield Static("", classes="flexible-spacer")

                    # Tab 5: Interface

                    with TabPane("Интерфейс", id="tab-appearance"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]НАСТРОЙКИ ИНТЕРФЕЙСА[/bold]\n"
                                "[dim]Внешний вид приложения (изменения сохраняются автоматически)[/dim]",
                                classes="tab-header",
                            )

                            # Theme
                            current_theme = getattr(config, "theme", "default")
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Цветовая схема\n[dim]Требуется перезапуск[/dim]",
                                    classes="param-label"
                                )
                                yield Select(
                                    [
                                        ("Классический", "default"),
                                        ("Monokai", "monokai"),
                                        ("Dracula", "dracula"),
                                        ("Nord", "nord"),
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
            self.notify(f"Ошибка: {e}", severity="error")

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
            status = "включен" if event.value else "выключен"
            self.notify(f"Режим отладки {status}", severity="information")

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
        llm_table.add_columns("", "Название", "Модель", "API URL", "API ключ")

        new_cursor_row = 0
        for idx, llm_name in enumerate(llms):
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            llm_table.add_row(
                is_current,
                llm_name,
                cfg.get("model", "N/A"),
                cfg.get("api_url", "N/A"),
                format_api_key_display(cfg.get("api_key", "")),
            )
            # Запоминаем новую позицию для старой LLM
            if old_llm_name and llm_name == old_llm_name:
                new_cursor_row = idx

        # Восстанавливаем позицию курсора и highlight
        if keep_cursor_position and old_llm_name and len(llms) > 0:
            try:
                # Устанавливаем cursor_coordinate для правильного highlight
                llm_table.cursor_coordinate = (new_cursor_row, 0)
            except Exception:
                try:
                    # Альтернативный способ
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
        elif btn_id == "select-llm-btn":
            self.select_current_llm()

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
        """Handle double-click on DataTable."""
        self.select_current_llm()

    # LLM Methods
    def select_current_llm(self) -> None:
        """Select current LLM from table."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM из списка", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)
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
            f"[bold]Текущая LLM:[/bold] [#e07333]{llm_name}[/#e07333]\n\n"
            f"[bold]Папка конфига:[/bold] {config_dir}\n"
            f"[bold]Папка бинарника:[/bold] {bin_path}"
        )

        self.refresh_status()
        self.notify(f"Текущая LLM: {llm_name}", severity="information")

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
                self.notify(f"LLM '{result['name']}' добавлена", severity="information")

        self.push_screen(
            LLMEditDialog(title="Добавление LLM"),
            handle_result
        )

    def edit_llm(self) -> None:
        """Edit selected LLM."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM для редактирования", severity="warning")
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
                self.notify(f"LLM '{llm_name}' обновлена", severity="information")

        self.push_screen(
            LLMEditDialog(
                title=f"Редактирование {llm_name}",
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
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM для удаления", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)

        if llm_name == config.current_llm:
            self.notify("Нельзя удалить текущую LLM", severity="error")
            return

        def handle_confirm(confirm):
            if confirm:
                config.remove_llm(llm_name)
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"LLM '{llm_name}' удалена", severity="information")

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
                config.save()
                self.refresh_status()
                self.notify(f"Температура: {value}", severity="information")
            else:
                self.notify("Температура должна быть от 0.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_max_tokens(self) -> None:
        """Set max tokens parameter."""
        input_field = self.query_one("#max-tokens-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.max_tokens = None
            config.save()
            self.refresh_status()
            self.notify("Максимум токенов: без ограничений", severity="information")
        else:
            try:
                num_value = int(value)
                if num_value > 0:
                    config.max_tokens = num_value
                    config.save()
                    self.refresh_status()
                    self.notify(f"Максимум токенов: {num_value}", severity="information")
                else:
                    self.notify("Должно быть положительным", severity="error")
            except ValueError:
                self.notify("Неверный числовой формат", severity="error")

    def set_top_p(self) -> None:
        """Set top_p parameter."""
        input_field = self.query_one("#top-p-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 1.0:
                config.top_p = value
                config.save()
                self.refresh_status()
                self.notify(f"Top P: {value}", severity="information")
            else:
                self.notify("Top P должен быть от 0.0 до 1.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_frequency_penalty(self) -> None:
        """Сет frequency penalty."""
        input_field = self.query_one("#freq-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.frequency_penalty = value
                config.save()
                self.refresh_status()
                self.notify(f"Штраф частоты: {value}", severity="information")
            else:
                self.notify("Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_presence_penalty(self) -> None:
        """Set presence penalty."""
        input_field = self.query_one("#pres-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.presence_penalty = value
                config.save()
                self.refresh_status()
                self.notify(f"Штраф присутствия: {value}", severity="information")
            else:
                self.notify("Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_seed(self) -> None:
        """Set seed parameter."""
        input_field = self.query_one("#seed-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.seed = None
            config.save()
            self.refresh_status()
            self.notify("Seed: случайный", severity="information")
        else:
            try:
                num_value = int(value)
                config.seed = num_value
                config.save()
                self.refresh_status()
                self.notify(f"Seed: {num_value}", severity="information")
            except ValueError:
                self.notify("Неверный числовой формат", severity="error")

    # User Content Methods
    def save_user_content(self) -> None:
        """Save user content."""
        text_area = self.query_one("#content-textarea", TextArea)
        config.user_content = text_area.text
        config.save()
        self.refresh_status()
        self.notify("Контент сохранён", severity="information")

    # System Settings Methods
    def set_stream_delay(self) -> None:
        """Set stream delay."""
        input_field = self.query_one("#stream-delay-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.001 <= value <= 0.1:
                config.set("global", "sleep_time", value)
                self.refresh_status()
                self.notify(f"Задержка стрима: {value} сек", severity="information")
            else:
                self.notify("Должно быть от 0.001 до 0.1", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_refresh_rate(self) -> None:
        """Set refresh rate."""
        input_field = self.query_one("#refresh-rate-input", Input)
        try:
            value = int(input_field.value)
            if 1 <= value <= 60:
                config.set("global", "refresh_per_second", value)
                self.refresh_status()
                self.notify(f"Частота обновлений: {value} Гц", severity="information")
            else:
                self.notify("Должно быть от 1 до 60", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    # Language & Theme Methods
    def set_language(self, lang: str) -> None:
        """Set interface language."""
        setattr(config, "language", lang)
        config.save()
        translator.set_language(lang)
        self.refresh_status()
        lang_name = "English" if lang == "en" else "Русский"
        self.notify(f"Язык: {lang_name}", severity="information")

    def set_theme(self, theme: str) -> None:
        """Set interface theme."""
        setattr(config, "theme", theme)
        config.save()
        self.refresh_status()
        theme_names = {
            "default": "Классический",
            "monokai": "Monokai",
            "dracula": "Dracula",
            "nord": "Nord",
        }
        theme_name = theme_names.get(theme, theme)
        self.notify(f"Тема: {theme_name}", severity="information")

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
        self.notify("Статус обновлён", severity="information")

    def action_reset_settings(self) -> None:
        """Сброс настроек к значениям по умолчанию."""
        message = (
            "Внимание! Все настройки, включая API ключи,\n"
            "будут сброшены к настройкам по умолчанию.\n\n"
            "Продолжить?"
        )

        def handle_confirm(result):
            if result:
                try:
                    # Загружаем default_config.yaml
                    default_config_path = Path(__file__).parent / "default_config.yaml"

                    if not default_config_path.exists():
                        self.notify("Файл default_config.yaml не найден", severity="error")
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

                    self.notify("Настройки успешно сброшены к значениям по умолчанию", severity="information")

                except Exception as e:
                    self.notify(f"Ошибка при сбросе настроек: {e}", severity="error")

        self.push_screen(ConfirmDialog(message, "Сброс настроек"), handle_confirm)

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
            current_theme = getattr(config, "theme", "default")
            theme_select.value = current_theme

            # Обновляем панель с системной информацией и текущей LLM
            if hasattr(config, 'config_path'):
                config_dir = Path(config.config_path).parent
            else:
                config_dir = Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
            bin_path = Path(sys.executable).parent
            current_llm = config.current_llm or "Не выбрана"

            system_info_display = self.query_one("#system-info-display", Static)
            system_info_display.update(
                f"[bold]Текущая LLM:[/bold] [#e07333]{current_llm}[/#e07333]\n\n"
                f"[bold]Папка конфига:[/bold] {config_dir}\n"
                f"[bold]Папка бинарника:[/bold] {bin_path}"

            )

        except Exception:
            # Некоторые виджеты могут быть не найдены, это нормально
            pass


def main_menu():
    """Entry point for running the config menu."""
    try:
        # Показываем интро перед запуском меню
        show_intro()

        app = ConfigMenuApp()
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске меню настроек: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_menu()
