# AI-eBash

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/ai-ebash.svg)](https://pypi.org/project/ai-ebash/)
[![GitHub Stars](https://img.shields.io/github/stars/Vivatist/ai-ebash.svg)](https://github.com/Vivatist/ai-ebash/stargazers)

> **Console utility for integrating artificial intelligence into your terminal.** Ask AI questions and execute suggested scripts and commands directly from the command line. Perfect for beginners in Linux and Windows administration.

🌍 **Available in:** [English](README.md) | [Русский](docs/locales/README_ru.md)

## Table of Contents

- [AI-eBash](#ai-ebash)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
    - [Linux (pipx)](#linux-pipx)
    - [Linux (DEB Package)](#linux-deb-package)
    - [Windows (Experimental)](#windows-experimental)
  - [Uninstall](#uninstall)
    - [If installed via pipx](#if-installed-via-pipx)
    - [If installed via DEB package](#if-installed-via-deb-package)
    - [If installed via Windows:](#if-installed-via-windows)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Dialog Mode](#dialog-mode)
    - [Code Execution](#code-execution)
  - [Configuration](#configuration)
    - [Initial Setup](#initial-setup)
    - [Supported AI Providers](#supported-ai-providers)
    - [Configuration File](#configuration-file)
  - [Security](#security)
    - [Best Practices](#best-practices)
  - [Contributing](#contributing)
    - [Development Environment Setup](#development-environment-setup)
    - [Contribution Guidelines](#contribution-guidelines)
    - [Areas for Contribution](#areas-for-contribution)
  - [License](#license)
  - [Contacts](#contacts)

## Features

- **Fast AI Queries** - Get instant responses from AI models through the command line
- **Interactive Dialog Mode** - Chat with AI in dialog mode with conversation context preservation
- **Code Execution** - Execute scripts and commands suggested by AI
- **User-Friendly Interface** - Formatted output with syntax highlighting
- **Multiple AI Providers** - Support for OpenAI, Anthropic and other providers
- **Localization Ready** - Support for multiple languages (in development)


## Installation

### Linux (pipx)

**Recommended installation method for Linux**

1. **Install pipx** (if not already installed):
   ```bash
   sudo apt update
   sudo apt install pipx python3-venv -y
   pipx ensurepath
   ```

2. **Restart your terminal**

3. **Install AI-eBash**:
   ```bash
   pipx install ai-ebash
   ```


> **Note:** If pipx doesn't work, you can install via pip:
> ```bash
> pip install ai-ebash
> ```

### Linux (DEB Package)

1. **Download the latest DEB package**:
   ```bash
   wget -qO ai-ebash.deb $(wget -qO- https://api.github.com/repos/Vivatist/ai-ebash/releases/latest \
     | grep "browser_download_url.*\.deb" | cut -d '"' -f 4)
   ```

2. **Install the package**:
   ```bash
   sudo dpkg -i ./ai-ebash.deb
   sudo apt-get install -f -y
   ```

3. **Restart your terminal**

### Windows (Experimental)

1. **Install Python 3.11+** (if not already installed)

2. **Install AI-eBash**:
   ```cmd
   pip install ai-ebash
   ```

3. **Restart your terminal**

## Uninstall

To completely remove the utility:

### If installed via pipx
```bash
pipx uninstall ai-ebash
```

### If installed via DEB package
```bash
sudo apt remove python3-ai-ebash
# Or for complete deletion, including configuration files:
sudo apt purge python3-ai-ebash
```

or you can also use dpkg.:

```bash
sudo dpkg -r python3-ai-ebash
# Or for complete deletion, including configuration files:
sudo dpkg -P python3-ai-ebash
```

### If installed via Windows:
```bash
pip uninstall ai-ebash
```

## Usage

### Basic Usage

```bash
# Simple question
ai What's today's date?

# Get help
ai --help
```

### Dialog Mode

```bash
# Start interactive conversation
ai -d "Help me learn Python"

# In dialog mode you can:
# - Ask clarifying questions
# - Execute code blocks suggested by AI
# - Get command explanations
```

### Code Execution

In dialog mode, AI responses may contain executable code blocks:

```bash
ai -d Show how to create a Python script
```

Then execute the suggested code by entering the block number:

[Code #1]
```python
print("Hello, World!")
```

## Configuration

### Initial Setup

Run the setup mode to configure your AI provider:

```bash
ai -s
```

### Supported AI Providers

- **OpenAI** (GPT-3.5, GPT-4)
- **Anthropic** (Claude)
- **OpenRouter** (Multiple models)
- **Local Models** (Ollama, LM Studio)

### Configuration File

Settings are stored in:
- **Linux:** `~/.config/ai-ebash/config.json`
- **Windows:** `%APPDATA%\ai-ebash\config.json`

## Security

> [!WARNING]
> Never execute code from untrusted sources without verification!

### Best Practices

1. **Verify code before execution**
   ```bash
   # Always check what AI suggests
   ai "Delete all files from /tmp"  # Don't execute this blindly!
   ```

2. **Use safe commands**
   ```bash
   # Prefer these instead of destructive operations
   ai Show disk usage
   ai Show running processes
   ```

## Contributing

I'd be happy to have your help! Here's how to get started:

### Development Environment Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/ai-ebash.git
   cd ai-ebash
   ```

3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

### Contribution Guidelines

- 📝 **Code Style**: Follow PEP 8
- 🧪 **Testing**: Add tests for new features
- 📚 **Documentation**: Update README for new features
- 🔄 **Pull Requests**: Use clear commit messages

### Areas for Contribution

- 🌍 **Localization** - Add support for new languages
- 🤖 **AI Providers** - Integrate new AI services
- 🎨 **UI/UX** - Improve terminal interface
- 📊 **Analytics** - Add usage statistics

## License

This project is licensed under the MIT License.

## Contacts

- **Author**: Andrey Bochkarev
- **Email**: andrey.bch.1976@gmail.com
- **GitHub Issues**: [Report bugs or request features](https://github.com/Vivatist/ai-ebash/issues)
- **Discussions**: [Join community discussions](https://github.com/Vivatist/ai-ebash/discussions)

---

<div align="center">

**Made with ❤️ for the Linux community**

[⭐ Star on GitHub](https://github.com/Vivatist/ai-ebash) • [🐛 Report issues](https://github.com/Vivatist/ai-ebash/issues) • [💬 Join discussions](https://github.com/Vivatist/ai-ebash/discussions)

</div>
