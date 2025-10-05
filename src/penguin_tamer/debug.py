"""Debug utilities for LLM request visualization."""

import json
from typing import List, Dict

# Ленивый импорт Rich
_console = None
_panel = None
_syntax = None


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


def debug_print_messages(messages: List[Dict[str, str]], 
                        client = None,
                        phase: str = "request") -> None:
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
    Console = _get_console()
    Panel = _get_panel()
    Syntax = _get_syntax()
    
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
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print("=" * 90 + "\n")
    
    # Создаём полную структуру API запроса
    api_request = {
        "model": model,
        "messages": messages,
        "stream": True  # Всегда используется в penguin-tamer
    }
    
    # Добавляем параметры генерации если они заданы
    if temperature is not None:
        api_request["temperature"] = temperature
    if max_tokens is not None:
        api_request["max_tokens"] = max_tokens
    if top_p is not None and top_p != 1.0:
        api_request["top_p"] = top_p
    if frequency_penalty is not None and frequency_penalty != 0.0:
        api_request["frequency_penalty"] = frequency_penalty
    if presence_penalty is not None and presence_penalty != 0.0:
        api_request["presence_penalty"] = presence_penalty
    if stop is not None:
        api_request["stop"] = stop
    if seed is not None:
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
    title_color = "bold yellow" if phase == "request" else "bold green"
    
    api_panel = Panel(
        api_syntax,
        title=f"[{title_color}]{api_title}[/{title_color}]",
        border_style=border_color,
        padding=(1, 1)
    )
    console.print(api_panel)
    console.print()
    
    # Роли с цветами и иконками
    role_colors = {
        "system": "magenta",
        "user": "green", 
        "assistant": "blue"
    }
    
    role_icons = {
        "system": "⚙️",
        "user": "👤",
        "assistant": "🤖"
    }
    
    # Выводим каждое сообщение как отдельный JSON
    console.print(f"[bold white]>>> Messages Breakdown ({len(messages)} total):[/bold white]")
    console.print()
    
    for idx, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        role_color = role_colors.get(role, "white")
        role_icon = role_icons.get(role, "[?]")
        
        # Создаём JSON для конкретного сообщения
        message_json = json.dumps(msg, ensure_ascii=False, indent=2)
        
        # Подсветка синтаксиса для JSON
        message_syntax = Syntax(
            message_json,
            "json",
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
            background_color="default"
        )
        
        # Заголовок с иконкой и ролью
        title = f"[bold]{role_icon} Message #{idx}: {role.upper()}[/bold]"
        
        # Статистика сообщения
        content_length = len(msg.get("content", ""))
        stats = f"[dim]Length: {content_length} chars[/dim]"
        
        # Создаём панель с JSON структурой
        panel = Panel(
            message_syntax,
            title=title,
            subtitle=stats,
            title_align="left",
            subtitle_align="right", 
            border_style=role_color,
            padding=(0, 1)
        )
        
        console.print(panel)
        console.print()  # Пустая строка между сообщениями
    
    # Итоговая статистика
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    total_tokens_estimate = total_chars // 4  # Примерная оценка токенов (1 токен ≈ 4 символа)
    
    stats_text = f"[dim]📊 Total: {len(messages)} messages | {total_chars} chars | ~{total_tokens_estimate} tokens[/dim]"
    console.print(stats_text)
    console.print("=" * 90 + "\n")
