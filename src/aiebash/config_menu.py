#!/usr/bin/env python3
"""
Меню конфигурации с использованием inquirer.

Позволяет управлять настройками config.yaml через интерактивное меню.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import inquirer
from aiebash.config_manager import config


def main_menu():
    """Главное меню приложения."""
    while True:
        questions = [
            inquirer.List('choice',
                         message="Выберите действие",
                         choices=[
                             ('Управление нейросетями', 'llm'),
                            ('Редактировать контент', 'content'),
                             ('Системные настройки', 'system'),
                             ('Выход', 'exit')
                         ])
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'llm':
            llm_management_menu()
        elif choice == 'system':
            system_settings_menu()
        elif choice == 'content':
            edit_user_content()
        elif choice == 'exit':
            break


def llm_management_menu():
    """Меню управления нейросетями."""
    while True:
        # Получаем список LLM с отметкой текущей
        available_llms = config.get_available_llms()
        current_llm = config.current_llm

        choices = []
        for llm in available_llms:
            marker = " [текущая]" if llm == current_llm else ""
            choices.append((f"{llm}{marker}", llm))

        choices.extend([
            ('Добавить новую нейросеть', 'add'),
            ('Назад', 'back')
        ])

        questions = [
            inquirer.List('choice',
                         message="Управление нейросетями",
                         choices=choices)
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'add':
            add_llm()
        elif choice == 'back':
            break
        else:
            # Выбрана конкретная LLM для редактирования
            edit_llm(choice)


def edit_llm(llm_name):
    """Редактирование настроек конкретной LLM."""
    llm_config = config.get_llm_config(llm_name)

    print(f"\nНастройки для: {llm_name}")
    print(f"Модель: {llm_config.get('model', '')}")
    print(f"API URL: {llm_config.get('api_url', '')}")
    print(f"API ключ: {'*' * len(llm_config.get('api_key', '')) if llm_config.get('api_key') else ''}")

    # Меню действий с LLM
    questions = [
        inquirer.List('action',
                     message="Выберите действие",
                     choices=[
                         ('Изменить модель', 'model'),
                         ('Изменить API URL', 'url'),
                         ('Изменить API ключ', 'key'),
                         ('Удалить нейросеть', 'delete'),
                         ('Сделать текущей', 'current'),
                         ('Назад', 'back')
                     ])
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return

    action = answers['action']

    if action == 'model':
        questions = [inquirer.Text('value', message="Новая модель", default=llm_config.get('model', ''))]
        answers = inquirer.prompt(questions)
        if answers:
            config.update_llm(llm_name, model=answers['value'])
            print("Модель обновлена")

    elif action == 'url':
        questions = [inquirer.Text('value', message="Новый API URL", default=llm_config.get('api_url', ''))]
        answers = inquirer.prompt(questions)
        if answers:
            config.update_llm(llm_name, api_url=answers['value'])
            print("API URL обновлен")

    elif action == 'key':
        questions = [inquirer.Password('value', message="Новый API ключ")]
        answers = inquirer.prompt(questions)
        if answers:
            config.update_llm(llm_name, api_key=answers['value'])
            print("API ключ обновлен")

    elif action == 'delete':
        if llm_name == config.current_llm:
            print("Нельзя удалить текущую нейросеть")
            return

        questions = [inquirer.Confirm('confirm', message=f"Удалить {llm_name}?", default=False)]
        answers = inquirer.prompt(questions)
        if answers and answers['confirm']:
            config.remove_llm(llm_name)
            print("Нейросеть удалена")

    elif action == 'current':
        config.current_llm = llm_name
        print(f"{llm_name} установлена как текущая")

    elif action == 'back':
        return


def add_llm():
    """Добавление новой LLM."""
    questions = [
        inquirer.Text('name', message="Имя нейросети"),
        inquirer.Text('model', message="Модель"),
        inquirer.Text('api_url', message="API URL"),
        inquirer.Password('api_key', message="API ключ (опционально)")
    ]

    answers = inquirer.prompt(questions)
    if answers and answers['name'] and answers['model'] and answers['api_url']:
        try:
            config.add_llm(
                answers['name'],
                answers['model'],
                answers['api_url'],
                answers.get('api_key', '')
            )
            print("Нейросеть добавлена")
        except ValueError as e:
            print(f"Ошибка: {e}")
    else:
        print("Все поля обязательны кроме API ключа")


def edit_user_content():
    """Редактирование пользовательского контента."""
    current_content = config.user_content

    print(f"\nТекущий контент:")
    print("-" * 60)
    print(current_content)
    print("-" * 60)

    print("\nИнструкция: Введите новый контент.")
    print("Для многострочного текста используйте \\n для новой строки.")
    print("Пример: Первая строка\\nВторая строка\\nТретья строка")
    print("Оставьте пустым и нажмите Enter для отмены изменений.")
    print()

    try:
        # Используем обычный input для избежания эхоинга каждой буквы
        user_input = input("Новый контент: ").strip()

        if not user_input:
            print("Изменения отменены - введен пустой текст")
            return

        # Заменяем \n на настоящие переносы строк
        new_content = user_input.replace('\\n', '\n')

        # Сохраняем новый контент
        config.user_content = new_content
        print("Контент обновлен успешно")

    except KeyboardInterrupt:
        print("\nИзменения отменены")
    except Exception as e:
        print(f"Ошибка при вводе: {e}")
        print("Изменения отменены")


def system_settings_menu():
    """Меню системных настроек."""
    while True:
        questions = [
            inquirer.List('choice',
                         message="Системные настройки",
                         choices=[
                             ('Уровень логирования', 'logging'),
                             ('Потоковый режим', 'stream'),
                             ('JSON режим', 'json'),
                             ('Назад', 'back')
                         ])
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'logging':
            set_log_level()
        elif choice == 'stream':
            set_stream_mode()
        elif choice == 'json':
            set_json_mode()
        elif choice == 'back':
            break


def set_log_level():
    """Настройка уровня логирования."""
    questions = [
        inquirer.List('level',
                     message="Уровень логирования",
                     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                     default=config.console_log_level)
    ]

    answers = inquirer.prompt(questions)
    if answers:
        config.console_log_level = answers['level']
        print("Уровень логирования обновлен")


def set_stream_mode():
    """Настройка потокового режима."""
    questions = [
        inquirer.List('mode',
                     message="Потоковый режим",
                     choices=[('Включен', True), ('Выключен', False)],
                     default=config.stream_mode)
    ]

    answers = inquirer.prompt(questions)
    if answers:
        config.stream_mode = answers['mode']
        print("Потоковый режим обновлен")


def set_json_mode():
    """Настройка JSON режима."""
    questions = [
        inquirer.List('mode',
                     message="JSON режим",
                     choices=[('Включен', True), ('Выключен', False)],
                     default=config.json_mode)
    ]

    answers = inquirer.prompt(questions)
    if answers:
        config.json_mode = answers['mode']
        print("JSON режим обновлен")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nВыход...")
    except Exception as e:
        print(f"Ошибка: {e}")
