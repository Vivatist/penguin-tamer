# flake8: noqa: E501
"""
Help content and documentation texts for the configuration menu.
English version.
"""

# Tab help texts - comprehensive documentation for each tab
TAB_HELP = {
    "tab-general": """# PENGUIN TAMER GENERAL SETTINGS
---
`Penguin Tamer` comes with several free models from OpenRouter pre-installed. To use them, obtain an API_KEY from your OpenRouter account.
## Getting **API_KEY** from OpenRouter
- In your account go to "Keys" section [https://openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
- Click "Create Key" and copy the created `API_KEY`
- In `Penguin Tamer` settings, open the LLM edit dialog and paste the copied `API_KEY` in the corresponding field.
---

`Penguin Tamer` can work with any compatible neural network. To do this, you need to specify **Model ID**, **API_URL** and **API_KEY**.

List of compatible free models on OpenRouter website (51 models) - [https://openrouter.ai/models/?q=free](https://openrouter.ai/models/?q=free)

---

Connecting any LLM in `Penguin Tamer` consists of three steps:

# Getting **Model ID**, **API_URL** and **API_KEY** using OpenRouter provider as example

Register on **OpenRouter** [openrouter.ai](https://openrouter.ai)

## 1. Finding **Model ID**
- Go to Models section [https://openrouter.ai/models/?q=free](https://openrouter.ai/models/?q=free)
- Select any model from the list
- In the model description find the `Model ID` field
- Example: `anthropic/claude-3-sonnet`

## 2. **API_URL**
- Same URL for all OpenRouter models: `https://openrouter.ai/api/v1`

## 3. Getting **API_KEY**
- In your account go to "Keys" section [https://openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
- Click "Create Key" and copy the created `API_KEY`

> 💡 **Tip:** Save the obtained `API_KEY` — it won't be available in your account later. This is a security policy of most LLM providers""",

    "tab-params": """# GENERATION PARAMETERS

Configure language model behavior during text generation.

---

## Temperature

**Range:** 0.0 - 2.0 | **Default:** 0.8

Controls creativity and randomness of responses:

- **0.0-0.3** — Deterministic, precise answers
  *Ideal for:* technical tasks, data extraction

- **0.4-0.7** — Balanced responses
  *Ideal for:* general use, Q&A

- **0.8-1.5** — Creative, diverse responses
  *Ideal for:* brainstorming, idea generation

- **1.6-2.0** — Very creative (may be unpredictable)

---

## Max Tokens

**Range:** 1 - ∞ | **Default:** unlimited

Limits the length of model's response:

- **100 tokens** ≈ 75 words ≈ 1-2 paragraphs
- **500 tokens** ≈ 375 words ≈ 1 page
- **2000 tokens** ≈ 1500 words ≈ 3-4 pages

*Leave empty for unlimited response length.*

---

## Top P (Nucleus Sampling)

**Range:** 0.0 - 1.0 | **Default:** 0.95

Alternative way to control randomness. Model selects from top N% most probable tokens.

> 💡 **Tip:** Change **either** `temperature` **or** `top_p`, but not both simultaneously.

---

## Frequency Penalty

**Range:** -2.0 to 2.0 | **Default:** 0.0

Reduces probability of repeating the same tokens:

- **0.3-0.5** — Light repetition reduction *(recommended)*
- **1.0-2.0** — Strong repetition avoidance

---

## Presence Penalty

**Range:** -2.0 to 2.0 | **Default:** 0.0

Increases probability of discussing new topics. Penalizes for the fact of token mention
(unlike frequency_penalty which penalizes for frequency).

---

## Seed

**Type:** integer or empty | **Default:** random

Ensures reproducibility of results. Same seed with same parameters will give identical response.

*Use for:* testing, prompt debugging, demonstrations

---

## Recommendations

Start with **defaults** and adjust gradually

Change **one parameter at a time** to understand the impact

Use **debug mode** to analyze requests

---

## Configuration Examples

### 🤖 System Administration Configuration (default)

```yaml
global:
  temperature: 0.8
  max_tokens: null
  top_p: 0.95
  frequency_penalty: 0.0
  presence_penalty: 0.0
  stop: null
  seed: null
```

**Characteristics:** Balanced approach with moderate creativity

### 🎯 Precise Technical Answers

```yaml
global:
  temperature: 0.2
  max_tokens: 2000
  top_p: 0.9
  frequency_penalty: 0.1
  presence_penalty: 0.0
  stop: null
  seed: null
```

**Use case:** Information extraction, technical documentation, terminal commands

### 💡 Creative Brainstorming

```yaml
global:
  temperature: 1.2
  max_tokens: null
  top_p: 0.98
  frequency_penalty: 0.5
  presence_penalty: 0.6
  stop: null
  seed: null
```

**Use case:** Idea generation, alternative solutions, unconventional approaches

### 📝 Brief Answers

```yaml
global:
  temperature: 0.5
  max_tokens: 500
  top_p: 0.9
  frequency_penalty: 0.2
  presence_penalty: 0.1
  stop: ["\n\n\n"]
  seed: null
```

**Use case:** Quick Q&A, short explanations

### 🧪 Testing and Debugging

```yaml
global:
  temperature: 0.7
  max_tokens: 1000
  top_p: 0.95
  frequency_penalty: 0.0
  presence_penalty: 0.0
  stop: null
  seed: 42  # Fixed result
```

> More details:
> [LLM_PARAMETERS_GUIDE](https://github.com/Vivatist/penguin-tamer/blob/main/docs/LLM_PARAMETERS_GUIDE.md)""",

    "tab-content": """# CUSTOM CONTEXT

Use this field for **system prompts** and **instructions** that should
automatically apply to each of your requests to the LLM.

This allows you to:
- Set the assistant's role and communication style
- Define response format
- Add specific context for your tasks
- Set communication language

---

Note that basic information about your working environment is already available to the model:

- Operating system
- Architecture
- User
- Home directory
- Current directory
- Hostname
- Local IP address
- Python version
- Python executable
- Virtual environment
- Virtual environment path
- System encoding
- Filesystem encoding
- System locale
- Temporary directory
- CPU count
- Current time
- Shell

---

## Examples

### Assistant Role

You are an experienced Python programmer.
Always provide detailed explanations with code examples.


### Response Format

Answer briefly and to the point.
Use bullet lists and headings.


### Communication Style

Communicate in a friendly and informal way,
use real-life examples to explain complex concepts.


### Specialization

You specialize in web development
with focus on React and TypeScript.



> 💡 **Tip:** Be specific — clear instructions give better results""",

    "tab-system": """# SYSTEM SETTINGS

Application behavior settings.

> ! **WARNING:** Resetting settings will delete all your configurations including API_KEY.

## Stream Delay (0.001-0.1 sec)
Pause between text chunks during streaming generation.
Used for debugging.


## Refresh Rate (1-60 Hz)
Terminal window update speed during generation.
Used for debugging.

---

## Debug Mode

- Information about API requests
- Display of tokens and execution time
- Error and warning details

""",

    "tab-appearance": """# INTERFACE SETTINGS

Application appearance and visual design.

---

### Available Themes

| Theme | Description |
|------|----------|
| **Classic** | Neutral, universal |
| **Monokai** | Bright accents on dark background |
| **Dracula** | Soft purple tones |
| **Nord** | Muted blue shades |
| **Solarized Dark** | Comfortable dark theme for eyes |
| **GitHub Dark** | Familiar theme for developers |
| **Matrix** | Cyberpunk in "Matrix" style |
| **Minimal** | Black and white, no distracting colors |




""",
}


