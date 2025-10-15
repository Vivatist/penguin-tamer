"""Test script to display all error messages from error_handlers.py in all localizations."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest.mock import Mock  # noqa: E402
from rich.console import Console  # noqa: E402
from openai import (  # noqa: E402
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    PermissionDeniedError,
    NotFoundError,
    APIStatusError,
    APIError,
    OpenAIError,
)
from penguin_tamer.error_handlers import ErrorHandler  # noqa: E402
from penguin_tamer.i18n import translator  # noqa: E402


def create_mock_request():
    """Create a mock request object."""
    request = Mock()
    request.url = "https://api.openai.com/v1/chat/completions"
    request.method = "POST"
    return request


def create_mock_response(status_code: int):
    """Create a mock response object."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {"error": {"message": "Test error"}}
    response.text = "Test error response"
    return response


def display_all_errors(console: Console, lang: str):
    """Display all error types for a given language."""
    # Set language
    translator.set_language(lang)

    # Create error handlers
    handler_normal = ErrorHandler(console, debug_mode=False)
    handler_debug = ErrorHandler(console, debug_mode=True)

    # Define all error cases to test
    test_cases = [
        {
            "name": "1. APIConnectionError",
            "error": APIConnectionError(request=create_mock_request()),
            "description": "Connection error"
        },
        {
            "name": "2. AuthenticationError",
            "error": AuthenticationError(
                message="Invalid API key",
                response=create_mock_response(401),
                body=None
            ),
            "description": "Authentication failed (401)"
        },
        {
            "name": "3. RateLimitError",
            "error": RateLimitError(
                message="Rate limit exceeded",
                response=create_mock_response(429),
                body=None
            ),
            "description": "Rate limit exceeded (429)"
        },
        {
            "name": "4. APITimeoutError",
            "error": APITimeoutError(request=create_mock_request()),
            "description": "Timeout error"
        },
        {
            "name": "5. BadRequestError",
            "error": BadRequestError(
                message="Invalid request",
                response=create_mock_response(400),
                body=None
            ),
            "description": "Bad request (400)"
        },
        {
            "name": "6. PermissionDeniedError",
            "error": PermissionDeniedError(
                message="Access denied",
                response=create_mock_response(403),
                body=None
            ),
            "description": "Permission denied (403)"
        },
        {
            "name": "7. NotFoundError",
            "error": NotFoundError(
                message="Resource not found",
                response=create_mock_response(404),
                body=None
            ),
            "description": "Not found (404)"
        },
        {
            "name": "8. APIStatusError (403 access denied)",
            "error": APIStatusError(
                message="Access denied to organization",
                response=create_mock_response(403),
                body=None
            ),
            "description": "Organization access denied (403)"
        },
        {
            "name": "9. APIStatusError (404)",
            "error": APIStatusError(
                message="Model not found",
                response=create_mock_response(404),
                body=None
            ),
            "description": "Model not found (404)"
        },
        {
            "name": "10. APIStatusError (500)",
            "error": APIStatusError(
                message="Internal server error",
                response=create_mock_response(500),
                body=None
            ),
            "description": "Internal server error (500)"
        },
        {
            "name": "11. APIError (generic)",
            "error": APIError(
                message="Generic API error",
                request=create_mock_request(),
                body=None
            ),
            "description": "Generic API Error"
        },
        {
            "name": "12. OpenAIError (generic)",
            "error": OpenAIError("Unexpected OpenAI SDK error"),
            "description": "Generic OpenAI SDK Error"
        },
        {
            "name": "13. ValueError (unknown)",
            "error": ValueError("Some unexpected error"),
            "description": "Unknown exception type"
        }
    ]

    # Test each error case
    for case in test_cases:
        console.print("\n[bold yellow]" + "-" * 80 + "[/bold yellow]")
        console.print(f"[bold yellow]{case['name']}: {case['description']}[/bold yellow]")
        console.print("[bold yellow]" + "-" * 80 + "[/bold yellow]\n")

        # Test in normal mode
        console.print("[cyan]Normal mode (debug_mode=False):[/cyan]")
        message = handler_normal.handle(case["error"])
        console.print(message)

        # Test in debug mode
        console.print("\n[magenta]Debug mode (debug_mode=True):[/magenta]")
        message = handler_debug.handle(case["error"])
        console.print(message)


def main():
    """Main function to test all error messages in all localizations."""
    console = Console(force_terminal=True, legacy_windows=False)

    console.print("\n[bold green]" + "=" * 80 + "[/bold green]")
    console.print("[bold green]ERROR MESSAGES TEST - ALL LOCALIZATIONS[/bold green]")
    console.print("[bold green]" + "=" * 80 + "[/bold green]")

    # Get available localizations
    locales_dir = Path(__file__).parent.parent / "src" / "penguin_tamer" / "locales"
    available_langs = []

    for locale_file in locales_dir.glob("*.json"):
        if locale_file.stem != "template_locale":
            available_langs.append(locale_file.stem)

    # Always test English (even without en.json file)
    if "en" not in available_langs:
        available_langs.insert(0, "en")

    console.print(f"\nAvailable localizations: {', '.join(available_langs)}")

    # Test each localization
    for lang in available_langs:
        console.print("\n[bold green]" + "=" * 80 + "[/bold green]")
        console.print(f"[bold green]Testing Error Messages - Language: {lang.upper()}[/bold green]")
        console.print("[bold green]" + "=" * 80 + "[/bold green]")

        display_all_errors(console, lang)

    console.print("\n[bold green]" + "=" * 80 + "[/bold green]")
    console.print("[bold green]TEST COMPLETE[/bold green]")
    console.print("[bold green]" + "=" * 80 + "[/bold green]\n")


if __name__ == "__main__":
    main()
