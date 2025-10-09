"""
Modal dialogs for the configuration menu.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from penguin_tamer.text_utils import format_api_key_display


class LLMEditDialog(ModalScreen):
    """Modal dialog for adding or editing LLM with all fields in one screen."""

    def __init__(
        self,
        title: str = "Добавление LLM",
        name: str = "",
        model: str = "",
        api_url: str = "",
        api_key: str = "",
        name_editable: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title_text = title
        self.default_name = name
        self.default_model = model
        self.default_api_url = api_url
        self.default_api_key = api_key
        self.name_editable = name_editable
        self.result = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="llm-dialog-title"),
            Container(
                Static("Название LLM:", classes="llm-field-label"),
                Input(
                    value=self.default_name,
                    id="llm-name-input",
                    disabled=not self.name_editable,
                    placeholder="Любое, например: GPT-4, Claude, Gemini"
                ),
                Static("Модель:", classes="llm-field-label"),
                Input(
                    value=self.default_model,
                    id="llm-model-input",
                    placeholder="Например: gpt-4-turbo-preview"
                ),
                Static("API URL:", classes="llm-field-label"),
                Input(
                    value=self.default_api_url,
                    id="llm-url-input",
                    placeholder="Например: https://api.openai.com/v1"
                ),
                Static("API ключ (необязательно):", classes="llm-field-label"),
                Input(
                    value="",  # Оставляем пустым при редактировании
                    id="llm-key-input",
                    placeholder=(
                        f"Текущий: {format_api_key_display(self.default_api_key)}"
                        if self.default_api_key
                        else "Оставьте пустым, если не требуется"
                    )
                ),
                classes="llm-fields-container"
            ),
            Horizontal(
                Button("Сохранить", variant="success", id="save-btn"),
                Button("Отмена", variant="success", id="cancel-btn"),
                classes="llm-dialog-buttons",
            ),
            classes="llm-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            name_input = self.query_one("#llm-name-input", Input)
            model_input = self.query_one("#llm-model-input", Input)
            url_input = self.query_one("#llm-url-input", Input)
            key_input = self.query_one("#llm-key-input", Input)

            name = name_input.value.strip()
            model = model_input.value.strip()
            api_url = url_input.value.strip()
            api_key = key_input.value.strip()

            # Validation
            if not name:
                self.notify("Название LLM обязательно", severity="error")
                name_input.focus()
                return
            if not model:
                self.notify("Модель обязательна", severity="error")
                model_input.focus()
                return
            if not api_url:
                self.notify("API URL обязателен", severity="error")
                url_input.focus()
                return

            self.result = {
                "name": name,
                "model": model,
                "api_url": api_url,
                "api_key": api_key
            }
        self.dismiss(self.result)


class ConfirmDialog(ModalScreen):
    """Диалог подтверждения действия."""

    def __init__(self, message: str, title: str = "Подтверждение") -> None:
        super().__init__()
        self.message = message
        self.title = title
        self.result = False

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, classes="input-dialog-title"),
            Static(self.message, classes="input-dialog-prompt"),
            Horizontal(
                Button("Да", variant="error", id="confirm-yes-btn"),
                Button("Отмена", variant="success", id="confirm-no-btn"),
                classes="input-dialog-buttons",
            ),
            classes="input-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes-btn":
            self.result = True
        self.dismiss(self.result)
