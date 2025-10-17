"""Penguin Tamer - AI-powered terminal assistant."""

# debug_print_messages moved to debug module
# Old imports are kept for backward compatibility
from penguin_tamer.llm_clients import ClientFactory, LLMConfig

__all__ = ["ClientFactory", "LLMConfig"]

# TODO: добавить возможность сохранения 10 последних сессий и их возобновления
