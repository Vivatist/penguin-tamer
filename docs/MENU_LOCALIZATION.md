# Menu Localization System

## Overview

Penguin Tamer now has a separate localization system for the configuration menu, independent from the main application's i18n system.

## Structure

```
src/penguin_tamer/menu/
├── locales/
│   ├── __init__.py       # Package initializer
│   ├── menu_i18n.py      # Menu translator class
│   ├── en.json           # English UI strings (empty, as English is used as keys)
│   ├── ru.json           # Russian translations
│   ├── menu_content.py   # English help content (TAB_HELP, WIDGET_HELP)
│   └── help_content_ru.py # Russian help content
├── info_panel.py         # Uses menu_translator for help
└── config_menu.py        # Uses t() for UI strings
```

## Key Components

### 1. MenuTranslator (`menu/locales/menu_i18n.py`)

- **Purpose**: Separate translator for menu UI
- **Location**: Now inside `locales/` directory for better organization
- **Default language**: English (`en`)
- **Key features**:
  - English-as-key approach (no translation file needed for English)
  - Lazy loading of localization files
  - Automatic help content loading based on language
  - Caching for performance

```python
from penguin_tamer.menu.locales.menu_i18n import menu_translator, t

# Set language
menu_translator.set_language("ru")

# Translate strings
text = t("Settings")  # Returns "Настройки" in Russian

# Get localized help
tab_help, widget_help = menu_translator.get_help_content()
```

### 2. Localization Files (`menu/locales/`)

#### `en.json`
Empty `{}` - English text is used directly as keys.

#### `ru.json`
Contains all Russian translations:
```json
{
  "General": "Общие",
  "Save": "Сохранить",
  "Temperature set to {value}": "Temperature установлена на {value}"
}
```

### 3. Help Content Files

#### `menu_content.py` (English)
Contains TAB_HELP and WIDGET_HELP dictionaries in English.

#### `help_content_ru.py` (Russian)
Contains TAB_HELP and WIDGET_HELP dictionaries in Russian.

## Usage in Config Menu

### Initialization

```python
def main_menu():
    # Initialize menu translator with current language
    current_lang = getattr(config, "language", "en")
    menu_translator.set_language(current_lang)

    app = ConfigMenuApp()
    app.run()
```

### Synchronizing Language Changes

```python
def set_language(self, lang: str) -> None:
    """Set interface language."""
    setattr(config, "language", lang)
    config.save()
    # Sync both translators
    translator.set_language(lang)  # Main app translator
    menu_translator.set_language(lang)  # Menu translator
    self.refresh_status()
```

### Using t() in UI

```python
# TabPane labels
with TabPane(t("General"), id="tab-general"):
    ...

# Static labels
yield Static(
    f"[bold]{t('GENERAL SETTINGS')}[/bold]\n"
    f"[dim]{t('System information and LLM management')}[/dim]",
    classes="tab-header",
)

# Buttons
yield Button(
    t("Save"),
    id="save-content-btn",
    variant="success",
)

# Notifications
self.notify(t("User context saved"), severity="information")
```

## Adding New Languages

### 1. Create translation file

Create `menu/locales/<lang>.json`:
```json
{
  "General": "Général",
  "Save": "Enregistrer",
  ...
}
```

### 2. Create help content file

Create `help_content_<lang>.py` with TAB_HELP and WIDGET_HELP.

### 3. Update menu_i18n.py

Add language support in `get_help_content()`:
```python
elif self._lang == "fr":
    from . import help_content_fr
    result = (help_content_fr.TAB_HELP, help_content_fr.WIDGET_HELP)
```

### 4. Update language selector in config_menu.py

Add language to Select widget:
```python
yield Select(
    [("English", "en"), ("Русский", "ru"), ("Français", "fr")],
    ...
)
```

## Benefits

1. **Separation of concerns**: Menu translations don't interfere with main app translations
2. **Performance**: Lazy loading and caching of translations
3. **Scalability**: Easy to add new languages
4. **Flexibility**: Help content can be completely different per language
5. **English-as-key**: No duplication of English strings

## Implementation Status

✅ Created `menu_i18n.py` with MenuTranslator class
✅ Created `menu/locales/` directory structure
✅ Created `en.json` (empty) and `ru.json` (complete)
✅ Renamed `help_content_en.py` → `menu_content.py`
✅ Updated `info_panel.py` to use menu_translator
✅ Updated `config_menu.py` imports and language synchronization
✅ Started replacing hardcoded strings with `t()` calls

🚧 Ongoing: Complete replacement of all hardcoded Russian strings in config_menu.py

## Future Enhancements

- Add more languages (French, German, Spanish, etc.)
- Create translation extraction tool
- Add language detection from system locale
- Implement fallback language chain (e.g., pt_BR → pt → en)
