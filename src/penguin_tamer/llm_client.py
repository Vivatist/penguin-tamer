import threading
from typing import List, Dict
import time
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t
from penguin_tamer.config_manager import config
from penguin_tamer.themes import get_code_theme

# Ленивый импорт Rich
_markdown = None
_live = None
_console = None
_panel = None
_syntax = None
_text = None


def _get_console():
    """Ленивый импорт Console для отладки"""
    global _console
    if _console is None:
        from rich.console import Console
        _console = Console
    return _console


def _get_panel():
    """Ленивый импорт Panel для отладки"""
    global _panel
    if _panel is None:
        from rich.panel import Panel
        _panel = Panel
    return _panel


def _get_syntax():
    """Ленивый импорт Syntax для отладки"""
    global _syntax
    if _syntax is None:
        from rich.syntax import Syntax
        _syntax = Syntax
    return _syntax


def _get_text():
    """Ленивый импорт Text для отладки"""
    global _text
    if _text is None:
        from rich.text import Text
        _text = Text
    return _text


def debug_print_messages(messages: List[Dict[str, str]], 
                        model: str = None, 
                        temperature: float = None,
                        max_tokens: int = None,
                        top_p: float = None,
                        frequency_penalty: float = None,
                        presence_penalty: float = None,
                        stop: list = None,
                        seed: int = None) -> None:
    """
    Выводит структуру сообщений для LLM в удобном читаемом формате.
    
    Полезно для отладки: показывает все сообщения, отправляемые в API,
    с подсветкой ролей и красивым форматированием контента.
    
    Args:
        messages: Список сообщений в формате OpenAI (role, content)
        model: Название модели
        temperature: Значение temperature (0.0-2.0)
        max_tokens: Максимум токенов в ответе
        top_p: Nucleus sampling (0.0-1.0)
        frequency_penalty: Штраф за повторы (-2.0 до 2.0)
        presence_penalty: Штраф за упоминание (-2.0 до 2.0)
        stop: Стоп-последовательности
        seed: Seed для детерминизма
    
    Example:
        >>> debug_print_messages(
        ...     [{"role": "system", "content": "You are a helper"},
        ...      {"role": "user", "content": "Hello!"}],
        ...     model="gpt-4",
        ...     temperature=0.7,
        ...     max_tokens=2000
        ... )
    """
    Console = _get_console()
    Panel = _get_panel()
    Text = _get_text()
    
    console = Console()
    
    # Заголовок с основными параметрами
    title_parts = ["🔍 LLM Request Debug"]
    if model:
        title_parts.append(f"Model: {model}")
    
    title = " | ".join(title_parts)
    
    console.print("\n" + "=" * 80)
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print("=" * 80 + "\n")
    
    # Панель с параметрами генерации
    params_lines = []
    if temperature is not None:
        params_lines.append(f"🌡️  Temperature: [bold yellow]{temperature}[/bold yellow]")
    if max_tokens is not None:
        params_lines.append(f"📏 Max Tokens: [bold cyan]{max_tokens}[/bold cyan]")
    if top_p is not None and top_p != 1.0:
        params_lines.append(f"🎯 Top P: [bold green]{top_p}[/bold green]")
    if frequency_penalty is not None and frequency_penalty != 0.0:
        params_lines.append(f"🔁 Frequency Penalty: [bold magenta]{frequency_penalty}[/bold magenta]")
    if presence_penalty is not None and presence_penalty != 0.0:
        params_lines.append(f"💭 Presence Penalty: [bold blue]{presence_penalty}[/bold blue]")
    if stop is not None:
        stop_str = str(stop) if len(str(stop)) < 50 else str(stop)[:47] + "..."
        params_lines.append(f"🛑 Stop: [dim]{stop_str}[/dim]")
    if seed is not None:
        params_lines.append(f"🌱 Seed: [bold white]{seed}[/bold white]")
    
    if params_lines:
        params_panel = Panel(
            "\n".join(params_lines),
            title="[bold]Generation Parameters[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(params_panel)
        console.print()
    
    # Роли с цветами
    role_colors = {
        "system": "bold magenta",
        "user": "bold green",
        "assistant": "bold blue"
    }
    
    role_icons = {
        "system": "⚙️",
        "user": "👤",
        "assistant": "🤖"
    }
    
    # Выводим каждое сообщение
    for idx, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        role_color = role_colors.get(role, "white")
        role_icon = role_icons.get(role, "❓")
        
        # Заголовок сообщения
        header = Text()
        header.append(f"{role_icon} ", style="bold")
        header.append(f"Message #{idx}: ", style="dim")
        header.append(f"{role.upper()}", style=role_color)
        
        # Ограничиваем длину контента для читаемости
        if len(content) > 500:
            display_content = content[:500] + f"\n\n[dim]... (truncated, total {len(content)} chars)[/dim]"
        else:
            display_content = content
        
        # Создаём панель с сообщением
        panel = Panel(
            display_content,
            title=header,
            title_align="left",
            border_style=role_color,
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()  # Пустая строка между сообщениями
    
    # Итоговая статистика
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    console.print(f"[dim]Total messages: {len(messages)} | Total characters: {total_chars}[/dim]")
    console.print("=" * 80 + "\n")


def _get_markdown():
    global _markdown
    if _markdown is None:
        from rich.markdown import Markdown
        _markdown = Markdown
    return _markdown


def _create_markdown(text: str, theme_name: str = "default"):
    """
    Создаёт Markdown объект с правильной темой для блоков кода.
    
    Args:
        text: Текст в формате Markdown
        theme_name: Название темы
    
    Returns:
        Markdown объект с применённой темой
    """
    Markdown = _get_markdown()
    code_theme = get_code_theme(theme_name)
    return Markdown(text, code_theme=code_theme)

def _get_live():
    global _live
    if _live is None:
        from rich.live import Live
        _live = Live
    return _live

# Ленивый импорт OpenAI (самый тяжелый модуль)
_openai_client = None


def _get_openai_client():
    """Ленивый импорт OpenAI клиента"""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI
    return _openai_client


class OpenRouterClient:

    def _spinner(self, stop_spinner: threading.Event, status_message: dict) -> None:
        """Визуальный индикатор работы ИИ с динамическим статусом.
        status_message - словарь с ключом 'text' для обновления сообщения.
        """
        try:
            with self.console.status("[dim]" + status_message.get('text', t('Ai thinking...')) + "[/dim]", spinner="dots", spinner_style="dim") as status:
                while not stop_spinner.is_set():
                    # Обновляем статус, если он изменился
                    current_text = status_message.get('text', t('Ai thinking...'))
                    status.update(f"[dim]{current_text}[/dim]")
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def __init__(self, console, api_key: str, api_url: str, model: str,
                 system_message: dict[str, str],
                 temperature: float = 0.7,
                 max_tokens: int = None,
                 top_p: float = 0.95,
                 frequency_penalty: float = 0.0,
                 presence_penalty: float = 0.0,
                 stop: list = None,
                 seed: int = None):
        self.console = console
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.seed = seed
        self.messages: List[Dict[str, str]] = [system_message]
        self._client = None  # Ленивая инициализация

    @property
    def client(self):
        """Ленивая инициализация OpenAI клиента"""
        if self._client is None:
            self._client = _get_openai_client()(api_key=self.api_key, base_url=self.api_url)
        return self._client


    def ask_stream(self, user_input: str, educational_prompt: list = []) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени"""
        # Показ спиннера в отдельном потоке с динамическим статусом
        stop_spinner = threading.Event()
        status_message = {'text': t('Sending request...')}
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner, status_message), daemon=True)
        spinner_thread.start()

        self.messages.extend(educational_prompt)
        self.messages.append({"role": "user", "content": user_input})
        reply_parts = []

        # Debug mode: показываем структуру запроса
        import os
        if os.getenv("PT_DEBUG") == "1" or config.get("global", "debug_mode", False):
            stop_spinner.set()  # Останавливаем спиннер для чистого вывода
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.1)
            debug_print_messages(
                self.messages, 
                model=self.model, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=self.stop,
                seed=self.seed
            )
            # Перезапускаем спиннер
            stop_spinner.clear()
            spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner, status_message), daemon=True)
            spinner_thread.start()
        
        # Флаг прерывания для потока
        interrupted = threading.Event()
        
        try:
            # Фаза 1: Отправка запроса
            # Подготавливаем параметры API
            api_params = {
                "model": self.model,
                "messages": self.messages,
                "temperature": self.temperature,
                "stream": True
            }
            
            # Добавляем опциональные параметры только если они заданы
            if self.max_tokens is not None:
                api_params["max_tokens"] = self.max_tokens
            if self.top_p is not None and self.top_p != 1.0:
                api_params["top_p"] = self.top_p
            if self.frequency_penalty != 0.0:
                api_params["frequency_penalty"] = self.frequency_penalty
            if self.presence_penalty != 0.0:
                api_params["presence_penalty"] = self.presence_penalty
            if self.stop is not None:
                api_params["stop"] = self.stop
            if self.seed is not None:
                api_params["seed"] = self.seed
            
            stream = self.client.chat.completions.create(**api_params)

            # Фаза 2: Ожидание ответа от модели
            status_message['text'] = t('Ai thinking...')
            
            # Ждем первый чанк с контентом перед запуском Live
            first_content_chunk = None
            for chunk in stream:
                if interrupted.is_set():
                    raise KeyboardInterrupt("Stream interrupted")
                if chunk.choices[0].delta.content:
                    first_content_chunk = chunk.choices[0].delta.content
                    reply_parts.append(first_content_chunk)
                    break
            
            # Останавливаем спиннер после получения первого чанка
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.1)

            sleep_time = config.get("global", "sleep_time", 0.01)
            refresh_per_second = config.get("global", "refresh_per_second", 10)
            theme_name = config.get("global", "markdown_theme", "default")
            
            # Используем Live для динамического обновления отображения с Markdown
            with _get_live()(console=self.console, refresh_per_second=refresh_per_second, auto_refresh=True) as live:
                # Показываем первый чанк
                if first_content_chunk:
                    markdown = _create_markdown(first_content_chunk, theme_name)
                    live.update(markdown)
                
                # Продолжаем обрабатывать остальные чанки
                for chunk in stream:
                    if interrupted.is_set():
                        raise KeyboardInterrupt("Stream interrupted")
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        reply_parts.append(text)
                        # Объединяем все части и обрабатываем как Markdown
                        full_text = "".join(reply_parts)
                        markdown = _create_markdown(full_text, theme_name)
                        live.update(markdown)
                        time.sleep(sleep_time)  # Небольшая задержка для плавности обновления
            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except KeyboardInterrupt:
            # Устанавливаем флаг прерывания
            interrupted.set()
            # Останавливаем спиннер
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)
            raise
        except Exception as e:
            # Останавливаем спиннер в случае ошибки
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)
            raise
  


    def __str__(self) -> str:
        """Человекочитаемое представление клиента со всеми полями.

        Примечание: значение `api_key` маскируется (видны только последние 4 символа),
        а сложные объекты выводятся кратко.
        """

        items = {}
        for k, v in self.__dict__.items():
            if k == 'api_key':
                items[k] = format_api_key_display(v)
            elif k == 'messages' or k == 'console' or k == '_client':
                continue
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
