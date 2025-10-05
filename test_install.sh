#!/usr/bin/env bash

# Helper function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Helper function to ask for command name
ask_command_name() {
    local default_name="pt"
    local suggestions=("pt" "ai" "chat" "llm" "ask")
    
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
}

# Test the function
echo "Testing ask_command_name function:"
echo "===================================="
echo
CMD_NAME=$(ask_command_name)
echo
echo "===================================="
echo "Selected command name: $CMD_NAME"
echo "===================================="
