#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config


# Простой ленивый логгер
_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        from aiebash.logger import configure_logger
        _logger = configure_logger(config.get("logging"))
    return _logger


# Простой класс-заглушка для логгера
class LazyLogger:
    def info(self, msg):
        _get_logger().info(msg)

    def debug(self, msg):
        _get_logger().debug(msg)

    def error(self, msg):
        _get_logger().error(msg)

    def critical(self, msg, exc_info=None):
        _get_logger().critical(msg, exc_info=exc_info)

logger = LazyLogger()

# Простой декоратор без импорта
def log_execution_time(func):
    """Простой декоратор времени выполнения"""
    return func  # Временно отключаем для ускорения загрузки


# Ленивый импорт i18n
_i18n_initialized = False


def _ensure_i18n():
    global _i18n_initialized, t, translator
    if not _i18n_initialized:
        from aiebash.i18n import t, translator
        # Initialize translator language from config (default 'en')
        try:
            translator.set_language(getattr(config, 'language', 'en'))
        except Exception:
            pass
        _i18n_initialized = True


def t_lazy(text, **kwargs):
    """Ленивая загрузка переводчика"""
    _ensure_i18n()
    return t(text, **kwargs)


# Используем t_lazy вместо t для отложенной инициализации
t = t_lazy

# Ленивые импорты для ускорения загрузки
_prompt_toolkit_imported = False
_rich_console = None
_script_executor = None
_formatter_text = None

def _ensure_prompt_toolkit():
    """Ленивый импорт prompt_toolkit"""
    global _prompt_toolkit_imported
    if not _prompt_toolkit_imported:
        global HTML, prompt, FileHistory, Style
        from prompt_toolkit import HTML, prompt
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style
        _prompt_toolkit_imported = True


def _get_console():
    """Ленивый импорт rich.console"""
    global _rich_console
    if _rich_console is None:
        from rich.console import Console
        _rich_console = Console
    return _rich_console


def _get_script_executor():
    """Ленивый импорт script_executor"""
    global _script_executor
    if _script_executor is None:
        from aiebash.script_executor import run_code_block
        _script_executor = run_code_block
    return _script_executor


def _get_formatter_text():
    """Ленивый импорт formatter_text"""
    global _formatter_text
    if _formatter_text is None:
        from aiebash.formatter_text import extract_labeled_code_blocks
        _formatter_text = extract_labeled_code_blocks
    return _formatter_text

# Импортируем только самое необходимое для быстрого старта
from aiebash.llm_client import OpenRouterClient
from aiebash.arguments import parse_args
from aiebash.error_messages import connection_error


STREAM_OUTPUT_MODE: bool = config.get("global", "stream_output_mode")
logger.info(f"Settings - Stream output mode: {STREAM_OUTPUT_MODE}")

# Ленивый импорт Markdown из rich (легкий модуль) для ускорения загрузки
_markdown = None


def _get_markdown():
    global _markdown
    if _markdown is None:
        from rich.markdown import Markdown
        _markdown = Markdown
    return _markdown

educational_text = (
    "ALWAYS number code blocks in your replies so the user can reference them. "
    "Numbering format: [Code #1]\n```bash ... ```, [Code #2]\n```bash ... ```, "
    "etc. Insert the numbering BEFORE the block "
    "If there are multiple code blocks, number them sequentially. "
    "In each new reply, start numbering from 1 again. Do not discuss numbering; just do it automatically."
)
EDUCATIONAL_CONTENT = [{'role': 'user', 'content': educational_text}]

@log_execution_time
def get_system_content() -> str:
    """Construct system prompt content with lazy system info loading"""
    user_content = config.get("global", "user_content", "")
    json_mode = config.get("global", "json_mode", False)

    if json_mode:
        additional_content_json = (
            "You must always respond with a single JSON object containing fields 'cmd' and 'info'. "
        )
    else:
        additional_content_json = ""

    # Базовая информация без вызова медленной системной информации
    additional_content_main = (
        "Your name is Ai-eBash, a sysadmin assistant. Always state this when asked who you are. "
        "You and the user always work in a terminal. "
        "Respond based on the user's environment and commands. "
    )
    
    system_content = f"{user_content} {additional_content_json} {additional_content_main}".strip()
    return system_content


# === Основная логика ===
@log_execution_time
def run_single_query(chat_client: OpenRouterClient, query: str, console) -> None:
    """Run a single query (optionally streaming)"""
    logger.info(f"Running query: '{query[:50]}'...")
    try:
        if STREAM_OUTPUT_MODE:
            reply = chat_client.ask_stream(query)
        else:
            reply = chat_client.ask(query)
            console.print(_get_markdown()(reply))
    except Exception as e:
        console.print(connection_error(e))
        logger.error(f"Connection error: {e}")


