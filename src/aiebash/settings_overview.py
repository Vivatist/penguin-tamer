#!/usr/bin/env python3
"""
Pretty console output of current application settings.

Shows:
1) Current LLM and its settings
2) User content and temperature
3) Table of all added LLMs and their settings (current marked)
4) Console log level
"""
from typing import Optional

from aiebash.config_manager import config
from aiebash.formatter_text import format_api_key_display
from aiebash.i18n import t


def _plain_overview_print():
    print("=" * 60)
    print(t("Settings overview"))
    print("=" * 60)

    # Текущая LLM
    current_llm = config.current_llm or "(not selected)"
    current_cfg = config.get_current_llm_config() or {}

    print("\n" + t("Current LLM") + ":")
    print(f"  {t('Name')}: {current_llm}")
    if current_cfg:
        print(f"  {t('Model')}: {current_cfg.get('model', '')}")
        print(f"  API URL: {current_cfg.get('api_url', '')}")
        print(f"  {t('API key')}: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        print("  " + t("No settings found"))

    # Контент и температура
    print("\n" + t("Content and temperature") + ":")
    content = config.user_content or t("(empty)")
    print("  " + t("Content") + ":")
    for line in str(content).splitlines() or [content]:
        print(f"    {line}")
    print(f"  {t('Temperature')}: {config.temperature}")

    # Все LLM
    print("\n" + t("Available LLMs") + ":")
    llms = config.get_available_llms() or []
    if not llms:
        print("  " + t("No LLMs added"))
    else:
        header = f"{t('LLM'):20} | {t('Model'):20} | {'API URL':30} | {t('API key')}"
        print(header)
        print("-" * len(header))
        for name in llms:
            cfg = config.get_llm_config(name) or {}
            is_current = name == config.current_llm
            current_mark = " ✓" if is_current else "  "
            row = [
                f"{current_mark}{name}",
                cfg.get('model', '') or '',
                cfg.get('api_url', '') or '',
                format_api_key_display(cfg.get('api_key', '') or ''),
            ]
            print(f"{row[0]:20} | {row[1]:20} | {row[2]:30} | {row[3]}")

    # Логирование
    print("\n" + t("Logging") + ":")
    print(f"  {t('Console log level')}: {config.console_log_level}")
    
    file_enabled = getattr(config, 'file_enabled', False)
    if file_enabled:
        file_level = getattr(config, 'file_log_level', 'DEBUG')
        print(f"  {t('File logging')}: On ({file_level})")
    else:
        print(f"  {t('File logging')}: Off")
    
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

    console.rule(t("Settings overview"))

    # Текущая LLM
    current_llm = config.current_llm
    current_cfg = config.get_current_llm_config() or {}

    current_lines = []
    current_lines.append(t("Current LLM") + f": [bold]{current_llm or t('(not selected)')}[/bold]")
    if current_cfg:
        current_lines.append(f"{t('Model')}: {current_cfg.get('model', '')}")
        current_lines.append(f"API URL: {current_cfg.get('api_url', '')}")
        current_lines.append(f"{t('API key')}: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        current_lines.append(t("No settings found"))

    console.print(Panel.fit("\n".join(current_lines), title=t("Current LLM")))

    # Контент и температура
    content = config.user_content or t("(empty)")
    content_lines = [t("Content") + ":"]
    if content:
        for line in str(content).splitlines() or [content]:
            content_lines.append(f"  {line}")
    content_lines.append(f"\n{t('Temperature')}: [bold]{config.temperature}[/bold]")
    console.print(Panel.fit("\n".join(content_lines), title=t("Content & Temperature")))

    # Все LLM в таблице
    llms = config.get_available_llms() or []
    if llms:
        table = Table(title=t("Available LLMs"), show_lines=False, expand=True)
        table.add_column(t("LLM"), style="bold")
        table.add_column(t("Model"))
        table.add_column("API URL")
        table.add_column(t("API key"))

        for name in llms:
            cfg = config.get_llm_config(name) or {}
            is_current = name == current_llm
            
            # Выделяем текущую LLM зеленым цветом
            if is_current:
                name_display = f"[green]{name}[/green]"
                model_display = f"[green]{cfg.get('model', '') or ''}[/green]"
                url_display = f"[green]{cfg.get('api_url', '') or ''}[/green]"
                key_display = f"[green]{format_api_key_display(cfg.get('api_key', '') or '')}[/green]"
            else:
                name_display = name
                model_display = cfg.get('model', '') or ''
                url_display = cfg.get('api_url', '') or ''
                key_display = format_api_key_display(cfg.get('api_key', '') or '')
            
            table.add_row(
                name_display,
                model_display,
                url_display,
                key_display,
            )
        console.print(table)
    else:
        console.print(Panel.fit(t("No LLMs added"), title=t("Added LLMs")))

    # Логирование
    logging_info = []
    logging_info.append(f"{t('Console log level')}: [bold]{config.console_log_level}[/bold]")
    
    file_enabled = getattr(config, 'file_enabled', False)
    if file_enabled:
        file_level = getattr(config, 'file_log_level', 'DEBUG')
        logging_info.append(f"{t('File logging')}: [green]On[/green] ({file_level})")
    else:
        logging_info.append(f"{t('File logging')}: [dim]Off[/dim]")
    
    console.print(Panel.fit("\n".join(logging_info), title=t("Logging")))

    console.rule()
