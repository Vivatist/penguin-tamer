from typing import List, Dict
from openai import OpenAI
from openai import RateLimitError, APIError, OpenAIError, AuthenticationError
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
import time

from aiebash.formatter_text import annotate_code_blocks



class OpenRouterChat:
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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature
            )

            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})

            # токены
            usage = response.usage
            if usage:
                print(f"[TOKENS] input={usage.prompt_tokens}, "
                      f"output={usage.completion_tokens}, "
                      f"total={usage.total_tokens}")
            reply, code_blocks = annotate_code_blocks(reply)
            return reply, code_blocks

        except Exception as e:
            return self._handle_api_error(e)

    def ask_stream(self, user_input: str) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени"""
        self.messages.append({"role": "user", "content": user_input})

        reply_parts = []
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                stream=True
            )

            # Используем Live для динамического обновления отображения с Markdown
            with Live(console=self.console, refresh_per_second=20, auto_refresh=True) as live:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        reply_parts.append(text)
                        # print(text)
                        # Объединяем все части и обрабатываем как Markdown
                        full_text = "".join(reply_parts)
                        markdown = Markdown(full_text)
                        live.update(markdown)

            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
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
