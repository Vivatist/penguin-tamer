"""
Modal dialogs for the configuration menu.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, Select, LoadingIndicator
from textual import work

from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.menu.locales.menu_i18n import t
from penguin_tamer.config_manager import config


class LLMEditDialog(ModalScreen):
    """Modal dialog for adding or editing LLM with provider support."""

    def __init__(
        self,
        title: str = "Добавление LLM",
        provider: str = "",
        model: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title_text = title
        self.default_provider = provider
        self.default_model = model
        self.result = None
        self.available_models = []  # Список моделей от провайдера
        self.loading_models = False

    def compose(self) -> ComposeResult:
        # Получаем список провайдеров для Select
        providers = config.get("supported_Providers") or {}
        provider_options = [(t("Select provider..."), "")]
        provider_options.extend([(name, name) for name in providers.keys()])
        
        yield Container(
            Static(self.title_text, classes="llm-dialog-title"),
            Container(
                # Provider Select
                Static(t("Provider:"), classes="llm-field-label"),
                Container(
                    Select(
                        provider_options,
                        value=self.default_provider if self.default_provider else "",
                        id="provider-select",
                        allow_blank=False,
                    ),
                    LoadingIndicator(id="models-loading", classes="hidden"),
                    classes="provider-select-container"
                ),
                
                # Model Select (динамически заполняется)
                Static(t("Model:"), classes="llm-field-label"),
                Select(
                    [(t("Select provider first..."), "")],
                    value="",
                    id="model-select",
                    allow_blank=False,
                    disabled=True
                ),
                classes="llm-fields-container"
            ),
            Horizontal(
                Button(t("Save"), variant="success", id="save-btn"),
                Button(t("Cancel"), variant="success", id="cancel-btn"),
                classes="llm-dialog-buttons",
            ),
            classes="llm-dialog-container",
        )

    def on_mount(self) -> None:
        """Set focus when dialog opens."""
        provider_select = self.query_one("#provider-select", Select)
        provider_select.focus()
        
        # Если задан провайдер по умолчанию, загружаем его модели
        if self.default_provider:
            self.load_provider_data(self.default_provider)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "provider-select" and event.value:
            # Провайдер выбран - загружаем модели
            self.load_provider_data(str(event.value))
        elif event.select.id == "model-select" and event.value:
            # Модель выбрана - ничего не делаем, просто запоминаем
            pass

    def load_provider_data(self, provider_name: str) -> None:
        """Загружает данные провайдера и запускает загрузку моделей."""
        providers = config.get("supported_Providers") or {}
        provider_config = providers.get(provider_name, {})
        
    def load_provider_data(self, provider_name: str) -> None:
        """Загружает данные провайдера и запускает загрузку моделей."""
        providers = config.get("supported_Providers") or {}
        provider_config = providers.get(provider_name, {})
        
        if not provider_config:
            return
        
        # Запускаем загрузку моделей
        api_list_url = provider_config.get("api_list", "")
        api_key = provider_config.get("api_key", "")
        if api_list_url:
            self.fetch_models(api_list_url, api_key)

    @work(exclusive=True, thread=True)
    def fetch_models(self, api_list_url: str, api_key: str) -> None:
        """Загружает список моделей от провайдера (в отдельном потоке)."""
        from penguin_tamer.menu.provider_utils import fetch_models_from_provider, format_model_for_select
        
        # Показываем индикатор загрузки
        self.loading_models = True
        self.app.call_from_thread(self.show_loading, True)
        
        # Запрашиваем модели
        models = fetch_models_from_provider(api_list_url, api_key)
        self.available_models = models
        
        # Скрываем индикатор загрузки и обновляем список
        self.loading_models = False
        self.app.call_from_thread(self.show_loading, False)
        self.app.call_from_thread(self.update_model_select, models)

    def show_loading(self, show: bool) -> None:
        """Показывает/скрывает индикатор загрузки."""
        try:
            loading = self.query_one("#models-loading", LoadingIndicator)
            if show:
                loading.remove_class("hidden")
            else:
                loading.add_class("hidden")
        except Exception:
            pass

    def update_model_select(self, models: list) -> None:
        """Обновляет список моделей в Select."""
        from penguin_tamer.menu.provider_utils import format_model_for_select
        
        try:
            model_select = self.query_one("#model-select", Select)
            
            if not models:
                # Нет моделей - показываем сообщение
                model_select.set_options([(t("No models available"), "")])
                model_select.disabled = True
                self.notify(
                    t("Failed to load models from provider"),
                    severity="warning",
                    timeout=3
                )
            else:
                # Форматируем модели для Select
                options = [format_model_for_select(model) for model in models]
                model_select.set_options(options)
                model_select.disabled = False
                
                # Если есть default_model, пытаемся его выбрать
                if self.default_model:
                    for option_text, option_value in options:
                        if option_value == self.default_model:
                            model_select.value = option_value
                            break
                
                self.notify(
                    t("Loaded {count} models", count=len(models)),
                    severity="information",
                    timeout=2
                )
        except Exception as e:
            self.notify(
                t("Error updating model list: {error}", error=str(e)),
                severity="error"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            provider_select = self.query_one("#provider-select", Select)
            model_select = self.query_one("#model-select", Select)

            provider = str(provider_select.value) if provider_select.value else ""
            model = str(model_select.value) if model_select.value else ""

            # Validation
            if not provider:
                self.notify(t("Provider is required"), severity="error")
                provider_select.focus()
                return
            if not model:
                self.notify(t("Model is required"), severity="error")
                model_select.focus()
                return

            self.result = {
                "provider": provider,
                "model": model
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
                Button(t("Yes"), variant="error", id="confirm-yes-btn"),
                Button(t("Cancel"), variant="success", id="confirm-no-btn"),
                classes="input-dialog-buttons",
            ),
            classes="input-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes-btn":
            self.result = True
        self.dismiss(self.result)


class ApiKeyMissingDialog(ModalScreen):
    """Dialog to inform user about missing API key."""

    def __init__(self, t_func) -> None:
        """Initialize dialog with translation function.

        Args:
            t_func: Translation function from menu_i18n
        """
        super().__init__()
        self.t = t_func

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Static("🐧", classes="api-key-dialog-icon"),
                Static(
                    self.t("API Key Required"),
                    classes="api-key-dialog-title"
                ),
                Static(
                    self.t(
                        "You have entered `Penguin Tamer` configuration "
                        "because the default LLM does not have an `API_KEY`. "
                        "To continue working, select any LLM and add the key by clicking the `Settings` button."
                    ),
                    classes="api-key-dialog-message"
                ),
                classes="api-key-dialog-content"
            ),
            Container(
                Button(
                    self.t("OK"),
                    variant="success",
                    id="api-key-ok-btn"
                ),
                classes="api-key-dialog-button-container"
            ),
            classes="api-key-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle OK button press."""
        if event.button.id == "api-key-ok-btn":
            self.dismiss(True)


