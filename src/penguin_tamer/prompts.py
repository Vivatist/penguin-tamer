"""System prompts and educational prompts for LLM interactions."""

from typing import List

from penguin_tamer.config_manager import config
from penguin_tamer.system_info import get_system_info_text
from penguin_tamer.i18n import t


def get_system_prompt() -> List[dict[str, str]]:
    """
    Construct the system prompt for LLM.

    Returns:
        List[dict]: List containing system message in OpenAI format
    """
    user_prompt = config.get("global", "user_content", "")

    base_prompt = t(
        "Your name is Penguin Tamer, a sysadmin assistant. "
        "You and the user always work in a terminal. "
        "Respond based on the user's environment and commands."
    )

    # Получаем актуальную информацию о системе
    system_info = get_system_info_text()
    system_info_prompt = t("The current system information is as follows:") + f"\n{system_info}\n"

    if user_prompt:
        system_prompt = f"{user_prompt} {base_prompt} {system_info_prompt}".strip()
    else:
        system_prompt = f"{base_prompt} {system_info_prompt}".strip()

    return [{"role": "system", "content": system_prompt}]


def get_educational_prompt() -> List[dict[str, str]]:
    """
    Get educational prompt for teaching LLM to number code blocks.

    This prompt is sent once at the beginning of a conversation to instruct
    the model to automatically number all code blocks for easy reference.

    Returns:
        List[dict]: List containing educational messages in OpenAI format
    """
    educational_user_prompt = t(
        "IF your response contains code blocks, ALWAYS number the code blocks so that the user can link to them. "
        "Numbering format: \n"
        "[Code #1]\n"
        "```bash\n"
        "echo \"Hello, World!\"\n"
        "```\n"
        "[Code #2]\n"
        "```bash\n"
        "echo \"Hello, World!\"\n"
        "```\n"
        "etc. Insert the numbering BEFORE the block. "
        "If there are multiple code blocks, number them sequentially. "
        "In each new reply, start numbering from 1 again. "
        "Don't discuss the numbering, don't report it, and don't talk about it; just number it."
    )

    educational_assistant_prompt = t(
        "Understood. All subsequent responses will contain numbered code blocks in the specified format.\n"
        "\n"
        "[Code #1]\n"
        "```bash\n"
        "echo \"Ready to work. Please provide a task to execute.\"\n"
        "```"
    )

    return [
        {"role": "user", "content": educational_user_prompt},
        {"role": "assistant", "content": educational_assistant_prompt}
    ]
