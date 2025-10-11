import argparse

from penguin_tamer.i18n import t


def _get_version() -> str:
    """Get version from installed package metadata."""
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("penguin-tamer")
        except PackageNotFoundError:
            return "0.7.0.dev0"
    except ImportError:
        # Fallback for older Python versions
        try:
            import pkg_resources
            return pkg_resources.get_distribution("penguin-tamer").version
        except Exception:
            return "0.7.0.dev0"


__version__ = _get_version()


parser = argparse.ArgumentParser(
    prog="pt",
    description=t("🐧 Penguin Tamer - AI-powered terminal assistant. "
                  "Chat with LLMs (OpenAI, HuggingFace, Ollama, etc.) directly from your terminal."),
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