@log_execution_time
def run_dialog_mode(chat_client: OpenRouterClient, console, initial_user_prompt: str = None) -> None:
    """Interactive dialog mode"""
    
    # Загружаем prompt_toolkit только когда нужен диалоговый режим
    _ensure_prompt_toolkit()

    # История команд хранится рядом с настройками в пользовательской папке
    history_file_path = config.user_config_dir / "cmd_history"
    history = FileHistory(str(history_file_path))

    logger.info("Starting dialog mode")

    # Use module global EDUCATIONAL_CONTENT inside the function
    global EDUCATIONAL_CONTENT

    last_code_blocks = []  # code blocks from the last AI answer

    # If there is an initial prompt, process it
    if initial_user_prompt:
        initial_user_prompt
        try:
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(_get_markdown()(reply))
            else:
                reply = chat_client.ask(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(_get_markdown()(reply))
            EDUCATIONAL_CONTENT = []  # clear educational content after first use
            last_code_blocks = _get_formatter_text()(reply)
        except Exception as e:
            console.print(connection_error(e))
            logger.error(f"Connection error: {e}")
        console.print()

    # Main dialog loop
    while True:
        try:

            # Define prompt styles
            style = Style.from_dict({
                "prompt": "bold fg:green",
            })
            if last_code_blocks:
                placeholder = HTML(t("<i><gray>The number of the code block to execute or the next question... Ctrl+C - exit</gray></i>"))
            else:
                placeholder = HTML(t("<i><gray>Your question... Ctrl+C - exit</gray></i>"))

            user_prompt = prompt([("class:prompt", ">>> ")], placeholder=placeholder, history=history, 
                                style=style, multiline=False, wrap_lines=True, enable_history_search=True)
            # Disallow empty input
            if not user_prompt:
                continue

            # Exit commands
            if user_prompt.lower() in ['exit', 'quit', 'q']:
                break

            # If a number is entered
            if user_prompt.isdigit():
                block_index = int(user_prompt)
                if 1 <= block_index <= len(last_code_blocks):
                    _get_script_executor()(console, last_code_blocks, block_index)
                    console.print()
                    continue
                else:
                    console.print(f"[dim]Code block #{user_prompt} not found.[/dim]")
                    continue

            # Если введен текст, отправляем как запрос к AI
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(user_prompt, educational_content=EDUCATIONAL_CONTENT)
            else:
                reply = chat_client.ask(user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(_get_markdown()(reply))
            EDUCATIONAL_CONTENT = []  # clear educational content after first use
            last_code_blocks = _get_formatter_text()(reply)
            console.print()  # new line after answer

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(connection_error(e))
            logger.error(f"Connection error: {e}")


def _create_chat_client(console):
    """Ленивое создание LLM клиента только когда он действительно нужен"""
    logger.info("Initializing OpenRouterChat client")

    llm_config = config.get_current_llm_config()
    
    chat_client = OpenRouterClient(
        console=console,
        logger=logger,
        api_key=llm_config["api_key"],
        api_url=llm_config["api_url"],
        model=llm_config["model"],
        system_content=get_system_content(),
        temperature=config.get("global", "temperature", 0.7)
    )
    logger.info("OpenRouterChat client created: " + f"{chat_client}")
    return chat_client


@log_execution_time
def main() -> None:

    try:
        args = parse_args()

        # Settings mode - не нужен LLM клиент
        if args.settings:
            logger.info("Starting configuration mode")
            from aiebash.config_menu import main_menu
            main_menu()
            logger.info("Configuration mode finished")
            return 0

        # Создаем консоль и клиент только если они нужны для AI операций
        console = _get_console()()
        chat_client = _create_chat_client(console)

        # Determine execution mode
        dialog_mode: bool = args.dialog
        prompt_parts: list = args.prompt or []
        prompt: str = " ".join(prompt_parts).strip()

        if dialog_mode or not prompt:
            # Dialog mode
            logger.info("Starting in dialog mode")
            run_dialog_mode(chat_client, console, prompt if prompt else None)
        else:
            # Single query mode
            logger.info("Starting in single-query mode")

            run_single_query(chat_client, prompt, console)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.critical(f"Unhandled error: {e}", exc_info=True)
        return 1
    finally:
        print()  # print empty line anyway

    logger.info("Program finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
