#!/usr/bin/env bash
set -euo pipefail

echo "🐧 Penguin Tamer Quick Installer"
echo "--------------------------------"

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1️⃣ Check Python (>=3.11)
echo "🔍 Checking Python installation..."
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
    echo "➡ Please install Python 3.11 or newer first:"
    echo "   • Ubuntu/Debian: sudo apt update && sudo apt install python3.11 python3.11-venv -y"
    echo "   • CentOS/RHEL: sudo yum install python3.11 -y"
    echo "   • Fedora: sudo dnf install python3.11 -y"
    echo "   • Arch: sudo pacman -S python -y"
    echo "   • macOS: brew install python@3.11"
    echo "   • Windows: Download from https://python.org/downloads/"
    exit 1
fi

echo "✅ Found $($PYTHON_CMD --version)"

# 2️⃣ Check and install pipx
echo "🔍 Checking pipx installation..."
if ! command_exists pipx; then
    echo "📦 Installing pipx and dependencies..."
    
    # Install pipx based on OS
    if command_exists apt-get; then
        echo "🔄 Using apt-get (Debian/Ubuntu)..."
        sudo apt-get update -qq
        sudo apt-get install -y pipx python3-venv
    elif command_exists yum; then
        echo "🔄 Using yum (CentOS/RHEL)..."
        sudo yum install -y python3-pip python3-venv
        $PYTHON_CMD -m pip install --user pipx
    elif command_exists dnf; then
        echo "🔄 Using dnf (Fedora)..."
        sudo dnf install -y pipx python3-venv
    elif command_exists pacman; then
        echo "🔄 Using pacman (Arch Linux)..."
        sudo pacman -S --noconfirm python-pipx
    elif command_exists brew; then
        echo "🔄 Using brew (macOS)..."
        brew install pipx
    else
        echo "🔄 Installing via pip..."
        $PYTHON_CMD -m pip install --user pipx
    fi
    
    # Verify pipx installation
    if ! command_exists pipx && ! $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
        echo "❌ Failed to install pipx."
        echo "➡ Please install manually: sudo apt install pipx"
        exit 1
    fi
    
    echo "✅ pipx installed successfully."
else
    echo "✅ pipx is already installed."
fi

# 3️⃣ Ensure pipx path is configured
echo "� Configuring pipx path..."
if command_exists pipx; then
    pipx ensurepath >/dev/null 2>&1 || true
elif $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
    $PYTHON_CMD -m pipx ensurepath >/dev/null 2>&1 || true
fi

# 4️⃣ Install Penguin Tamer via pipx
echo "🚀 Installing Penguin Tamer from PyPI..."
if command_exists pipx; then
    pipx install penguin-tamer --force
elif $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
    $PYTHON_CMD -m pipx install penguin-tamer --force
else
    echo "❌ pipx not found after installation. Falling back to pip..."
    $PYTHON_CMD -m pip install --user penguin-tamer --upgrade
fi

# 5️⃣ Add common pipx paths to current session
PIPX_PATHS=(
    "$HOME/.local/bin"
    "$HOME/Library/Python/3.*/bin"
    "/opt/homebrew/bin"
)

for path_pattern in "${PIPX_PATHS[@]}"; do
    # Handle glob patterns
    for path in $path_pattern; do
        if [ -d "$path" ] && [[ ":$PATH:" != *":$path:"* ]]; then
            export PATH="$path:$PATH"
        fi
    done 2>/dev/null || true
done

# 6️⃣ Verify installation
echo "🔍 Verifying installation..."
if command_exists pt; then
    echo "✅ Penguin Tamer installed successfully!"
    PT_VERSION=$(pt --version 2>/dev/null || echo "unknown")
    echo "🎯 Version: $PT_VERSION"
    echo "📍 Location: $(which pt)"
else
    echo "⚠️ Installation completed, but 'pt' command not found in current PATH."
    echo ""
    echo "� Please restart your terminal or run:"
    echo "   source ~/.bashrc"
    echo "   # or"
    echo "   source ~/.zshrc"
    echo ""
    echo "📝 If the issue persists, manually add pipx bin to your PATH:"
    echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
fi

# 7️⃣ Final instructions
echo ""
echo "🎉 Installation process complete!"
echo "======================================"
echo ""
echo "👉 Run Penguin Tamer with:"
echo "   pt --help              # Show help"
echo "   pt -s                  # Open settings to configure AI provider"
echo "   pt -d                  # Interactive dialog mode"
echo "   pt \"your question\"     # Quick AI query"
echo ""
echo "⚙️ Next steps:"
echo "   1. Configure your AI provider: pt -s"
echo "   2. Test the installation: pt \"hello world\""
echo ""
echo "📚 Documentation: https://github.com/Vivatist/penguin-tamer"
echo "🐛 Issues: https://github.com/Vivatist/penguin-tamer/issues"
echo ""
echo "💡 If 'pt' command is not found after restarting terminal:"
echo "   pipx ensurepath"