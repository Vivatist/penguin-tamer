import threading
from typing import List, Dict
import time
from aiebash.formatter_text import format_api_key_display
from aiebash.i18n import t
from aiebash.logger import log_execution_time
from aiebash.config_manager import config

# Ленивый импорт Rich
_console = None
_markdown = None
_live = None

def _get_console():
    global _console
    if _console is None:
        from rich.console import Console
        _console = Console()
    return _console

def _get_markdown():
    global _markdown
    if _markdown is None:
        from rich.markdown import Markdown
        _markdown = Markdown
    return _markdown

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

    def _spinner(self, stop_spinner: threading.Event) -> None:
        """Визуальный индикатор работы ИИ с точечным спиннером.
        Пока stop_event не установлен, показывает "Аи печатает...".
        """
        console = _get_console()
        with console.status("[dim]" + t('Ai thinking...') + "[/dim]", spinner="dots", spinner_style="dim"):
            while not stop_spinner.is_set():
                time.sleep(0.1)
        # console.print("[green]Ai: [/green]")

    @log_execution_time
    def __init__(self, console, logger, api_key: str, api_url: str, model: str,
                 system_content: str,
                 temperature: float = 0.7):
        self.console = console
        self.logger = logger
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]
        self._client = None  # Ленивая инициализация

    @property
    def client(self):
        """Ленивая инициализация OpenAI клиента"""
        if self._client is None:
            self._client = _get_openai_client()(api_key=self.api_key, base_url=self.api_url)
        return self._client

    @log_execution_time
    def ask(self, user_input: str, educational_content: list = None) -> str:
        """Обычный (не потоковый) режим с сохранением контекста"""
        if educational_content is None:
            educational_content = []
        self.messages.extend(educational_content)
        self.messages.append({"role": "user", "content": user_input})

        # Показ спиннера в отдельном потоке
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
        spinner_thread.start()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature
            )

            reply = response.choices[0].message.content

            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()


            self.messages.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()
            raise


    @log_execution_time
    def ask_stream(self, user_input: str, educational_content: list = None) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени"""
        if educational_content is None:
            educational_content = []
        self.messages.extend(educational_content)
        self.messages.append({"role": "user", "content": user_input})
        reply_parts = []
        # Показ спиннера в отдельном потоке
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
        spinner_thread.start()
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                stream=True
            )

            # Ждем первый чанк с контентом перед запуском Live
            first_content_chunk = None
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    first_content_chunk = chunk.choices[0].delta.content
                    reply_parts.append(first_content_chunk)
                    break
            
            # Останавливаем спиннер после получения первого чанка
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join()

            sleep_time = config.get("global", "sleep_time", 0.01)
            refresh_per_second = config.get("global", "refresh_per_second", 10)
            # Используем Live для динамического обновления отображения с Markdown
            with _get_live()(console=self.console, refresh_per_second=refresh_per_second, auto_refresh=True) as live:
                # Показываем первый чанк
                if first_content_chunk:
                    markdown = _get_markdown()(first_content_chunk)
                    live.update(markdown)
                
                # Продолжаем обрабатывать остальные чанки
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        reply_parts.append(text)
                        # Объединяем все части и обрабатываем как Markdown
                        full_text = "".join(reply_parts)
                        markdown = _get_markdown()(full_text)
                        live.update(markdown)
                        time.sleep(sleep_time)  # Небольшая задержка для плавности обновления
            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except Exception as e:
            # Останавливаем спиннер в случае ошибки
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join()
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
            elif k == 'messages' or k == 'console' or k == '_client' or k == 'logger':
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
