"""
Response Provider Interface - abstraction for different response sources.

This module defines the interface that separates demo system from LLM client.
Implements Dependency Inversion Principle - high-level modules (llm_client)
don't depend on low-level modules (demo), both depend on abstraction.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional
from dataclasses import dataclass


@dataclass
class StreamChunk:
    """Single chunk of streaming response."""
    content: str
    finish_reason: Optional[str] = None


class ResponseProvider(ABC):
    """
    Abstract interface for providing LLM responses.
    
    Implementations can fetch responses from:
    - Real LLM API (LLMResponseProvider)
    - Demo recordings (DemoResponseProvider)
    - Mock data for testing (MockResponseProvider)
    """
    
    @abstractmethod
    def get_response_stream(self, user_input: str, messages: list) -> Iterator[StreamChunk]:
        """
        Get streaming response for user input.
        
        Args:
            user_input: User's message
            messages: Conversation history
            
        Yields:
            StreamChunk objects
            
        Raises:
            Exception: If response generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider can provide responses.
        
        Returns:
            True if provider is ready to provide responses
        """
        pass


class LLMResponseProvider(ResponseProvider):
    """
    Response provider that fetches from real LLM API.
    
    Wraps OpenAI client and converts API response to StreamChunk format.
    """
    
    def __init__(self, api_client, api_params: dict):
        """
        Initialize LLM response provider.
        
        Args:
            api_client: OpenAI client instance
            api_params: Parameters for API call (model, temperature, etc)
        """
        self.client = api_client
        self.params = api_params
    
    def get_response_stream(self, user_input: str, messages: list) -> Iterator[StreamChunk]:
        """Get streaming response from LLM API."""
        try:
            stream = self.client.chat.completions.create(
                messages=messages,
                stream=True,
                **self.params
            )
            
            for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    if choice.delta and choice.delta.content:
                        yield StreamChunk(
                            content=choice.delta.content,
                            finish_reason=choice.finish_reason
                        )
                        
        except Exception:
            # Let the caller handle the exception
            raise
    
    def is_available(self) -> bool:
        """Check if LLM client is configured."""
        return self.client is not None


class DemoResponseProvider(ResponseProvider):
    """
    Response provider that plays back recorded demo responses.
    
    Reads from demo manager and converts DemoResponse to StreamChunk format.
    """
    
    def __init__(self, demo_manager):
        """
        Initialize demo response provider.
        
        Args:
            demo_manager: DemoManager instance with loaded session
        """
        self.demo_manager = demo_manager
    
    def get_response_stream(self, user_input: str, messages: list) -> Iterator[StreamChunk]:
        """Get streaming response from demo recording."""
        if not self.demo_manager.has_more_responses():
            return
        
        demo_response = self.demo_manager.play_next_response(advance_index=True)
        if demo_response is None:
            return
        
        # Convert demo chunks to StreamChunk format
        for chunk_text in demo_response.chunks:
            yield StreamChunk(content=chunk_text)
    
    def is_available(self) -> bool:
        """Check if demo has more responses."""
        return self.demo_manager.has_more_responses()


class MockResponseProvider(ResponseProvider):
    """
    Mock response provider for testing.
    
    Returns predefined responses without API calls or demo files.
    """
    
    def __init__(self, responses: list[str]):
        """
        Initialize mock provider.
        
        Args:
            responses: List of responses to return
        """
        self.responses = responses
        self.index = 0
    
    def get_response_stream(self, user_input: str, messages: list) -> Iterator[StreamChunk]:
        """Return next predefined response."""
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            
            # Split into chunks for realistic streaming
            chunk_size = 10
            for i in range(0, len(response), chunk_size):
                yield StreamChunk(content=response[i:i+chunk_size])
    
    def is_available(self) -> bool:
        """Check if more mock responses available."""
        return self.index < len(self.responses)
