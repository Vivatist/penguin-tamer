import re
import platform
from aiebash.logger import log_execution_time


@log_execution_time
def format_api_key_display(api_key: str) -> str:
    """Форматирует отображение API ключа для логирования"""
    if not api_key:
        return "(не задан)"
    elif len(api_key) <= 10:
        return api_key
    else:
        return f"{api_key[:5]}...{api_key[-5:]}"


@log_execution_time
def extract_labeled_code_blocks(text: str) -> list[str]:
    """
    Извлекает содержимое блоков кода, у которых сверху есть подпись в квадратных скобках.
    Подпись может быть любой: [Код #1], [Пример], [Test], и т.п.
    """
    pattern = r"\[[^\]]+\]\s*```.*?\n(.*?)```"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    return [m.strip() for m in matches]
