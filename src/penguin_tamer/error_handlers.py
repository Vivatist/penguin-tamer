"""Centralized error handling system for Penguin Tamer.

This module provides:
- Centralized exception handling
- Custom exception hierarchy
- Error context management
- Logging integration
- User-friendly error messages
"""
import functools
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum

from penguin_tamer.i18n import t
from penguin_tamer.utils.lazy_import import lazy_import


# Ленивый импорт исключений OpenAI
@lazy_import
def get_openai_exceptions():
    """Lazy import of OpenAI exceptions."""
    from openai import (
        RateLimitError, APIError as OpenAIAPIError, OpenAIError,
        AuthenticationError, APIConnectionError, PermissionDeniedError,
        NotFoundError, BadRequestError, APIStatusError, APITimeoutError
    )
    return {
        'RateLimitError': RateLimitError,
        'APIError': OpenAIAPIError,
        'OpenAIError': OpenAIError,
        'AuthenticationError': AuthenticationError,
        'APIConnectionError': APIConnectionError,
        'PermissionDeniedError': PermissionDeniedError,
        'NotFoundError': NotFoundError,
        'BadRequestError': BadRequestError,
        'APIStatusError': APIStatusError,
        'APITimeoutError': APITimeoutError
    }


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    user_message: Optional[str] = None
    technical_details: Optional[Dict[str, Any]] = None
    recoverable: bool = True


class PenguinTamerError(Exception):
    """Base exception for all Penguin Tamer errors."""

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.context = context or ErrorContext(operation="unknown")
        self.original_error = original_error


class APIError(PenguinTamerError):
    """Errors related to API communication."""
    pass


class ConfigurationError(PenguinTamerError):
    """Errors related to configuration."""
    pass


class ValidationError(PenguinTamerError):
    """Errors related to input validation."""
    pass


