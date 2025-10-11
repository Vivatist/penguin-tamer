# Contributing to Penguin Tamer

## Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/Vivatist/penguin-tamer.git
cd penguin-tamer
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install in development mode
```bash
pip install -r requirements-dev.txt
```

This will:
- Install all production dependencies from `requirements.txt`
- Install the package in editable mode (`-e .`)
- Allow you to modify code and see changes immediately

### 4. Verify installation
```bash
python -c "from penguin_tamer import __main__; print('✅ Installation successful')"
```

## Project Structure

```
penguin-tamer/
├── src/penguin_tamer/       # Main package
│   ├── __main__.py          # Entry point
│   ├── config_manager.py    # Configuration management
│   ├── llm_client.py        # LLM client
│   ├── default_config.yaml  # Default configuration
│   └── locales/             # Translations
├── pyproject.toml           # Project metadata and dependencies
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

## Running the Application

```bash
# Using the installed command
pt "your prompt here"

# Using Python module
python -m penguin_tamer "your prompt here"

# Dialog mode
pt

# Settings menu
pt -s
```

## Making Changes

1. Make your changes to the code
2. Test your changes
3. Commit and push

## Dependencies

- **Production**: Listed in `pyproject.toml` and `requirements.txt`
- **Development**: Listed in `requirements-dev.txt`

To update dependencies:
1. Update version in `pyproject.toml`
2. Regenerate `requirements.txt`: `pip freeze > requirements.txt`
3. Test the changes

## Questions?

Open an issue on GitHub: https://github.com/Vivatist/penguin-tamer/issues
