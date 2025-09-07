#!/usr/bin/env python3
import sys
import json
import requests
from settings import API_URL, MODEL, CONTEXT, EXTRA_CONTEXT
import os
import subprocess

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

def main():
    if len(sys.argv) < 2:
        print("Использование: ai ваш запрос к ИИ без кавычек")
        sys.exit(1)

    # Объединяем все аргументы в одну строку
    prompt = " ".join(sys.argv[1:])

    # Формируем полный контекст
    system_context = get_system_context()
    full_context = system_context + "\n" + "\n".join(EXTRA_CONTEXT)

    # Отправляем как системное сообщение + пользовательский запрос
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": full_context},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            print(answer)
        else:
            print("Ошибка: неожиданный формат ответа:", data)

    except requests.exceptions.HTTPError as e:
        print("HTTP ошибка:", e)
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
