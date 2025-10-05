#!/usr/bin/env bash
set -euo pipefail

echo "=== Penguin Tamer One-Line Installer ==="
echo "========================================="
echo

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Helper function to ask for command name
ask_command_name() {
    local default_name="pt"
    local suggestions=("pt" "ai" "chat" "llm" "ask")
    
    # Check if running in interactive mode (not piped from curl)
    if [ -t 0 ]; then
        # Interactive mode - show menu
        echo "[*] Choose command name for Penguin Tamer:"
        echo "    Available suggestions: ${suggestions[*]}"
        echo "    Or enter your own custom name"
        echo
        
        # Check which suggestions are already taken
        local available=()
        local taken=()
        for cmd in "${suggestions[@]}"; do
            if command_exists "$cmd"; then
                taken+=("$cmd")
            else
                available+=("$cmd")
            fi
        done
        
        if [ ${#taken[@]} -gt 0 ]; then
            echo "[!] Already taken: ${taken[*]}"
        fi
        if [ ${#available[@]} -gt 0 ]; then
            echo "[+] Available: ${available[*]}"
        fi
        echo
        
        # Interactive prompt
        while true; do
            read -p ">>> Enter command name [default: $default_name]: " cmd_name
            cmd_name="${cmd_name:-$default_name}"
            
            # Validate command name
            if [[ ! "$cmd_name" =~ ^[a-z][a-z0-9_-]*$ ]]; then
                echo "[!] Invalid name. Use lowercase letters, numbers, hyphens, and underscores only."
                continue
            fi
            
            # Check if already exists
            if command_exists "$cmd_name"; then
                echo "[!] Command '$cmd_name' is already taken. Try another name."
                continue
            fi
            
            # Confirm choice
            read -p ">>> Use '$cmd_name' as command name? [Y/n]: " confirm
            confirm="${confirm:-Y}"
            if [[ "$confirm" =~ ^[Yy] ]]; then
                echo "$cmd_name"
                return 0
            fi
        done
    else
        # Non-interactive mode (piped) - use default or first available
        local chosen_name="$default_name"
        
        # If default is taken, try to find first available from suggestions
        if command_exists "$chosen_name"; then
            for cmd in "${suggestions[@]}"; do
                if ! command_exists "$cmd"; then
                    chosen_name="$cmd"
                    break
                fi
            done
        fi
        
        echo "$chosen_name"
        return 0
    fi
}

# 1. Check Python (>=3.11)
echo "[*] Checking Python installation..."
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
    echo "[!] Python 3.11+ not found."
    echo ">>> Please install Python 3.11 or newer first:"
    echo "    - Ubuntu/Debian:  sudo apt update && sudo apt install python3.11 python3.11-venv -y"
    echo "    - CentOS/RHEL:    sudo yum install python3.11 -y"
    echo "    - Fedora:         sudo dnf install python3.11 -y"
    echo "    - Arch Linux:     sudo pacman -S python -y"
    echo "    - macOS:          brew install python@3.11"
    echo "    - Windows:        Download from https://python.org/downloads/"
    exit 1
fi

echo "[+] Found $($PYTHON_CMD --version)"

# 2. Check and install pipx
echo "[*] Checking pipx installation..."
if ! command_exists pipx; then
    echo "[+] Installing pipx and dependencies..."
    
    # Install pipx based on OS
    if command_exists apt-get; then
        echo ">>> Using apt-get (Debian/Ubuntu)..."
        sudo apt-get update -qq
        sudo apt-get install -y pipx python3-venv
    elif command_exists yum; then
        echo ">>> Using yum (CentOS/RHEL)..."
        sudo yum install -y python3-pip python3-venv
        $PYTHON_CMD -m pip install --user pipx
    elif command_exists dnf; then
        echo ">>> Using dnf (Fedora)..."
        sudo dnf install -y pipx python3-venv
    elif command_exists pacman; then
        echo ">>> Using pacman (Arch Linux)..."
        sudo pacman -S --noconfirm python-pipx
    elif command_exists brew; then
        echo ">>> Using brew (macOS)..."
        brew install pipx
    else
        echo ">>> Installing via pip..."
        $PYTHON_CMD -m pip install --user pipx
    fi
    
    # Verify pipx installation
    if ! command_exists pipx && ! $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
        echo "[!] Failed to install pipx."
        echo ">>> Please install manually: sudo apt install pipx"
        exit 1
    fi
    
    echo "[+] pipx installed successfully."
else
    echo "[+] pipx is already installed."
fi

# 3. Ensure pipx path is configured
echo "[*] Configuring pipx path..."
if command_exists pipx; then
    pipx ensurepath >/dev/null 2>&1 || true
elif $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
    $PYTHON_CMD -m pipx ensurepath >/dev/null 2>&1 || true
fi

# 4. Ask for command name
echo
CMD_NAME=$(ask_command_name)
echo "[+] Installing with command name: $CMD_NAME"
echo

# 5. Install Penguin Tamer via pipx
echo "[+] Installing Penguin Tamer from PyPI..."
INSTALL_OUTPUT=""
if command_exists pipx; then
    INSTALL_OUTPUT=$(pipx install penguin-tamer --force 2>&1)
elif $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
    INSTALL_OUTPUT=$($PYTHON_CMD -m pipx install penguin-tamer --force 2>&1)
else
    echo "[!] pipx not found after installation. Falling back to pip..."
    $PYTHON_CMD -m pip install --user penguin-tamer --upgrade
fi

# Extract version from pipx output
INSTALLED_VERSION=""
if echo "$INSTALL_OUTPUT" | grep -q "installed package penguin-tamer"; then
    INSTALLED_VERSION=$(echo "$INSTALL_OUTPUT" | grep "installed package penguin-tamer" | sed -n 's/.*penguin-tamer \([0-9][^,]*\).*/\1/p')
fi

# 6. Create alias/symlink if custom name requested
if [ "$CMD_NAME" != "pt" ]; then
    echo "[*] Creating command alias: $CMD_NAME -> pt"
    
    # Determine pipx bin directory
    PIPX_BIN_DIR=""
    if command_exists pipx; then
        PIPX_BIN_DIR=$(pipx environment --value PIPX_BIN_DIR 2>/dev/null)
    fi
    
    # Fallback to common locations if environment command fails
    if [ -z "$PIPX_BIN_DIR" ]; then
        if [ -d "$HOME/.local/bin" ]; then
            PIPX_BIN_DIR="$HOME/.local/bin"
        elif [ -d "/usr/local/bin" ]; then
            PIPX_BIN_DIR="/usr/local/bin"
        else
            PIPX_BIN_DIR="$HOME/.local/bin"
        fi
    fi
    
    # Wait a moment for pipx to finish creating the binary
    sleep 1
    
    # Try to find pt in common locations
    PT_PATH=""
    for search_path in "$PIPX_BIN_DIR" "$HOME/.local/bin" "/usr/local/bin"; do
        if [ -f "$search_path/pt" ]; then
            PT_PATH="$search_path/pt"
            PIPX_BIN_DIR="$search_path"
            break
        fi
    done
    
    # Create symlink
    if [ -n "$PT_PATH" ] && [ -f "$PT_PATH" ]; then
        if ln -sf "$PT_PATH" "$PIPX_BIN_DIR/$CMD_NAME" 2>/dev/null; then
            echo "[+] Command '$CMD_NAME' is now available (symlink to pt)"
            echo ">>> Location: $PIPX_BIN_DIR/$CMD_NAME -> $PT_PATH"
        else
            echo "[!] Could not create symlink. You can manually create it:"
            echo "    ln -sf $PT_PATH $PIPX_BIN_DIR/$CMD_NAME"
            echo "    Or add alias to your shell config:"
            echo "    alias $CMD_NAME='pt'"
        fi
    else
        echo "[!] 'pt' not found in expected locations"
        echo "    Searched: $PIPX_BIN_DIR, $HOME/.local/bin, /usr/local/bin"
        echo "    You can manually create alias after restart:"
        echo "    alias $CMD_NAME='pt'"
        echo "    Or create symlink when 'pt' appears:"
        echo "    ln -sf \$(which pt) \$(dirname \$(which pt))/$CMD_NAME"
    fi
fi

# 7. Add common pipx paths to current session
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

# 8. Verify installation
echo "[*] Verifying installation..."
if command_exists "$CMD_NAME"; then
    echo "[+] Penguin Tamer installed successfully!"
    
    # Try to get version from command --version first
    CMD_VERSION=$($CMD_NAME --version 2>/dev/null | cut -d' ' -f2 2>/dev/null || echo "")
    
    # If that fails, use version from installation output
    if [ -z "$CMD_VERSION" ] && [ -n "$INSTALLED_VERSION" ]; then
        CMD_VERSION="$INSTALLED_VERSION"
    fi
    
    # Try pipx list as another fallback
    if [ -z "$CMD_VERSION" ] && command_exists pipx; then
        CMD_VERSION=$(pipx list 2>/dev/null | grep "penguin-tamer" | sed -n 's/.*penguin-tamer \([0-9][^,)]*\).*/\1/p' || echo "")
    fi
    
    # Final fallback
    if [ -z "$CMD_VERSION" ]; then
        CMD_VERSION="installed"
    fi
    
    echo ">>> Version: $CMD_VERSION"
    echo ">>> Location: $(which $CMD_NAME)"
else
    echo "[!] Installation completed, but '$CMD_NAME' command not found in current PATH."
    echo ""
    echo "[*] Please restart your terminal or run:"
    echo "    source ~/.bashrc"
    echo "    # or"
    echo "    source ~/.zshrc"
    echo ""
    echo "[*] If the issue persists, manually add pipx bin to your PATH:"
    echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
fi

# 9. Final instructions
echo ""
echo "[+] Installation process complete!"
echo "======================================"
echo ""
echo ">>> Run Penguin Tamer with:"
echo "    $CMD_NAME --help                    # Show help"
echo "    $CMD_NAME -s                        # Open settings to configure AI provider"
echo "    $CMD_NAME -d                        # Interactive dialog mode"
echo "    $CMD_NAME \"your question\"           # Quick AI query"
echo ""
echo "[*] Next steps:"
echo "    1. Configure your AI provider:    $CMD_NAME -s"
echo "    2. Test the installation:         $CMD_NAME \"hello world\""
echo ""
echo "[*] Documentation:    https://github.com/Vivatist/penguin-tamer"
echo "[*] Issues:           https://github.com/Vivatist/penguin-tamer/issues"
echo ""
echo "[!] If '$CMD_NAME' command is not found after restarting terminal:"
echo "    pipx ensurepath"