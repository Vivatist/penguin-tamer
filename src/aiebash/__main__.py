#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config_manager

# Теперь импортируем и настраиваем логгер
from aiebash.logger import configure_logger

# Получаем настройки логирования и настраиваем логгер
logging_config = config_manager.get_logging_config()
logger = configure_logger(logging_config)

# Импортируем OpenRouterChat вместо старых модулей
from aiebash.llm_chat import OpenRouterChat
from aiebash.arguments import parse_args, parser
from rich.console import Console
from rich.markdown import Markdown
from aiebash.script_executor import run_code_block


# === Считываем глобальные настройки ===
logger.info("Загрузка настроек...")
CONTEXT: str = config_manager.get_value("global", "context", "")
CURRENT_LLM: str = config_manager.get_value("global", "current_LLM", "openai_over_proxy")
TEMPERATURE: float = config_manager.get_value("global","temperature", 0.7)

logger.debug(f"Заданы настройки - Системный контекст: {'(пусто)' if not CONTEXT else CONTEXT[:30] + '...'}")
logger.debug(f"Заданы настройки - Текущий LLM: {CURRENT_LLM}")

# Настройки конкретного LLM (например, openai_over_proxy)
MODEL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("model", "")
API_URL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_url", "")
API_KEY = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_key", "")


logger.debug(f"Заданы настройки - Модель: {MODEL}")
logger.debug(f"Заданы настройки - API URL: {API_URL}")
logger.debug(f"Заданы настройки - API Key: {'(не задан)' if not API_KEY else f'{API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else API_KEY}'}")
logger.debug(f"Заданы настройки - Temperature: {TEMPERATURE}")

console = Console()

# === Инициализация OpenRouterChat клиента ===
logger.debug("Инициализация OpenRouterChat клиента")
try:
    chat_client = OpenRouterChat(
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
def run_single_query(chat_client: OpenRouterChat, query: str, console: Console) -> None:
    """Выполнение одиночного запроса в потоковом режиме"""
    logger.info(f"Выполнение запроса: '{query[:50]}'...")
    try:
        # Используем потоковый режим для вывода ответа
        response = chat_client.ask_stream(query)
        logger.info("Запрос выполнен успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        console.print(f"[red]Ошибка:[/red] {e}")


def run_dialog_mode(chat_client: OpenRouterChat, console: Console, initial_prompt: str = None) -> None:
    """Интерактивный режим диалога"""
    
    logger.info("Запуск режима диалога")

    logger.info("[bold green]Режим диалога активирован![/bold green]")
    logger.info("Введите ваш запрос или 'exit' для выхода.")
    console.print()

    last_code_blocks = []  # Список блоков кода из последнего ответа AI

    # Если есть начальный промпт, обрабатываем его
    if initial_prompt:
        console.print(f"[bold blue]Начальный запрос:[/bold blue] {initial_prompt}")
        try:
            reply, code_blocks = chat_client.ask(initial_prompt)
            last_code_blocks = code_blocks
            console.print(Markdown(reply))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке начального запроса: {e}")
            console.print(f"[red]Ошибка:[/red] {e}")
        console.print()

    # Основной цикл диалога
    while True:
        try:
            user_input = console.input("[bold cyan]Вы:[/bold cyan] ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q', 'выход']:
                console.print("[yellow]До свидания![/yellow]")
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
                    console.print(f"[red]Блок кода #{user_input} не найден.[/red]")
                    continue

            # Если введен текст, отправляем как запрос к AI
            console.print("[bold green]AI:[/bold green] ", end="")
            response, code_blocks = chat_client.ask(user_input)
            last_code_blocks = code_blocks
            console.print(Markdown(response))
            console.print()  # Новая строка после ответа

        except KeyboardInterrupt:
            console.print("\n[yellow]Диалог прерван пользователем[/yellow]")
            break
        except Exception as e:
            logger.error(f"Ошибка в режиме диалога: {e}")
            console.print(f"[red]Ошибка:[/red] {e}")
def main() -> None:
    try:
        args = parse_args()
        logger.info("Разбор аргументов командной строки...")
        logger.debug(f"Полученные аргументы: dialog={args.dialog}, settings={args.settings}, prompt={args.prompt or '(пусто)'}")

        # Обработка режима настройки
        if args.settings:
            logger.info("Запуск конфигурационного режима")
            try:
                from aiebash.config_manager import run_configuration_dialog
                run_configuration_dialog()
                logger.info("Конфигурационный режим завершен")
                return 0
            except Exception as e:
                logger.error(f"Ошибка в режиме конфигурации: {e}", exc_info=True)
                return 1

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
