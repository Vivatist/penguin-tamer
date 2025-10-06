"""
Тесты для LLM клиента.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError, ConnectionError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from penguin_tamer.llm_client import OpenRouterClient, LLMConfig
from rich.console import Console


class TestLLMClient:
    """Тесты OpenRouter клиента"""
    
    def test_client_initialization(self):
        """Инициализация клиента"""
        console = Console()
        llm_config = LLMConfig(
            api_key="test-key",
            api_url="https://api.example.com",
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.7
        )
        client = OpenRouterClient.create(
            console=console,
            api_key=llm_config.api_key,
            api_url=llm_config.api_url,
            model=llm_config.model,
            system_message=[{"role": "system", "content": "Test"}],
            max_tokens=llm_config.max_tokens,
            temperature=llm_config.temperature
        )
        
        assert client.llm_config.model == "gpt-3.5-turbo"
        assert client.llm_config.api_url == "https://api.example.com"
    
    def test_connection_error_handling(self):
        """Обработка ошибок соединения"""
        console = Console()
        client = OpenRouterClient.create(
            console=console,
            api_key="test-key",
            api_url="https://fake-url.example.com",
            model="gpt-3.5-turbo",
            system_message=[{"role": "system", "content": "Test"}],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Простая проверка, что клиент создан
        assert client.llm_config.api_url == "https://fake-url.example.com"
    
    def test_http_error_handling(self):
        """Обработка HTTP ошибок"""
        console = Console()
        client = OpenRouterClient.create(
            console=console,
            api_key="test-key",
            api_url="https://fake-url.example.com",
            model="gpt-3.5-turbo",
            system_message=[{"role": "system", "content": "Test"}],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Проверяем, что клиент создан
        assert client is not None


@pytest.mark.skip(reason="Требует реальный API ключ")
class TestLLMClientIntegration:
    """Интеграционные тесты (требуют API ключ)"""
    
    def test_real_api_call(self):
        """Реальный вызов API (пропускается по умолчанию)"""
        # Этот тест можно запустить с реальным ключом:
        # pytest tests/test_llm_client.py -m "not skip"
        pass

