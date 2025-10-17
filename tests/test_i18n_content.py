#!/usr/bin/env python3
"""
Тесты для системы локализации user_content.
"""

import pytest
from penguin_tamer.i18n_content import (
    get_default_user_content,
    is_default_user_content,
    DEFAULT_USER_CONTENT
)


class TestI18nContent:
    """Тесты для локализованного контента."""

    def test_get_default_user_content_en(self):
        """Получение английской версии user_content."""
        content = get_default_user_content("en")
        assert "You are a professional" in content
        assert "Linux and Windows" in content
        assert "console tamers" in content

    def test_get_default_user_content_ru(self):
        """Получение русской версии user_content."""
        content = get_default_user_content("ru")
        assert "Ты - профессионал" in content
        assert "Linux и Windows" in content
        assert "укротители консоли" in content

    def test_get_default_user_content_unknown_language(self):
        """Неизвестный язык должен возвращать английскую версию."""
        content = get_default_user_content("fr")
        assert content == DEFAULT_USER_CONTENT["en"]

    def test_is_default_user_content_en(self):
        """Проверка английской дефолтной версии."""
        content = DEFAULT_USER_CONTENT["en"]
        assert is_default_user_content(content, "en")
        assert is_default_user_content(content)  # Без указания языка

    def test_is_default_user_content_ru(self):
        """Проверка русской дефолтной версии."""
        content = DEFAULT_USER_CONTENT["ru"]
        assert is_default_user_content(content, "ru")
        assert is_default_user_content(content)  # Без указания языка

    def test_is_default_user_content_with_whitespace(self):
        """Проверка с дополнительными пробелами."""
        content = "  " + DEFAULT_USER_CONTENT["en"] + "  \n"
        assert is_default_user_content(content, "en")

    def test_is_not_default_user_content(self):
        """Изменённый контент не должен считаться дефолтным."""
        custom_content = "This is my custom system message"
        assert not is_default_user_content(custom_content)
        assert not is_default_user_content(custom_content, "en")
        assert not is_default_user_content(custom_content, "ru")

    def test_is_not_default_user_content_partial_match(self):
        """Частичное совпадение не считается дефолтным."""
        partial = DEFAULT_USER_CONTENT["en"] + " Extra text"
        assert not is_default_user_content(partial)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
