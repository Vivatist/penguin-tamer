#!/usr/bin/env python3
"""
Modern Textual-based configuration menu for Penguin Tamer.

Features:
- Rich TUI with real-time status display
- Multi-line text input with proper text area
- Visual hints and descriptions for all settings
- Tabbed interface for organized navigation
- Live config preview
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Static, Input, TextArea,
    Label, Tabs, Tab, DataTable, Select, Switch
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual import on
from textual.reactive import reactive

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from penguin_tamer.config_manager import config
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t, translator


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation."""
    
    def __init__(self, message: str, title: str = "Confirm", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.title = title
        self.result = False

    def compose(self) -> ComposeResult:
        with Container(id="dialog-container"):
            yield Static(self.title, id="dialog-title")
            yield Static(self.message, id="dialog-message")
            with Horizontal(id="dialog-buttons"):
                yield Button("Yes", variant="success", id="yes-btn")
                yield Button("No", variant="error", id="no-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.result = True
            self.dismiss(True)
        else:
            self.result = False
            self.dismiss(False)


class InputDialog(ModalScreen):
    """Modal dialog for text input."""
    
    def __init__(self, prompt: str, default: str = "", title: str = "Input", multiline: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompt
        self.default = default
        self.title = title
        self.multiline = multiline
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="input-dialog-container"):
            yield Static(self.title, id="input-dialog-title")
            yield Static(self.prompt, id="input-dialog-prompt")
            
            if self.multiline:
                text_area = TextArea(self.default, id="input-field")
                text_area.border_title = "Enter text (Ctrl+D to save)"
                yield text_area
            else:
                yield Input(value=self.default, placeholder=self.prompt, id="input-field")
            
            with Horizontal(id="input-dialog-buttons"):
                yield Button("OK", variant="success", id="ok-btn")
                yield Button("Cancel", variant="error", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            input_widget = self.query_one("#input-field")
            if isinstance(input_widget, TextArea):
                self.result = input_widget.text
            else:
                self.result = input_widget.value
            self.dismiss(self.result)
        else:
            self.result = None
            self.dismiss(None)


class StatusPanel(Static):
    """Panel showing current configuration status."""
    
    def compose(self) -> ComposeResult:
        yield Static(self.render_status(), id="status-content")
    
    def render_status(self) -> str:
        """Generate status text."""
        lines = []
        lines.append("[bold cyan]═══ Current Configuration ═══[/bold cyan]\n")
        
        # Current LLM
        current_llm = config.current_llm or "(not selected)"
        current_cfg = config.get_current_llm_config() or {}
        
        lines.append(f"[bold]🤖 Current LLM:[/bold] [green]{current_llm}[/green]")
        if current_cfg:
            lines.append(f"   Model: {current_cfg.get('model', 'N/A')}")
            lines.append(f"   API URL: {current_cfg.get('api_url', 'N/A')}")
            lines.append(f"   API Key: {format_api_key_display(current_cfg.get('api_key', ''))}")
        
        lines.append("")
        
        # Generation parameters
        lines.append("[bold]⚙️  Generation Parameters:[/bold]")
        lines.append(f"   Temperature: [cyan]{config.temperature}[/cyan]")
        lines.append(f"   Max Tokens: [cyan]{config.max_tokens if config.max_tokens else 'unlimited'}[/cyan]")
        lines.append(f"   Top P: [cyan]{config.top_p}[/cyan]")
        lines.append(f"   Frequency Penalty: [cyan]{config.frequency_penalty}[/cyan]")
        lines.append(f"   Presence Penalty: [cyan]{config.presence_penalty}[/cyan]")
        lines.append(f"   Seed: [cyan]{config.seed if config.seed else 'random'}[/cyan]")
        
        lines.append("")
        
        # User content preview
        content = config.user_content or "(empty)"
        lines.append("[bold]📝 User Content:[/bold]")
        content_lines = content.split('\n')[:3]
        for line in content_lines:
            lines.append(f"   {line[:60]}")
        if len(content.split('\n')) > 3:
            lines.append("   [dim]...[/dim]")
        
        lines.append("")
        
        # System settings
        lines.append("[bold]🔧 System:[/bold]")
        lines.append(f"   Language: [cyan]{getattr(config, 'language', 'en')}[/cyan]")
        lines.append(f"   Theme: [cyan]{getattr(config, 'theme', 'default')}[/cyan]")
        lines.append(f"   Debug: [cyan]{'ON' if getattr(config, 'debug', False) else 'OFF'}[/cyan]")
        
        return "\n".join(lines)
    
    def refresh_status(self) -> None:
        """Update status display."""
        content = self.query_one("#status-content", Static)
        content.update(self.render_status())


class LLMManagementTab(ScrollableContainer):
    """Tab for managing LLMs."""
    
    def compose(self) -> ComposeResult:
        yield Static("[bold]🤖 LLM Management[/bold]\n[dim]Manage your AI language models[/dim]", classes="tab-header")
        
        # LLM List Table
        table = DataTable(id="llm-table")
        table.border_title = "Available LLMs"
        table.add_columns("✓", "Name", "Model", "API URL", "Key")
        self.update_llm_table(table)
        yield table
        
        # Action buttons
        with Horizontal(classes="button-row"):
            yield Button("➕ Add LLM", id="add-llm-btn", variant="success")
            yield Button("✏️  Edit Selected", id="edit-llm-btn", variant="primary")
            yield Button("✅ Set as Current", id="set-current-llm-btn", variant="default")
            yield Button("🗑️  Delete", id="delete-llm-btn", variant="error")
    
    def update_llm_table(self, table: DataTable) -> None:
        """Populate LLM table with current data."""
        table.clear()
        current = config.current_llm
        for llm_name in config.get_available_llms():
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            table.add_row(
                is_current,
                llm_name,
                cfg.get('model', '')[:30],
                cfg.get('api_url', '')[:40],
                format_api_key_display(cfg.get('api_key', ''))
            )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-llm-btn":
            self.add_llm()
        elif event.button.id == "edit-llm-btn":
            self.edit_selected_llm()
        elif event.button.id == "set-current-llm-btn":
            self.set_current_llm()
        elif event.button.id == "delete-llm-btn":
            self.delete_selected_llm()
    
    def add_llm(self) -> None:
        """Add a new LLM."""
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
                        try:
                            config.add_llm(name, model, api_url, api_key or "")
                            self.update_llm_table(self.query_one("#llm-table", DataTable))
                            self.app.query_one(StatusPanel).refresh_status()
                            self.notify(f"✅ LLM '{name}' added successfully", severity="information")
                        except ValueError as e:
                            self.notify(f"❌ Error: {e}", severity="error")
                    
                    self.app.push_screen(
                        InputDialog("Enter API key (optional):", title="Add LLM"),
                        handle_key
                    )
                
                self.app.push_screen(
                    InputDialog("Enter API URL:", title="Add LLM"),
                    handle_url
                )
            
            self.app.push_screen(
                InputDialog("Enter model name:", title="Add LLM"),
                handle_model
            )
        
        self.app.push_screen(
            InputDialog("Enter LLM name:", title="Add LLM"),
            handle_name
        )
    
    def edit_selected_llm(self) -> None:
        """Edit selected LLM."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Please select an LLM first", severity="warning")
            return
        
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])
        cfg = config.get_llm_config(llm_name) or {}
        
        def handle_model(model):
            if model is not None:
                config.update_llm(llm_name, model=model)
            
            def handle_url(url):
                if url is not None:
                    config.update_llm(llm_name, api_url=url)
                
                def handle_key(key):
                    if key is not None:
                        config.update_llm(llm_name, api_key=key)
                    
                    self.update_llm_table(table)
                    self.app.query_one(StatusPanel).refresh_status()
                    self.notify(f"✅ LLM '{llm_name}' updated", severity="information")
                
                self.app.push_screen(
                    InputDialog("API Key:", default=cfg.get('api_key', ''), title=f"Edit {llm_name}"),
                    handle_key
                )
            
            self.app.push_screen(
                InputDialog("API URL:", default=cfg.get('api_url', ''), title=f"Edit {llm_name}"),
                handle_url
            )
        
        self.app.push_screen(
            InputDialog("Model:", default=cfg.get('model', ''), title=f"Edit {llm_name}"),
            handle_model
        )
    
    def set_current_llm(self) -> None:
        """Set selected LLM as current."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Please select an LLM first", severity="warning")
            return
        
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])
        config.current_llm = llm_name
        
        self.update_llm_table(table)
        self.app.query_one(StatusPanel).refresh_status()
        self.notify(f"✅ Current LLM set to '{llm_name}'", severity="information")
    
    async def delete_selected_llm(self) -> None:
        """Delete selected LLM."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("⚠️ Please select an LLM first", severity="warning")
            return
        
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])
        
        if llm_name == config.current_llm:
            self.notify("❌ Cannot delete current LLM", severity="error")
            return
        
        def handle_confirm(confirm):
            if confirm:
                config.remove_llm(llm_name)
                self.update_llm_table(table)
                self.app.query_one(StatusPanel).refresh_status()
                self.notify(f"✅ LLM '{llm_name}' deleted", severity="information")
        
        self.app.push_screen(
            ConfirmDialog(f"Delete LLM '{llm_name}'?", title="Confirm Delete"),
            handle_confirm
        )


class GenerationParamsTab(ScrollableContainer):
    """Tab for generation parameters."""
    
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]⚙️  Generation Parameters[/bold]\n" +
            "[dim]Control how the AI generates responses[/dim]",
            classes="tab-header"
        )
        
        # Temperature
        yield Static("\n[bold]Temperature[/bold] (0.0 - 2.0)", classes="param-label")
        yield Static(
            "[dim]Controls randomness. Lower = more focused, Higher = more creative[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.temperature),
            placeholder="0.7",
            id="temperature-input"
        )
        yield Button("Set Temperature", id="set-temp-btn", classes="param-btn")
        
        # Max Tokens
        yield Static("\n[bold]Max Tokens[/bold]", classes="param-label")
        yield Static(
            "[dim]Maximum length of response. Leave empty for unlimited[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.max_tokens) if config.max_tokens else "",
            placeholder="null (unlimited)",
            id="max-tokens-input"
        )
        yield Button("Set Max Tokens", id="set-max-tokens-btn", classes="param-btn")
        
        # Top P
        yield Static("\n[bold]Top P[/bold] (0.0 - 1.0)", classes="param-label")
        yield Static(
            "[dim]Nucleus sampling. Controls diversity of word choices[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.top_p),
            placeholder="1.0",
            id="top-p-input"
        )
        yield Button("Set Top P", id="set-top-p-btn", classes="param-btn")
        
        # Frequency Penalty
        yield Static("\n[bold]Frequency Penalty[/bold] (-2.0 - 2.0)", classes="param-label")
        yield Static(
            "[dim]Reduces repetition of tokens based on frequency[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.frequency_penalty),
            placeholder="0.0",
            id="freq-penalty-input"
        )
        yield Button("Set Frequency Penalty", id="set-freq-penalty-btn", classes="param-btn")
        
        # Presence Penalty
        yield Static("\n[bold]Presence Penalty[/bold] (-2.0 - 2.0)", classes="param-label")
        yield Static(
            "[dim]Reduces repetition of topics already mentioned[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.presence_penalty),
            placeholder="0.0",
            id="pres-penalty-input"
        )
        yield Button("Set Presence Penalty", id="set-pres-penalty-btn", classes="param-btn")
        
        # Seed
        yield Static("\n[bold]Seed[/bold]", classes="param-label")
        yield Static(
            "[dim]For deterministic generation. Leave empty for random[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.seed) if config.seed else "",
            placeholder="null (random)",
            id="seed-input"
        )
        yield Button("Set Seed", id="set-seed-btn", classes="param-btn")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle parameter updates."""
        try:
            if event.button.id == "set-temp-btn":
                value = float(self.query_one("#temperature-input", Input).value)
                if not 0.0 <= value <= 2.0:
                    raise ValueError("Temperature must be between 0.0 and 2.0")
                config.temperature = value
                self.notify("✅ Temperature updated", severity="information")
            
            elif event.button.id == "set-max-tokens-btn":
                value = self.query_one("#max-tokens-input", Input).value.strip()
                if not value or value.lower() in ['null', 'none', '']:
                    config.max_tokens = None
                else:
                    config.max_tokens = int(value)
                self.notify("✅ Max tokens updated", severity="information")
            
            elif event.button.id == "set-top-p-btn":
                value = float(self.query_one("#top-p-input", Input).value)
                if not 0.0 <= value <= 1.0:
                    raise ValueError("Top P must be between 0.0 and 1.0")
                config.top_p = value
                self.notify("✅ Top P updated", severity="information")
            
            elif event.button.id == "set-freq-penalty-btn":
                value = float(self.query_one("#freq-penalty-input", Input).value)
                if not -2.0 <= value <= 2.0:
                    raise ValueError("Frequency penalty must be between -2.0 and 2.0")
                config.frequency_penalty = value
                self.notify("✅ Frequency penalty updated", severity="information")
            
            elif event.button.id == "set-pres-penalty-btn":
                value = float(self.query_one("#pres-penalty-input", Input).value)
                if not -2.0 <= value <= 2.0:
                    raise ValueError("Presence penalty must be between -2.0 and 2.0")
                config.presence_penalty = value
                self.notify("✅ Presence penalty updated", severity="information")
            
            elif event.button.id == "set-seed-btn":
                value = self.query_one("#seed-input", Input).value.strip()
                if not value or value.lower() in ['null', 'none', '']:
                    config.seed = None
                else:
                    config.seed = int(value)
                self.notify("✅ Seed updated", severity="information")
            
            self.app.query_one(StatusPanel).refresh_status()
            
        except ValueError as e:
            self.notify(f"❌ Invalid value: {e}", severity="error")


