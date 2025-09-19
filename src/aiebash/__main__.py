#!/usr/bin/env python3
import sys
from pathlib import Path

from aiebash.formatter_text import extract_labeled_code_blocks

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config_manager

# Теперь импортируем и настраиваем логгер
from aiebash.logger import configure_logger, log_execution_time

# Получаем настройки логирования и настраиваем логгер
logging_config = config_manager.get_logging_config()
logger = configure_logger(logging_config)

# Импортируем OpenRouterChat вместо старых модулей
from aiebash.llm_client import OpenRouterClient
from aiebash.arguments import parse_args, parser
from rich.console import Console
from rich.markdown import Markdown
from aiebash.script_executor import run_code_block


# === Считываем глобальные настройки ===
logger.info("Загрузка настроек...")
CONTEXT: str = config_manager.get_value("global", "context", "")
CURRENT_LLM: str = config_manager.get_value("global", "current_LLM", "openai_over_proxy")
TEMPERATURE: float = config_manager.get_value("global","temperature", 0.7)

logger.info(f"Заданы настройки - Системный контекст: {'(пусто)' if not CONTEXT else CONTEXT[:30] + '...'}")
logger.info(f"Заданы настройки - Текущий LLM: {CURRENT_LLM}")

# Настройки конкретного LLM (например, openai_over_proxy)
MODEL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("model", "")
API_URL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_url", "")
API_KEY = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_key", "")


logger.info(f"Заданы настройки - Модель: {MODEL}")
logger.info(f"Заданы настройки - API URL: {API_URL}")
logger.info(f"Заданы настройки - API Key: {'(не задан)' if not API_KEY else f'{API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else API_KEY}'}")
logger.info(f"Заданы настройки - Temperature: {TEMPERATURE}")


console = Console()

# === Инициализация OpenRouterChat клиента ===
logger.debug("Инициализация OpenRouterChat клиента")
try:
    chat_client = OpenRouterClient(
        console=console,
        api_key=API_KEY,
        api_url=API_URL,
        model=MODEL,
        system_context=CONTEXT or "You are a helpful assistant.",
        temperature=TEMPERATURE
    )
except Exception as e:
    logger.error(f"Ошибка при создании OpenRouterChat клиента: {e}", exc_info=True)
    sys.exit(1)


# === Основная логика ===
@log_execution_time
def run_single_query(chat_client: OpenRouterClient, query: str, console: Console) -> None:
    """Выполнение одиночного запроса в потоковом режиме"""
    logger.info(f"Выполнение запроса: '{query[:50]}'...")
    try:
        # Используем потоковый режим для вывода ответа
        reply = chat_client.ask_stream(query)
        # console.print(Markdown(reply))
        logger.info("Запрос выполнен успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        console.print(f"[dim]Ошибка:[/dim] {e}")



@log_execution_time
def run_dialog_mode(chat_client: OpenRouterClient, console: Console, initial_prompt: str = None) -> None:
    """Интерактивный режим диалога"""
    
    additional_context = " ВСЕГДА нумеруй блоки кода в ответах, чтобы пользователь мог ссылаться на них. Формат нумерации: [Код #1]\n```bash ... ```, [Код 2]\n```bash ... ```, и так далее. Если в ответе есть несколько блоков кода, нумеруй их последовательно. В новом ответе начинай нумерацию с 1. Обсуждать с пользователем нумерацию не нужно, просто делай это автоматически."

    logger.info("Запуск режима диалога")

    last_code_blocks = []  # Список блоков кода из последнего ответа AI

    # Если есть начальный промпт, обрабатываем его
    if initial_prompt:
        initial_prompt += additional_context
        try:
            reply = chat_client.ask_stream(initial_prompt)
            last_code_blocks = extract_labeled_code_blocks(reply)
        except Exception as e:
            logger.error(f"Ошибка при обработке начального запроса: {e}")
            console.print(f"[dim]Ошибка:[/dim] {e}")
        console.print()

    # Основной цикл диалога
    while True:
        try:
            user_input = console.input("[bold cyan]Вы:[/bold cyan] ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q', 'выход']:
                console.print("[dim]До свидания![/dim]")
                break

            if not user_input:
                continue

            # Проверка, если введено число
            if user_input.isdigit():
                block_index = int(user_input)
                if 1 <= block_index <= len(last_code_blocks):
                    run_code_block(console, last_code_blocks, block_index)
                    console.print()
                    continue
                else:
                    console.print(f"[dim]Блок кода #{user_input} не найден.[/dim]")
                    continue

            # Если введен текст, отправляем как запрос к AI
            reply = chat_client.ask_stream(user_input)
            console.print()  # Новая строка после ответа

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Ошибка в режиме диалога: {e}")
            console.print(f"[dim]Ошибка:[/dim] {e}")




@log_execution_time
def main() -> None:
    try:
        args = parse_args()


        # Обработка режима настройки
        if args.settings:
            logger.info("Запуск конфигурационного режима")
            from aiebash.config_manager import run_configuration_dialog
            run_configuration_dialog()
            logger.info("Конфигурационный режим завершен")
            return 0


        # Определяем режим работы
        dialog_mode: bool = args.dialog
        prompt_parts: list = args.prompt or []
        prompt: str = " ".join(prompt_parts).strip()

        if dialog_mode:
            # Режим диалога
            logger.info("Запуск в режиме диалога")
            run_dialog_mode(chat_client, console, prompt if prompt else None)
        else:
            # Обычный режим (одиночный запрос)
            logger.info("Запуск в режиме одиночного запроса")
            if not prompt:
                logger.warning("Запрос не предоставлен, показываем справку")
                parser.print_help()
                return 1

            run_single_query(chat_client, prompt, console)

    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        return 130
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)
        return 1

    logger.info("Программа завершена успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
