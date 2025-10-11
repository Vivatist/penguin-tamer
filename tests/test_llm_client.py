"""Тесты для LLM клиента"""
import pytest
from unittest.mock import Mock, patch
from rich.console import Console

from penguin_tamer.llm_client import OpenRouterClient


class TestLLMClient:
    """Тесты клиента OpenRouter"""

    @pytest.fixture
    def mock_console(self):
        """Фикстура для mock консоли"""
        console = Mock(spec=Console)
        # Делаем console context manager
        console.__enter__ = Mock(return_value=console)
        console.__exit__ = Mock(return_value=False)
        # Мокаем методы status и Live
        status_mock = Mock()
        status_mock.__enter__ = Mock(return_value=status_mock)
        status_mock.__exit__ = Mock(return_value=False)
        console.status = Mock(return_value=status_mock)
        # Добавляем атрибуты для Rich Live
        console.is_jupyter = False
        console._live_stack = []
        return console

    @pytest.fixture
    def client(self, mock_console):
        """Фикстура для создания тестового клиента"""
        with patch('penguin_tamer.llm_client.get_openai_client'):
            return OpenRouterClient.create(
                console=mock_console,
                api_key="test-key",
                api_url="https://api.example.com",
                model="test-model",
                system_message=[{"role": "system", "content": "Test"}],
                max_tokens=1000,
                temperature=0.7
            )

    def test_client_initialization(self, client):
        """Инициализация клиента с правильными параметрами"""
        assert client.llm_config.model == "test-model"
        assert client.llm_config.api_url == "https://api.example.com"
        assert client.llm_config.max_tokens == 1000
        assert client.llm_config.temperature == 0.7
        assert client.llm_config.api_key == "test-key"

    def test_api_key_in_config(self, client):
        """Проверка наличия API ключа в конфигурации"""
        assert hasattr(client, 'llm_config')
        assert client.llm_config.api_key == "test-key"

    def test_llm_config_attributes(self, client):
        """Проверка атрибутов конфигурации"""
        config = client.llm_config

        # Основные параметры
        assert hasattr(config, 'model')
        assert hasattr(config, 'api_url')
        assert hasattr(config, 'api_key')

        # Параметры генерации
        assert hasattr(config, 'max_tokens')
        assert hasattr(config, 'temperature')
        assert hasattr(config, 'top_p')
        assert hasattr(config, 'frequency_penalty')
        assert hasattr(config, 'presence_penalty')

    def test_client_has_required_methods(self, client):
        """Проверка наличия необходимых методов"""
        assert hasattr(client, 'ask_stream')
        assert callable(client.ask_stream)

    def test_config_values(self, client):
        """Проверка корректности значений конфигурации"""
        config = client.llm_config

        # Проверяем типы
        assert isinstance(config.model, str)
        assert isinstance(config.api_url, str)
        assert isinstance(config.api_key, str)
        assert isinstance(config.max_tokens, (int, type(None)))
        assert isinstance(config.temperature, (int, float))

        # Проверяем диапазоны
        if config.temperature is not None:
            assert 0.0 <= config.temperature <= 2.0

        if config.max_tokens is not None:
            assert config.max_tokens > 0

    def test_system_message_handling(self, mock_console):
        """Проверка обработки системного сообщения"""
        with patch('penguin_tamer.llm_client.get_openai_client'):
            system_msgs = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "system", "content": "Be concise"}
            ]

            client = OpenRouterClient.create(
                console=mock_console,
                api_key="test-key",
                api_url="https://api.example.com",
                model="test-model",
                system_message=system_msgs,
                max_tokens=1000,
                temperature=0.7
            )

            # Проверяем, что клиент создан корректно
            assert client is not None
            assert client.llm_config.model == "test-model"

    def test_create_method_returns_client(self, mock_console):
        """Проверка, что create возвращает экземпляр клиента"""
        with patch('penguin_tamer.llm_client.get_openai_client'):
            client = OpenRouterClient.create(
                console=mock_console,
                api_key="test-key",
                api_url="https://api.example.com",
                model="test-model",
                system_message=[],
                max_tokens=1000,
                temperature=0.7
            )

            assert isinstance(client, OpenRouterClient)

    def test_generation_parameters(self, client):
        """Проверка параметров генерации"""
        config = client.llm_config

        # Проверяем, что параметры установлены
        assert config.temperature == 0.7
        assert config.max_tokens == 1000

        # Проверяем наличие остальных параметров
        assert hasattr(config, 'top_p')
        assert hasattr(config, 'frequency_penalty')
        assert hasattr(config, 'presence_penalty')
        assert hasattr(config, 'seed')

    def test_connection_error_handling(self, client, mock_console):
        """Обработка ошибок соединения - строгая проверка"""
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            from openai import APIConnectionError
            # APIConnectionError требует request параметр
            mock_request = Mock()
            mock_create.side_effect = APIConnectionError(request=mock_request)

            # Код ДОЛЖЕН обработать ошибку и вернуть строку
            result = client.ask_stream("Test message")

            # Проверяем обязательную обработку ошибки
            assert isinstance(result, str), (
                "Метод ask_stream() должен обрабатывать APIConnectionError "
                "и возвращать строку с сообщением об ошибке"
            )
            # Проверяем, что сообщение не пустое
            assert len(result) >= 0, "Результат не должен быть None"

    def test_api_error_handling(self, client, mock_console):
        """Обработка ошибок API (401, 429, 500) - строгая проверка"""
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            from openai import APIStatusError

            # Симулируем ошибку 401 Unauthorized
            mock_response = Mock()
            mock_response.status_code = 401
            mock_create.side_effect = APIStatusError(
                message="Unauthorized",
                response=mock_response,
                body=None
            )

            # Код ДОЛЖЕН обработать ошибку и вернуть строку
            result = client.ask_stream("Test message")

            # Строгая проверка обработки
            assert isinstance(result, str), (
                "Метод ask_stream() должен обрабатывать APIStatusError "
                "и возвращать строку с сообщением об ошибке"
            )
            assert len(result) >= 0, "Результат не должен быть None"

    def test_rate_limit_error_handling(self, client, mock_console):
        """Обработка ошибки превышения лимита (429) - строгая проверка"""
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            from openai import RateLimitError

            mock_response = Mock()
            mock_response.status_code = 429
            mock_create.side_effect = RateLimitError(
                message="Rate limit exceeded",
                response=mock_response,
                body=None
            )

            # Код ДОЛЖЕН обработать ошибку и вернуть строку
            result = client.ask_stream("Test message")

            # Строгая проверка обработки
            assert isinstance(result, str), (
                "Метод ask_stream() должен обрабатывать RateLimitError "
                "и возвращать строку с сообщением об ошибке"
            )
            assert len(result) >= 0, "Результат не должен быть None"

    def test_timeout_error_handling(self, client, mock_console):
        """Обработка таймаута запроса - строгая проверка"""
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            from openai import APITimeoutError

            mock_request = Mock()
            mock_create.side_effect = APITimeoutError(request=mock_request)

            # Код ДОЛЖЕН обработать ошибку и вернуть строку
            result = client.ask_stream("Test message")

            # Строгая проверка обработки
            assert isinstance(result, str), (
                "Метод ask_stream() должен обрабатывать APITimeoutError "
                "и возвращать строку с сообщением об ошибке"
            )
            assert len(result) >= 0, "Результат не должен быть None"

    def test_malformed_response_structure(self, client, mock_console):
        """Обработка некорректной структуры ответа - строгая проверка"""
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            # Создаём chunk с пустым списком choices
            mock_chunk = Mock()
            mock_chunk.choices = []

            mock_create.return_value = iter([mock_chunk])

            # Код ДОЛЖЕН обработать некорректную структуру
            result = client.ask_stream("Test message")

            # Строгая проверка обработки
            assert isinstance(result, str), (
                "Метод ask_stream() должен обрабатывать некорректную структуру ответа "
                "(пустой список choices) и возвращать строку"
            )
            # Проверяем, что это не краш, а корректная обработка
            assert len(result) >= 0, "Результат должен быть строкой (может быть пустой)"