# Widget help texts - detailed help for specific input fields
WIDGET_HELP = {
    "temp-input": """[bold cyan]TEMPERATURE[/bold cyan]

Controls creativity and randomness of responses.

[bold]Range:[/bold] 0.0 - 2.0

[bold]Low values (0.0-0.5):[/bold]
• More predictable responses
• Suitable for technical tasks
• Facts and accuracy

[bold]Medium values (0.6-1.0):[/bold]
• Balance of creativity and accuracy
• Suitable for most tasks

[bold]High values (1.1-2.0):[/bold]
• Very creative responses
• Suitable for creative tasks
• May be less accurate""",

    "max-tokens-input": """[bold cyan]MAX TOKENS[/bold cyan]

Limits the length of generated response.

[bold]Values:[/bold]
• Empty or 0 = unlimited
• Number > 0 = maximum token count

[bold]Approximately:[/bold]
• 100 tokens ≈ 75 words
• 500 tokens ≈ 375 words
• 1000 tokens ≈ 750 words

[bold]Recommendations:[/bold]
• Short answers: 100-300
• Medium answers: 500-1000
• Long answers: 1500-3000""",

    "top-p-input": """[bold cyan]TOP P (Nucleus Sampling)[/bold cyan]

Controls diversity of word choice.

[bold]Range:[/bold] 0.0 - 1.0

[bold]How it works:[/bold]
Model selects from top N% most probable tokens.

[bold]Low values (0.1-0.5):[/bold]
• More conservative choice
• Predictable responses

[bold]Medium values (0.6-0.9):[/bold]
• Balance of diversity
• Recommended for most tasks

[bold]High values (0.95-1.0):[/bold]
• Maximum diversity
• More unexpected responses""",

    "freq-penalty-input": """[bold cyan]FREQUENCY PENALTY[/bold cyan]

Reduces repetition of the same words.

[bold]Range:[/bold] -2.0 to 2.0

[bold]Negative values:[/bold]
• Encourages repetitions
• Rarely used

[bold]Zero value (0.0):[/bold]
• No penalties
• Default

[bold]Positive values:[/bold]
• 0.1-0.5: light repetition reduction
• 0.6-1.0: noticeable reduction
• 1.1-2.0: strong reduction (may be unnatural)""",

    "pres-penalty-input": """[bold cyan]PRESENCE PENALTY[/bold cyan]

Encourages discussing new topics.

[bold]Range:[/bold] -2.0 to 2.0

[bold]Negative values:[/bold]
• Focus on current topic
• Deep discussion

[bold]Zero value (0.0):[/bold]
• Natural behavior
• Default

[bold]Positive values:[/bold]
• 0.1-0.5: light topic diversity
• 0.6-1.0: noticeable diversity
• 1.1-2.0: maximum diversity (may lose focus)""",

    "seed-input": """[bold cyan]SEED[/bold cyan]

Ensures reproducibility of results.

[bold]Values:[/bold]
• Empty or 0 = random generation
• Any number = fixed seed

[bold]Use cases:[/bold]
• Testing: same seed will give same results
• Debugging: reproducing issues
• Experiments: comparing different parameters

[bold]Note:[/bold]
Same seed with same parameters will give identical response.""",

    "stream-delay-input": """[bold cyan]STREAM DELAY[/bold cyan]

Pause between text chunks during streaming generation.

[bold]Range:[/bold] 0.001 - 0.1 seconds

[bold]Small values (0.001-0.01):[/bold]
• Fast display
• May flicker

[bold]Medium values (0.02-0.05):[/bold]
• Comfortable speed
• Recommended

[bold]Large values (0.06-0.1):[/bold]
• Slow display
• Easier to read in real-time""",

    "refresh-rate-input": """[bold cyan]REFRESH RATE[/bold cyan]

Interface update speed.

[bold]Range:[/bold] 1-60 Hz (updates per second)

[bold]Low values (1-10):[/bold]
• Less system load
• May be less smooth

[bold]Medium values (10-30):[/bold]
• Optimal balance
• Recommended (10 by default)

[bold]High values (30-60):[/bold]
• Very smooth interface
• Higher CPU load""",

    "debug-switch": """[bold cyan]DEBUG MODE[/bold cyan]

Enables detailed logging.

[bold]Disabled (OFF):[/bold]
• Normal operation mode
• Only important messages
• Recommended for daily use

[bold]Enabled (ON):[/bold]
• Detailed request information
• Parameter logging
• Display of tokens and execution time
• Useful for diagnosing issues

[bold]Use cases:[/bold]
• Development and testing
• Finding API issues
• Performance analysis""",

    "language-select": """[bold cyan]INTERFACE LANGUAGE[/bold cyan]

Select language for menu and messages.

[bold]Available languages:[/bold]
• English (en)
• Русский (ru)

[bold]What will change:[/bold]
• Menu language
• System messages
• Hints and descriptions

[bold]Note:[/bold]
Communication language with LLM depends on your prompt, not this setting.""",

    "theme-select": """[bold cyan]COLOR SCHEME[/bold cyan]

Select interface color scheme.

[bold]Available themes:[/bold]
• Classic (default) - standard theme
• Monokai - dark with contrasting accents
• Dracula - popular dark theme with purple tones
• Nord - cold northern tones
• Solarized Dark - scientifically selected palette, comfortable for eyes
• GitHub Dark - familiar theme for developers in GitHub style
• Matrix - green monochrome in cyberpunk style
• Minimal - minimalist black and white theme

[bold]Theme selection affects:[/bold]
• Interface colors
• Text contrast
• Overall perception

[bold]Recommendation:[/bold]
Choose a theme that is comfortable for your eyes.""",
}
