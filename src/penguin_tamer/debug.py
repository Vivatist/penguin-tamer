"""Debug utilities for LLM request visualization."""

import json
from typing import List, Dict
from penguin_tamer.utils.lazy_import import lazy_import


# Ленивые импорты Rich через декоратор
@lazy_import
def get_console():
    """Ленивый импорт Console для отладки"""
    from rich.console import Console
    return Console


@lazy_import
def get_panel():
    """Ленивый импорт Panel для отладки"""
    from rich.panel import Panel
    return Panel


@lazy_import
def get_syntax():
    """Ленивый импорт Syntax для отладки"""
    from rich.syntax import Syntax
    return Syntax


def debug_print_messages(
    messages: List[Dict[str, str]],
    client=None,
    phase: str = "request"
) -> None:
    """
    Выводит полную JSON структуру API запроса в режиме отладки.

    Показывает чистый JSON с подсветкой синтаксиса без рамок и панелей.

    Args:
        messages: Список сообщений в формате OpenAI (role, content)
        client: Объект OpenRouterClient с конфигурацией LLM
        phase: Фаза отладки ("request" или "response")

    Example:
        >>> debug_print_messages(
        ...     [{"role": "system", "content": "You are a helper"},
        ...      {"role": "user", "content": "Hello!"}],
        ...     client=openrouter_client,
        ...     phase="request"
        ... )
    """
    Console = get_console()
    Syntax = get_syntax()

    console = Console()

    # Извлекаем параметры из клиента
    if client:
        model = client.model
        temperature = client.temperature
        max_tokens = client.max_tokens
        top_p = client.top_p
        frequency_penalty = client.frequency_penalty
        presence_penalty = client.presence_penalty
        stop = client.stop
        seed = client.seed
    else:
        # Fallback значения если клиент не передан
        model = None
        temperature = None
        max_tokens = None
        top_p = None
        frequency_penalty = None
        presence_penalty = None
        stop = None
        seed = None

    # Создаём полную структуру API запроса
    api_request = {
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True}
    }

    # Добавляем параметры генерации
    api_request["temperature"] = temperature
    if max_tokens is not None:
        api_request["max_tokens"] = max_tokens
    if top_p is not None:
        api_request["top_p"] = top_p
    if frequency_penalty is not None:
        api_request["frequency_penalty"] = frequency_penalty
    if presence_penalty is not None:
        api_request["presence_penalty"] = presence_penalty
    if stop is not None:
        api_request["stop"] = stop
    if seed is not None:
        api_request["seed"] = seed

    # Простой заголовок
    phase_title = ">>> API Request" if phase == "request" else "<<< API Response"
    console.print(f"\n[cyan]{phase_title}[/cyan]")

    # Выводим чистый JSON с подсветкой синтаксиса
    full_request_json = json.dumps(api_request, ensure_ascii=False, indent=2)
    api_syntax = Syntax(
        full_request_json,
        "json",
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
        background_color="default"
    )
    console.print(api_syntax)
    console.print()  # Пустая строка после JSON
