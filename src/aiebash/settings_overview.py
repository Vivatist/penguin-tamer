#!/usr/bin/env python3
"""
Модуль аккуратного вывода текущих настроек приложения в консоль.

Показывает:
1) Текущую нейросеть и её настройки
2) Пользовательский контент и температуру
3) Таблицу со всеми добавленными LLM и их настройками (текущая помечена)
4) Уровень логирования в консоль
"""
from typing import Optional

from aiebash.config_manager import config
from aiebash.formatter_text import format_api_key_display


def _plain_overview_print():
    print("=" * 60)
    print("Обзор настроек")
    print("=" * 60)

    # Текущая LLM
    current_llm = config.current_llm or "(не выбрана)"
    current_cfg = config.get_current_llm_config() or {}

    print("\nТекущая нейросеть:")
    print(f"  Имя: {current_llm}")
    if current_cfg:
        print(f"  Модель: {current_cfg.get('model', '')}")
        print(f"  API URL: {current_cfg.get('api_url', '')}")
        print(f"  API ключ: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        print("  Настройки не найдены")

    # Контент и температура
    print("\nКонтент и Температура:")
    content = config.user_content or "(пусто)"
    print("  Контент:")
    for line in str(content).splitlines() or [content]:
        print(f"    {line}")
    print(f"  Температура: {config.temperature}")

    # Все LLM
    print("\nСписок доступных нейросетей:")
    llms = config.get_available_llms() or []
    if not llms:
        print("  Нет добавленных нейросетей")
    else:
        header = f"{'Нейросеть':20} | {'Модель':20} | {'API URL':30} | {'API ключ'}"
        print(header)
        print("-" * len(header))
        for name in llms:
            cfg = config.get_llm_config(name) or {}
            mark = " [текущая]" if name == config.current_llm else ""
            row = [
                f"{name}{mark}",
                cfg.get('model', '') or '',
                cfg.get('api_url', '') or '',
                format_api_key_display(cfg.get('api_key', '') or ''),
            ]
            print(f"{row[0]:20} | {row[1]:20} | {row[2]:30} | {row[3]}")

    # Логирование
    print("\nЛогирование:")
    print(f"  Уровень логирования (консоль): {config.console_log_level}")
    print("=" * 60)


def print_settings_overview(console: Optional[object] = None) -> None:
    """Печатает обзор настроек. Использует rich, если доступен, иначе plain.

    Args:
        console: Опционально переданный rich.Console для вывода
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
    except Exception:
        _plain_overview_print()
        return

    console = console or Console()

    console.rule("Обзор настроек")

    # Текущая LLM
    current_llm = config.current_llm
    current_cfg = config.get_current_llm_config() or {}

    current_lines = []
    current_lines.append(f"Текущая нейросеть: [bold]{current_llm or '(не выбрана)'}[/bold]")
    if current_cfg:
        current_lines.append(f"Модель: {current_cfg.get('model', '')}")
        current_lines.append(f"API URL: {current_cfg.get('api_url', '')}")
        current_lines.append(f"API ключ: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        current_lines.append("Настройки не найдены")

    console.print(Panel.fit("\n".join(current_lines), title="Текущая нейросеть"))

    # Контент и температура
    content = config.user_content or "(пусто)"
    content_lines = ["Контент:"]
    if content:
        for line in str(content).splitlines() or [content]:
            content_lines.append(f"  {line}")
    content_lines.append(f"\nТемпература: [bold]{config.temperature}[/bold]")
    console.print(Panel.fit("\n".join(content_lines), title="Контент и Температура"))

    # Все LLM в таблице
    llms = config.get_available_llms() or []
    if llms:
        table = Table(title="Доступные нейросети", show_lines=False, expand=True)
        table.add_column("Нейросеть", style="bold")
        table.add_column("Модель")
        table.add_column("API URL")
        table.add_column("API ключ")

        for name in llms:
            cfg = config.get_llm_config(name) or {}
            name_display = f"{name} [текущая]" if name == current_llm else name
            table.add_row(
                name_display,
                cfg.get('model', '') or '',
                cfg.get('api_url', '') or '',
                format_api_key_display(cfg.get('api_key', '') or ''),
            )
        console.print(table)
    else:
        console.print(Panel.fit("Нет добавленных нейросетей", title="Доступные нейросети"))

    # Логирование
    console.print(Panel.fit(f"Уровень логирования (консоль): [bold]{config.console_log_level}[/bold]", title="Логирование"))

    console.rule()