class UserContentTab(ScrollableContainer):
    """Tab for user content."""
    
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]📝 User Content[/bold]\n" +
            "[dim]Custom content to include in every request[/dim]",
            classes="tab-header"
        )
        
        current_content = config.user_content or ""
        
        text_area = TextArea(current_content, id="content-textarea")
        text_area.border_title = "User Content (multi-line)"
        yield text_area
        
        yield Static(
            "\n[dim]💡 Tip: Use this to add context, instructions, or preferences that should apply to all conversations[/dim]",
            classes="param-hint"
        )
        
        with Horizontal(classes="button-row"):
            yield Button("💾 Save Content", id="save-content-btn", variant="success")
            yield Button("🔄 Reset", id="reset-content-btn", variant="error")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle content updates."""
        if event.button.id == "save-content-btn":
            text_area = self.query_one("#content-textarea", TextArea)
            config.user_content = text_area.text
            self.app.query_one(StatusPanel).refresh_status()
            self.notify("✅ User content saved", severity="information")
        
        elif event.button.id == "reset-content-btn":
            confirm = await self.app.push_screen_wait(
                ConfirmDialog("Clear all user content?", title="Confirm Reset")
            )
            if confirm:
                config.user_content = ""
                text_area = self.query_one("#content-textarea", TextArea)
                text_area.text = ""
                self.app.query_one(StatusPanel).refresh_status()
                self.notify("✅ User content cleared", severity="information")


class SystemSettingsTab(ScrollableContainer):
    """Tab for system settings."""
    
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold]🔧 System Settings[/bold]\n" +
            "[dim]Configure application behavior[/dim]",
            classes="tab-header"
        )
        
        # Language
        yield Static("\n[bold]Language[/bold]", classes="param-label")
        yield Static("[dim]Application interface language[/dim]", classes="param-hint")
        with Horizontal(classes="button-row"):
            yield Button("English (en)", id="lang-en-btn")
            yield Button("Русский (ru)", id="lang-ru-btn")
        
        # Theme
        yield Static("\n[bold]Theme[/bold]", classes="param-label")
        yield Static("[dim]Syntax highlighting theme for code blocks[/dim]", classes="param-hint")
        with Horizontal(classes="button-row"):
            yield Button("Default", id="theme-default-btn")
            yield Button("Monokai", id="theme-monokai-btn")
            yield Button("Dracula", id="theme-dracula-btn")
            yield Button("Nord", id="theme-nord-btn")
        
        # Debug Mode
        yield Static("\n[bold]Debug Mode[/bold]", classes="param-label")
        yield Static(
            "[dim]Show detailed LLM request/response information[/dim]",
            classes="param-hint"
        )
        yield Switch(value=getattr(config, 'debug', False), id="debug-switch")
        
        # Stream Settings
        yield Static("\n[bold]Stream Delay[/bold] (0.001 - 0.1s)", classes="param-label")
        yield Static(
            "[dim]Delay between text updates. Lower = faster, higher CPU usage[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.get("global", "sleep_time", 0.01)),
            placeholder="0.01",
            id="sleep-time-input"
        )
        yield Button("Set Stream Delay", id="set-sleep-time-btn", classes="param-btn")
        
        yield Static("\n[bold]Refresh Rate[/bold] (1 - 60 Hz)", classes="param-label")
        yield Static(
            "[dim]Interface update frequency. Higher = smoother, higher CPU usage[/dim]",
            classes="param-hint"
        )
        yield Input(
            value=str(config.get("global", "refresh_per_second", 10)),
            placeholder="10",
            id="refresh-rate-input"
        )
        yield Button("Set Refresh Rate", id="set-refresh-rate-btn", classes="param-btn")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle system settings."""
        try:
            if event.button.id == "lang-en-btn":
                config.language = "en"
                translator.set_language("en")
                self.notify("✅ Language set to English", severity="information")
            
            elif event.button.id == "lang-ru-btn":
                config.language = "ru"
                translator.set_language("ru")
                self.notify("✅ Язык установлен: Русский", severity="information")
            
            elif event.button.id.startswith("theme-"):
                theme = event.button.id.replace("theme-", "").replace("-btn", "")
                config.theme = theme
                self.notify(f"✅ Theme set to {theme}", severity="information")
            
            elif event.button.id == "set-sleep-time-btn":
                value = float(self.query_one("#sleep-time-input", Input).value)
                if not 0.001 <= value <= 0.1:
                    raise ValueError("Sleep time must be between 0.001 and 0.1")
                config.set("global", "sleep_time", value)
                self.notify("✅ Stream delay updated", severity="information")
            
            elif event.button.id == "set-refresh-rate-btn":
                value = int(self.query_one("#refresh-rate-input", Input).value)
                if not 1 <= value <= 60:
                    raise ValueError("Refresh rate must be between 1 and 60")
                config.set("global", "refresh_per_second", value)
                self.notify("✅ Refresh rate updated", severity="information")
            
            self.app.query_one(StatusPanel).refresh_status()
            
        except ValueError as e:
            self.notify(f"❌ Invalid value: {e}", severity="error")
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle debug mode toggle."""
        config.debug = event.value
        status = "enabled" if event.value else "disabled"
        self.notify(f"✅ Debug mode {status}", severity="information")
        self.app.query_one(StatusPanel).refresh_status()


class ConfigMenuApp(App):
    """Main Textual configuration app."""
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #left-panel {
        width: 60%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    
    #right-panel {
        width: 40%;
        height: 100%;
        border: solid $secondary;
        padding: 1;
        background: $surface;
    }
    
    .tab-header {
        padding: 1;
        margin-bottom: 1;
        background: $boost;
        border: solid $primary;
    }
    
    .param-label {
        margin-top: 1;
        color: $accent;
    }
    
    .param-hint {
        margin-bottom: 1;
        color: $text-muted;
    }
    
    .param-btn {
        width: 100%;
        margin-bottom: 1;
    }
    
    .button-row {
        height: auto;
        margin-bottom: 1;
    }
    
    .button-row Button {
        margin-right: 1;
    }
    
    #dialog-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #dialog-message {
        width: 100%;
        margin-bottom: 1;
    }
    
    #dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    #dialog-buttons Button {
        margin: 0 1;
    }
    
    #input-dialog-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #input-dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #input-dialog-prompt {
        width: 100%;
        margin-bottom: 1;
    }
    
    #input-field {
        width: 100%;
        margin-bottom: 1;
    }
    
    #input-dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    #input-dialog-buttons Button {
        margin: 0 1;
    }
    
    #status-content {
        padding: 1;
    }
    
    #llm-table {
        height: 50%;
        margin-bottom: 1;
    }
    
    #content-textarea {
        height: 30;
        margin-bottom: 1;
    }
    
    DataTable {
        height: 1fr;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit"),
        ("f1", "help", "Help"),
    ]
    
    TITLE = "🐧 Penguin Tamer - Configuration Menu"
    SUB_TITLE = "Manage your AI settings"
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal():
            # Left panel - tabs with settings
            with Vertical(id="left-panel"):
                with Tabs():
                    yield Tab("🤖 LLMs", id="tab-llms")
                    yield Tab("⚙️  Generation", id="tab-params")
                    yield Tab("📝 Content", id="tab-content")
                    yield Tab("🔧 System", id="tab-system")
                
                yield LLMManagementTab(id="llm-tab")
                yield GenerationParamsTab(id="params-tab")
                yield UserContentTab(id="content-tab")
                yield SystemSettingsTab(id="system-tab")
            
            # Right panel - live status
            with Vertical(id="right-panel"):
                yield StatusPanel(id="status-panel")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize app state."""
        # Show only first tab content
        self.query_one("#params-tab").display = False
        self.query_one("#content-tab").display = False
        self.query_one("#system-tab").display = False
    
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab switching."""
        # Hide all tabs
        self.query_one("#llm-tab").display = False
        self.query_one("#params-tab").display = False
        self.query_one("#content-tab").display = False
        self.query_one("#system-tab").display = False
        
        # Show selected tab
        if event.tab.id == "tab-llms":
            self.query_one("#llm-tab").display = True
        elif event.tab.id == "tab-params":
            self.query_one("#params-tab").display = True
        elif event.tab.id == "tab-content":
            self.query_one("#content-tab").display = True
        elif event.tab.id == "tab-system":
            self.query_one("#system-tab").display = True
    
    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Use tabs to navigate settings. Q or Ctrl+C to quit.",
            title="Help",
            severity="information"
        )


def main():
    """Run the Textual configuration menu."""
    try:
        # Ensure translator uses current config language
        translator.set_language(getattr(config, 'language', 'en'))
    except Exception:
        pass
    
    app = ConfigMenuApp()
    app.run()


if __name__ == "__main__":
    main()
