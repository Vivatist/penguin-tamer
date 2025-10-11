"""Universal lazy import decorator to reduce boilerplate code.

This module provides a decorator for lazy loading of modules and functions,
which helps to:
- Reduce startup time by deferring imports
- Eliminate 200+ lines of repetitive lazy import code
- Improve code maintainability

Example usage:
    from penguin_tamer.utils.lazy_import import lazy_import

    @lazy_import
    def get_console():
        from rich.console import Console
        return Console

    # Later in code:
    Console = get_console()
    console = Console()
"""

from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')


def lazy_import(import_func: Callable[[], T]) -> Callable[[], T]:
    """Decorator for lazy module/function imports with caching.

    Wraps an import function to cache its result after first call,
    avoiding repeated imports while maintaining lazy loading behavior.

    Args:
        import_func: Function that performs the import and returns the result

    Returns:
        Wrapped function that caches and returns the imported object

    Example:
        >>> @lazy_import
        ... def get_openai():
        ...     from openai import OpenAI
        ...     return OpenAI
        ...
        >>> # First call imports and caches
        >>> OpenAI = get_openai()
        >>> # Subsequent calls return cached value
        >>> OpenAI2 = get_openai()
        >>> assert OpenAI is OpenAI2
    """
    # Use dict instead of single variable to avoid closure issues
    cache: dict[str, Any] = {'value': None, 'initialized': False}

    @wraps(import_func)
    def wrapper() -> T:
        if not cache['initialized']:
            cache['value'] = import_func()
            cache['initialized'] = True
        return cache['value']

    return wrapper


def lazy_import_from(module_path: str, *names: str) -> Callable[[], Any]:
    """Factory function for creating lazy imports from specific modules.

    Provides a more concise way to create lazy imports when you know
    the module path and names at decoration time.

    Args:
        module_path: Module path like 'rich.console'
        *names: Names to import from the module

    Returns:
        Lazy import function

    Example:
        >>> get_console = lazy_import_from('rich.console', 'Console')
        >>> Console = get_console()
    """
    @lazy_import
    def _import():
        module = __import__(module_path, fromlist=names)
        if len(names) == 1:
            return getattr(module, names[0])
        return tuple(getattr(module, name) for name in names)

    return _import
