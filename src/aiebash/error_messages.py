from aiebash.i18n import t

_openai_exceptions = None

# Lazy import of OpenAI exceptions and map to names
def _get_openai_exceptions():
    """Lazy import of OpenAI exceptions"""
    global _openai_exceptions
    if _openai_exceptions is None:
        from openai import (RateLimitError, APIError, OpenAIError, AuthenticationError, 
                            APIConnectionError, PermissionDeniedError, NotFoundError, BadRequestError)
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
    """Map API errors to localized messages (English as keys)."""
    try:
        body = getattr(error, 'body', None)
        msg = body.get('message') if isinstance(body, dict) else str(error)
    except Exception:
        msg = str(error)
    if isinstance(error, _get_openai_exceptions()['RateLimitError']):
        return t("[dim]Error 429: Exceeding the quota. Message from the provider: {message}. "
                 "You can change LLM in settings: 'ai --settings'[/dim]").format(message=msg)
    elif isinstance(error, _get_openai_exceptions()['BadRequestError']):
        return t("[dim]Error 400: {message}. Check model name.[/dim]").format(message=msg)
    elif isinstance(error, _get_openai_exceptions()['AuthenticationError']):
        link_url = ("https://github.com/Vivatist/ai-ebash/blob/main/docs/locales/"
                    "README_ru.md#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-"
                    "%D1%82%D0%BE%D0%BA%D0%B5%D0%BD%D0%B0-api_key-%D0%B8-%D0%BF%D0%BE%D0%B4"
                    "%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BA-%D0%BF%D1%80%D0%B5"
                    "%D0%B4%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE"
                    "%D0%B9-%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D1%81%D0%B5%D1%82%D0%B8")
        return t("[dim]Error 401: Authentication failed. Check your API_KEY. "
                 "[link={link}]How to get a key?[/link][/dim]").format(link=link_url)
    elif isinstance(error, _get_openai_exceptions()['APIConnectionError']):
        return t("[dim]No connection, please check your Internet connection[/dim]")
    elif isinstance(error, _get_openai_exceptions()['PermissionDeniedError']):
        return t("[dim]Error 403: Your region is not supported. Use VPN or change the LLM. "
                 "You can change LLM in settings: 'ai --settings'[/dim]")
    elif isinstance(error, _get_openai_exceptions()['NotFoundError']):
        return t("[dim]Error 404: Resource not found. Check API_URL and Model in settings.[/dim]")
    elif isinstance(error, _get_openai_exceptions()['APIError']):
        return t("[dim]Error API: {error}. Check the LLM settings, there may be an incorrect API_URL[/dim]").format(error=error)
    elif isinstance(error, _get_openai_exceptions()['OpenAIError']):
        return t("[dim]Please check your API_KEY. See provider docs for obtaining a key. "
                 "[link={link}]How to get a key?[/link][/dim]").format(link=link_url)
    else:
        return t("[dim]Unknown error: {error}[/dim]").format(error=error)
