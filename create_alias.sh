#!/usr/bin/env bash
# Quick script to create an alternative command name for Penguin Tamer

set -euo pipefail

echo "=== Penguin Tamer: Create Alternative Command Name ==="
echo "======================================================="
echo

# Check if pt is installed
if ! command -v pt >/dev/null 2>&1; then
    echo "[!] Error: 'pt' command not found."
    echo "    Please install Penguin Tamer first:"
    echo "    curl -sSL https://raw.githubusercontent.com/Vivatist/penguin-tamer/main/install.sh | bash"
    exit 1
fi

PT_PATH=$(which pt)
echo "[+] Found 'pt' at: $PT_PATH"
echo

# Ask for desired command name
read -p ">>> Enter desired command name (e.g., ai, chat, llm): " cmd_name

# Validate
if [ -z "$cmd_name" ]; then
    echo "[!] Error: Command name cannot be empty"
    exit 1
fi

if [[ ! "$cmd_name" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    echo "[!] Error: Invalid name. Use lowercase letters, numbers, hyphens, and underscores only."
    exit 1
fi

if [ "$cmd_name" = "pt" ]; then
    echo "[!] Error: Command name is already 'pt'"
    exit 1
fi

# Check if name is already taken
if command -v "$cmd_name" >/dev/null 2>&1; then
    echo "[!] Warning: Command '$cmd_name' already exists:"
    which "$cmd_name"
    read -p ">>> Continue anyway? [y/N]: " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Determine target directory
TARGET_DIR=$(dirname "$PT_PATH")
TARGET_PATH="$TARGET_DIR/$cmd_name"

echo
echo "[*] Creating symlink: $TARGET_PATH -> $PT_PATH"

# Try to create symlink
if ln -sf "$PT_PATH" "$TARGET_PATH" 2>/dev/null; then
    echo "[+] Success! Command '$cmd_name' is now available."
    echo
    echo ">>> Test it:"
    echo "    $cmd_name --version"
    echo "    $cmd_name --help"
else
    echo "[!] Failed to create symlink. Trying with sudo..."
    if sudo ln -sf "$PT_PATH" "$TARGET_PATH" 2>/dev/null; then
        echo "[+] Success! Command '$cmd_name' is now available."
        echo
        echo ">>> Test it:"
        echo "    $cmd_name --version"
        echo "    $cmd_name --help"
    else
        echo "[!] Failed to create symlink. You can add an alias instead:"
        echo
        echo "For bash, add to ~/.bashrc:"
        echo "    alias $cmd_name='pt'"
        echo
        echo "For zsh, add to ~/.zshrc:"
        echo "    alias $cmd_name='pt'"
        echo
        echo "Then reload your shell config:"
        echo "    source ~/.bashrc    # or ~/.zshrc"
    fi
fi
