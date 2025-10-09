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
_get_theme_func = None


def _get_theme():
    """Ленивый импорт get_theme"""
    global _get_theme_func
    if _get_theme_func is None:
        from penguin_tamer.themes import get_theme
        _get_theme_func = get_theme
    return _get_theme_func


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
from penguin_tamer.llm_client import OpenRouterClient, LLMConfig
from penguin_tamer.arguments import parse_args
from penguin_tamer.error_handlers import connection_error
from penguin_tamer.dialog_input import DialogInputFormatter
from penguin_tamer.prompts import get_system_prompt, get_educational_prompt


# === Основная логика ===
def run_single_query(chat_client: OpenRouterClient, query: str, console) -> None:
    """Run a single query (optionally streaming)"""
    try:
        chat_client.ask_stream(query)
    except Exception as e:
        console.print(connection_error(e))


def _is_exit_command(prompt: str) -> bool:
    """Check if user wants to exit."""
    return prompt.lower() in ['exit', 'quit', 'q']


def _add_command_to_context(
    chat_client: OpenRouterClient, command: str, result: dict, block_number: int = None
) -> None:
    """Add executed command and its result to chat context.

    Args:
        chat_client: LLM client to add context to
        command: Executed command
        result: Execution result dictionary
        block_number: Optional code block number
    """
    # Формируем сообщение пользователя о выполнении команды
    if block_number is not None:
        user_message = t("Execute code block #{number}:").format(number=block_number) + f"\n```\n{command}\n```"
    else:
        user_message = t("Execute command: {command}").format(command=command)

    # Формируем системное сообщение с результатом
    if result['interrupted']:
        system_message = t("Command execution was interrupted by user (Ctrl+C).")
    elif result['success']:
        output_parts = []
        if result['stdout']:
            output_parts.append(t("Output:") + f"\n{result['stdout']}")
        if result['stderr']:
            output_parts.append(t("Errors:") + f"\n{result['stderr']}")

        if output_parts:
            system_message = t("Command executed successfully (exit code: 0).") + "\n" + "\n".join(output_parts)
        else:
            system_message = t("Command executed successfully (exit code: 0). No output.")
    else:
        output_parts = [t("Command failed with exit code: {code}").format(code=result['exit_code'])]
        if result['stdout']:
            output_parts.append(t("Output:") + f"\n{result['stdout']}")
        if result['stderr']:
            output_parts.append(t("Errors:") + f"\n{result['stderr']}")
        system_message = "\n".join(output_parts)

    # Добавляем в контекст диалога
    chat_client.messages.append({"role": "user", "content": user_message})
    chat_client.messages.append({"role": "system", "content": system_message})


def _handle_direct_command(console, chat_client: OpenRouterClient, prompt: str) -> bool:
    """Execute direct shell command (starts with dot) and add to context.

    Args:
        console: Rich console for output
        chat_client: LLM client to add command context
        prompt: User input

    Returns:
        True if command was handled, False otherwise
    """
    if not prompt.startswith('.'):
        return False

    command = prompt[1:].strip()
    if not command:
        console.print(t("[dim]Empty command after '.' - skipping.[/dim]"))
        return True

    console.print(t("[dim]>>> Executing command:[/dim] {command}").format(command=command))

    # Выполняем команду и получаем результат
    result = _get_execute_handler()(console, command)
    console.print()

    # Добавляем команду и результат в контекст
    _add_command_to_context(chat_client, command, result)

    return True


def _handle_code_block_execution(console, chat_client: OpenRouterClient, prompt: str, code_blocks: list) -> bool:
    """Execute code block by number and add to context.

    Args:
        console: Rich console for output
        chat_client: LLM client to add command context
        prompt: User input
        code_blocks: List of available code blocks

    Returns:
        True if code block was executed, False otherwise
    """
    if not prompt.isdigit():
        return False

    block_index = int(prompt)
    if 1 <= block_index <= len(code_blocks):
        code = code_blocks[block_index - 1]

        # Выполняем блок кода и получаем результат
        result = _get_script_executor()(console, code_blocks, block_index)
        console.print()

        # Добавляем команду и результат в контекст
        _add_command_to_context(chat_client, code, result, block_number=block_index)

        return True

    console.print(t("[dim]Code block #{number} not found.[/dim]").format(number=prompt))
    return True


