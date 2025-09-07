#!/usr/bin/env python3
import sys
import json
import requests
from settings import API_URL, MODEL, CONTEXT, EXTRA_CONTEXT
import os
import subprocess
import re

# ANSI цвета и стили
YELLOW = "\033[33m"
GRAY_ITALIC = "\033[90m\033[3m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_system_context():
    """Подставляем реальные значения вместо $SHELL, $HOME, lsb_release"""
    try:
        ubuntu_version = subprocess.check_output(
            ["lsb_release", "-ds"], text=True
        ).strip()
    except Exception:
        ubuntu_version = "Ubuntu unknown"

    shell = os.environ.get("SHELL", "bash")
    home = os.environ.get("HOME", "/home/user")

    context = CONTEXT.replace("$(lsb_release -ds)", ubuntu_version)
    context = context.replace("$SHELL", shell).replace("$HOME", home)
    return context

def highlight_code_blocks(text):
    """Подсветка блоков кода в жёлтый"""
    def repl(match):
        code = match.group(1)
        return f"{YELLOW}{code}{RESET}"
    pattern = re.compile(r"```.*?\n(.*?)```", re.DOTALL)
    return pattern.sub(repl, text)

def highlight_explanation_blocks(text):
    """Подсветка блоков между ### ... ### в серый курсив"""
    def repl(match):
        content = match.group(1).strip()
        return f"{GRAY_ITALIC}{content}{RESET}"
    pattern = re.compile(r"###(.*?)###", re.DOTALL)
    return pattern.sub(repl, text)

def highlight_inline_code(text):
    """Подсветка инлайн-кода `...` в зелёный"""
    def repl(match):
        code = match.group(1)
        return f"{GREEN}{code}{RESET}"
    pattern = re.compile(r"`([^`]+)`")
    return pattern.sub(repl, text)

def highlight_bold(text):
    """Подсветка текста между **...** жирным"""
    def repl(match):
        bold_text = match.group(1)
        return f"{BOLD}{bold_text}{RESET}"
    # Чтобы не путать с markdown `***`, обрабатываем только пары **
    pattern = re.compile(r"\*\*(.*?)\*\*")
    return pattern.sub(repl, text)

def format_answer(text):
    """Применяем все правила форматирования"""
    text = highlight_code_blocks(text)
    text = highlight_explanation_blocks(text)
    text = highlight_inline_code(text)
    text = highlight_bold(text)
    return text

def main():
    if len(sys.argv) < 2:
        print("Использование: ai ваш запрос к ИИ без кавычек")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])

    system_context = get_system_context()
    full_context = system_context + "\n" + "\n".join(EXTRA_CONTEXT)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": full_context},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            answer = format_answer(answer)
            print(answer)
        else:
            print("Ошибка: неожиданный формат ответа:", data)

    except requests.exceptions.HTTPError as e:
        print("HTTP ошибка:", e)
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
