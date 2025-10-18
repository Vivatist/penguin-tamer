"""
Client Factory - Фабрика для создания клиентов LLM на основе конфигурации.

Выбирает правильную реализацию клиента (OpenRouter, OpenAI, Pollinations)
на основе параметра client_name из конфигурации провайдера.
"""

from typing import List, Dict
from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.llm_clients.openrouter_client import OpenRouterClient
from penguin_tamer.llm_clients.openai_client import OpenAIClient
from penguin_tamer.llm_clients.pollinations_client import PollinationsClient
from penguin_tamer.llm_clients.mistral_client import MistralClient


class ClientFactory:
    """Factory for creating LLM clients based on configuration."""

    # Mapping client_name -> Client class
    _CLIENT_REGISTRY = {
        'openrouter': OpenRouterClient,
        'openai': OpenAIClient,
        'pollinations': PollinationsClient,
        'mistral': MistralClient,
    }

    @classmethod
    def create_client(
        cls,
        client_name: str,
        console: object,
        system_message: List[Dict[str, str]],
        llm_config: LLMConfig
    ) -> AbstractLLMClient:
        """Create LLM client based on client_name.

        Args:
            client_name: Name of client implementation ('openrouter', 'openai', 'pollinations', 'mistral')
            console: Rich console instance
            system_message: System messages for LLM
            llm_config: Complete LLM configuration

        Returns:
            Concrete LLM client instance

        Raises:
            ValueError: If client_name is not recognized
        """
        client_name_lower = client_name.lower()

        if client_name_lower not in cls._CLIENT_REGISTRY:
            available = ', '.join(cls._CLIENT_REGISTRY.keys())
            raise ValueError(
                f"Unknown client_name: '{client_name}'. "
                f"Available clients: {available}"
            )

        client_class = cls._CLIENT_REGISTRY[client_name_lower]
        return client_class(
            console=console,
            system_message=system_message,
            llm_config=llm_config
        )

    @classmethod
    def get_available_clients(cls) -> List[str]:
        """Get list of available client names.

        Returns:
            List of client names: ['openrouter', 'openai', 'pollinations', 'mistral']
        """
        return list(cls._CLIENT_REGISTRY.keys())

    @classmethod
    def register_client(cls, name: str, client_class: type):
        """Register a new client implementation (for extensions/plugins).

        Args:
            name: Client name (lowercase)
            client_class: Client class (must inherit from AbstractLLMClient)
        """
        if not issubclass(client_class, AbstractLLMClient):
            raise TypeError(
                f"Client class must inherit from AbstractLLMClient, "
                f"got {client_class.__name__}"
            )
        cls._CLIENT_REGISTRY[name.lower()] = client_class

    @classmethod
    def get_client_for_static_methods(cls, client_name: str) -> type:
        """Get client class for using static methods (like fetch_models).

        Args:
            client_name: Name of client implementation

        Returns:
            Client class (not instance)

        Raises:
            ValueError: If client_name is not recognized
        """
        client_name_lower = client_name.lower()

        if client_name_lower not in cls._CLIENT_REGISTRY:
            available = ', '.join(cls._CLIENT_REGISTRY.keys())
            raise ValueError(
                f"Unknown client_name: '{client_name}'. "
                f"Available clients: {available}"
            )

        return cls._CLIENT_REGISTRY[client_name_lower]
