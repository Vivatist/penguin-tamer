#!/usr/bin/env python3
"""
Pretty console output of current application settings.

Shows:
1) Current LLM and its settings
2) User content and temperature
3) Table of all added LLMs and their settings (current marked)
4) Paths to config and Python executable
"""
from typing import Optional

from penguin_tamer.config_manager import config
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t


def _plain_overview_print():
    print("=" * 60)
    print(t("Settings overview"))
    print("=" * 60)

    # Текущая LLM
    current_llm = config.current_llm or "(not selected)"
    current_cfg = config.get_current_llm_effective_config() or {}

    print("\n" + t("Current LLM") + ":")
    print(f"  {t('Name')}: {current_llm}")
    if current_cfg:
        print(f"  {t('Provider')}: {current_cfg.get('provider', '')}")
        print(f"  {t('Model')}: {current_cfg.get('model', '')}")
        print(f"  {t('API key')}: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        print("  " + t("No settings found"))

    # Контент и параметры генерации
    print("\n" + t("Content and generation parameters") + ":")
    content = config.user_content or t("(empty)")
    print("  " + t("Content") + ":")
    for line in str(content).splitlines() or [content]:
        print(f"    {line}")
    print(f"\n  {t('Temperature')}: {config.temperature}")
    print(f"  {t('Max tokens')}: {config.max_tokens if config.max_tokens is not None else t('unlimited')}")
    print(f"  Top P: {config.top_p}")
    print(f"  {t('Frequency penalty')}: {config.frequency_penalty}")
    print(f"  {t('Presence penalty')}: {config.presence_penalty}")
    print(f"  Seed: {config.seed if config.seed is not None else t('random')}")

    # Все LLM
    print("\n" + t("Available LLMs") + ":")
    llms = config.get_available_llms() or []
    if not llms:
        print("  " + t("No LLMs added"))
    else:
        header = f"{'  ':3} | {t('Provider'):20} | {t('Model'):40}"
        print(header)
        print("-" * len(header))
        for llm_id in llms:
            cfg = config.get_llm_config(llm_id) or {}
            is_current = llm_id == config.current_llm
            current_mark = " ✓" if is_current else "  "
            row = [
                current_mark,
                cfg.get('provider', '') or '',
                cfg.get('model', '') or '',
            ]
            print(f"{row[0]:3} | {row[1]:20} | {row[2]:40}")

    # Пути
    print("\n" + t("Paths") + ":")
    print(f"  {t('Config file')}: {config.config_path}")

    import sys
    print(f"  {t('Python executable')}: {sys.executable}")

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
    except Exception:
        _plain_overview_print()
        return

    console = console or Console()

    console.rule(t("Settings overview"))

    # Текущая LLM
    current_llm = config.current_llm
    current_cfg = config.get_current_llm_effective_config() or {}

    current_lines = []
    current_lines.append(t("Current LLM") + f": [bold]{current_llm or t('(not selected)')}[/bold]")
    if current_cfg:
        current_lines.append(f"{t('Provider')}: {current_cfg.get('provider', '')}")
        current_lines.append(f"{t('Model')}: {current_cfg.get('model', '')}")
        current_lines.append(f"{t('API key')}: {format_api_key_display(current_cfg.get('api_key', ''))}")
    else:
        current_lines.append(t("No settings found"))

    console.print(Panel.fit("\n".join(current_lines), title=t("Current LLM")))

    # Контент и параметры генерации
    content = config.user_content or t("(empty)")
    content_lines = [t("Content") + ":"]
    if content:
        for line in str(content).splitlines() or [content]:
            content_lines.append(f"  {line}")

    # Параметры генерации
    content_lines.append(f"\n[bold]{t('Generation parameters')}:[/bold]")
    content_lines.append(f"{t('Temperature')}: [cyan]{config.temperature}[/cyan]")
    max_tokens_display = config.max_tokens if config.max_tokens is not None else t('unlimited')
    content_lines.append(f"{t('Max tokens')}: [cyan]{max_tokens_display}[/cyan]")
    content_lines.append(f"Top P: [cyan]{config.top_p}[/cyan]")
    content_lines.append(f"{t('Frequency penalty')}: [cyan]{config.frequency_penalty}[/cyan]")
    content_lines.append(f"{t('Presence penalty')}: [cyan]{config.presence_penalty}[/cyan]")
    content_lines.append(f"Seed: [cyan]{config.seed if config.seed is not None else t('random')}[/cyan]")

    console.print(Panel.fit("\n".join(content_lines), title=t("Content & Generation")))

    # Все LLM в таблице
    llms = config.get_available_llms() or []
    if llms:
        table = Table(title=t("Available LLMs"), show_lines=False, expand=True)
        table.add_column("", style="bold", width=3)
        table.add_column(t("Provider"), width=20)
        table.add_column(t("Model"), width=40)

        for llm_id in llms:
            cfg = config.get_llm_config(llm_id) or {}
            is_current = llm_id == current_llm

            # Выделяем текущую LLM зеленым цветом
            if is_current:
                current_mark = "[green]✓[/green]"
                provider_display = f"[green]{cfg.get('provider', '') or ''}[/green]"
                model_display = f"[green]{cfg.get('model', '') or ''}[/green]"
            else:
                current_mark = ""
                provider_display = cfg.get('provider', '') or ''
                model_display = cfg.get('model', '') or ''

            table.add_row(
                current_mark,
                provider_display,
                model_display,
            )
        console.print(table)
    else:
        console.print(Panel.fit(t("No LLMs added"), title=t("Added LLMs")))

    # Пути
    import sys
    paths_info = []
    paths_info.append(f"{t('Config file')}:")
    paths_info.append(f"  [cyan]{config.config_path}[/cyan]")
    paths_info.append(f"{t('Python executable')}:")
    paths_info.append(f"  [cyan]{sys.executable}[/cyan]")

    console.print(Panel.fit("\n".join(paths_info), title=t("Paths")))

    console.rule()
