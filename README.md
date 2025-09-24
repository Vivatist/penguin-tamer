# Ai-eBash!

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/ai-ebash.svg)](https://pypi.org/project/ai-ebash/)
[![GitHub Stars](https://img.shields.io/github/stars/Vivatist/ai-ebash.svg)](https://github.com/Vivatist/ai-ebash/stargazers)

> **Integrate artificial intelligence into your terminal.** Ask questions to ***ChatGPT***, ***Deep Seek***, ***Grok*** and many other large language models (LLM). Execute scripts and commands suggested by the neural network directly from the command line. Perfect for beginners in Linux and Windows administration.

🌍 **Available in:** [English](README.md) | [Русский](/docs/locales/README_ru.md)

![pgram response1](/docs/img/en_intro.gif)

## Table of Contents

- [Ai-eBash!](#ai-ebash)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
    - [Features](#features)
    - [Quick Start](#quick-start)
  - [Connecting to Neural Networks](#connecting-to-neural-networks)
    - [Getting a Token (API\_KEY) and Connecting to a Pre-installed Model](#getting-a-token-api_key-and-connecting-to-a-pre-installed-model)
    - [Adding a New Model](#adding-a-new-model)
      - [Connection Example](#connection-example)
  - [Examples](#examples)
    - [Quick Query](#quick-query)
    - [Dialog Mode](#dialog-mode)
    - [Running Code from AI Response](#running-code-from-ai-response)
  - [Security](#security)
    - [Best Practices](#best-practices)
  - [Installation](#installation)
    - [Ubuntu/Debian (pipx)](#ubuntudebian-pipx)
    - [Ubuntu/Debian (DEB Package)](#ubuntudebian-deb-package)
    - [Windows (Experimental)](#windows-experimental)
  - [Removal](#removal)
    - [If installed with pipx](#if-installed-with-pipx)
    - [If installed as DEB package](#if-installed-as-deb-package)
    - [If installed on Windows](#if-installed-on-windows)
  - [Configuration](#configuration)
    - [Initial Setup](#initial-setup)
    - [Supported AI Providers](#supported-ai-providers)
    - [Configuration File](#configuration-file)
    - [Reset Settings](#reset-settings)
  - [Contributing](#contributing)
    - [Areas for Contribution](#areas-for-contribution)
    - [Development Environment Setup](#development-environment-setup)
    - [Contribution Guidelines](#contribution-guidelines)
  - [License](#license)
  - [Contacts](#contacts)

## Description

### Features

- **Quick AI queries** — Get answers from large language models via the command line
- **No GUI** — Communicate with your chosen AI in natural language and any locale: ai how to install Russian fonts?
- **Interactive dialog mode** — Chat with AI in dialog mode with preserved conversation context
- **Code execution** — Execute scripts and commands suggested by AI in the console
- **Friendly interface** — Formatted output with syntax highlighting — just like you’re used to when working with neural networks
- **Multiple AI providers** — Support for OpenAI, OpenRouter, DeepSeek, Anthropic and other popular providers
- **Multi-language support** — En and Ru are available now. You can [(help with translation)](#contributing) into other languages.

### Quick Start

Install AI-eBash using one of the convenient [methods](#installation).

Run the program `ai who are you?`. In a couple of seconds, the neural network will respond:

![program response1](/docs/img/ru_img1.png)

Try something more complex:

![program response2](/docs/img/ru_img3.png)

On first launch, the program uses a Microsoft-hosted model — **DeepSeek-R1-Lite-Preview** with a public token. This is not the best option since you may see a quota-exceeded message due to high traffic, but it’s fine for a test run.

**For full operation, you need to [obtain](#getting-a-token-api_key-and-connecting-to-a-pre-installed-model) a personal token and add it to the selected model in the program [settings](#installation).**

> [!NOTE]
> AI-eBash can work with any neural network that supports API access. Today this includes almost all large language models (LLMs) on the market. [How to add a new model](#adding-a-new-model).

## Connecting to Neural Networks
AI-eBash ships with several popular models pre-configured, such as **DeepSeek**, **Grok 4 Fast**, **Qwen3 Coder**. However, provider policies don’t allow full operation without authorization. You must obtain a personal token (API_KEY) from the provider’s website.

### Getting a Token (API_KEY) and Connecting to a Pre-installed Model
We recommend the provider [OpenRouter](https://openrouter.ai/models?max_price=0) — simple registration and dozens of popular models available for free with a single token.

- Register on the [website](https://openrouter.ai/)
- Get a token by clicking **[Create API key](https://openrouter.ai/settings/keys)**. Save it — OpenRouter will show it only once!
- Add the token to AI-eBash in the [settings](#configuration) of the selected model
- Make this model the current one

**Done! Now the selected model will answer you in the console. You can connect any other model from this website in the same way.**

> [!NOTE]
> One OpenRouter token is valid for **all** models available from this provider.

A similar procedure applies to other providers, although with **OpenRouter** available, you may not need it.

### Adding a New Model
To add a **new** model to AI-eBash, including a local model or one from major providers, simply enter in AI-eBash [settings](#configuration):
 - API_KEY (your personal token)
 - API_URL (API base URL)
 - model (model name)

You can find this information on the provider’s website in the *API* section.

#### Connection Example
Using the example of the free **Meta: Llama 3.1** model listed on [OpenRouter](https://openrouter.ai/models?max_price=0) among dozens of other free models.

Open the model’s page and find the [API](https://openrouter.ai/meta-llama/llama-3.1-405b-instruct:free/api) section.

Among the connection examples, look for information similar to:

 - **API_URL** — for OpenRouter, this parameter is called ***base_url***
 - **model** — listed as ***model***

How to get **API_KEY** is described [above](#getting-a-token-api_key-and-connecting-to-a-pre-installed-model).

Enter these values (***without quotes***) in AI-eBash settings and set this model as current. Now ***Meta: Llama 3.1*** will answer your questions.

## Examples

### Quick Query

```bash
# Simple question
ai kernel update script
```

### Dialog Mode

To start a dialog, use the `-d` key or simply type `ai` and press `Enter`.
In dialog mode, AI-eBash preserves the conversation context throughout the session.

```bash
a i -d what python version is installed?
```

```bash
a i  # Enter
```

### Running Code from AI Response

When **in dialog mode**, if the response contains code blocks — they are numbered. To run code, simply enter the block number in the console.

![dialog mode](/docs/img/en_img4.gif)

## Security

> [!WARNING]
> Never execute code suggested by the neural network if you’re not sure what it does!

### Best Practices

1. **Review code before execution**
   ```bash
   # Always check what AI suggests
   ai Delete all files from /tmp  # Don’t run this blindly!
   ```

2. **Use safe commands**
   ```bash
   # Prefer these over destructive operations
   ai Show disk usage
   ai Show running processes
   ```

## Installation

### Ubuntu/Debian (pipx)

**Recommended installation method**

1. **Install pipx** (if not installed):
   ```bash
   sudo apt update
   sudo apt install pipx python3-venv -y
   pipx ensurepath
   ```

2. **Restart the terminal**

3. **Install AI-eBash**:
   ```bash
   pipx install ai-ebash
   ```

> **Note:** If pipx doesn’t work, you can install via pip:
> ```bash
> pip install ai-ebash
> ```

### Ubuntu/Debian (DEB Package)

1. **Download the latest DEB package from [GitHub](https://github.com/Vivatist/ai-ebash/releases/latest)**:
   ```bash
   wget -qO ai-ebash.deb $(wget -qO- https://api.github.com/repos/Vivatist/ai-ebash/releases/latest \
     | grep "browser_download_url.*\.deb" | cut -d '"' -f 4)
   ```

2. **Install the package**:
   ```bash
   sudo dpkg -i ./ai-ebash.deb
   sudo apt-get install -f -y
   ```

3. **Restart the terminal**

### Windows (Experimental)

1. **Install Python 3.11+** (if not installed)

2. **Install AI-eBash**:
   ```cmd
   pip install ai-ebash
   ```

3. **Restart the terminal**

## Removal

### If installed with pipx
```bash
pipx uninstall ai-ebash
```

### If installed as DEB package
```bash
sudo apt remove ai-ebash
# Or for complete deletion, including configuration files:
sudo apt purge ai-ebash
```

or you can also use dpkg:

```bash
sudo dpkg -r ai-ebash
# Or for complete deletion, including configuration files:
sudo dpkg -P ai-ebash
```

### If installed on Windows
```bash
pip uninstall ai-ebash
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
- **Local models** (Ollama, LM Studio)

And many others that support API access.

### Configuration File

Settings are stored in:
- **Linux:** `~/.config/ai-ebash/config.yaml`
- **Windows:** `%APPDATA%\ai-ebash\config.yaml`

### Reset Settings

To restore defaults, delete the configuration file manually or run:
```bash
# For Linux
rm ~/.config/ai-ebash/config.yaml
```
```bash
# For Windows
rm %APPDATA%\ai-ebash\config.yaml
```

## Contributing

I’ll be glad for any help!

### Areas for Contribution
 
- 🌍 **Localization** — Adding support for new languages ([template](https://github.com/Vivatist/ai-ebash/blob/main/src/aiebash/locales/template_locale.json)), including [README.md](https://github.com/Vivatist/ai-ebash/blob/main/README.md)
- 🤖 **AI Providers** — Integrating new AI providers
- 🎨 **UI/UX** — Improving the configuration manager interface (yes, it’s not perfect)
- 🔧 **Tools** — Creating additional utilities
- 💡 **Ideas** — I welcome any ideas to improve and develop AI-eBash. [Join the discussion](https://github.com/Vivatist/ai-ebash/discussions/10#discussion-8924293)

Here’s how to get started:

### Development Environment Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/ai-ebash.git
   cd ai-ebash
   ```

3. **Set up the development environment**:
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

## License

This project is licensed under the MIT License.

## Contacts

- **Author**: Andrey Bochkarev
- **GitHub Issues**: [🐛 Report issues](https://github.com/Vivatist/ai-ebash/issues)
- **Discussions**: [💬 Join](https://github.com/Vivatist/ai-ebash/discussions)

---

<div align="center">

**Created with ❤️ for the Linux community**

[⭐ Star on GitHub](https://github.com/Vivatist/ai-ebash)
</div>
