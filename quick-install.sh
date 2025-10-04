#!/usr/bin/env bash
set -euo pipefail

echo "🐧 Penguin Tamer Quick Installer"
echo "--------------------------------"

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

# 2️⃣ Check and install pip if needed
if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
    echo "📦 Installing pip..."
    
    # Try different methods to install pip
    if command_exists apt-get; then
        echo "🔄 Using apt-get to install pip..."
        sudo apt-get update >/dev/null 2>&1
        sudo apt-get install -y python3-pip python3-venv
    elif command_exists yum; then
        echo "🔄 Using yum to install pip..."
        sudo yum install -y python3-pip
    elif command_exists dnf; then
        echo "🔄 Using dnf to install pip..."
        sudo dnf install -y python3-pip
    elif command_exists pacman; then
        echo "🔄 Using pacman to install pip..."
        sudo pacman -S --noconfirm python-pip
    elif command_exists brew; then
        echo "🔄 Using brew to install pip..."
        brew install python
    else
        echo "❌ Could not install pip automatically."
        echo "➡ Please install pip manually:"
        echo "   • Ubuntu/Debian: sudo apt install python3-pip python3-venv"
        echo "   • CentOS/RHEL: sudo yum install python3-pip"
        echo "   • Fedora: sudo dnf install python3-pip"
        echo "   • Arch: sudo pacman -S python-pip"
        echo "   • macOS: brew install python"
        exit 1
    fi
    
    # Verify pip installation
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        echo "❌ Failed to install pip. Please install it manually."
        exit 1
    fi
    echo "✅ pip installed successfully."
else
    echo "✅ pip is available."
fi

# 3️⃣ Upgrade pip
echo "📦 Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --user >/dev/null 2>&1

# 4️⃣ Install Penguin Tamer directly via pip (simpler approach)
echo "🚀 Installing Penguin Tamer from PyPI..."
$PYTHON_CMD -m pip install --user penguin-tamer --upgrade

# 5️⃣ Add user's local bin to PATH if needed
USER_BIN="$HOME/.local/bin"
if [ -d "$USER_BIN" ] && [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    echo "📝 Adding $USER_BIN to PATH for this session..."
    export PATH="$USER_BIN:$PATH"
fi

# 6️⃣ Verify installation
if command_exists pt; then
    echo "✅ Penguin Tamer installed successfully!"
    echo "🎯 Version: $(pt --version 2>/dev/null || echo 'installed')"
else
    echo "⚠️ Installation completed, but 'pt' command not found in current PATH."
    echo "📝 Try running: export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "📝 Or restart your terminal and try: pt --help"
fi

# 7️⃣ Done!
echo
echo "🎉 Installation complete!"
echo "👉 Run Penguin Tamer with:"
echo "   pt --help        # Show help"
echo "   pt -d           # Interactive dialog mode"
echo "   pt \"your prompt\" # Quick AI query"
echo
echo "📚 Documentation: https://github.com/Vivatist/penguin-tamer"
echo
echo "💡 If 'pt' is not found, add this line to your ~/.bashrc or ~/.zshrc:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""