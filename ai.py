#!/usr/bin/env python3
import os
import json
import requests
import settings

HISTORY_FILE = "/tmp/deepseek_history.json"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Проверка ключа
API_KEY = settings.API_KEY
if not API_KEY:
    print("Ошибка: не найден ключ API_KEY")
    exit(1)
print("Ключ API загружен.", API_KEY[:4] + "..." + API_KEY[-4:])

# Загружаем историю
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = {"messages": []}

print("=== DeepSeek Chat (напиши 'exit' для выхода, 'clear' для очистки истории) ===")

while True:
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nВыход.")
        break

    if user_input.lower() == "exit":
        print("Выход из DeepSeek Chat.")
        break
    if user_input.lower() == "clear":
        history = {"messages": []}
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print("История очищена.")
        continue

    # Добавляем сообщение пользователя
    history["messages"].append({"role": "user", "content": user_input})

    # Запрос к OpenRouter
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": history["messages"]
        },
        timeout=60
    )

    if response.status_code != 200:
        print("Ошибка запроса:", response.status_code, response.text)
        continue

    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    print(reply)

    # Добавляем ответ ассистента в историю
    history["messages"].append({"role": "assistant", "content": reply})

    # Сохраняем историю
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
