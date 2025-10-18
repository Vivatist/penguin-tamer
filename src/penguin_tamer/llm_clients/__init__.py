"""
LLM Clients package - различные реализации клиентов для взаимодействия с LLM API.

Поддерживаемые клиенты:
- OpenRouterClient - для OpenRouter API
- OpenAIClient - для OpenAI API
- PollinationsClient - для Pollinations API
- MistralClient - для Mistral AI API
"""

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.llm_clients.stream_processor import StreamProcessor
from penguin_tamer.llm_clients.openrouter_client import OpenRouterClient
from penguin_tamer.llm_clients.openai_client import OpenAIClient
from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
from penguin_tamer.llm_clients.mistral_client import MistralClient
from penguin_tamer.llm_clients.factory import ClientFactory

__all__ = [
    'AbstractLLMClient',
    'LLMConfig',
    'StreamProcessor',
    'OpenRouterClient',
    'OpenAIClient',
    'PollinationsClient',
    'MistralClient',
    'ClientFactory',
]
