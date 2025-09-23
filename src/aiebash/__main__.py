#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config   

# Теперь импортируем и настраиваем логгер
from aiebash.logger import configure_logger, log_execution_time
from aiebash.i18n import t, translator

# Получаем настройки логирования и настраиваем логгер
logger = configure_logger(config.get("logging"))

# Initialize translator language from config (default 'en')
try:
    translator.set_language(getattr(config, 'language', 'en'))
except Exception:
    pass

from prompt_toolkit import HTML, prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

# Импортируем OpenRouterChat вместо старых модулей
from aiebash.llm_client import OpenRouterClient
from aiebash.arguments import parse_args
from rich.console import Console
from aiebash.script_executor import run_code_block
from aiebash.sys_info import get_system_info_text
from aiebash.formatter_text import extract_labeled_code_blocks
from aiebash.error_messages import connection_error


STREAM_OUTPUT_MODE: bool = config.get("global","stream_output_mode")
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
EDUCATIONAL_CONTENT = [{'role': 'user', 'content': educational_text},]

@log_execution_time
def get_system_content() -> str:
    """Construct system prompt content"""
    user_content = config.get("global", "user_content", "")
    json_mode = config.get("global", "json_mode", False)

    if json_mode:
        additional_content_json = (
            "You must always respond with a single JSON object containing fields 'cmd' and 'info'. "
        )
    else:
        additional_content_json = ""

    additional_content_main = (
        "Your name is Ai-eBash, a sysadmin assistant. Always state this when asked who you are. "
        "You and the user always work in a terminal. "
        f"Environment for both of you: {get_system_info_text()}, respond based on this unless user specifies otherwise. "
    )
    
    system_content = f"{user_content} {additional_content_json} {additional_content_main}".strip()
    return system_content



# === Основная логика ===
@log_execution_time
def run_single_query(chat_client: OpenRouterClient, query: str, console: Console) -> None:
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
def run_dialog_mode(chat_client: OpenRouterClient, console: Console, initial_user_prompt: str = None) -> None:
    """Interactive dialog mode"""
    
    history = FileHistory(".cmd_history")

    logger.info("Starting dialog mode")

    # Use module global EDUCATIONAL_CONTENT inside the function
    global EDUCATIONAL_CONTENT

    last_code_blocks = []  # code blocks from the last AI answer

    # If there is an initial prompt, process it
    if initial_user_prompt:
        initial_user_prompt
        try:
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(initial_user_prompt)
            else:
                reply = chat_client.ask(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                EDUCATIONAL_CONTENT = []  # clear educational content after first use
                console.print(_get_markdown()(reply))
            last_code_blocks = extract_labeled_code_blocks(reply)
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
                placeholder = HTML("<i><ansiblack>The number of the code block to execute or the next question... Ctrl+C - exit</ansiblack></i>")
            else:
                placeholder = HTML("<i><ansiblack>Your question... Ctrl+C - exit</ansiblack></i>")

            user_prompt = prompt([("class:prompt", ">>> ")], placeholder=placeholder, history=history, style=style, multiline=False, wrap_lines=True, enable_history_search=True)
            # Disallow empty input
            if not user_prompt:
                continue

            # Exit commandsКто 
            if user_prompt.lower() in ['exit', 'quit', 'q']:
                break

            # If a number is entered
            if user_prompt.isdigit():
                block_index = int(user_prompt)
                if 1 <= block_index <= len(last_code_blocks):
                    run_code_block(console, last_code_blocks, block_index)
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
            last_code_blocks = extract_labeled_code_blocks(reply)
            console.print()  # new line after answer

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(connection_error(e))
            logger.error(f"Connection error: {e}")


@log_execution_time
def main() -> None:

    console = Console()

    # === Initialize OpenRouterChat client ===
    logger.info("Initializing OpenRouterChat client")

    llm_config = config.get_current_llm_config()
    chat_client = OpenRouterClient(
        console=console,
        logger=logger,
        api_key = llm_config["api_key"],
        api_url = llm_config["api_url"],
        model = llm_config["model"],
        system_content=get_system_content(),
        temperature=config.get("global","temperature", 0.7)
    )
    logger.info("OpenRouterChat client created: " + f"{chat_client}")
    

    try:
        args = parse_args()

        # Settings mode
        if args.settings:
            logger.info("Starting configuration mode")
            from aiebash.config_menu import main_menu
            main_menu()
            logger.info("Configuration mode finished")
            return 0

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