class ProviderEditDialog(ModalScreen):
    """Modal dialog for adding or editing Provider."""

    def __init__(
        self,
        title: str = "Добавление провайдера",
        name: str = "",
        api_list: str = "",
        api_url: str = "",
        api_key: str = "",
        name_editable: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title_text = title
        self.default_name = name
        self.default_api_list = api_list
        self.default_api_url = api_url
        self.default_api_key = api_key
        self.name_editable = name_editable
        self.result = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="llm-dialog-title"),
            Container(
                Static(t("Provider Name:"), classes="llm-field-label"),
                Input(
                    value=self.default_name,
                    id="provider-name-input",
                    disabled=not self.name_editable,
                    placeholder=t("For example: OpenRouter, OpenAI")
                ),
                Static(t("API List URL:"), classes="llm-field-label"),
                Input(
                    value=self.default_api_list,
                    id="provider-api-list-input",
                    placeholder=t("For example: https://openrouter.ai/api/v1/models")
                ),
                Static(t("API_URL:"), classes="llm-field-label"),
                Input(
                    value=self.default_api_url,
                    id="provider-url-input",
                    placeholder=t("For example: https://openrouter.ai/api/v1")
                ),
                Static(t("API_KEY:"), classes="llm-field-label"),
                Input(
                    value="",  # Оставляем пустым при редактировании
                    id="provider-key-input",
                    placeholder=(
                        t("Current: {apikey}", apikey=format_api_key_display(self.default_api_key))
                        if self.default_api_key
                        else t("Optional: Provider-level API key")
                    )
                ),
                classes="llm-fields-container"
            ),
            Horizontal(
                Button(t("Save"), variant="success", id="save-btn"),
                Button(t("Cancel"), variant="success", id="cancel-btn"),
                classes="llm-dialog-buttons",
            ),
            classes="llm-dialog-container",
        )

    def on_mount(self) -> None:
        """Set focus to first input when dialog opens."""
        if self.name_editable:
            name_input = self.query_one("#provider-name-input", Input)
            name_input.focus()
        else:
            api_list_input = self.query_one("#provider-api-list-input", Input)
            api_list_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            name_input = self.query_one("#provider-name-input", Input)
            api_list_input = self.query_one("#provider-api-list-input", Input)
            url_input = self.query_one("#provider-url-input", Input)
            key_input = self.query_one("#provider-key-input", Input)

            name = name_input.value.strip()
            api_list = api_list_input.value.strip()
            api_url = url_input.value.strip()
            api_key = key_input.value.strip()

            # Validation
            if not name:
                self.notify(t("Provider name is required"), severity="error")
                name_input.focus()
                return
            if not api_list:
                self.notify(t("API List URL is required"), severity="error")
                api_list_input.focus()
                return
            if not api_url:
                self.notify(t("API URL is required"), severity="error")
                url_input.focus()
                return

            self.result = {
                "name": name,
                "api_list": api_list,
                "api_url": api_url,
                "api_key": api_key
            }
        self.dismiss(self.result)
