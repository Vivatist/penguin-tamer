"""
Mistral Client - Implementation for Mistral AI API.

Uses native Mistral AI API with SSE streaming:
POST https://api.mistral.ai/v1/chat/completions
API documentation: https://docs.mistral.ai/
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
import json

from penguin_tamer.llm_clients.base import AbstractLLMClient, LLMConfig
from penguin_tamer.utils.lazy_import import lazy_import

# Lazy import requests for API calls
@lazy_import
def get_requests_module():
    """Lazy import requests for API requests"""
    import requests
    return requests

# Lazy import sseclient for SSE streaming
@lazy_import
def get_sseclient_module():
    """Lazy import sseclient for SSE streaming"""
    import sseclient
    return sseclient


@dataclass
class MistralClient(AbstractLLMClient):
    """Mistral AI-specific implementation of LLM client.
    
    Uses native Mistral AI API with SSE streaming:
    POST https://api.mistral.ai/v1/chat/completions
    Requires API key for authentication.
    
    This class contains ONLY Mistral API-specific logic:
    - Request parameter preparation (Mistral format)
    - SSE streaming support
    - Response parsing (SSE events)
    """

    # === API-specific methods (request formation and response parsing) ===

    def _prepare_api_params(self, user_input: str) -> dict:
        """Prepare parameters for Mistral AI API request.
        
        Mistral uses OpenAI-compatible format with some differences:
        POST https://api.mistral.ai/v1/chat/completions
        
        Args:
            user_input: User input text
            
        Returns:
            dict: Parameters for Mistral API endpoint
        """
        # Build messages list including current request
        # Do NOT add to self.messages - StreamProcessor will do it
        messages = self.messages + [{"role": "user", "content": user_input}] if user_input else self.messages

        # Mistral uses OpenAI-compatible format
        api_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        # Add temperature if set
        if self.temperature is not None and self.temperature != 1.0:
            api_params["temperature"] = self.temperature

        # Add max_tokens if set
        if self.max_tokens is not None and self.max_tokens > 0:
            api_params["max_tokens"] = self.max_tokens

        # Add top_p if set
        if self.top_p is not None and self.top_p != 1.0:
            api_params["top_p"] = self.top_p

        # Mistral uses 'random_seed' instead of 'seed'
        if self.seed is not None:
            api_params["random_seed"] = self.seed

        # Mistral does not support frequency_penalty and presence_penalty in the same way
        # They are not documented, so we skip them

        # Add stop sequences if set
        if self.stop is not None:
            api_params["stop"] = self.stop

        return api_params

    def _create_stream(self, api_params: dict):
        """Create SSE stream for Mistral AI API.
        
        Mistral supports streaming via SSE with OpenAI-compatible format.
        
        Args:
            api_params: Request parameters (Mistral format)
            
        Returns:
            Iterator of SSE events for streaming processing
        """
        requests = get_requests_module()
        sseclient = get_sseclient_module()
        
        # Mistral API endpoint
        url = f"{self.api_url}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(url, headers=headers, json=api_params, stream=True, timeout=30)
            response.raise_for_status()
            client = sseclient.SSEClient(response)
            return client.events()
        except Exception as e:
            raise RuntimeError(f"Mistral API error: {e}")

    def _extract_chunk_content(self, chunk) -> Optional[str]:
        """Extract text content from SSE event.
        
        Mistral uses OpenAI-compatible format:
        {"choices": [{"delta": {"content": "..."}}]}
        
        Args:
            chunk: SSE event from Mistral
            
        Returns:
            str or None: Text from chunk or None if empty/done
        """
        # chunk is SSE event
        if not hasattr(chunk, 'data'):
            return None
            
        data = chunk.data.strip()
        
        # Check for completion marker
        if data == '[DONE]':
            return None
            
        try:
            parsed = json.loads(data)
            content = parsed.get('choices', [{}])[0].get('delta', {}).get('content')
            return content
        except (json.JSONDecodeError, IndexError, KeyError):
            return None

    def _extract_usage_stats(self, chunk) -> Optional[dict]:
        """Extract usage statistics from SSE event.
        
        Mistral provides usage in the last chunk.
        
        Args:
            chunk: SSE event from Mistral
            
        Returns:
            dict or None: {'prompt_tokens': int, 'completion_tokens': int} or None
        """
        if not hasattr(chunk, 'data'):
            return None
            
        data = chunk.data.strip()
        
        if data == '[DONE]':
            return None
            
        try:
            parsed = json.loads(data)
            usage = parsed.get('usage')
            if usage:
                return {
                    'prompt_tokens': usage.get('prompt_tokens', 0),
                    'completion_tokens': usage.get('completion_tokens', 0)
                }
        except (json.JSONDecodeError, KeyError):
            pass
        
        return None

    def _extract_rate_limits(self, stream) -> None:
        """Extract rate limit information from Mistral API response.
        
        Mistral provides rate limit info in response headers:
        x-ratelimit-limit-requests, x-ratelimit-remaining-requests, etc.
        
        Args:
            stream: SSEClient stream
        """
        try:
            # SSEClient wraps the response, try to access headers
            if hasattr(stream, 'resp') and hasattr(stream.resp, 'headers'):
                headers = stream.resp.headers
            elif hasattr(stream, 'response') and hasattr(stream.response, 'headers'):
                headers = stream.response.headers
            else:
                return
            
            # Mistral rate limit headers (similar to OpenAI)
            if 'x-ratelimit-limit-requests' in headers:
                self.rate_limit_requests = int(headers['x-ratelimit-limit-requests'])
            if 'x-ratelimit-limit-tokens' in headers:
                self.rate_limit_tokens = int(headers['x-ratelimit-limit-tokens'])
            if 'x-ratelimit-remaining-requests' in headers:
                self.rate_limit_remaining_requests = int(headers['x-ratelimit-remaining-requests'])
            if 'x-ratelimit-remaining-tokens' in headers:
                self.rate_limit_remaining_tokens = int(headers['x-ratelimit-remaining-tokens'])
        except (AttributeError, ValueError, KeyError):
            # Silently ignore if headers are not accessible
            pass

    # === Main streaming method ===

    def ask_stream(self, user_input: str) -> str:
        """Main method for streaming generation with Mistral.
        
        Delegates UI/orchestration to StreamProcessor,
        only responsible for parameter preparation.
        
        Args:
            user_input: User query
            
        Returns:
            str: Complete response from LLM
        """
        from penguin_tamer.llm_clients.stream_processor import StreamProcessor
        
        processor = StreamProcessor(self)
        return processor.process(user_input)

    # === Model listing methods ===

    @staticmethod
    def fetch_models(
        api_list_url: str,
        api_key: str = "",
        model_filter: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Fetch list of available models from Mistral AI API.
        
        Mistral requires API key for authentication.
        Returns models in format: {"data": [{"id": "...", ...}]}
        
        Args:
            api_list_url: Mistral models endpoint (e.g., "https://api.mistral.ai/v1/models")
            api_key: API key for authentication (required for Mistral)
            model_filter: Filter string to match against model id (case-insensitive, optional)
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Display Name"}, ...]
            Returns empty list on error.
        
        Example:
            >>> models = MistralClient.fetch_models(
            ...     "https://api.mistral.ai/v1/models",
            ...     api_key="..."
            ... )
            >>> print(models[0])
            {'id': 'mistral-large-latest', 'name': 'Mistral Large'}
        """
        try:
            requests = get_requests_module()
            
            # Mistral requires API key
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(api_list_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Mistral format: {"data": [{"id": "...", ...}]}
            models = []
            if "data" in data and isinstance(data["data"], list):
                for model in data["data"]:
                    if isinstance(model, dict) and "id" in model:
                        model_id = model["id"]
                        # Format model name from id
                        # e.g., "mistral-large-latest" -> "Mistral Large"
                        parts = model_id.replace('-latest', '').replace('-', ' ').split()
                        model_name = ' '.join(word.capitalize() for word in parts)
                        models.append({"id": model_id, "name": model_name})
            
            # Apply filter if specified
            if model_filter:
                filter_lower = model_filter.lower()
                models = [
                    model for model in models
                    if filter_lower in model["id"].lower() or filter_lower in model["name"].lower()
                ]
            
            return models
        
        except Exception:
            # Return empty list on any error
            return []

    def get_available_models(self, model_filter: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get list of available models for current client configuration.
        
        Instance method that uses client's api_url with "/models" endpoint
        and client's api_key for authentication.
        
        Args:
            model_filter: Optional filter string to match against model id
        
        Returns:
            List of model dictionaries: [{"id": "model-id", "name": "Model Name"}, ...]
            Returns empty list on error.
        
        Example:
            >>> client = MistralClient(...)
            >>> models = client.get_available_models(model_filter="large")
        """
        # Determine URL for fetching models list
        # Usually base_url + "/models"
        base_url = self.api_url.rstrip('/')
        
        # If URL already contains "/chat/completions" or other endpoint, remove it
        if '/chat/completions' in base_url:
            base_url = base_url.split('/chat/completions')[0]
        
        api_list_url = f"{base_url}/models"
        
        # Use static method to fetch models
        return self.fetch_models(api_list_url, self.api_key, model_filter)
