import argparse

from aiebash.logger import logger, log_execution_time
from aiebash.i18n import t


parser = argparse.ArgumentParser(
    prog="ai",
    description=t("A CLI to chat with LLMs (OpenAI, HuggingFace, Ollama, etc.) directly from your terminal."),
)

parser.add_argument(
    "-d",
    "--dialog",
    action="store_true",
    help=t("Dialog mode with ability to execute code blocks from the answer. Type the block number and press Enter. Exit: exit, quit or Ctrl+C."),
)

parser.add_argument(
    "-s",
    "--settings",
    action="store_true",
    help=t("Open interactive settings menu."),
)

parser.add_argument(
    "prompt",
    nargs="*",
    help=t("Your prompt to the AI."),
)


@log_execution_time
def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    args = parser.parse_args()
    logger.info("Parsing command line arguments...")
    logger.debug(f"Args received: dialog={args.dialog}, settings={args.settings}, prompt={args.prompt or '(empty)'}")
    return args
