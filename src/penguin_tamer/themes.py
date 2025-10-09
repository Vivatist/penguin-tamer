#!/usr/bin/env python3
"""
Темы для оформления Markdown в Rich.

Модуль содержит готовые цветовые схемы для отображения Markdown
и подсветки синтаксиса в блоках кода.
"""

from rich.theme import Theme
from typing import Dict

# Кэш для созданных тем
_markdown_themes_cache: Dict[str, Theme] = {}

# Сопоставление тем с встроенными темами подсветки синтаксиса Rich
CODE_THEMES = {
    "default": "monokai",
    "monokai": "monokai",
    "dracula": "dracula",
    "nord": "nord",
    "solarized_dark": "solarized-dark",
    "github": "github-dark",
    "matrix": "vim",  # vim тема зелёная
    "minimal": "bw",
}

# Доступные code_theme в Rich:
# monokai, dracula, nord, solarized-dark, solarized-light,
# github-dark, vim, emacs, vs, xcode, paraiso-dark, paraiso-light,
# fruity, bw (black & white)

# Определения тем
THEMES = {
    "default": {
        "markdown.h1": "bold cyan",
        "markdown.h2": "bold bright_cyan",
        "markdown.h3": "bold blue",
        "markdown.h4": "bold bright_blue",
        "markdown.code": "bright_yellow on grey11",
        "markdown.code_block": "bright_white on grey11",
        "markdown.link": "blue underline",
        "markdown.item.bullet": "bright_green",
        "markdown.block_quote": "italic bright_black",
    },

    "monokai": {
        "markdown.h1": "bold bright_magenta",
        "markdown.h2": "bold magenta",
        "markdown.h3": "bold bright_cyan",
        "markdown.h4": "bold cyan",
        "markdown.code": "bright_yellow on grey11",
        "markdown.code_block": "bright_green on grey11",
        "markdown.link": "bright_blue underline",
        "markdown.item.bullet": "bright_yellow",
        "markdown.block_quote": "italic bright_black",
        "markdown.emphasis": "italic bright_cyan",
        "markdown.strong": "bold bright_red",
    },

    "dracula": {
        "markdown.h1": "bold bright_magenta",
        "markdown.h2": "bold magenta",
        "markdown.h3": "bold bright_cyan",
        "markdown.h4": "bold cyan",
        "markdown.h5": "bold green",
        "markdown.code": "bright_green on grey11",
        "markdown.code_block": "bright_white on grey11",
        "markdown.link": "bright_cyan underline",
        "markdown.item.bullet": "bright_magenta",
        "markdown.block_quote": "italic bright_black",
        "markdown.emphasis": "italic bright_magenta",
        "markdown.strong": "bold bright_red",
    },

    "nord": {
        "markdown.h1": "bold bright_cyan",
        "markdown.h2": "bold cyan",
        "markdown.h3": "bold bright_blue",
        "markdown.h4": "bold blue",
        "markdown.code": "bright_white on bright_black",
        "markdown.code_block": "bright_cyan on bright_black",
        "markdown.link": "cyan underline",
        "markdown.item.bullet": "bright_blue",
        "markdown.block_quote": "italic blue",
        "markdown.emphasis": "italic cyan",
        "markdown.strong": "bold bright_white",
    },

    "solarized_dark": {
        "markdown.h1": "bold bright_yellow",
        "markdown.h2": "bold yellow",
        "markdown.h3": "bold bright_blue",
        "markdown.h4": "bold blue",
        "markdown.code": "bright_cyan on bright_black",
        "markdown.code_block": "green on bright_black",
        "markdown.link": "blue underline",
        "markdown.item.bullet": "bright_green",
        "markdown.block_quote": "italic bright_black",
        "markdown.emphasis": "italic cyan",
        "markdown.strong": "bold bright_yellow",
    },

    "github": {
        "markdown.h1": "bold blue",
        "markdown.h2": "bold blue",
        "markdown.h3": "bold blue",
        "markdown.h4": "bold blue",
        "markdown.code": "red on white",
        "markdown.code_block": "black on white",
        "markdown.link": "blue underline",
        "markdown.item.bullet": "black",
        "markdown.block_quote": "italic bright_black",
        "markdown.emphasis": "italic",
        "markdown.strong": "bold",
    },

    "matrix": {
        "markdown.h1": "bold bright_green",
        "markdown.h2": "bold green",
        "markdown.h3": "bold bright_green",
        "markdown.h4": "bold green",
        "markdown.code": "bright_green on black",
        "markdown.code_block": "green on black",
        "markdown.link": "bright_green underline",
        "markdown.item.bullet": "bright_green",
        "markdown.block_quote": "italic green",
        "markdown.emphasis": "italic bright_green",
        "markdown.strong": "bold bright_green",
        "markdown.text": "green",
    },

    "minimal": {
        "markdown.h1": "bold white",
        "markdown.h2": "bold white",
        "markdown.h3": "bold bright_white",
        "markdown.h4": "bold bright_white",
        "markdown.code": "white on bright_black",
        "markdown.code_block": "bright_white on bright_black",
        "markdown.link": "white underline",
        "markdown.item.bullet": "white",
        "markdown.block_quote": "italic bright_black",
        "markdown.emphasis": "italic",
        "markdown.strong": "bold",
    },
}


def get_theme(theme_name: str = "default") -> Theme:
    """
    Возвращает тему Rich для Markdown.

    Доступные темы:
    - default: Классическая тема (cyan заголовки, желтый код)
    - monokai: Темная тема в стиле Monokai
    - dracula: Популярная Dracula тема
    - nord: Холодная Nord тема
    - solarized_dark: Solarized Dark тема
    - github: GitHub-стиль (светлая тема)
    - matrix: Зеленая Matrix тема
    - minimal: Минималистичная черно-белая тема

    Args:
        theme_name: Название темы

    Returns:
        Theme объект Rich
    """
    # Проверяем есть ли тема в кэше
    if theme_name in _markdown_themes_cache:
        return _markdown_themes_cache[theme_name]

    # Получаем выбранную тему или дефолтную
    selected_theme = THEMES.get(theme_name, THEMES["default"])
    created_theme = Theme(selected_theme)

    # Сохраняем в кэш
    _markdown_themes_cache[theme_name] = created_theme

    return created_theme


def get_code_theme(theme_name: str = "default") -> str:
    """
    Возвращает название темы для подсветки синтаксиса в блоках кода.

    Args:
        theme_name: Название темы

    Returns:
        Название темы для Rich Syntax
    """
    return CODE_THEMES.get(theme_name, "monokai")


def get_available_themes() -> list[str]:
    """
    Возвращает список доступных тем.

    Returns:
        Список названий тем
    """
    return list(THEMES.keys())
