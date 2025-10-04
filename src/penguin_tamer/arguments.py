import argparse

from penguin_tamer.i18n import t
from penguin_tamer._version import __version__


parser = argparse.ArgumentParser(
    prog="pt",
    description=t("🐧 Penguin Tamer - AI-powered terminal assistant. "
                  "Chat with LLMs (OpenAI, HuggingFace, Ollama, etc.) directly from your terminal."),
)

parser.add_argument(
    "-d",
    "--dialog",
    action="store_true",
    help=t("Dialog mode with ability to execute code blocks from the answer. "
           "Type the block number and press Enter. Exit: exit, quit or Ctrl+C."),
)

parser.add_argument(
    "-s",
    "--settings",
    action="store_true",
    help=t("Open interactive settings menu."),
)

parser.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
)

parser.add_argument(
    "prompt",
    nargs="*",
    help=t("Your prompt to the AI."),
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    args = parser.parse_args()
    return args
