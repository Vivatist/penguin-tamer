# Mistral AI Client - Usage Guide

## Overview

The `MistralClient` provides native integration with Mistral AI API using SSE (Server-Sent Events) streaming. This client is specifically designed to work directly with Mistral's API without OpenAI SDK dependency issues.

## Key Features

- ✅ **Native SSE Streaming** - Uses `sseclient` for real-time responses
- ✅ **Full API Support** - Supports all Mistral AI parameters
- ✅ **No OpenAI SDK Conflicts** - Direct API integration
- ✅ **Rate Limit Tracking** - Monitors API usage limits
- ✅ **Token Usage Stats** - Tracks prompt and completion tokens

## Configuration

### 1. Get API Key

Get your API key from: https://console.mistral.ai/

### 2. Add to Config

```yaml
supported_Providers:
  Mistral:
    client_name: "mistral"   # Important: must be "mistral", not "openai"
    api_url: "https://api.mistral.ai/v1"
    api_list: "https://api.mistral.ai/v1/models"
    api_key: "YOUR_API_KEY_HERE"
    filter: null
```

### 3. Create LLM Entry

```yaml
supported_LLMs:
  llm_mistral:
    provider: Mistral
    model: "mistral-large-latest"  # or mistral-medium-latest, mistral-small-latest, etc.
```

## Available Models

- `mistral-large-latest` - Most capable model (128k context)
- `mistral-medium-latest` - Balanced performance (128k context)
- `mistral-small-latest` - Fast and efficient (128k context)
- `open-mistral-7b` - Open source model
- `open-mistral-nemo` - Open source Nemo model

## Differences from OpenAI Client

| Feature | MistralClient (SSE) | OpenAI SDK Client |
|---------|---------------------|-------------------|
| Streaming | SSE via `sseclient` | OpenAI SDK |
| API Format | Native Mistral | OpenAI-compatible |
| Seed Parameter | `random_seed` | `seed` |
| Penalties | Not supported | Supported |
| Error Format | "Input should be string" prevented | May occur with list params |

## Common Issues

### ❌ Error: "Input data should be a string, not <class 'list'>"

**Cause**: Using wrong client type in config (e.g., `client_name: "openai"` instead of `client_name: "mistral"`)

**Solution**: 
```yaml
Mistral:
  client_name: "mistral"  # ✅ Correct
  # NOT "openai" ❌
```

### ❌ Authentication Error

**Cause**: Invalid or missing API key

**Solution**: 
1. Check API key at https://console.mistral.ai/
2. Ensure no extra spaces in config
3. Key should start with your account prefix

## Usage Example

```python
from penguin_tamer.llm_clients import MistralClient, LLMConfig
from rich.console import Console

# Create config
config = LLMConfig(
    api_key="your-mistral-api-key",
    api_url="https://api.mistral.ai/v1",
    model="mistral-large-latest",
    temperature=0.7,
    max_tokens=2000
)

# Create client
console = Console()
client = MistralClient(
    console=console,
    system_message=[{"role": "system", "content": "You are a helpful assistant"}],
    llm_config=config
)

# Ask question
response = client.ask_stream("Explain quantum computing in simple terms")
print(response)
```

## API Parameters

### Supported Parameters

- `temperature` (0.0-1.0) - Controls randomness
- `max_tokens` - Maximum response length
- `top_p` (0.0-1.0) - Nucleus sampling
- `random_seed` - For reproducible outputs
- `stop` - Stop sequences (list of strings)

### Not Supported

- `frequency_penalty` - Not documented in Mistral API
- `presence_penalty` - Not documented in Mistral API

## Rate Limits

Mistral provides rate limit information in response headers:
- `x-ratelimit-limit-requests` - Total requests allowed
- `x-ratelimit-remaining-requests` - Requests remaining
- `x-ratelimit-limit-tokens` - Total tokens allowed
- `x-ratelimit-remaining-tokens` - Tokens remaining

Enable debug mode to see these limits:
```yaml
global:
  debug_mode: true
```

## Troubleshooting

### Test Connection

```bash
pt "test message"  # If Mistral is current LLM
```

### Check Client Type

```python
from penguin_tamer.config_manager import config

llm_id = config.current_llm
llm_config = config.get_llm_config(llm_id)
provider = llm_config["provider"]
provider_config = config.get_provider_config(provider)

print(f"Client name: {provider_config['client_name']}")
# Should print: Client name: mistral
```

### Enable Debug Mode

Set in config:
```yaml
global:
  debug_mode: true
```

This will show:
- Full request/response structure
- Token usage statistics
- Rate limit information
- API errors with details

## Comparison with OpenRouter

If you don't have a Mistral API key, you can use Mistral models through OpenRouter:

```yaml
supported_LLMs:
  llm_mistral_via_openrouter:
    provider: "OpenRouter"
    model: "mistralai/mistral-large"
```

**Pros of OpenRouter:**
- ✅ Single API key for multiple providers
- ✅ Free tier available
- ✅ No separate Mistral account needed

**Pros of Direct Mistral:**
- ✅ Native API features
- ✅ Latest models immediately available
- ✅ Direct support from Mistral
- ✅ Potentially lower latency

## Credits

This client uses:
- `sseclient-py` for SSE streaming
- Native Mistral AI API (v1)
- Compatible with penguin-tamer's StreamProcessor architecture
