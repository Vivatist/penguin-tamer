# Install Script Behavior

## Command Name Selection

The `install.sh` script automatically handles command name selection differently based on how it's executed:

### Non-Interactive Mode (Piped from curl)

When the script is piped from curl:
```bash
curl -sSL https://raw.githubusercontent.com/Vivatist/penguin-tamer/main/install.sh | bash
```

The script:
1. Detects non-interactive mode (no TTY)
2. Automatically selects a command name:
   - Uses `pt` by default
   - If `pt` is already taken, tries: `ai`, `chat`, `llm`, `ask` (in order)
   - Installs silently without prompting

This ensures the installation completes without hanging on user input.

### Interactive Mode (Direct execution)

When the script is downloaded and run directly:
```bash
curl -sSL -o install.sh https://raw.githubusercontent.com/Vivatist/penguin-tamer/main/install.sh
bash install.sh
```

The script:
1. Detects interactive mode (TTY available)
2. Shows available command name suggestions
3. Indicates which names are already taken
4. Prompts user to enter their preferred name
5. Validates the input:
   - Must start with lowercase letter
   - Can contain: lowercase letters, numbers, hyphens, underscores
   - Must not conflict with existing commands
6. Asks for confirmation before proceeding

## Technical Implementation

The detection is done using the bash test `[ -t 0 ]`:
- Returns true if stdin (fd 0) is a terminal (TTY)
- Returns false if stdin is a pipe (e.g., from curl)

Example from the code:
```bash
if [ -t 0 ]; then
    # Interactive mode - show menu and prompt
else
    # Non-interactive mode - use defaults
fi
```

## Command Name Symlink

After installation via pipx, the main command is always `pt`. If a custom name is chosen:
1. The script creates a symlink: `$CUSTOM_NAME -> pt`
2. Both `pt` and `$CUSTOM_NAME` work identically
3. The symlink is placed in the same pipx bin directory

Example:
```bash
# If user chooses "ai"
ln -sf $HOME/.local/bin/pt $HOME/.local/bin/ai

# Now both work:
pt --help
ai --help
```

## Troubleshooting

If installation hangs:
- You're likely running in a context where stdin isn't fully piped
- Solution: Download and run the script directly (interactive mode)

If command isn't found after installation:
- Add pipx bin to PATH: `pipx ensurepath`
- Or manually: `export PATH="$HOME/.local/bin:$PATH"`
- Restart your terminal

## Testing

Test non-interactive mode locally:
```bash
echo "" | bash install.sh
```

Test interactive mode:
```bash
bash install.sh
```
