"""
Базовый абстрактный класс для LLM клиентов.

Определяет общий интерфейс и предоставляет служебные методы для всех реализаций.
"""

import threading
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager

from penguin_tamer.text_utils import format_api_key_display


@dataclass
class LLMConfig:
    """Complete LLM configuration including connection and generation parameters."""
    # Connection parameters
    api_key: str
    api_url: str
    model: str

    # Generation parameters
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    seed: Optional[int] = None


@dataclass
class AbstractLLMClient(ABC):
    """Abstract base class for LLM clients.
    
    Defines common interface and provides utility methods for all implementations.
    Concrete clients (OpenRouterClient, OpenAIClient, etc.) must implement abstract methods.
    """

    # Core parameters
    console: object
    system_message: List[Dict[str, str]]
    llm_config: LLMConfig

    # Internal state (not part of constructor)
    messages: List[Dict[str, str]] = field(init=False)
    _demo_manager: Optional[object] = field(default=None, init=False)
    
    # Token usage statistics
    total_prompt_tokens: int = field(default=0, init=False)
    total_completion_tokens: int = field(default=0, init=False)
    total_requests: int = field(default=0, init=False)
    
    # Rate limit information (if available from API)
    rate_limit_requests: Optional[int] = field(default=None, init=False)
    rate_limit_tokens: Optional[int] = field(default=None, init=False)
    rate_limit_remaining_requests: Optional[int] = field(default=None, init=False)
    rate_limit_remaining_tokens: Optional[int] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize internal state after dataclass construction."""
        self.messages = self.system_message.copy()

    # === Properties для доступа к LLM параметрам ===
    
    @property
    def api_key(self) -> str:
        return self.llm_config.api_key

    @property
    def api_url(self) -> str:
        return self.llm_config.api_url

    @property
    def model(self) -> str:
        return self.llm_config.model

    @property
    def temperature(self) -> float:
        return self.llm_config.temperature

    @property
    def max_tokens(self) -> Optional[int]:
        return self.llm_config.max_tokens

    @property
    def top_p(self) -> float:
        return self.llm_config.top_p

    @property
    def frequency_penalty(self) -> float:
        return self.llm_config.frequency_penalty

    @property
    def presence_penalty(self) -> float:
        return self.llm_config.presence_penalty

    @property
    def stop(self) -> Optional[List[str]]:
        return self.llm_config.stop

    @property
    def seed(self) -> Optional[int]:
        return self.llm_config.seed

    # === Служебные методы (общие для всех клиентов) ===

    def set_demo_manager(self, demo_manager):
        """Set demo manager for recording LLM chunks.

        Args:
            demo_manager: Demo manager instance
        """
        self._demo_manager = demo_manager

    def init_dialog_mode(self, educational_prompt: List[Dict[str, str]]) -> None:
        """Initialize dialog mode by adding educational prompt to messages.

        Should be called once at the start of dialog mode to teach the model
        to number code blocks automatically.

        Args:
            educational_prompt: Educational messages to add
        """
        self.messages.extend(educational_prompt)

    @classmethod
    def create(cls, console, api_key: str, api_url: str, model: str,
               system_message: List[Dict[str, str]], **llm_params):
        """Factory method for backward compatibility with old constructor signature."""
        llm_config = LLMConfig(
            api_key=api_key,
            api_url=api_url,
            model=model,
            **llm_params
        )
        return cls(
            console=console,
            system_message=system_message,
            llm_config=llm_config
        )

    def print_token_statistics(self) -> None:
        """Print token usage statistics for the entire session.
        
        Only prints if debug mode is enabled and there were any requests.
        """
        from penguin_tamer.config_manager import config
        
        debug_mode = config.get("global", "debug", False)
        
        if not debug_mode:
            return
            
        if self.total_requests == 0:
            self.console.print("\n[yellow]⚠️  No token usage data collected (API may not provide usage statistics)[/yellow]\n")
            return
            
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        
        self.console.print("\n[bold cyan]Token Usage Statistics:[/bold cyan]")
        self.console.print(f"[cyan]Total requests:[/cyan] {self.total_requests}")
        self.console.print(f"[cyan]Prompt tokens:[/cyan] {self.total_prompt_tokens:,}")
        self.console.print(f"[cyan]Completion tokens:[/cyan] {self.total_completion_tokens:,}")
        self.console.print(f"[bold cyan]Total tokens:[/bold cyan] {total_tokens:,}")
        
        # Show rate limits if available
        if self.rate_limit_requests or self.rate_limit_tokens:
            self.console.print(f"\n[bold cyan]API Rate Limits:[/bold cyan]")
            if self.rate_limit_requests:
                remaining = self.rate_limit_remaining_requests or "?"
                self.console.print(f"[cyan]Requests:[/cyan] {remaining}/{self.rate_limit_requests:,} remaining")
            if self.rate_limit_tokens:
                remaining = self.rate_limit_remaining_tokens or "?"
                self.console.print(f"[cyan]Tokens:[/cyan] {remaining:,}/{self.rate_limit_tokens:,} remaining")
        
        self.console.print()  # Empty line at the end

    def __str__(self) -> str:
        """Человекочитаемое представление клиента со всеми полями.

        Примечание: значение `api_key` маскируется (видны только последние 4 символа),
        а сложные объекты выводятся кратко.
        """
        items = {}
        for k, v in self.__dict__.items():
            if k == 'messages' or k == 'console' or k.startswith('_'):
                continue
            elif k == 'llm_config':
                # Создаем копию LLMConfig с замаскированным api_key
                config_dict = {
                    'api_key': format_api_key_display(v.api_key),
                    'api_url': v.api_url,
                    'model': v.model,
                    'temperature': v.temperature,
                    'max_tokens': v.max_tokens,
                    'top_p': v.top_p,
                    'frequency_penalty': v.frequency_penalty,
                    'presence_penalty': v.presence_penalty,
                    'stop': v.stop,
                    'seed': v.seed
                }
                config_repr = ', '.join(f'{key}={val!r}' for key, val in config_dict.items())
                items[k] = f"LLMConfig({config_repr})"
            else:
                try:
                    items[k] = v
                except Exception:
                    items[k] = f"<unrepr {type(v).__name__}>"

        parts = [f"{self.__class__.__name__}("]
        for key, val in items.items():
            parts.append(f"  {key}={val!r},")
        parts.append(")")
        return "\n".join(parts)

    def _spinner(self, stop_spinner: threading.Event, status_message: dict) -> None:
        """Визуальный индикатор работы ИИ с динамическим статусом.
        
        Общий метод для всех клиентов. Показывает анимированный спиннер
        с возможностью обновления текста сообщения.
        
        Args:
            stop_spinner: Event для остановки спиннера
            status_message: Словарь с ключом 'text' для динамического обновления сообщения
        """
        from penguin_tamer.i18n import t
        import time
        
        try:
            with self.console.status(
                "[dim]" + status_message.get('text', t('Ai thinking...')) + "[/dim]",
                spinner="dots",
                spinner_style="dim"
            ) as status:
                while not stop_spinner.is_set():
                    # Обновляем статус, если он изменился
                    current_text = status_message.get('text', t('Ai thinking...'))
                    status.update(f"[dim]{current_text}[/dim]")
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def _create_markdown(self, text: str, theme_name: str = "default"):
        """Создаёт Markdown объект с правильной темой для блоков кода.
        
        Общий метод для всех клиентов. Используется для рендеринга ответов LLM
        с подсветкой синтаксиса в терминале.
        
        Args:
            text: Текст в формате Markdown
            theme_name: Название темы для подсветки кода
        
        Returns:
            Rich Markdown объект с применённой темой
        """
        from rich.markdown import Markdown
        from penguin_tamer.themes import get_code_theme
        
        code_theme = get_code_theme(theme_name)
        return Markdown(text, code_theme=code_theme)

    @contextmanager
    def _managed_spinner(self, initial_message: str):
        """Context manager для управления спиннером.
        
        Args:
            initial_message: Начальное сообщение для отображения в спиннере
            
        Yields:
            dict: Словарь со статусным сообщением, которое можно обновлять
        """
        stop_spinner = threading.Event()
        status_message = {'text': initial_message}
        spinner_thread = threading.Thread(
            target=self._spinner,
            args=(stop_spinner, status_message),
            daemon=True
        )
        spinner_thread.start()

        try:
            yield status_message
        finally:
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)

    def _debug_print_if_enabled(self, phase: str) -> None:
        """Печать debug информации если режим отладки включён.

        Args:
            phase: 'request' или 'response'
        """
        from penguin_tamer.config_manager import config
        from penguin_tamer.debug import debug_print_messages
        
        if config.get("global", "debug", False):
            debug_print_messages(
                self.messages,
                client=self,
                phase=phase
            )

    @abstractmethod
    def _extract_rate_limits(self, stream) -> None:
        """Extract rate limit information from API response stream.
        
        Provider-specific method. Each client should implement its own logic
        based on the headers format used by its API provider.
        
        Args:
            stream: API response stream object
        """
        pass

    @abstractmethod
    def _create_stream(self, api_params: dict):
        """Create API stream object (provider-specific).
        
        Args:
            api_params: API parameters prepared by _prepare_api_params()
            
        Returns:
            Stream object from provider SDK
        """
        pass

    @abstractmethod
    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Extract text content from stream chunk (provider-specific).
        
        Args:
            chunk: Stream chunk from API
            
        Returns:
            Text content or None if chunk has no content
        """
        pass

    @abstractmethod
    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Extract usage statistics from chunk (provider-specific).
        
        Args:
            chunk: Stream chunk from API
            
        Returns:
            Dict with 'prompt_tokens' and 'completion_tokens', or None
        """
        pass

    # === Абстрактные методы (должны быть реализованы в подклассах) ===

    @abstractmethod
    def ask_stream(self, user_input: str) -> str:
        """Send streaming request to LLM and return response.
        
        Args:
            user_input: User's message text
            
        Returns:
            Complete AI response text
            
        Raises:
            KeyboardInterrupt: When interrupted by user
        """
        pass

    @staticmethod
    @abstractmethod
    def fetch_models(api_list_url: str, api_key: str = "", model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """Fetch list of available models from provider API.
        
        Static method that can be used without creating client instance.
        
        Args:
            api_list_url: URL endpoint to fetch models list
            api_key: API key for authentication (optional)
            model_filter: Filter string to match against model id/name (optional)
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Name"}, ...]
            Returns empty list on error.
        """
        pass

    @abstractmethod
    def get_available_models(self, model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """Get list of available models for current client configuration.
        
        Instance method that uses client's api_url and api_key.
        
        Args:
            model_filter: Optional filter string
        
        Returns:
            List of model dictionaries
        """
        pass
