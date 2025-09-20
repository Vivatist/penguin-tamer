#!/usr/bin/env python3
import os
import platform
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
from aiebash.arguments import parse_args
from rich.console import Console
from aiebash.script_executor import run_code_block


# === Считываем глобальные настройки ===
logger.info("Загрузка настроек...")
USER_CONTENT: str = config_manager.get_value("global", "user_content", "")
CURRENT_LLM: str = config_manager.get_value("global", "current_LLM", "openai_over_proxy")
STREAM_OUTPUT_MODE: bool = config_manager.get_value("global","stream_output_mode", False)
JSON_MODE: bool = config_manager.get_value("global", "json_mode", False)

logger.info(f"Заданы настройки - Контент пользователя: {'(пусто)' if not USER_CONTENT else USER_CONTENT[:30] + '...'}")
logger.info(f"Заданы настройки - Текущий LLM: {CURRENT_LLM}")
logger.info(f"Заданы настройки - Режим потокового вывода: {STREAM_OUTPUT_MODE}")
logger.info(f"Заданы настройки - Режим ответов в формате JSON: {JSON_MODE}")


# Ленивый импорт Markdown из rich (легкий модуль) для ускорения загрузки
_markdown = None
def _get_markdown():
    global _markdown
    if _markdown is None:
        from rich.markdown import Markdown
        _markdown = Markdown
    return _markdown

console = Console()

educational_text = \
    f"ВСЕГДА нумеруй блоки кода в ответах, чтобы пользователь мог " \
    f"ссылаться на них. Формат нумерации: [Код #1]\n```bash ... ```, [Код 2]\n```bash ... ```, и так далее. " \
    f"Если в ответе есть несколько блоков кода, нумеруй их последовательно. " \
    f"В каждом своем новом ответе начинай нумерацию с начала 1, 2, 3 и т.д.. Обсуждать с пользователем " \
    f"нумерацию не нужно, просто делай это автоматически."
EDUCATIONAL_CONTENT = [{'role': 'user', 'content': educational_text},]

@log_execution_time
def get_system_content() -> str:
    """Конструирует системный контекст"""
    user_content = config_manager.get_value("global", "user_content", "")
    json_mode = config_manager.get_value("global", "json_mode", False)

    if json_mode:
        additional_content_json = f"Вы всегда отвечаете одним объектом JSON, содержащим поля 'cmd' и 'info'. "
    else:
        additional_content_json = ""

    additional_content_main= \
        f"Ты - Ai-eBash, продвинутая утилита, ассистент системного администратора. Мы всегда работаем в терминале. Пользователь использует '{platform.platform()}'. " \
        f"Имя пользователя - '{os.getenv('USER', 'неизвестно')}', а домашняя директория - '{Path.home()}'. " \
        f"Вы всегда должны использовать LC_TIME {os.getenv('LC_TIME', 'C')}."

    system_content = f"{user_content} {additional_content_json} {additional_content_main}".strip()
    return system_content

# === Инициализация OpenRouterChat клиента ===
logger.info("Инициализация OpenRouterChat клиента")

try:
    chat_client = OpenRouterClient(
        console=console,
        api_key=config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_key", ""),
        api_url=config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_url", ""),
        model=config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("model", ""),
        system_content=get_system_content(),
        temperature=config_manager.get_value("global","temperature", 0.7)
    )
    logger.info("OpenRouterChat клиент создан:" + f"{chat_client}")
except Exception as e:
    logger.error(f"Ошибка при создании OpenRouterChat клиента: {e}", exc_info=True)
    sys.exit(1)

# === Основная логика ===
@log_execution_time
def run_single_query(chat_client: OpenRouterClient, query: str, console: Console) -> None:
    """Выполнение одиночного запроса в потоковом режиме"""
    logger.info(f"Выполнение запроса: '{query[:50]}'...")
    try:
        if STREAM_OUTPUT_MODE:
            reply = chat_client.ask_stream(query)
        else:
            reply = chat_client.ask(query)
            console.print(_get_markdown()(reply))
        logger.info("Запрос выполнен успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        console.print(f"[dim]Ошибка:[/dim] {e}")

@log_execution_time
def run_dialog_mode(chat_client: OpenRouterClient, console: Console, initial_user_prompt: str = None) -> None:
    """Интерактивный режим диалога"""
    
    logger.info("Запуск режима диалога")

    # Используем модульную глобальную переменную EDUCATIONAL_CONTENT внутри функции
    global EDUCATIONAL_CONTENT

    last_code_blocks = []  # Список блоков кода из последнего ответа AI

    # Если есть начальный промпт, обрабатываем его
    if initial_user_prompt:
        initial_user_prompt
        try:
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(initial_user_prompt)
            else:
                reply = chat_client.ask(initial_user_prompt, educational_content=EDUCATIONAL_CONTENT)
                EDUCATIONAL_CONTENT = [] # Очищаем образовательный контент после первого использования
                console.print(_get_markdown()(reply))
            last_code_blocks = extract_labeled_code_blocks(reply)
        except Exception as e:
            logger.error(f"Ошибка при обработке начального запроса: {e}")
            console.print(f"[dim]Ошибка:[/dim] {e}")
        console.print()

    # Основной цикл диалога
    while True:
        try:
            user_prompt = console.input("[cyan]Вы:[/cyan] ").strip()

            # Запрет пустого ввода
            if not user_prompt:
                continue

            # Команды выхода
            if user_prompt.lower() in ['exit', 'quit', 'q', 'выход']:
                break

            # Проверка, если введено число
            if user_prompt.isdigit():
                block_index = int(user_prompt)
                if 1 <= block_index <= len(last_code_blocks):
                    run_code_block(console, last_code_blocks, block_index)
                    console.print()
                    continue
                else:
                    console.print(f"[dim]Блок кода #{user_prompt} не найден.[/dim]")
                    continue

            # Если введен текст, отправляем как запрос к AI
            if STREAM_OUTPUT_MODE:
                reply = chat_client.ask_stream(user_prompt, educational_content=EDUCATIONAL_CONTENT)
            else:
                reply = chat_client.ask(user_prompt, educational_content=EDUCATIONAL_CONTENT)    
                console.print(_get_markdown()(reply))
            EDUCATIONAL_CONTENT = [] # Очищаем образовательный контент после первого использования
            last_code_blocks = extract_labeled_code_blocks(reply)
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

        if dialog_mode or not prompt:
            # Режим диалога
            logger.info("Запуск в режиме диалога")
            run_dialog_mode(chat_client, console, prompt if prompt else None)
        else:
            # Обычный режим (одиночный запрос)
            logger.info("Запуск в режиме одиночного запроса")

            run_single_query(chat_client, prompt, console)

    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        return 130
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)
        return 1
    finally:
        print()  # Печатаем пустую строку в любом случае

    logger.info("Программа завершена успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
