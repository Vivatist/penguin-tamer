# openai_client.py
import json, requests
from typing import List

from .llm_interface import LLMClient
from rich.prompt import Prompt
from rich.console import Console
from aiebash.logger import logger

try:
    from .formatter_text import _format_api_key_display
except ImportError:
    # Для случаев, когда модуль запускается напрямую
    from formatter_text import _format_api_key_display


class DefaultClient(LLMClient):
    def __init__(self, model: str, api_url: str, api_key: str = None, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.model = model
        self.api_url = api_url
        self.api_key = api_key

    def configure_llm(self, console: Console) -> dict:

        console.print("\n[bold]Настройка OpenAI через прокси:[/bold]")

        # Текущие значения
        current_model = getattr(self, 'model', 'gpt-4o-mini')
        current_api_key = getattr(self, 'api_key', '')

        # Настройка модели
        new_model = Prompt.ask("Модель", default=current_model)
        if not new_model.strip():
            new_model = current_model

        # Настройка API ключа
        new_api_key = Prompt.ask("API Key", default=current_api_key)

        # Возвращаем обновленные настройки
        return {
            "model": new_model,
            "api_key": new_api_key,
            "api_url": self.api_url  # URL остается фиксированным
        }

    def _send_chat(self, messages: List[dict]) -> str:

        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:

            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)

            status_code = resp.status_code

            resp.raise_for_status()
            data = resp.json()

            if "usage" in data:
                usage = data["usage"]

            if "choices" in data and data["choices"]:
                answer = data["choices"][0]["message"]["content"]
                return answer

            raise RuntimeError("Unexpected API response format")

        except Exception as e:
            raise

