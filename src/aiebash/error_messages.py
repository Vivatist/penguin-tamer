_openai_exceptions = None

# ленивый импорт исключений OpenAI и обработка ошибок с пользовательскими сообщениями
def _get_openai_exceptions():
    """Ленивый импорт OpenAI исключений"""
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
    """Обработка ошибок API с соответствующим выводом сообщений"""   
    if isinstance(error, _get_openai_exceptions()['RateLimitError']):
        return (f"[dim]Ошибка 429: Вы превысили текущую квоту запросов, пожалуйста, проверьте свой тарифный план и платежные реквизиты у провайдера нейросети. Либо попробуйте отправить запрос через некоторое время, если пользуетесь бесплатным тарифом. Сменить нейросеть можно в настройках: 'ai --settings'[/dim]")
    elif isinstance(error, _get_openai_exceptions()['BadRequestError']):
        return (f"[dim]Ошибка 400: {getattr(error, 'body', None)['message']}. Проверьте название модели.[/dim]")
    elif isinstance(error, _get_openai_exceptions()['AuthenticationError']):
        return ("[dim]Ошибка 401: Отказ в авторизации.Проверьте свой ключ API_KEY. Для получения ключа обратитесь к поставщику API. [link=https://github.com/Vivatist/ai-bash]Как получить ключ?[/link][/dim]")
    elif isinstance(error, _get_openai_exceptions()['APIConnectionError']):
        return (f"[dim]Нет соединения, проверьте подключение к интернету[/dim]")
    elif isinstance(error, _get_openai_exceptions()['PermissionDeniedError']):
        return (f"[dim]Ошибка 403: Ваш регион не поддерживается, используйте VPN либо смените нейросеть. Сменить нейросеть можно в настройках: 'ai --settings'[/dim]")
    elif isinstance(error, _get_openai_exceptions()['NotFoundError']):
        return ("[dim]Ошибка 404: Ресурс не найден. Проверьте API_URL в настройках.[/dim]")
    elif isinstance(error, _get_openai_exceptions()['APIError']):
        return (f"[dim]Ошибка API: {error}[/dim]")
    elif isinstance(error, _get_openai_exceptions()['OpenAIError']):
        return (f"[dim]Ошибка клиента OpenAI: {error}[/dim]")
    else:
        return (f"[dim]Неизвестная ошибка: {error}[/dim]")
