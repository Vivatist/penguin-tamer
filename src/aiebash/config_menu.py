#!/usr/bin/env python3
"""
Configuration menu using inquirer.

Manage config.yaml via interactive menu with clean cancel behavior and carousel navigation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import inquirer
from aiebash.config_manager import config
from aiebash.formatter_text import format_api_key_display
from aiebash.i18n import t, translator
from aiebash.settings_overview import print_settings_overview


def prompt_clean(questions):
    """Wrapper over inquirer.prompt: suppresses 'Cancelled by user' noise and
    returns None on Ctrl+C to avoid extra output."""
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
    """Main settings menu."""
    # Ensure translator uses current config language
    try:
        translator.set_language(getattr(config, 'language', 'en'))
    except Exception:
        pass
    # Показать обзор текущих настроек при входе в меню
    try:
        print_settings_overview()
    except Exception:
        # Не блокируем меню, если обзор по какой-то причине упал
        pass

    while True:
        questions = [
            inquirer.List('choice',
                         message=t("Settings"),
                         choices=[
                            (t('Select current LLM'), 'select'),
                            (t('Model management'), 'llm'),
                            (t('Generation temperature'), 'temp'),
                            (t('User content'), 'content'),
                            (t('System'), 'system'),
                            (t('Show current settings'), 'overview'),
                            (t('Language'), 'language'),
                            (t('Exit'), 'exit')
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
        elif choice == 'overview':
            print_settings_overview()
        elif choice == 'language':
            set_language()
        elif choice == 'exit':
            break


def llm_management_menu():
    """LLM management menu."""
    while True:
        # Получаем список LLM с отметкой текущей
        available_llms = config.get_available_llms()
        current_llm = config.current_llm

        choices = []
        for llm in available_llms:
            marker = f" [{t('current')}]" if llm == current_llm else ""
            choices.append((f"{llm}{marker}", llm))

        choices.extend([
            (t('Add LLM'), 'add'),
            (t('Back'), 'back')
        ])

        questions = [
            inquirer.List('choice',
                         message=t('LLM management'),
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
    """Edit specific LLM settings."""
    llm_config = config.get_llm_config(llm_name)

    print(f"\nSettings for: {llm_name}")
    print(f"Model: {llm_config.get('model', '')}")
    print(f"API URL: {llm_config.get('api_url', '')}")
    print(f"API key: {format_api_key_display(llm_config.get('api_key', ''))}")

    # Меню действий с LLM
    questions = [
        inquirer.List('action',
                     message=t('Settings'),
                     choices=[
                         (t('Model'), 'model'),
                         (t('Base URL'), 'url'),
                         (t('API key'), 'key'),
                         (t('Delete LLM'), 'delete'),
                         (t('Back'), 'back')
                     ],
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if not answers:
        return

    action = answers['action']

    if action == 'model':
        questions = [inquirer.Text('value', message=t('Model'), default=llm_config.get('model', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, model=answers['value'])
            print(t('Updated'))

    elif action == 'url':
        questions = [inquirer.Text('value', message=t('Base URL'), default=llm_config.get('api_url', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, api_url=answers['value'])
            print(t('Updated'))

    elif action == 'key':
        questions = [inquirer.Text('value', message=t('API key'), default=llm_config.get('api_key', ''))]
        answers = prompt_clean(questions)
        if answers:
            config.update_llm(llm_name, api_key=answers['value'])
            print(t('Updated'))

    elif action == 'delete':
        if llm_name == config.current_llm:
            print("Cannot delete current LLM")
            return

        questions = [inquirer.Confirm('confirm', message=t("Delete '{name}'?", name=llm_name), default=False)]
        answers = prompt_clean(questions)
        if answers and answers['confirm']:
            config.remove_llm(llm_name)
            print(t('Deleted'))

    elif action == 'back':
        return


def add_llm():
    """Add new LLM."""
    questions = [
        inquirer.Text('name', message=t('Name')),
        inquirer.Text('model', message=t('Model')),
        inquirer.Text('api_url', message='API URL'),
        inquirer.Text('api_key', message=t('API key'))
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
            print(t('Added'))
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("All fields are required except API key")


def select_current_llm():
    """Select current LLM from available list."""
    while True:
        available_llms = config.get_available_llms()
        if not available_llms:
            print("No available LLMs. Please add one first.")
            return

        current_llm = config.current_llm
        choices = []
        for llm in available_llms:
            marker = f" [{t('current')}]" if llm == current_llm else ""
            choices.append((f"{llm}{marker}", llm))

        choices.append((t('Back'), 'back'))

        questions = [
            inquirer.List(
                'llm',
                message=t('Select current LLM'),
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
                print(f"Current LLM set: {selected}")
                continue  # Остаемся в меню с новым маркером
            else:
                print("This LLM is already current")
                continue  # Остаемся в меню
        else:
            print("LLM selection cancelled")
            return  # Остаемся в меню


def edit_user_content():
    """Edit user content."""
    current_content = config.user_content

    print(f"\nCurrent content:")
    print("-" * 60)
    print(current_content)
    print("-" * 60)

    print("\nInstruction: Enter new content.")
    print("For multiline text use \\n to insert new lines.")
    print("Example: First line\\nSecond line\\nThird line")
    print("Leave empty and press Enter to cancel.")
    print()

    try:
        # Use plain input to avoid echoing each char
        user_input = input("New content: ").strip()

        if not user_input:
            print("Changes cancelled - empty input")
            return

    # Replace \n with real new lines
        new_content = user_input.replace('\\n', '\n')

        # Сохраняем новый контент
        config.user_content = new_content
        print("Content updated")

    except KeyboardInterrupt:
        print("\nChanges cancelled")
    except Exception as e:
        print(f"Input error: {e}")
        print("Changes cancelled")


def system_settings_menu():
    """System settings menu."""
    while True:
        questions = [
            inquirer.List('choice',
                         message=t('System settings'),
                         choices=[
                             (t('Console log level'), 'logging'),
                             (t('File logging'), 'file_logging'),
                             (t('Stream mode'), 'stream'),
                             (t('JSON mode'), 'json'),
                             (t('Back'), 'back')
                         ],
                         carousel=True)
        ]

        answers = prompt_clean(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'logging':
            set_log_level()
        elif choice == 'file_logging':
            set_file_logging()
        elif choice == 'stream':
            set_stream_mode()
        elif choice == 'json':
            set_json_mode()
        elif choice == 'back':
            break


def set_log_level():
    """Console log level setting."""
    questions = [
        inquirer.List('level',
                     message=t('Console log level'),
                     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                     default=config.console_log_level,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.console_log_level = answers['level']
        print(t('Updated'))


def set_file_logging():
    """File logging setting."""
    current_state = getattr(config, 'file_enabled', False)
    questions = [
        inquirer.List('enabled',
                     message=t('File logging'),
                     choices=[('On', True), ('Off', False)],
                     default=current_state,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.file_enabled = answers['enabled']
        print(t('Updated'))


def set_stream_mode():
    """Stream mode setting."""
    questions = [
        inquirer.List('mode',
                     message=t('Stream mode'),
                     choices=[('On', True), ('Off', False)],
                     default=config.stream_mode,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.stream_mode = answers['mode']
        print(t('Updated'))


def set_json_mode():
    """JSON mode setting."""
    questions = [
        inquirer.List('mode',
                     message=t('JSON mode'),
                     choices=[('On', True), ('Off', False)],
                     default=config.json_mode,
                     carousel=True)
    ]

    answers = prompt_clean(questions)
    if answers:
        config.json_mode = answers['mode']
        print(t('Updated'))


def set_temperature():
    """Set generation temperature (0.0–1.0)."""
    current = config.temperature
    print(f"\nCurrent temperature: {current}")
    print("Hint: Temperature controls randomness/creativity of responses.")
    print(t('Enter a value between 0.0 and 1.0 (dot or comma).'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message='Temperature (0.0–1.0)',
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print("Temperature change cancelled")
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print("Temperature change cancelled")
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if not (0.0 <= value <= 1.0):
            print(t('Temperature must be between 0.0 and 1.0.'))
            continue

        config.temperature = value
        print(f"Temperature updated: {value}")
        return


def _get_available_languages() -> list[tuple[str, str]]:
    """Return list of (label, code) languages available. Always include English."""
    langs = [('English (en)', 'en')]
    try:
        locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
        if os.path.isdir(locales_dir) and os.path.isfile(os.path.join(locales_dir, 'ru.json')):
            langs.append(('Русский (ru)', 'ru'))
    except Exception:
        pass
    return langs


def set_language():
    """Language selection setting."""
    current = getattr(config, 'language', 'en')
    choices = _get_available_languages()
    questions = [
        inquirer.List('lang', message=t('Language'), choices=choices, default=current, carousel=True)
    ]
    answers = prompt_clean(questions)
    if not answers:
        return
    lang = answers['lang']
    # Persist and apply
    try:
        # If ConfigManager exposes property
        setattr(config, 'language', lang)
    except Exception:
        # Best-effort fallback: try to set top-level
        try:
            config.update_section('language', lang)  # not ideal, but prevents crash
        except Exception:
            pass
    translator.set_language(lang)
    print(t('Updated'))


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExit...")
    except Exception as e:
        print(f"Error: {e}")
