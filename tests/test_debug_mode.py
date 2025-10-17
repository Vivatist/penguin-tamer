"""Test debug mode error output."""
from unittest.mock import Mock
from rich.console import Console
from penguin_tamer.error_handlers import ErrorHandler, ErrorContext, ErrorSeverity
from openai import APIConnectionError


def test_error_without_debug_mode():
    """Test error message without debug mode."""
    console = Console()
    handler = ErrorHandler(console=console, debug_mode=False)

    # Create mock request
    mock_request = Mock()
    error = APIConnectionError(request=mock_request)

    context = ErrorContext(
        operation="test operation",
        severity=ErrorSeverity.ERROR,
        recoverable=True
    )
    message = handler.handle(error, context)

    # Should NOT contain debug info, but should be formatted as dim italic
    assert "dim italic" in message
    assert "APIConnectionError" not in message
    assert "Connection error" in message


def test_error_with_debug_mode():
    """Test error message with debug mode enabled."""
    console = Console()
    handler = ErrorHandler(console=console, debug_mode=True)

    # Create mock request
    mock_request = Mock()
    error = APIConnectionError(request=mock_request)

    context = ErrorContext(
        operation="test operation",
        severity=ErrorSeverity.ERROR,
        recoverable=True
    )
    message = handler.handle(error, context)

    # SHOULD contain debug info (now without "Debug:" prefix)
    assert "dim italic" in message
    assert "APIConnectionError" in message
