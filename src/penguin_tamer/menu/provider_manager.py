"""
Provider Manager - Modal screen for managing LLM providers.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from penguin_tamer.config_manager import config
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.menu.locales.menu_i18n import t
from penguin_tamer.menu.dialogs import ProviderEditDialog, ConfirmDialog


class ProviderManagerScreen(ModalScreen):
    """Modal screen for managing LLM providers (CRUD operations)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        """Create the provider manager UI."""
        yield Container(
            Static(t("Provider Management"), classes="provider-manager-title"),
            Container(
                DataTable(
                    id="provider-table",
                    cursor_type="row",
                    zebra_stripes=True,
                    show_header=True
                ),
                classes="provider-table-container"
            ),
            Horizontal(
                Button(t("Add"), variant="success", id="add-provider-btn"),
                Button(t("Edit"), variant="success", id="edit-provider-btn"),
                Button(t("Delete"), variant="error", id="delete-provider-btn"),
                Button(t("Close"), variant="success", id="close-provider-btn"),
                classes="provider-manager-buttons",
            ),
            classes="provider-manager-container",
        )

    def on_mount(self) -> None:
        """Initialize provider table on mount."""
        self.update_provider_table()

    def update_provider_table(self) -> None:
        """Update provider table with current data."""
        table = self.query_one("#provider-table", DataTable)
        
        # Save cursor position
        old_cursor_row = table.cursor_row if table.row_count > 0 else 0
        
        table.clear(columns=True)
        # Добавляем колонки с указанием ширины
        table.add_column(t("Provider Name"), width=30)
        table.add_column(t("API Key"), width=32)

        providers = config.get("supported_Providers") or {}
        
        for provider_name, provider_config in providers.items():
            api_key = format_api_key_display(provider_config.get("api_key", ""))
            
            table.add_row(
                provider_name,
                api_key
            )
        
        # Restore cursor position
        if table.row_count > 0:
            try:
                table.cursor_coordinate = (min(old_cursor_row, table.row_count - 1), 0)
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        if btn_id == "add-provider-btn":
            self.add_provider()
        elif btn_id == "edit-provider-btn":
            self.edit_provider()
        elif btn_id == "delete-provider-btn":
            self.delete_provider()
        elif btn_id == "close-provider-btn":
            self.dismiss()

    def add_provider(self) -> None:
        """Add new provider."""
        def handle_result(result):
            if result:
                # Добавляем провайдера в конфиг
                providers = config.get("supported_Providers") or {}
                providers[result["name"]] = {
                    "api_list": result["api_list"],
                    "api_url": result["api_url"],
                    "api_key": result["api_key"],
                    "filter": result.get("filter", None)
                }
                config.update_section("supported_Providers", providers)
                config.save()
                self.update_provider_table()
                self.notify(t("Provider '{name}' added", name=result['name']), severity="information")

        self.app.push_screen(
            ProviderEditDialog(title=t("Add Provider")),
            handle_result
        )

    def edit_provider(self) -> None:
        """Edit selected provider."""
        table = self.query_one("#provider-table", DataTable)

        if table.cursor_row < 0:
            self.notify(t("Select provider to edit"), severity="warning")
            return

        row = table.get_row_at(table.cursor_row)
        provider_name = str(row[0])
        
        providers = config.get("supported_Providers") or {}
        provider_config = providers.get(provider_name, {})

        def handle_result(result):
            if result:
                # Если API ключ не был изменен (пустой), оставляем старый
                api_key_to_save = result["api_key"] if result["api_key"] else provider_config.get("api_key", "")
                
                providers[provider_name] = {
                    "api_list": result["api_list"],
                    "api_url": result["api_url"],
                    "api_key": api_key_to_save,
                    "filter": result.get("filter", None)
                }
                config.update_section("supported_Providers", providers)
                config.save()
                self.update_provider_table()
                self.notify(t("Provider '{name}' updated", name=provider_name), severity="information")

        self.app.push_screen(
            ProviderEditDialog(
                title=t("Edit {name}", name=provider_name),
                name=provider_name,
                api_list=provider_config.get("api_list", ""),
                api_url=provider_config.get("api_url", ""),
                api_key=provider_config.get("api_key", ""),
                model_filter=provider_config.get("filter", "") or "",
                name_editable=False  # При редактировании имя не меняется
            ),
            handle_result
        )

    def delete_provider(self) -> None:
        """Delete selected provider."""
        table = self.query_one("#provider-table", DataTable)

        if table.cursor_row < 0:
            self.notify(t("Select provider to delete"), severity="warning")
            return

        row = table.get_row_at(table.cursor_row)
        provider_name = str(row[0])

        def handle_confirm(confirm):
            if confirm:
                providers = config.get("supported_Providers") or {}
                if provider_name in providers:
                    del providers[provider_name]
                    config.update_section("supported_Providers", providers)
                    config.save()
                    self.update_provider_table()
                    self.notify(t("Provider '{name}' deleted", name=provider_name), severity="information")

        self.app.push_screen(
            ConfirmDialog(
                t("Delete provider '{name}'?", name=provider_name),
                title=t("Confirmation")
            ),
            handle_confirm,
        )
