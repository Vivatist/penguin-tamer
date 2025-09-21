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
from aiebash.formatter_text import format_api_key_display


def prompt_clean(questions):
    """Обертка над inquirer.prompt: подавляет строку 'Cancelled by user' и
    возвращает None при Ctrl+C, чтобы не было лишнего вывода."""
    old_out_write = sys.stdout.write
    old_err_write = sys.stderr.write

    def _filter_out(s):
        try:
            if s and 'Cancelled by user' in str(s):
                return 0
        except Exception:
            pass
        return old_out_write(s)

    def _filter_err(s):
        try:
            if s and 'Cancelled by user' in str(s):
                return 0
        except Exception:
            pass
        return old_err_write(s)

    sys.stdout.write = _filter_out
    sys.stderr.write = _filter_err
    try:
        try:
            return inquirer.prompt(questions)
        except KeyboardInterrupt:
            return None
    finally:
        sys.stdout.write = old_out_write
        sys.stderr.write = old_err_write


def main_menu():
    """Главное меню приложения."""
    while True:
        questions = [
            inquirer.List('choice',
                         message="Выберите действие",
                         choices=[
                            ('Выбрать нейросеть', 'select'),
                            ('Управление нейросетями', 'llm'),
                            ('Температура генерации', 'temp'),
                            ('Редактировать контент', 'content'),
                            ('Системные настройки', 'system'),
                            ('Выход', 'exit')
                         ],
                         carousel=True)
        ]

        answers = prompt_clean(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'llm':
            llm_management_menu()
        elif choice == 'system':
            system_settings_menu()
        elif choice == 'content':
            edit_user_content()
        elif choice == 'temp':
            set_temperature()
        elif choice == 'select':
            select_current_llm()
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
                         choices=choices,
                         carousel=True)
        ]

        answers = prompt_clean(questions)
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
    print(f"API ключ: {format_api_key_display(llm_config.get('api_key', ''))}")

    # Меню действий с LLM
    questions = [
        inquirer.List('action',
                     message="Выберите действие",
                     choices=[
                         ('Изменить модель', 'model'),
                         ('Изменить API URL', 'url'),
                         ('Изменить API ключ', 'key'),
                         ('Удалить нейросеть', 'delete'),
                         ('Назад', 'back')
                     ],
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if not answers:
        return

    action = answers['action']

    if action == 'model':
        questions = [inquirer.Text('value', message="Новая модель", default=llm_config.get('model', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, model=answers['value'])
            print("Модель обновлена")

    elif action == 'url':
        questions = [inquirer.Text('value', message="Новый API URL", default=llm_config.get('api_url', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, api_url=answers['value'])
            print("API URL обновлен")

    elif action == 'key':
        questions = [inquirer.Text('value', message="Новый API ключ", default=llm_config.get('api_key', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, api_key=answers['value'])
            print("API ключ обновлен")

    elif action == 'delete':
        if llm_name == config.current_llm:
            print("Нельзя удалить текущую нейросеть")
            return

        questions = [inquirer.Confirm('confirm', message=f"Удалить {llm_name}?", default=False)]
        answers = prompt_clean(questions)
        if answers and answers['confirm']:
            config.remove_llm(llm_name)
            print("Нейросеть удалена")

    elif action == 'back':
        return


def add_llm():
    """Добавление новой LLM."""
    questions = [
        inquirer.Text('name', message="Имя нейросети"),
        inquirer.Text('model', message="Модель"),
        inquirer.Text('api_url', message="API URL"),
        inquirer.Text('api_key', message="API ключ (опционально)")
    ]

    answers = prompt_clean(questions)
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


def select_current_llm():
    """Выбор текущей нейросети из списка доступных."""
    while True:
        available_llms = config.get_available_llms()
        if not available_llms:
            print("Нет доступных нейросетей. Сначала добавьте хотя бы одну.")
            return

        current_llm = config.current_llm
        choices = []
        for llm in available_llms:
            marker = " [текущая]" if llm == current_llm else ""
            choices.append((f"{llm}{marker}", llm))

        choices.append(('Назад', 'back'))

        questions = [
            inquirer.List(
                'llm',
                message="Выберите текущую нейросеть",
                choices=choices,
                default=current_llm if current_llm in available_llms else None,
                carousel=True,
            )
        ]

        answers = prompt_clean(questions)
        if answers and answers.get('llm'):
            selected = answers['llm']
            if selected == 'back':
                return
            if selected != current_llm:
                config.current_llm = selected
                print(f"Текущая нейросеть установлена: {selected}")
                continue  # Остаемся в меню с новым маркером
            else:
                print("Эта нейросеть уже текущая")
                continue  # Остаемся в меню
        else:
            print("Выбор нейросети отменен")
            return  # Остаемся в меню


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
                         ],
                         carousel=True)
        ]

        answers = prompt_clean(questions)
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
                     default=config.console_log_level,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.console_log_level = answers['level']
        print("Уровень логирования обновлен")


def set_stream_mode():
    """Настройка потокового режима."""
    questions = [
        inquirer.List('mode',
                     message="Потоковый режим",
                     choices=[('Включен', True), ('Выключен', False)],
                     default=config.stream_mode,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.stream_mode = answers['mode']
        print("Потоковый режим обновлен")


def set_json_mode():
    """Настройка JSON режима."""
    questions = [
        inquirer.List('mode',
                     message="JSON режим",
                     choices=[('Включен', True), ('Выключен', False)],
                     default=config.json_mode,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.json_mode = answers['mode']
        print("JSON режим обновлен")


def set_temperature():
    """Настройка температуры генерации (0.0–1.0)."""
    current = config.temperature
    print(f"\nТекущая температура: {current}")
    print("Подсказка: Температура регулирует степень случайности и креативности генерируемых ответов.")
    print("Допустимое значение от 0.0 до 1.0. Можно вводить через запятую или точку.")

    while True:
        questions = [
            inquirer.Text(
                'value',
                message="Введите новое значение температуры (0.0–1.0)",
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print("Изменение температуры отменено")
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print("Изменение температуры отменено")
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print("Ошибка: введите число в формате 0.0–1.0 (можно использовать запятую)")
            continue

        if not (0.0 <= value <= 1.0):
            print("Ошибка: значение должно быть в диапазоне от 0.0 до 1.0")
            continue

        config.temperature = value
        print(f"Температура обновлена: {value}")
        return


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nВыход...")
    except Exception as e:
        print(f"Ошибка: {e}")
