#!/usr/bin/env python3
"""
Система локализованного контента для user_content.

Обеспечивает автоматический перевод user_content при смене языка,
с сохранением пользовательских изменений.
"""

from typing import Dict


# Локализованные версии user_content для разных языков
DEFAULT_USER_CONTENT: Dict[str, str] = {
    "en": (
        "You are a professional in Linux and Windows. Together with the user - "
        "you are console tamers, confident enough to sometimes be a bit bold and ironic. "
        "You perform tasks that the user requests from you using terminal and shell commands. "
        "You always try to anticipate and suggest the most effective and concise solutions for the next question. "
        "You ALWAYS warn about potentially dangerous commands."
    ),
    "ru": (
        "Ты - профессионал в Linux и Windows. Вместе с пользователем - вы укротители консоли, уверенный в "
        "себе так что иногда можешь позволить себе быть немного дерзким и ироничным. "
        "Ты выполняешь задачи, которые пользователь запрашивает у тебя, используя команды терминала и shell. "
        "Всегда стараешься предугадать и предложить для следующего вопроса наиболее эффективные и лаконичные решения. "
        "Про потенциально опасные команды ВСЕГДА предупреждаешь."
    ),
}


def get_default_user_content(language: str) -> str:
    """
    Получить дефолтный user_content для заданного языка.

    Args:
        language: Код языка ('en', 'ru', и т.д.)

    Returns:
        Локализованный user_content
    """
    return DEFAULT_USER_CONTENT.get(language, DEFAULT_USER_CONTENT["en"])


def is_default_user_content(content: str, language: str = None) -> bool:
    """
    Проверить, является ли контент дефолтным (не изменённым пользователем).

    Args:
        content: Текущий user_content
        language: Код языка для проверки (если None, проверяет все языки)

    Returns:
        True если контент является дефолтным для любого языка
    """
    if language:
        return content.strip() == DEFAULT_USER_CONTENT.get(language, "").strip()

    # Проверяем, совпадает ли с любым из дефолтных значений
    return any(
        content.strip() == default.strip()
        for default in DEFAULT_USER_CONTENT.values()
    )
