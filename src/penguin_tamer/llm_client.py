# Backward compatibility module
from penguin_tamer.llm_clients.base import LLMConfig, AbstractLLMClient
from penguin_tamer.llm_clients.openrouter_client import OpenRouterClient
from penguin_tamer.llm_clients.openai_client import OpenAIClient
from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
from penguin_tamer.llm_clients.factory import ClientFactory

__all__ = ["LLMConfig", "AbstractLLMClient", "OpenRouterClient", "OpenAIClient", "PollinationsClient", "ClientFactory"]

