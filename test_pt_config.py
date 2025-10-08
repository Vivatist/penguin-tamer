#!/usr/bin/env python
"""Тест конфигурации для pt"""
import sys
sys.path.insert(0, 'src')

from penguin_tamer.config_manager import config
from penguin_tamer.llm_client import OpenRouterClient, LLMConfig
from penguin_tamer.prompts import get_system_prompt
from rich.console import Console

console = Console()

print("=== Проверка конфигурации ===")
print(f"Current LLM: {config.current_llm}")

llm_config = config.get_current_llm_config()
print(f"Model: {llm_config.get('model')}")
print(f"API URL: {llm_config.get('api_url')}")
print(f"API key exists: {bool(llm_config.get('api_key'))}")
print(f"API key length: {len(llm_config.get('api_key', ''))}")

print("\n=== Создание клиента ===")
full_llm_config = LLMConfig(
    api_key=llm_config["api_key"],
    api_url=llm_config["api_url"],
    model=llm_config["model"],
    temperature=config.get("global", "temperature", 0.7),
    max_tokens=config.get("global", "max_tokens", None),
    top_p=config.get("global", "top_p", 0.95),
    frequency_penalty=config.get("global", "frequency_penalty", 0.0),
    presence_penalty=config.get("global", "presence_penalty", 0.0),
    stop=config.get("global", "stop", None),
    seed=config.get("global", "seed", None)
)

chat_client = OpenRouterClient(
    console=console,
    system_message=get_system_prompt(),
    llm_config=full_llm_config
)

print(f"Client created")
print(f"Client API URL: {chat_client.api_url}")
print(f"Client model: {chat_client.model}")

# Проверяем заголовки
_ = chat_client.client
print(f"Client has default_headers: {hasattr(chat_client._client, 'default_headers')}")
if hasattr(chat_client._client, 'default_headers'):
    print(f"Default headers: {chat_client._client.default_headers}")

print("\n=== Тестовый запрос ===")
try:
    response = chat_client.ask_stream("Скажи только 'OK'")
    print(f"Success! Response: {response[:50]}...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
