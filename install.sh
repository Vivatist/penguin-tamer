#!/usr/bin/env bash
set -euo pipefail

echo "=== Penguin Tamer One-Line Installer ==="
echo "========================================="
echo

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

# 4. Install Penguin Tamer via pipx
echo "[+] Installing Penguin Tamer from PyPI..."
echo "    This may take a minute - downloading and installing dependencies..."
echo ""

# Function to show penguin animation
penguin_spin() {
    local pid=$1
    local delay=0.15
    local width=40
    local frames=('🐧' '🐧' '🐧' '🐧')
    local messages=(
        "Waddling to PyPI..."
        "Catching packages..."
        "Installing deps..."
        "Almost there..."
    )
    local pos=0
    local direction=1
    local frame=0
    local msg_idx=0
    local counter=0

    # Hide cursor
    tput civis 2>/dev/null || printf "\033[?25l"

    while ps -p $pid > /dev/null 2>&1; do
        # Clear line
        printf "\r%*s\r" $((width + 40)) ""

        # Build animation line
        local line=""
        local i
        for ((i=0; i<width; i++)); do
            if [ $i -eq $pos ]; then
                line="${line}${frames[$frame]}"
            else
                line="${line} "
            fi
        done

        # Print with message
        printf " %s  %s" "$line" "${messages[$msg_idx]}"

        # Update position
        pos=$((pos + direction))

        # Bounce at edges
        if [ $pos -ge $((width - 1)) ]; then
            direction=-1
        elif [ $pos -le 0 ]; then
            direction=1
            msg_idx=$(( (msg_idx + 1) % ${#messages[@]} ))
        fi

        # Update frame and counter
        frame=$(( (frame + 1) % ${#frames[@]} ))
        counter=$((counter + 1))

        sleep $delay
    done

    # Clear animation line and show cursor
    printf "\r%*s\r" $((width + 40)) ""
    tput cnorm 2>/dev/null || printf "\033[?25h"
}

INSTALL_OUTPUT=""
if command_exists pipx; then
    # Run pipx install in background to show penguin animation
    pipx install penguin-tamer --force > /tmp/pt_install.log 2>&1 &
    INSTALL_PID=$!
    penguin_spin $INSTALL_PID
    wait $INSTALL_PID
    INSTALL_EXIT=$?
    INSTALL_OUTPUT=$(cat /tmp/pt_install.log)
    rm -f /tmp/pt_install.log

    if [ $INSTALL_EXIT -ne 0 ]; then
        echo "[!] Installation failed. Output:"
        echo "$INSTALL_OUTPUT"
        exit 1
    fi
elif $PYTHON_CMD -m pipx --version >/dev/null 2>&1; then
    $PYTHON_CMD -m pipx install penguin-tamer --force > /tmp/pt_install.log 2>&1 &
    INSTALL_PID=$!
    penguin_spin $INSTALL_PID
    wait $INSTALL_PID
    INSTALL_EXIT=$?
    INSTALL_OUTPUT=$(cat /tmp/pt_install.log)
    rm -f /tmp/pt_install.log

    if [ $INSTALL_EXIT -ne 0 ]; then
        echo "[!] Installation failed. Output:"
        echo "$INSTALL_OUTPUT"
        exit 1
    fi
else
    echo "[!] pipx not found after installation. Falling back to pip..."
    $PYTHON_CMD -m pip install --user penguin-tamer --upgrade
fi

echo "[✓] Download and installation complete!"
echo ""

# Extract version from pipx output
INSTALLED_VERSION=""
if echo "$INSTALL_OUTPUT" | grep -q "installed package penguin-tamer"; then
    INSTALLED_VERSION=$(echo "$INSTALL_OUTPUT" | grep "installed package penguin-tamer" | sed -n 's/.*penguin-tamer \([0-9][^,]*\).*/\1/p')
fi

# 5. Add common pipx paths to current session
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

# 6. Verify installation
echo "[*] Verifying installation..."
if command_exists pt; then
    # Try to get version from pt --version command first
    PT_VERSION=$(pt --version 2>/dev/null | cut -d' ' -f2 2>/dev/null || echo "")

    # If that fails, use version from installation output
    if [ -z "$PT_VERSION" ] && [ -n "$INSTALLED_VERSION" ]; then
        PT_VERSION="$INSTALLED_VERSION"
    fi

    # Try pipx list as another fallback
    if [ -z "$PT_VERSION" ] && command_exists pipx; then
        PT_VERSION=$(pipx list 2>/dev/null | grep "penguin-tamer" | sed -n 's/.*penguin-tamer \([0-9][^,)]*\).*/\1/p' || echo "")
    fi

    # Final fallback
    if [ -z "$PT_VERSION" ]; then
        PT_VERSION="unknown"
    fi

    # Colors (ANSI escape codes)
    ORANGE='\033[1;38;5;208m'    # Bold Orange (#e07333)
    TEAL='\033[1;38;5;30m'       # Bold Teal (#007c6e)
    RESET='\033[0m'              # Reset formatting

    # Print colorful success message with penguin celebration
    echo ""
    echo "    🐧  🎉  🐧  🎉  🐧"
    echo ""
    echo -e "${ORANGE}Penguin Tamer${RESET} ${TEAL}${PT_VERSION}${RESET} installed successfully!"
    echo ">>> Location: $(which pt)"
else
    echo "[!] Installation completed, but 'pt' command not found in current PATH."
    echo ""
    echo "[*] Please restart your terminal or run:"
    echo "    source ~/.bashrc"
    echo "    # or"
    echo "    source ~/.zshrc"
    echo ""
    echo "[*] If the issue persists, manually add pipx bin to your PATH:"
    echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
fi

# 7. Final instructions
echo ""
echo "[+] Installation process complete!"
echo "======================================"
echo ""
echo ">>> Run Penguin Tamer with:"
echo "    pt --help                    # Show help"
echo "    pt -s                        # Open settings to configure AI provider"
echo "    pt -d                        # Interactive dialog mode"
echo "    pt --version                 # Check version"
echo "    pt your question             # Quick AI query"
echo ""
echo "[*] Next steps:"
echo "    1. Configure your AI provider:    pt -s"
echo "    2. Test the installation:         pt hello world"
echo ""
echo "[*] Documentation:    https://github.com/Vivatist/penguin-tamer"
echo "[*] Issues:           https://github.com/Vivatist/penguin-tamer/issues"
echo ""
echo "[!] If 'pt' command is not found after restarting terminal:"
echo "    pipx ensurepath"
