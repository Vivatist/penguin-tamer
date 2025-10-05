# Changelog: Install Script Fix

## Problem
The installation script was hanging when executed via pipe (`curl | bash`) at step 4 (command name selection). The `read` command blocked waiting for user input, which is unavailable in non-interactive pipe mode.

## Solution
Modified `ask_command_name()` function to detect execution mode:

### Non-Interactive Mode (Piped)
- Detects via `[ -t 0 ]` test (checks if stdin is a TTY)
- Automatically selects command name without prompting:
  - Default: `pt`
  - If `pt` exists: tries `ai`, `chat`, `llm`, `ask` in order
- Installation proceeds without user interaction

### Interactive Mode (Direct execution)
- Shows command name menu with suggestions
- Displays which names are taken/available
- Validates input format
- Confirms selection with user

## Files Modified

1. **install.sh**
   - Updated `ask_command_name()` function with TTY detection
   - Added automatic fallback for non-interactive mode
   - Added intelligent command name selection

2. **README.md** (English)
   - Added note about automatic command name selection
   - Added instructions for custom name selection

3. **docs/locales/README_ru.md** (Russian)
   - Added note about automatic command name selection
   - Added instructions for custom name selection

4. **docs/INSTALL_BEHAVIOR.md** (New)
   - Technical documentation of installer behavior
   - Explains TTY detection mechanism
   - Provides troubleshooting guide

## Testing

Tested both modes locally:

```bash
# Non-interactive (simulates curl | bash)
echo "" | bash install.sh
✓ Completes without hanging

# Interactive
bash install.sh
✓ Shows menu and prompts for input
```

## Result
- ✅ One-liner installation now works: `curl -sSL ... | bash`
- ✅ Interactive installation still available for custom names
- ✅ Backwards compatible
- ✅ No breaking changes
