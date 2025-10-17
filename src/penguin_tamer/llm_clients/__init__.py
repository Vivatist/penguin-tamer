"""
LLM Clients package - различные реализации клиентов для взаимодействия с LLM API.

Поддерживаемые клиенты:
- OpenRouterClient - для OpenRouter API
- OpenAIClient - для OpenAI API
- PollinationsClient - для Pollinations API (в разработке)
"""

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.llm_clients.openrouter_client import OpenRouterClient
from penguin_tamer.llm_clients.openai_client import OpenAIClient
from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
from penguin_tamer.llm_clients.factory import ClientFactory

__all__ = [
    'AbstractLLMClient',
    'LLMConfig',
    'OpenRouterClient',
    'OpenAIClient',
    'PollinationsClient',
    'ClientFactory',
]
