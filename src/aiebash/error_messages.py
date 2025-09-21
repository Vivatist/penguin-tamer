from aiebash.i18n import t

_openai_exceptions = None

# Lazy import of OpenAI exceptions and map to names
def _get_openai_exceptions():
    """Lazy import of OpenAI exceptions"""
    global _openai_exceptions
    if _openai_exceptions is None:
        from openai import RateLimitError, APIError, OpenAIError, AuthenticationError, APIConnectionError, PermissionDeniedError, NotFoundError, BadRequestError
        _openai_exceptions = {
            'RateLimitError': RateLimitError,
            'APIError': APIError,
            'OpenAIError': OpenAIError,
            'AuthenticationError': AuthenticationError,
            'APIConnectionError': APIConnectionError,
            'PermissionDeniedError': PermissionDeniedError,
            'NotFoundError': NotFoundError,
            'BadRequestError': BadRequestError
        }
    return _openai_exceptions


def connection_error(error: Exception) -> str:
    """Map API errors to user-facing messages (English as keys)."""
    if isinstance(error, _get_openai_exceptions()['RateLimitError']):
        return t("Error 429: You have exceeded your current quota. Check your plan and billing, or try later if on a free tier. You can change LLM in settings: 'ai --settings'")
    elif isinstance(error, _get_openai_exceptions()['BadRequestError']):
        try:
            body = getattr(error, 'body', None)
            msg = body.get('message') if isinstance(body, dict) else str(error)
        except Exception:
            msg = str(error)
        return t("Error 400: {message}. Check model name.", message=msg)
    elif isinstance(error, _get_openai_exceptions()['AuthenticationError']):
        return t("Error 401: Authentication failed. Check your API_KEY. See docs for obtaining a key.")
    elif isinstance(error, _get_openai_exceptions()['APIConnectionError']):
        return t("No connection. Please check your Internet connectivity.")
    elif isinstance(error, _get_openai_exceptions()['PermissionDeniedError']):
        return t("Error 403: Your region is not supported. Use VPN or change the LLM in settings: 'ai --settings'")
    elif isinstance(error, _get_openai_exceptions()['NotFoundError']):
        return t("Error 404: Resource not found. Check API_URL in settings.")
    elif isinstance(error, _get_openai_exceptions()['APIError']):
        return t("API error: {error}", error=str(error))
    elif isinstance(error, _get_openai_exceptions()['OpenAIError']):
        return t("Check your API_KEY. See provider docs for obtaining a key.")
    else:
        return t("Unknown error: {error}", error=str(error))
