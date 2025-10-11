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
    Выводит полную JSON структуру сообщений для LLM в удобном читаемом формате.

    Показывает сырые данные каждого сообщения как красиво отформатированный JSON
    с подсветкой синтаксиса, разделённые по отдельным панелям.

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
    Panel = get_panel()
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

    # Заголовок с основными параметрами
    phase_info = {
        "request": (">>> Raw LLM Request Data", ">>> Complete API Request"),
        "response": ("<<< LLM Response Data", "<<< Full Conversation State")
    }

    main_title, api_title = phase_info.get(phase, phase_info["request"])
    title_parts = [main_title]
    if model:
        title_parts.append(f"Model: {model}")

    title = " | ".join(title_parts)

    console.print("\n" + "=" * 90)
    console.print(f"[cyan]{title}[/cyan]")
    console.print("=" * 90 + "\n")

    # Создаём полную структуру API запроса
    api_request = {
        "model": model,
        "messages": messages,
        "stream": True  # Всегда используется в penguin-tamer
    }

    # Добавляем ВСЕ параметры генерации для полноты картины debug режима
    api_request["temperature"] = temperature
    api_request["max_tokens"] = max_tokens
    api_request["top_p"] = top_p
    api_request["frequency_penalty"] = frequency_penalty
    api_request["presence_penalty"] = presence_penalty
    api_request["stop"] = stop
    api_request["seed"] = seed

    # Панель с полным API запросом/ответом
    full_request_json = json.dumps(api_request, ensure_ascii=False, indent=2)
    api_syntax = Syntax(
        full_request_json,
        "json",
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
        background_color="default"
    )

    # Разные цвета для request/response
    border_color = "yellow" if phase == "request" else "green"
    title_color = "yellow" if phase == "request" else "green"

    api_panel = Panel(
        api_syntax,
        title=f"[{title_color}]{api_title}[/{title_color}]",
        border_style=border_color,
        padding=(1, 1)
    )
    console.print(api_panel)
    console.print()

    # Роли с цветами и префиксами
    role_colors = {
        "system": "magenta",
        "user": "green",
        "assistant": "blue"
    }

    role_icons = {
        "system": "[SYS]",
        "user": "[USER]",
        "assistant": "[AI]"
    }

    # Выводим каждое сообщение как отдельный JSON
    console.print(f"[white]>>> Messages Breakdown ({len(messages)} total):[/white]")
    console.print()

    for idx, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        role_color = role_colors.get(role, "white")
        role_icon = role_icons.get(role, "[?]")

        # Создаём структуру сообщения с форматированным содержимым
        content = msg.get("content", "")
        content_length = len(content)

        # Создаем красиво отформатированное представление сообщения
        formatted_message = f"[{role_color}]Role:[/{role_color}] {role}\n"
        formatted_message += f"[{role_color}]Content:[/{role_color}]\n"

        # Добавляем содержимое с отступом, сохраняя форматирование
        if content:
            # Разбиваем на строки и добавляем отступ
            content_lines = content.split('\n')
            for line in content_lines:
                formatted_message += f"  {line}\n"
        else:
            formatted_message += "  [dim](empty)[/dim]\n"

        # Заголовок с иконкой и ролью
        title = f"{role_icon} Message #{idx}: {role.upper()}"

        # Статистика сообщения
        stats = f"[dim]Length: {content_length} chars[/dim]"

        # Создаём панель с форматированным содержимым
        panel = Panel(
            formatted_message.rstrip(),
            title=title,
            subtitle=stats,
            title_align="left",
            subtitle_align="right",
            border_style=role_color,
            padding=(1, 1)
        )

        console.print(panel)
        console.print()  # Пустая строка между сообщениями

    # Итоговая статистика
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    total_tokens_estimate = total_chars // 4  # Примерная оценка токенов (1 токен ≈ 4 символа)

    console.print(f"\n> Total: {len(messages)} messages | {total_chars} chars | ~{total_tokens_estimate} tokens")
    console.print("=" * 90 + "\n")
