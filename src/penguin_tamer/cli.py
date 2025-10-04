#!/usr/bin/env python3
"""Command-line interface for Penguin Tamer."""
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки
from penguin_tamer.config_manager import config

# Ленивый импорт i18n
_i18n_initialized = False
def _ensure_i18n():
    global _i18n_initialized, t, translator
    if not _i18n_initialized:
        from penguin_tamer.i18n import t, translator
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

# Ленивые импорты (только для действительно редких операций)
_script_executor = None
_formatter_text = None
_execute_handler = None
_console_class = None
_markdown_class = None


def _get_console_class():
    """Ленивый импорт Console"""
    global _console_class
    if _console_class is None:
        from rich.console import Console
        _console_class = Console
    return _console_class


def _get_markdown_class():
    """Ленивый импорт Markdown"""
    global _markdown_class
    if _markdown_class is None:
        from rich.markdown import Markdown
        _markdown_class = Markdown
    return _markdown_class


def _get_script_executor():
    """Ленивый импорт command_executor"""
    global _script_executor
    if _script_executor is None:
        from penguin_tamer.command_executor import run_code_block
        _script_executor = run_code_block
    return _script_executor


def _get_execute_handler():
    """Ленивый импорт execute_and_handle_result для выполнения команд"""
    global _execute_handler
    if '_execute_handler' not in globals() or _execute_handler is None:
        from penguin_tamer.command_executor import execute_and_handle_result
        _execute_handler = execute_and_handle_result
    return _execute_handler

def _get_formatter_text():
    """Ленивый импорт text_utils"""
    global _formatter_text
    if _formatter_text is None:
        from penguin_tamer.text_utils import extract_labeled_code_blocks
        _formatter_text = extract_labeled_code_blocks
    return _formatter_text

# Импортируем только самое необходимое для быстрого старта
from penguin_tamer.llm_client import OpenRouterClient
from penguin_tamer.arguments import parse_args
from penguin_tamer.error_handlers import connection_error
from penguin_tamer.dialog_input import DialogInputFormatter

STREAM_OUTPUT_MODE: bool = config.get("global", "stream_output_mode")

educational_text = (
    "ALWAYS number code blocks in your replies so the user can reference them. "
    "Numbering format: [Code #1]\n```bash ... ```, [Code #2]\n```bash ... ```, "
    "etc. Insert the numbering BEFORE the block "
    "If there are multiple code blocks, number them sequentially. "
    "In each new reply, start numbering from 1 again. Do not discuss numbering; just do it automatically."
)
EDUCATIONAL_CONTENT = [{'role': 'user', 'content': educational_text}]

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
        "Your name is Penguin Tamer, a sysadmin assistant. "
        "You and the user always work in a terminal. "
        "Respond based on the user's environment and commands. "
    )
    
    system_content = f"{user_content} {additional_content_json} {additional_content_main}".strip()
    return system_content


# === Основная логика ===
def run_single_query(chat_client: OpenRouterClient, query: str, console) -> None:
    """Run a single query (optionally streaming)"""
    try:
        if STREAM_OUTPUT_MODE:
            reply = chat_client.ask_stream(query)
        else:
            reply = chat_client.ask(query)
            Markdown = _get_markdown_class()
            console.print(Markdown(reply))
    except Exception as e:
        console.print(connection_error(e))


def run_dialog_mode(chat_client: OpenRouterClient, console, initial_user_prompt: str = None) -> None:
    """Interactive dialog mode"""
    
    # История команд хранится рядом с настройками в пользовательской папке
    history_file_path = config.user_config_dir / "cmd_history"
    
    # Создаем форматтер ввода
    input_formatter = DialogInputFormatter(history_file_path)

    # Use module global EDUCATIONAL_CONTENT inside the function
    global EDUCATIONAL_CONTENT

    last_code_blocks = []  # code blocks from the last AI answer

    # If there is an initial prompt, process it
    if initial_user_prompt:
        initial_user_prompt
        try:
            Markdown = _get_markdown_class()
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(Markdown(reply))
            else:
                reply = chat_client.ask(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(Markdown(reply))
            EDUCATIONAL_CONTENT = []  # clear educational content after first use
            last_code_blocks = _get_formatter_text()(reply)
        except Exception as e:
            console.print(connection_error(e))
        console.print()

    # Main dialog loop
    while True:
        try:
            # Получаем ввод пользователя через форматтер
            user_prompt = input_formatter.get_input(console, has_code_blocks=bool(last_code_blocks), t=t)
            # Disallow empty input
            if not user_prompt:
                continue

            # Exit commands
            if user_prompt.lower() in ['exit', 'quit', 'q']:
                break

            # Command execution: if input starts with dot ".", execute as direct command
            if user_prompt.startswith('.'):
                command_to_execute = user_prompt[1:].strip()  # Remove the dot and strip spaces
                if command_to_execute:  # Only execute if there's something after the dot
                    console.print(f"[dim]>>> Executing command:[/dim] {command_to_execute}")
                    _get_execute_handler()(console, command_to_execute)
                    console.print()
                    continue
                else:
                    console.print("[dim]Empty command after '.' - skipping.[/dim]")
                    continue

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
                Markdown = _get_markdown_class()
                reply = chat_client.ask(user_prompt, educational_content=EDUCATIONAL_CONTENT)
                console.print(Markdown(reply))
            EDUCATIONAL_CONTENT = []  # clear educational content after first use
            last_code_blocks = _get_formatter_text()(reply)
            console.print()  # new line after answer

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(connection_error(e))


def _create_chat_client(console):
    """Ленивое создание LLM клиента только когда он действительно нужен"""

    llm_config = config.get_current_llm_config()
    
    chat_client = OpenRouterClient(
        console=console,
        api_key=llm_config["api_key"],
        api_url=llm_config["api_url"],
        model=llm_config["model"],
        system_content=get_system_content(),
        temperature=config.get("global", "temperature", 0.7)
    )
    return chat_client


def main() -> None:
    """Main entry point for Penguin Tamer CLI."""
    try:
        args = parse_args()

        # Settings mode - не нужен LLM клиент
        if args.settings:
            from penguin_tamer.config_menu import main_menu
            main_menu()
            return 0

        # Создаем консоль и клиент только если они нужны для AI операций
        Console = _get_console_class()
        console = Console()
        chat_client = _create_chat_client(console)

        # Determine execution mode
        dialog_mode: bool = args.dialog
        prompt_parts: list = args.prompt or []
        prompt: str = " ".join(prompt_parts).strip()

        if dialog_mode or not prompt:
            # Dialog mode
            run_dialog_mode(chat_client, console, prompt if prompt else None)
        else:
            # Single query mode

            run_single_query(chat_client, prompt, console)

    except KeyboardInterrupt:
        return 130
    except Exception as e:
        return 1
    finally:
        print()  # print empty line anyway

    return 0


if __name__ == "__main__":
    sys.exit(main())