class ErrorHandler:
    """Centralized error handler with strategy pattern using configuration dictionary."""

    def __init__(self, console=None, debug_mode: bool = False):
        """Initialize error handler.

        Args:
            console: Rich console for output
            debug_mode: Enable detailed error information
        """
        self.console = console
        self.debug_mode = debug_mode
        self.link_url = t("docs_link_get_api_key")

        # Configuration dictionary: exception name -> (message template, severity, extractor)
        # extractor is optional function to extract additional data from error
        self._error_configs = {
            'APIConnectionError': (
                "Connection error: Unable to connect to API. Please check your internet connection.",
                ErrorSeverity.ERROR,
                None
            ),
            'AuthenticationError': (
                "Error 401: Authentication failed. Check your API_KEY. "
                "[link={link}]How to get a key?[/link]",
                ErrorSeverity.CRITICAL,
                None
            ),
            'RateLimitError': (
                "Error 429: Exceeding the quota. Message from the provider: {body_msg}. "
                "You can change LLM in settings: 'pt -s'",
                ErrorSeverity.WARNING,
                lambda e: {'body_msg': self._extract_body_message(e)}
            ),
            'APITimeoutError': (
                "Request timeout: The request took too long. Please try again.",
                ErrorSeverity.WARNING,
                None
            ),
            'BadRequestError': (
                "Error 400: {body_msg}. Check model name.",
                ErrorSeverity.ERROR,
                lambda e: {'body_msg': self._extract_body_message(e)}
            ),
            'PermissionDeniedError': (
                "Error 403: Your region is not supported. Use VPN or change the LLM. "
                "You can change LLM in settings: 'pt -s'",
                ErrorSeverity.ERROR,
                None
            ),
            'NotFoundError': (
                "Error 404: Resource not found. Check API_URL and Model in settings.",
                ErrorSeverity.ERROR,
                None
            ),
            'APIError': (
                "Error API: {error}. Check the LLM settings, there may be an incorrect API_URL",
                ErrorSeverity.ERROR,
                lambda e: {'error': str(e)}
            ),
            'OpenAIError': (
                "Please check your API_KEY. See provider docs for obtaining a key. "
                "[link={link}]How to get a key?[/link]",
                ErrorSeverity.ERROR,
                None
            ),
        }

        self._handlers = {}
        self._register_handlers()

    def _extract_body_message(self, error: Exception) -> str:
        """Extract message from error body."""
        try:
            body = getattr(error, 'body', None)
            return body.get('message') if isinstance(body, dict) else str(error)
        except Exception:
            return str(error)

    def _register_handlers(self):
        """Register handlers from configuration dictionary."""
        exceptions = get_openai_exceptions()

        for exc_name, (msg_template, severity, extractor) in self._error_configs.items():
            exc_class = exceptions.get(exc_name)
            if exc_class:
                # Create handler with closure capturing config
                def make_handler(template, sev, extract_fn):
                    def handler(error, context):
                        return self._generic_handler(error, context, template, sev, extract_fn)
                    return handler

                self._handlers[exc_class] = make_handler(msg_template, severity, extractor)

        # Special handler for APIStatusError (needs custom logic)
        if 'APIStatusError' in exceptions:
            self._handlers[exceptions['APIStatusError']] = self._handle_api_status_error

    def handle(self, error: Exception, context: Optional[ErrorContext] = None) -> str:
        """Handle an exception and return user-friendly message.

        Args:
            error: The exception to handle
            context: Additional context information

        Returns:
            User-friendly error message
        """
        # Find appropriate handler
        for exc_type, handler in self._handlers.items():
            if isinstance(error, exc_type):
                return handler(error, context)

        # Fallback to generic handler
        return self._handle_generic_error(error, context)

    def _format_message(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        technical_details: Optional[str] = None
    ) -> str:
        """Format error message with appropriate styling.

        Args:
            message: Main error message
            severity: Error severity level
            technical_details: Optional technical details for debug mode

        Returns:
            Formatted message string
        """
        # All error messages are now gray italic (dim italic)
        formatted = f"[dim italic]{message}[/dim italic]"

        if self.debug_mode and technical_details:
            formatted += f"\n[dim italic]{technical_details}[/dim italic]"

        return formatted

    def _generic_handler(
        self,
        error: Exception,
        context: Optional[ErrorContext],
        msg_template: str,
        severity: ErrorSeverity,
        extractor: Optional[Callable] = None
    ) -> str:
        """Universal handler for all error types using configuration.

        Args:
            error: The exception
            context: Error context
            msg_template: Message template with placeholders
            severity: Error severity level
            extractor: Optional function to extract data from error

        Returns:
            Formatted error message
        """
        # Extract additional data if extractor provided
        data = {'link': self.link_url}
        if extractor:
            data.update(extractor(error))

        # Format message
        message = t(msg_template).format(**data)
        technical = f"{type(error).__name__}: {str(error)}"

        return self._format_message(message, severity, technical)

    def _handle_api_status_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle API status errors with detailed information.

        This handler requires special logic for different status codes.
        """
        status_code = getattr(error, 'status_code', 'unknown')
        response = getattr(error, 'response', None)
        technical = f"Status: {status_code}, Response: {response}"

        # Delegate to simpler handlers for known codes
        if status_code == 401:
            return self._generic_handler(
                error, context,
                "Error 401: Authentication failed. Check your API_KEY. "
                "[link={link}]How to get a key?[/link]",
                ErrorSeverity.CRITICAL,
                None
            )
        elif status_code == 403:
            message = t("Access denied: You don't have permission to access this resource.")
        elif status_code == 404:
            message = t("Not found: The requested model or endpoint was not found.")
            if response and self.debug_mode:
                try:
                    if hasattr(response, 'json'):
                        error_body = response.json()
                    elif hasattr(response, 'text'):
                        error_body = str(response.text)
                    else:
                        error_body = str(response)
                    technical += f"\nError body: {error_body}"
                except Exception:
                    pass
        elif status_code >= 500:
            message = t("Server error: The API server encountered an error. Please try again later.")
        else:
            message = t("API error ({code}): {msg}").format(
                code=status_code,
                msg=getattr(error, 'message', str(error))
            )

        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_generic_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle unknown errors."""
        message = t("Unexpected error: {error}").format(error=str(error))
        technical = f"{type(error).__name__}: {str(error)}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)


def handle_api_errors(
    operation: str = "API operation",
    default_return: Any = "",
    reraise: bool = False
):
    """Decorator for centralized API error handling.

    Args:
        operation: Description of the operation being performed
        default_return: Value to return on error (if not reraising)
        reraise: Whether to reraise exceptions after handling

    Usage:
        @handle_api_errors(operation="fetch user data", default_return=None)
        def fetch_user(user_id):
            # ... API call ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to get console from self if it's a method
                console = None
                if args and hasattr(args[0], 'console'):
                    console = args[0].console

                # Try to get debug mode from config
                try:
                    from penguin_tamer.config_manager import config
                    debug_mode = config.get("global", "debug", False)
                except Exception:
                    debug_mode = False

                # Create error handler and handle the error
                handler = ErrorHandler(console=console, debug_mode=debug_mode)
                context = ErrorContext(operation=operation)
                error_message = handler.handle(e, context)

                # Print error if console available
                if console:
                    console.print(error_message)

                if reraise:
                    raise
                return default_return

        return wrapper
    return decorator


# Backward compatibility function
def connection_error(error: Exception) -> str:
    """Legacy function for backward compatibility.

    Args:
        error: Exception to handle

    Returns:
        User-friendly error message

    Deprecated: Use ErrorHandler.handle() instead
    """
    handler = ErrorHandler(debug_mode=False)
    return handler.handle(error)
