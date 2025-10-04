#!/usr/bin/env bash
set -euo pipefail

echo "🐧 Penguin Tamer Installer"
echo "--------------------------"

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1️⃣ Check Python (>=3.11)
PYTHON_CMD=""
for cmd in python3 python; do
    if command_exists "$cmd"; then
        VERSION=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || echo "0.0")
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3.11+ not found."
    echo "➡ Please install Python 3.11 or newer:"
    echo "   • Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-pip"
    echo "   • macOS (Homebrew): brew install python@3.11"
    echo "   • Windows: Download from https://python.org/downloads/"
    exit 1
fi

echo "✅ Using $($PYTHON_CMD --version)"

# 2️⃣ Install/upgrade pip first
echo "📦 Ensuring pip is up to date..."
$PYTHON_CMD -m pip install --upgrade pip --user >/dev/null 2>&1 || true

# 3️⃣ Check and install pipx
if ! $PYTHON_CMD -m pip show pipx >/dev/null 2>&1; then
    echo "📦 Installing pipx..."
    $PYTHON_CMD -m pip install --user pipx
    echo "✅ pipx installed."
fi

# Ensure pipx path is set up
if command_exists pipx; then
    PIPX_CMD="pipx"
else
    # Try to find pipx in common locations
    for path in "$HOME/.local/bin/pipx" "$HOME/Library/Python/*/bin/pipx"; do
        if [ -x "$path" ]; then
            PIPX_CMD="$path"
            break
        fi
    done
    
    # If still not found, use python -m pipx
    if [ -z "${PIPX_CMD:-}" ]; then
        PIPX_CMD="$PYTHON_CMD -m pipx"
    fi
fi

# 4️⃣ Install Penguin Tamer
echo "🚀 Installing Penguin Tamer from PyPI..."
$PIPX_CMD install penguin-tamer --force

# 5️⃣ Verify installation
if command_exists pt; then
    echo "✅ Penguin Tamer installed successfully!"
    echo "🎯 Version: $(pt --version 2>/dev/null || echo 'installed')"
else
    echo "⚠️ Installation completed, but 'pt' command not found in PATH."
    echo "� You may need to restart your terminal or add pipx binary directory to PATH:"
    echo "   • Linux/macOS: export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "   • Add this line to your ~/.bashrc or ~/.zshrc"
fi

# 6️⃣ Done!
echo
echo "🎉 Installation complete!"
echo "👉 Run Penguin Tamer with:"
echo "   pt --help        # Show help"
echo "   pt -d           # Interactive dialog mode"
echo "   pt \"your prompt\" # Quick AI query"
echo
echo "📚 Documentation: https://github.com/Vivatist/penguin-tamer"
