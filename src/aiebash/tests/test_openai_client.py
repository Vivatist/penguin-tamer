import sys
from pathlib import Path
import pytest
from unittest.mock import patch
from requests.exceptions import HTTPError

# Добавляем путь к src
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from aiebash.llm_client import OpenRouterClient
    from aiebash.logger import log_execution_time
except ImportError:
    # Если не можем импортировать, создаем заглушки
    class OpenRouterClient:
        pass
    def log_execution_time(func):
        return func


def test_send_chat_raises_connection_error():
    from requests.exceptions import ConnectionError
    client = OpenRouterClient(model="gpt-3.5-turbo", api_url="https://any-url", api_key="fake-key")
    error_msg = "HTTPSConnectionPool(host='openai-proxy.andrey-bch-1976.workers.dev', port=443): Max retries exceeded with url: /v1/chat/completions (Caused by NameResolutionError('<urllib3.connection.HTTPSConnection object at 0x7a8bdb82d3a0>: Failed to resolve 'openai-proxy.andrey-bch-1976.workers.dev' ([Errno -3] Temporary failure in name resolution)'))"
    
    with patch("requests.post", side_effect=ConnectionError(error_msg)):
        with patch("builtins.print") as mock_print:
            with pytest.raises(ConnectionError) as exc_info:
                client.ask("test message")
            mock_print.assert_not_called()
    assert "Max retries exceeded" in str(exc_info.value)


@log_execution_time
def test_send_chat_raises_http_error_and_message_hidden():
    client = OpenRouterClient(model="gpt-3.5-turbo", api_url="https://fake-url", api_key="fake-key")
    error_msg = "403 Client Error: Forbidden for url: https://any-url"
    
    with patch("requests.post", side_effect=HTTPError(error_msg)):
        with patch("builtins.print") as mock_print:
            with pytest.raises(HTTPError) as exc_info:
                client.ask("test message")
            mock_print.assert_not_called()
    assert "403 Client Error: Forbidden" in str(exc_info.value)
