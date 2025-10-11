import logging
import sys
from pathlib import Path
from typing import Dict, Optional
import platform
from logging.handlers import RotatingFileHandler
from platformdirs import user_config_dir
from penguin_tamer.utils.lazy_import import lazy_import

# Константы
APP_NAME = "penguin-tamer"
log_dir = Path(user_config_dir(APP_NAME)) / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Заглушка для логгера по умолчанию (будет заменен)
logger = logging.getLogger('penguin-tamer')


# Ленивые импорты Rich через декоратор
@lazy_import
def get_rich_handler():
    """Ленивый импорт RichHandler"""
    from rich.logging import RichHandler
    return RichHandler


@lazy_import
def get_rich_console():
    """Ленивый импорт Rich Console"""
    from rich.console import Console
    return Console


# Одиночная переменная для отслеживания инициализации
_rich_traceback_installed = False


def ensure_rich_traceback():
    """Ленивая установка Rich traceback"""
    global _rich_traceback_installed
    if not _rich_traceback_installed:
        from rich.traceback import install
        install(show_locals=True)
        _rich_traceback_installed = True

# Преобразование строковых уровней в константы logging


def get_log_level(level_name: str) -> int:
    """Преобразует строковое имя уровня логирования в константу logging"""
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    return level_map.get(level_name.lower(), logging.INFO)


def configure_logger(config_data: Optional[Dict] = None) -> logging.Logger:
    """
    Настраивает и возвращает логгер с указанными параметрами.

    Args:
        config_data: Настройки логирования из конфигурации

    Returns:
        logging.Logger: Настроенный логгер
    """
    global logger

    # Значения по умолчанию
    log_level = logging.INFO
    console_level = logging.CRITICAL
    file_level = logging.DEBUG
    file_enabled = False

    # Применяем настройки из конфигурации, если они есть
    if config_data:
        log_level = get_log_level(config_data.get('level', 'INFO'))
        console_level = get_log_level(config_data.get('console_level', 'INFO'))
        file_level = get_log_level(config_data.get('file_level', 'DEBUG'))
        file_enabled = config_data.get('file_enabled', False)

    # Создаем новый логгер
    logger = logging.getLogger('penguin-tamer')
    logger.setLevel(log_level)

    # Очистка существующих обработчиков
    if logger.hasHandlers():
        logger.handlers.clear()

    # Консольный вывод с ленивой загрузкой Rich
    console = get_rich_console()()
    RichHandler = get_rich_handler()
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_path=False
    )
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    # Устанавливаем Rich traceback только при создании консольного обработчика
    ensure_rich_traceback()

    # Файловый вывод
    if file_enabled:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler = RotatingFileHandler(
            log_dir / "penguin-tamer.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Логируем системную информацию при запуске
    logger.info(f"Starting penguin-tamer on {platform.system()} {platform.release()}")
    logger.debug(f"Python {platform.python_version()}, interpreter: {sys.executable}")
    logger.debug(f"Log level: console={console_level}, file={file_level if file_enabled else 'disabled'}")

    return logger


# Первоначальная инициализация логгера с дефолтными настройками
logger = configure_logger(None)


def update_logger_config(config_data: dict):
    """
    Обновляет конфигурацию логгера на основе переданных настроек.
    Вызывается из settings.py после загрузки конфигурации.
    """
    global logger
    logger = configure_logger(config_data)
    logger.debug("Logger settings updated from config file")

# Вспомогательная функция для логирования времени выполнения


def log_execution_time(func):
    """Декоратор для логирования времени выполнения функции"""
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        # logger.debug(f"Starting execution of {func.__name__}")
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(f"Function {func.__name__} executed in {execution_time:.3f} s")
        return result
    return wrapper
