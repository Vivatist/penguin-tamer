# flake8: noqa: E501
"""
Internationalization system for configuration menu.

Separate from main i18n (src/penguin_tamer/i18n.py) to keep menu translations independent.
Uses the same Translator class approach but with menu-specific locales.

Default language: English (en)
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class MenuTranslator:
    """
    JSON-based i18n for menu. English text is used as the lookup key.

    Rules:
    - If translation for the key is missing, return the key itself
    - Locales are stored under `menu/locales/<lang>.json`
    - Default language is 'en'
    - Supports simple .format(**kwargs)
    - Separate from main application i18n
    """

    def __init__(self, base_dir: Optional[Path] = None, default_lang: str = "en") -> None:
        # Since menu_i18n.py is now in locales/, base_dir is the current directory
        self.base_dir = base_dir or Path(__file__).parent
        self.default_lang = default_lang
        self._lang = default_lang
        self._cache: Dict[str, Dict[str, str]] = {}
        self._help_content_cache: Dict[str, Any] = {}

    @property
    def lang(self) -> str:
        return self._lang

    def set_language(self, lang: Optional[str]) -> None:
        """Set current language. If None, use default."""
        if not lang:
            self._lang = self.default_lang
            return
        # lazily load
        if lang not in self._cache:
            self._cache[lang] = self._load_locale(lang)
        self._lang = lang
        # Clear help content cache when language changes
        self._help_content_cache.clear()

    def t(self, key: str, **kwargs: Any) -> str:
        """Translate a key with optional formatting."""
        # For English, return key itself (English-as-key approach)
        if self._lang == "en":
            text = key
        else:
            translations = self._cache.get(self._lang)
            if translations is None:
                translations = self._load_locale(self._lang)
                self._cache[self._lang] = translations
            text = translations.get(key, key)
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    def _load_locale(self, lang: str) -> Dict[str, str]:
        """Load locale file from menu/locales/<lang>.json"""
        path = Path(self.base_dir) / f"{lang}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure mapping of str->str
                return {str(k): str(v) for k, v in data.items()}
        except FileNotFoundError:
            return {}
        except Exception:
            return {}

    def get_help_content(self) -> tuple[Dict[str, str], Dict[str, str]]:
        """
        Load localized help content (TAB_HELP and WIDGET_HELP).

        Returns:
            tuple: (TAB_HELP dict, WIDGET_HELP dict) in current language
        """
        # Check cache first
        cache_key = f"{self._lang}_help"
        if cache_key in self._help_content_cache:
            return self._help_content_cache[cache_key]

        # Load from appropriate module
        if self._lang == "en":
            from . import help_content_en
            result = (help_content_en.TAB_HELP, help_content_en.WIDGET_HELP)
        elif self._lang == "ru":
            from . import help_content_ru
            result = (help_content_ru.TAB_HELP, help_content_ru.WIDGET_HELP)
        else:
            # Fallback to English for unsupported languages
            from . import help_content_en
            result = (help_content_en.TAB_HELP, help_content_en.WIDGET_HELP)

        # Cache the result
        self._help_content_cache[cache_key] = result
        return result


# Global instance
menu_translator = MenuTranslator()


def t(key: str, **kwargs: Any) -> str:
    """Shortcut for menu_translator.t()"""
    return menu_translator.t(key, **kwargs)
