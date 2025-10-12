#!/usr/bin/env python3
"""
Ручной тестовый скрипт для проверки всех доступных тем Rich Markdown.

Использование:
    python tests/test_all_themes.py

Отображает тестовый текст из formatted_text.md во всех доступных темах.
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from penguin_tamer.themes import get_available_themes, get_code_theme, THEMES  # noqa: E402


def load_test_markdown():
    """Загружает тестовый markdown из файла."""
    test_file = Path(__file__).parent / "formatted_text.md"
    with open(test_file, 'r', encoding='utf-8') as f:
        return f.read()


def display_theme_sample(console: Console, theme_name: str, markdown_text: str):
    """
    Отображает образец темы с тестовым markdown.

    Args:
        console: Rich Console объект
        theme_name: Название темы
        markdown_text: Текст в формате Markdown
    """
    # Получаем тему для markdown элементов
    theme_styles = THEMES.get(theme_name, THEMES["default"])
    theme = Theme(theme_styles)

    # Получаем тему для подсветки кода
    code_theme = get_code_theme(theme_name)

    # Создаём консоль с темой
    themed_console = Console(theme=theme)

    # Создаём Markdown с нужной темой подсветки кода
    markdown = Markdown(markdown_text, code_theme=code_theme)

    # Отображаем название темы
    console.print()
    console.print("=" * 80)
    console.print(f"[bold cyan]ТЕМА:[/bold cyan] [bold yellow]{theme_name.upper()}[/bold yellow]")
    console.print(f"[dim]Code theme: {code_theme}[/dim]")
    console.print("=" * 80)
    console.print()

    # Отображаем markdown с примененной темой
    themed_console.print(markdown)

    # Разделитель
    console.print()
    console.print("[dim]" + "─" * 80 + "[/dim]")
    console.print()


def main():
    """Главная функция теста."""
    console = Console()

    # Загружаем тестовый markdown
    try:
        markdown_text = load_test_markdown()
    except FileNotFoundError:
        console.print("[bold red]Ошибка:[/bold red] Файл formatted_text.md не найден!", style="bold red")
        sys.exit(1)

    # Получаем список всех доступных тем
    available_themes = get_available_themes()

    # Заголовок
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🎨 Тест всех доступных тем Rich Markdown[/bold cyan]\n"
        f"[dim]Доступно тем: {len(available_themes)}[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Отображаем каждую тему
    for idx, theme_name in enumerate(available_themes, 1):
        console.print(f"[bold blue]({idx}/{len(available_themes)})[/bold blue]", end=" ")
        display_theme_sample(console, theme_name, markdown_text)

        # Пауза между темами (кроме последней)
        if idx < len(available_themes):
            try:
                console.input("[dim]Нажмите Enter для следующей темы...[/dim]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Тест прерван пользователем[/yellow]")
                break

    # Итоги
    console.print()
    console.print(Panel.fit(
        "[bold green]✓ Тест завершён[/bold green]\n"
        f"[dim]Протестировано тем: {len(available_themes)}[/dim]",
        border_style="green"
    ))
    console.print()


if __name__ == "__main__":
    main()
