#!/usr/bin/env python3
"""Remove all emojis from textual_config_menu.py"""
import re

def remove_emojis(text):
    """Remove all emoji characters from text"""
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U00002600-\U000026FF"  # Misc symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002300-\U000023FF"  # Misc Technical
        "\uFE0F]+"  # Variation Selector-16
        , flags=re.UNICODE)
    return emoji_pattern.sub('', text)

# Read file
with open('src/penguin_tamer/textual_config_menu.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove emojis
content = remove_emojis(content)

# Clean up extra spaces
content = re.sub(r'  +', ' ', content)  # Multiple spaces to single
content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)  # Empty lines with spaces

# Write back
with open('src/penguin_tamer/textual_config_menu.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ All emojis removed successfully!")
