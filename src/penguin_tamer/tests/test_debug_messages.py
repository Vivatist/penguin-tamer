#!/usr/bin/env python3
"""
Пример использования debug_print_messages для отладки структуры LLM запросов.

Запуск:
    python test_debug_messages.py
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from penguin_tamer.llm_client import debug_print_messages


def test_simple_conversation():
    """Пример простого диалога"""
    print("\n=== Test 1: Simple Conversation ===\n")
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful Linux system administrator assistant."
        },
        {
            "role": "user",
            "content": "How do I list all files in a directory?"
        },
        {
            "role": "assistant",
            "content": "You can use the `ls` command:\n\n```bash\nls -la\n```\n\nThis shows all files including hidden ones with detailed information."
        },
        {
            "role": "user",
            "content": "What about sorting by modification time?"
        }
    ]
    
    debug_print_messages(
        messages, 
        model="gpt-4", 
        temperature=0.7,
        max_tokens=2000,
        top_p=0.95
    )


def test_educational_prompt():
    """Пример с educational prompt"""
    print("\n=== Test 2: With Educational Prompt ===\n")
    
    messages = [
        {
            "role": "system",
            "content": "Your name is Penguin Tamer, a sysadmin assistant. You and the user always work in a terminal."
        },
        {
            "role": "user",
            "content": "ALWAYS number code blocks in your replies so the user can reference them. Numbering format: [Code #1]\\n```bash ... ```"
        },
        {
            "role": "user",
            "content": "Show me how to install nginx"
        }
    ]
    
    debug_print_messages(
        messages, 
        model="microsoft/mai-ds-r1:free", 
        temperature=0.8,
        frequency_penalty=0.3,
        presence_penalty=0.2
    )


def test_long_content():
    """Пример с длинным контентом (для проверки обрезки)"""
    print("\n=== Test 3: Long Content (Truncation Test) ===\n")
    
    long_text = "This is a very long content. " * 50  # Создаём длинный текст
    
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant."
        },
        {
            "role": "user",
            "content": long_text
        }
    ]
    
    debug_print_messages(
        messages,
        temperature=0.5,
        max_tokens=1000,
        stop=["\n\n\n"]
    )


def test_multi_turn_conversation():
    """Пример многоходового диалога"""
    print("\n=== Test 4: Multi-turn Conversation ===\n")
    
    messages = [
        {"role": "system", "content": "You are a Python expert."},
        {"role": "user", "content": "What is a decorator?"},
        {"role": "assistant", "content": "A decorator is a function that modifies another function."},
        {"role": "user", "content": "Show me an example"},
        {"role": "assistant", "content": "```python\ndef my_decorator(func):\n    def wrapper():\n        print('Before')\n        func()\n        print('After')\n    return wrapper\n```"},
        {"role": "user", "content": "Thanks! How do I use it?"}
    ]
    
    debug_print_messages(
        messages, 
        model="deepseek-chat", 
        temperature=0.5,
        max_tokens=4000,
        top_p=0.9,
        frequency_penalty=0.5,
        presence_penalty=0.3,
        seed=42
    )


if __name__ == "__main__":
    print("🔍 Testing debug_print_messages function\n")
    
    # Запускаем все тесты
    test_simple_conversation()
    test_educational_prompt()
    test_long_content()
    test_multi_turn_conversation()
    
    print("\n✅ All tests completed!\n")
