"""
Pollinations Client - Реализация клиента для Pollinations API.

В РАЗРАБОТКЕ: Базовая структура для будущей реализации.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from penguin_tamer.llm_clients.base import AbstractLLMClient


@dataclass
class PollinationsClient(AbstractLLMClient):
    """Pollinations-specific implementation of LLM client.
    
    TODO: Implement Pollinations API integration.
    Currently raises NotImplementedError for all methods.
    """

    def ask_stream(self, user_input: str) -> str:
        """Send streaming request to Pollinations API.
        
        Args:
            user_input: User's message text
            
        Returns:
            Complete AI response text
            
        Raises:
            NotImplementedError: Pollinations client not yet implemented
        """
        raise NotImplementedError(
            "PollinationsClient is not yet implemented. "
            "Please use OpenRouterClient or OpenAIClient instead."
        )

    @staticmethod
    def fetch_models(api_list_url: str, api_key: str = "", model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """Fetch list of available models from Pollinations API.
        
        Args:
            api_list_url: URL endpoint to fetch models list
            api_key: API key for authentication (optional)
            model_filter: Filter string (optional)
        
        Returns:
            Empty list (not implemented yet)
        """
       
        raise NotImplementedError(
            "Implement Pollinations models fetching"
        )

    def get_available_models(self, model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """Get list of available models for Pollinations.
        
        Args:
            model_filter: Optional filter string
        
        Returns:
            Empty list (not implemented yet)
        """
        raise NotImplementedError(
            "Implement Pollinations models fetching"
        )
