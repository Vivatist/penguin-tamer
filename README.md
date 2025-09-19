# ��� AI-eBash

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/ai-ebash.svg)](https://pypi.org/project/ai-ebash/)
[![GitHub Issues](https://img.shields.io/github/issues/Vivatist/ai-ebash.svg)](https://github.com/Vivatist/ai-ebash/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Vivatist/ai-ebash.svg)](https://github.com/Vivatist/ai-ebash/stargazers)

> **Console utility for integrating artificial intelligence into your terminal.** Ask AI questions and execute suggested scripts and commands directly from the command line. Perfect for Linux administrators and developers.

![Demo](https://via.placeholder.com/800x400/333/fff?text=AI-eBash+Demo)

## ��� Table of Contents

- [✨ Features](#-features)
- [��� Quick Start](#-quick-start)
- [��� Installation](#-installation)
  - [Linux (pipx)](#linux-pipx)
  - [Linux (DEB package)](#linux-deb-package)
  - [Windows](#windows)
- [��� Usage](#-usage)
  - [Basic Usage](#basic-usage)
  - [Dialog Mode](#dialog-mode)
  - [Code Execution](#code-execution)
- [⚙️ Configuration](#️-configuration)
- [��� Security](#-security)
- [��� Contributing](#-contributing)
- [��� License](#-license)
- [��� Contact](#-contact)

## ✨ Features

- ��� **Fast AI Queries** - Get instant responses from AI models via command line
- ��� **Interactive Dialog Mode** - Chat with AI in conversational mode
- ⚡ **Code Execution** - Safely execute AI-suggested scripts and commands
- ��� **Rich Terminal UI** - Beautiful, formatted output with syntax highlighting
- ��� **Multiple AI Providers** - Support for OpenAI, Anthropic, and other providers
- ���️ **Security First** - Built-in safeguards for safe code execution
- ��� **Localization Ready** - Multi-language support
- ��� **Performance Monitoring** - Built-in timing and logging

## ��� Quick Start

```bash
# Install
pipx install ai-ebash

# Ask AI a question
ai "How to list all files in a directory?"

# Start interactive dialog
ai -d "Help me with Linux commands"
```

## ��� Installation

### Linux (pipx) ���

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

> **Note:** If pipx fails, you can also install via pip:
> ```bash
> pip install ai-ebash
> ```

### Linux (DEB Package) ���

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

### Windows (Experimental) ���

1. **Install Python 3.11+** (if not already installed)

2. **Install AI-eBash**:
   ```cmd
   pip install ai-ebash
   ```

3. **Restart your terminal**

## ��� Usage

### Basic Usage

```bash
# Simple question
ai "What is the current date?"

# With specific AI model
ai --model gpt-4 "Explain Docker containers"

# Get help
ai --help
```

### Dialog Mode

```bash
# Start interactive conversation
ai -d "Help me learn Python"

# In dialog mode you can:
# - Ask follow-up questions
# - Execute AI-suggested code blocks
# - Get explanations for commands
```

### Code Execution

In dialog mode, AI responses can include executable code blocks:

```bash
ai -d "Show me how to create a Python script"
```

Then execute suggested code by typing the block number:

```
AI: Here's a simple Python script:

[Code #1]
```python
print("Hello, World!")
```

You: 1
>>> Executing block #1...
Hello, World!
>>>
```

## ⚙️ Configuration

### First Time Setup

Run configuration mode to set up your AI provider:

```bash
ai --settings
```

### Supported AI Providers

- **OpenAI** (GPT-3.5, GPT-4)
- **Anthropic** (Claude)
- **OpenRouter** (Multiple models)
- **Local models** (Ollama, LM Studio)

### Configuration File

Settings are stored in:
- **Linux:** `~/.config/ai-ebash/config.json`
- **Windows:** `%APPDATA%\ai-ebash\config.json`

## ��� Security

> ⚠️ **WARNING:** Never execute code from untrusted sources without review!

### Safety Features

- ✅ **Code Review Required** - All code execution requires explicit user confirmation
- ✅ **Sandboxed Execution** - Commands run in isolated environment
- ✅ **Audit Logging** - All executed commands are logged
- ✅ **Input Validation** - Malicious input is filtered

### Best Practices

1. **Review Code Before Execution**
   ```bash
   # Always check what the AI suggests
   ai "Delete all files in /tmp"  # Don't run this blindly!
   ```

2. **Use Safe Commands**
   ```bash
   # Prefer these over destructive operations
   ai "Show disk usage"
   ai "List running processes"
   ```

3. **Monitor Execution**
   ```bash
   # Enable verbose logging
   ai --verbose "Run system diagnostics"
   ```

## ��� Contributing

We welcome contributions! Here's how to get started:

### Development Setup

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

4. **Run tests**:
   ```bash
   pytest
   ```

### Contribution Guidelines

- ��� **Code Style**: Follow PEP 8
- ��� **Testing**: Add tests for new features
- ��� **Documentation**: Update README for new features
- ��� **Pull Requests**: Use clear commit messages

### Areas for Contribution

- ��� **Localization** - Add support for more languages
- ��� **AI Providers** - Integrate new AI services
- ��� **UI/UX** - Improve terminal interface
- ��� **Analytics** - Add usage statistics
- ��� **Tools** - Create additional utilities

## ��� License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ��� Contact

- **Author**: Andrey Bochkarev
- **Email**: andrey.bch.1976@gmail.com
- **GitHub Issues**: [Report bugs or request features](https://github.com/Vivatist/ai-ebash/issues)
- **Discussions**: [Join community discussions](https://github.com/Vivatist/ai-ebash/discussions)

---

<div align="center">

**Made with ❤️ for the Linux community**

[⭐ Star us on GitHub](https://github.com/Vivatist/ai-ebash) • [��� Report Issues](https://github.com/Vivatist/ai-ebash/issues) • [��� Join Discussions](https://github.com/Vivatist/ai-ebash/discussions)

</div>