def _process_ai_query(chat_client: OpenRouterClient, console, prompt: str) -> list:
    """Send query to AI and extract code blocks from response.

    Returns:
        List of code blocks from AI response
    """
    reply = chat_client.ask_stream(prompt)
    code_blocks = []

    # Извлекаем блоки кода только если получен непустой ответ
    if reply:
        code_blocks = _get_formatter_text()(reply)

    console.print()
    return code_blocks


def _process_initial_prompt(chat_client: OpenRouterClient, console, prompt: str) -> list:
    """Process initial user prompt if provided.

    Returns:
        List of code blocks from response
    """
    if not prompt:
        return []

    try:
        return _process_ai_query(chat_client, console, prompt)
    except Exception as e:
        console.print(connection_error(e))
        console.print()
        return []


def run_dialog_mode(chat_client: OpenRouterClient, console, initial_user_prompt: str = None) -> None:
    """Interactive dialog mode with educational prompt for code block numbering.

    Args:
        chat_client: Initialized LLM client
        console: Rich console for output
        initial_user_prompt: Optional initial prompt to process before entering dialog loop
    """
    # Setup
    history_file_path = config.user_config_dir / "cmd_history"
    input_formatter = DialogInputFormatter(history_file_path)

    # Initialize dialog mode with educational prompt
    educational_prompt = get_educational_prompt()
    chat_client.init_dialog_mode(educational_prompt)

    # Process initial prompt if provided
    last_code_blocks = _process_initial_prompt(chat_client, console, initial_user_prompt)

    # Main dialog loop
    while True:
        try:
            # Get user input
            user_prompt = input_formatter.get_input(
                console,
                has_code_blocks=bool(last_code_blocks),
                t=t
            )

            if not user_prompt:
                continue

            # Check for exit
            if _is_exit_command(user_prompt):
                break

            # Handle direct command execution (with context)
            if _handle_direct_command(console, chat_client, user_prompt):
                continue

            # Handle code block execution (with context)
            if _handle_code_block_execution(console, chat_client, user_prompt, last_code_blocks):
                continue

            # Process as AI query
            last_code_blocks = _process_ai_query(chat_client, console, user_prompt)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(connection_error(e))


def _create_chat_client(console):
    """Ленивое создание LLM клиента только когда он действительно нужен"""

    # Убеждаемся, что i18n инициализирован перед созданием клиента
    _ensure_i18n()

    llm_config = config.get_current_llm_config()

    # Создаём полную конфигурацию LLM (подключение + генерация)
    full_llm_config = LLMConfig(
        # Connection parameters
        api_key=llm_config["api_key"],
        api_url=llm_config["api_url"],
        model=llm_config["model"],
        # Generation parameters
        temperature=config.get("global", "temperature", 0.7),
        max_tokens=config.get("global", "max_tokens", None),
        top_p=config.get("global", "top_p", 0.95),
        frequency_penalty=config.get("global", "frequency_penalty", 0.0),
        presence_penalty=config.get("global", "presence_penalty", 0.0),
        stop=config.get("global", "stop", None),
        seed=config.get("global", "seed", None)
    )

    # Создаём клиент с единой конфигурацией
    chat_client = OpenRouterClient(
        console=console,
        system_message=get_system_prompt(),
        llm_config=full_llm_config
    )
    return chat_client


def _create_console():
    """Создание Rich Console с темой из конфига."""
    Console = _get_console_class()
    theme_name = config.get("global", "markdown_theme", "default")
    markdown_theme = _get_theme()(theme_name)
    return Console(theme=markdown_theme)


def main() -> None:
    """Main entry point for Penguin Tamer CLI."""
    try:
        args = parse_args()

        # Settings mode - не нужен LLM клиент
        if args.settings:
            from penguin_tamer.menu.config_menu import main_menu
            main_menu()
            return 0

        # Создаем консоль и клиент только если они нужны для AI операций
        console = _create_console()
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
        print(f"Ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print()  # print empty line anyway

    return 0


if __name__ == "__main__":
    sys.exit(main())
