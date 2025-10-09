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


# Lazy import of OpenAI exceptions
_openai_exceptions = None


def _get_openai_exceptions():
    """Lazy import of OpenAI exceptions."""
    global _openai_exceptions
    if _openai_exceptions is None:
        from openai import (
            RateLimitError, APIError as OpenAIAPIError, OpenAIError,
            AuthenticationError, APIConnectionError, PermissionDeniedError,
            NotFoundError, BadRequestError, APIStatusError, APITimeoutError
        )
        _openai_exceptions = {
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
    return _openai_exceptions


class ErrorHandler:
    """Centralized error handler with strategy pattern."""

    def __init__(self, console=None, debug_mode: bool = False):
        """Initialize error handler.

        Args:
            console: Rich console for output
            debug_mode: Enable detailed error information
        """
        self.console = console
        self.debug_mode = debug_mode
        self.link_url = t("docs_link_get_api_key")
        self._handlers = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default error handlers for known exception types."""
        exceptions = _get_openai_exceptions()

        # API Connection Errors
        self._handlers[exceptions['APIConnectionError']] = self._handle_connection_error

        # Authentication Errors
        self._handlers[exceptions['AuthenticationError']] = self._handle_auth_error

        # Rate Limit Errors
        self._handlers[exceptions['RateLimitError']] = self._handle_rate_limit_error

        # API Status Errors
        self._handlers[exceptions['APIStatusError']] = self._handle_api_status_error

        # Timeout Errors
        self._handlers[exceptions['APITimeoutError']] = self._handle_timeout_error

        # Bad Request Errors
        self._handlers[exceptions['BadRequestError']] = self._handle_bad_request_error

        # Permission Errors
        self._handlers[exceptions['PermissionDeniedError']] = self._handle_permission_error

        # Not Found Errors
        self._handlers[exceptions['NotFoundError']] = self._handle_not_found_error

        # Generic API Errors
        self._handlers[exceptions['APIError']] = self._handle_api_error
        self._handlers[exceptions['OpenAIError']] = self._handle_openai_error

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

    def _handle_connection_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle API connection errors."""
        message = t(
            "Connection error: Unable to connect to API. "
            "Please check your internet connection."
        )
        technical = f"APIConnectionError: {str(error)}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_auth_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle authentication errors."""
        message = t(
            "Error 401: Authentication failed. Check your API_KEY. "
            "[link={link}]How to get a key?[/link]"
        ).format(link=self.link_url)
        technical = f"AuthenticationError: {str(error)}"
        return self._format_message(message, ErrorSeverity.CRITICAL, technical)

    def _handle_rate_limit_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle rate limit errors."""
        try:
            body = getattr(error, 'body', None)
            msg = body.get('message') if isinstance(body, dict) else str(error)
        except Exception:
            msg = str(error)

        message = t(
            "Error 429: Exceeding the quota. Message from the provider: {message}. "
            "You can change LLM in settings: 'ai --settings'"
        ).format(message=msg)
        technical = f"RateLimitError: {msg}"
        return self._format_message(message, ErrorSeverity.WARNING, technical)

    def _handle_api_status_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle API status errors with detailed information."""
        status_code = getattr(error, 'status_code', 'unknown')
        response = getattr(error, 'response', None)

        technical = f"Status: {status_code}, Response: {response}"

        if status_code == 401:
            return self._handle_auth_error(error, context)
        elif status_code == 403:
            message = t(
                "Access denied: You don't have permission to access this resource."
            )
        elif status_code == 404:
            message = t("Not found: The requested model or endpoint was not found.")
            # Add detailed error body if available
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
            message = t(
                "Server error: The API server encountered an error. "
                "Please try again later."
            )
        else:
            message = t("API error ({code}): {msg}").format(
                code=status_code,
                msg=getattr(error, 'message', str(error))
            )

        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_timeout_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle timeout errors."""
        message = t("Request timeout: The request took too long. Please try again.")
        technical = f"APITimeoutError: {str(error)}"
        return self._format_message(message, ErrorSeverity.WARNING, technical)

    def _handle_bad_request_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle bad request errors."""
        try:
            body = getattr(error, 'body', None)
            msg = body.get('message') if isinstance(body, dict) else str(error)
        except Exception:
            msg = str(error)

        message = t("Error 400: {message}. Check model name.").format(message=msg)
        technical = f"BadRequestError: {msg}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_permission_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle permission denied errors."""
        message = t(
            "Error 403: Your region is not supported. Use VPN or change the LLM. "
            "You can change LLM in settings: 'ai --settings'"
        )
        technical = f"PermissionDeniedError: {str(error)}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_not_found_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle not found errors."""
        message = t("Error 404: Resource not found. Check API_URL and Model in settings.")
        technical = f"NotFoundError: {str(error)}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_api_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle generic API errors."""
        message = t(
            "Error API: {error}. Check the LLM settings, "
            "there may be an incorrect API_URL"
        ).format(error=error)
        technical = f"APIError: {str(error)}"
        return self._format_message(message, ErrorSeverity.ERROR, technical)

    def _handle_openai_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None
    ) -> str:
        """Handle generic OpenAI errors."""
        message = t(
            "Please check your API_KEY. See provider docs for obtaining a key. "
            "[link={link}]How to get a key?[/link]"
        ).format(link=self.link_url)
        technical = f"OpenAIError: {str(error)}"
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
