#!/usr/bin/env python3
"""
Test script for menu localization system.
Tests MenuTranslator functionality and help content loading.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from penguin_tamer.menu.locales.menu_i18n import menu_translator, t  # noqa: E402


def test_translations():
    """Test basic translation functionality."""
    print("=" * 60)
    print("MENU LOCALIZATION SYSTEM TEST")
    print("=" * 60)

    # Test English (default)
    print("\n1. Testing English (default):")
    print("-" * 60)
    menu_translator.set_language("en")
    print(f"Language: {menu_translator.lang}")
    print(f"t('General'): {t('General')}")
    print(f"t('Save'): {t('Save')}")
    print(f"t('Temperature'): {t('Temperature')}")

    # Test Russian
    print("\n2. Testing Russian:")
    print("-" * 60)
    menu_translator.set_language("ru")
    print(f"Language: {menu_translator.lang}")
    print(f"t('General'): {t('General')}")
    print(f"t('Save'): {t('Save')}")
    print(f"t('Temperature'): {t('Temperature')}")

    # Test formatting
    print("\n3. Testing string formatting:")
    print("-" * 60)
    print(f"English: {menu_translator.t('Temperature set to {{value}}', value='0.8')}")
    print(f"Russian: {t('Temperature set to {value}', value='0.8')}")

    # Test missing key
    print("\n4. Testing missing translation key:")
    print("-" * 60)
    print(f"t('NonExistentKey'): {t('NonExistentKey')}")


def test_help_content():
    """Test help content loading."""
    print("\n5. Testing help content loading:")
    print("-" * 60)

    # English help
    menu_translator.set_language("en")
    tab_help_en, widget_help_en = menu_translator.get_help_content()
    print(f"English TAB_HELP keys: {list(tab_help_en.keys())[:3]}...")
    print(f"English WIDGET_HELP keys: {list(widget_help_en.keys())[:3]}...")

    # Russian help
    menu_translator.set_language("ru")
    tab_help_ru, widget_help_ru = menu_translator.get_help_content()
    print(f"Russian TAB_HELP keys: {list(tab_help_ru.keys())[:3]}...")
    print(f"Russian WIDGET_HELP keys: {list(widget_help_ru.keys())[:3]}...")

    # Check cache
    print(f"\nCache keys: {list(menu_translator._help_content_cache.keys())}")


def test_ui_strings():
    """Test common UI strings."""
    print("\n6. Testing common UI strings:")
    print("-" * 60)

    ui_strings = [
        "Exit",
        "Help",
        "Configuration",
        "General",
        "Context",
        "Generation",
        "System",
        "Interface",
        "Select",
        "Add",
        "Edit",
        "Delete",
        "Save",
    ]

    print("\nEnglish → Russian:")
    menu_translator.set_language("ru")
    for string in ui_strings:
        translated = t(string)
        print(f"  {string:20} → {translated}")


if __name__ == "__main__":
    try:
        test_translations()
        test_help_content()
        test_ui_strings()

        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
