import threading
from typing import List, Dict
from openai import OpenAI
from openai import RateLimitError, APIError, OpenAIError, AuthenticationError
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
import time




class OpenRouterClient:

    def _spinner(self, stop_spinner: threading.Event) -> None:
        """Визуальный индикатор работы ИИ с точечным спиннером.
        Пока stop_event не установлен, показывает "Аи печатает...".
        """
        console = Console()
        with console.status("[dim]Ai думает...[/dim]", spinner="dots", spinner_style="dim"):
            while not stop_spinner.is_set():
                time.sleep(0.1)

    def __init__(self, console: Console, api_key: str, api_url: str, model: str,
                 system_context: str = "You are a helpful assistant.",
                 temperature: float = 0.7):
        self.console = console
        self.client = OpenAI(api_key=api_key, base_url=api_url)
        self.model = model
        self.temperature = temperature
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_context}
        ]

    def ask(self, user_input: str) -> str:
        """Обычный (не потоковый) режим с сохранением контекста"""
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

            # токены
            usage = response.usage
            if usage:
                print(f"[TOKENS] input={usage.prompt_tokens}, "
                      f"output={usage.completion_tokens}, "
                      f"total={usage.total_tokens}")
            return reply

        except Exception as e:
            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()
            return self._handle_api_error(e)

    def ask_stream(self, user_input: str) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени"""
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

            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()

            # Используем Live для динамического обновления отображения с Markdown
            with Live(console=self.console, refresh_per_second=20, auto_refresh=True) as live:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        reply_parts.append(text)
                        # Объединяем все части и обрабатываем как Markdown
                        full_text = "".join(reply_parts)
                        markdown = Markdown(full_text)
                        live.update(markdown)
                        time.sleep(0.01)  # Небольшая задержка для плавности обновления
            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except Exception as e:
            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()
            return self._handle_api_error(e)

    def _handle_api_error(self, error: Exception) -> str:
        """Обработка ошибок API с соответствующим выводом сообщений"""
        if isinstance(error, RateLimitError):
            self.console.print("[dim]Ошибка 403: Доступ запрещён\nВозможные причины:\n-Превышен лимит запросов (попробуйте через некоторое время)\n-Не поддерживается ваш регион (используйте VPN)[/dim]")
        elif isinstance(error, AuthenticationError):
            self.console.print("[dim]Ошибка 401: Отказ в авторизации.Проверьте свой ключ API_KEY. Для получения ключа обратитесь к поставщику API. [link=https://github.com/Vivatist/ai-bash]Как получить ключ?[/link][/dim]")
        elif isinstance(error, APIError):
            self.console.print(f"[red]Ошибка API: {error}[/red]")
        elif isinstance(error, OpenAIError):
            self.console.print(f"[red]Ошибка клиента OpenAI: {error}[/red]")
        else:
            self.console.print(f"[red]Неизвестная ошибка: {error}[/red]")

        return "Ошибка при получении ответа."
