#!/usr/bin/env python3
"""
Configuration menu using inquirer.

Manage config.yaml via interactive menu with clean cancel behavior and carousel navigation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import inquirer
from penguin_tamer.config_manager import config
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t, translator
from penguin_tamer.settings_overview import print_settings_overview


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
                            (t('Generation parameters'), 'params'),
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
        elif choice == 'params':
            generation_parameters_menu()
        elif choice == 'system':
            system_settings_menu()
        elif choice == 'content':
            edit_user_content()
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
    """Системные настройки меню."""
    while True:
        questions = [
            inquirer.List('choice',
                         message=t('System settings'),
                         choices=[
                             (t('Stream delay'), 'sleep_time'),
                             (t('Stream refresh rate'), 'refresh_rate'),
                             (t('Back'), 'back')
                         ],
                         carousel=True)
        ]

        answers = prompt_clean(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'sleep_time':
            set_sleep_time()
        elif choice == 'refresh_rate':
            set_refresh_rate()
        elif choice == 'back':
            break


def set_sleep_time():
    """Set streaming delay (0.001-0.1 seconds)."""
    current = config.get("global", "sleep_time", 0.01)
    print(f"\n{t('Current stream delay')}: {current} {t('seconds')}")
    print(t('Controls delay between text updates in stream mode.'))
    print(t('Lower values = faster updates, higher CPU usage'))
    print(t('Enter a value between 0.001 and 0.1 seconds.'))

    while True:
        questions = [
            inquirer.Text('value', 
                         message=t('Stream delay (seconds)'), 
                         default=str(current))
        ]
        
        answers = prompt_clean(questions)
        if not answers:
            break
            
        try:
            value = float(answers['value'].replace(',', '.'))
            if 0.001 <= value <= 0.1:
                config.set("global", "sleep_time", value)
                print(t('Updated'))
                break
            else:
                print(t('Please enter a value between 0.001 and 0.1'))
        except ValueError:
            print(t('Please enter a valid number'))


def set_refresh_rate():
    """Set streaming refresh rate (1-60 updates per second)."""
    current = config.get("global", "refresh_per_second", 10)
    print(f"\n{t('Current refresh rate')}: {current} {t('updates per second')}")
    print(t('Controls how often the interface updates in stream mode.'))
    print(t('Higher values = smoother display, higher CPU usage'))
    print(t('Enter a value between 1 and 60.'))

    while True:
        questions = [
            inquirer.Text('value', 
                         message=t('Updates per second'), 
                         default=str(current))
        ]
        
        answers = prompt_clean(questions)
        if not answers:
            break
            
        try:
            value = int(answers['value'])
            if 1 <= value <= 60:
                config.set("global", "refresh_per_second", value)
                print(t('Updated'))
                break
            else:
                print(t('Please enter a value between 1 and 60'))
        except ValueError:
            print(t('Please enter a valid integer'))


def generation_parameters_menu():
    """Menu for generation parameters."""
    while True:
        questions = [
            inquirer.List('choice',
                         message=t("Generation Parameters"),
                         choices=[
                            (t('Temperature'), 'temp'),
                            (t('Max tokens'), 'max_tokens'),
                            (t('Top P'), 'top_p'),
                            (t('Frequency penalty'), 'freq_penalty'),
                            (t('Presence penalty'), 'pres_penalty'),
                            (t('Seed'), 'seed'),
                            (t('Back'), 'back')
                         ],
                         carousel=True)
        ]

        answers = prompt_clean(questions)
        if not answers:
            break

        choice = answers['choice']

        if choice == 'temp':
            set_temperature()
        elif choice == 'max_tokens':
            set_max_tokens()
        elif choice == 'top_p':
            set_top_p()
        elif choice == 'freq_penalty':
            set_frequency_penalty()
        elif choice == 'pres_penalty':
            set_presence_penalty()
        elif choice == 'seed':
            set_seed()
        elif choice == 'back':
            break


def set_temperature():
    """Set generation temperature (0.0–2.0)."""
    current = config.temperature
    print(f"\n{t('Current temperature')}: {current}")
    print(t('Temperature hint'))
    print(t('Enter a value between 0.0 and 2.0 (dot or comma).'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Temperature (0.0–2.0)'),
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Temperature change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Temperature change cancelled"))
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if not (0.0 <= value <= 2.0):
            print(t('Temperature must be between 0.0 and 2.0.'))
            continue

        config.temperature = value
        print(f"{t('Temperature updated')}: {value}")
        return


def set_max_tokens():
    """Set max tokens (null for unlimited)."""
    current = config.max_tokens
    current_str = str(current) if current is not None else "null"
    print(f"\n{t('Current max tokens')}: {current_str}")
    print(t('Max tokens hint'))
    print(t('Enter a number or null for unlimited.'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Max tokens (e.g., 2000 or null)'),
                default=current_str
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Max tokens change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Max tokens change cancelled"))
            return

        if raw.lower() in ['null', 'none', '']:
            config.max_tokens = None
            print(t('Max tokens set to unlimited'))
            return

        try:
            value = int(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if value < 1:
            print(t('Max tokens must be positive.'))
            continue

        config.max_tokens = value
        print(f"{t('Max tokens updated')}: {value}")
        return


def set_top_p():
    """Set top_p (0.0–1.0)."""
    current = config.top_p
    print(f"\n{t('Current top P')}: {current}")
    print(t('Top P hint'))
    print(t('Enter a value between 0.0 and 1.0 (dot or comma).'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Top P (0.0–1.0)'),
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Top P change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Top P change cancelled"))
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if not (0.0 <= value <= 1.0):
            print(t('Top P must be between 0.0 and 1.0.'))
            continue

        config.top_p = value
        print(f"{t('Top P updated')}: {value}")
        return


def set_frequency_penalty():
    """Set frequency penalty (-2.0 to 2.0)."""
    current = config.frequency_penalty
    print(f"\n{t('Current frequency penalty')}: {current}")
    print(t('Frequency penalty hint'))
    print(t('Enter a value between -2.0 and 2.0 (dot or comma).'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Frequency penalty (-2.0–2.0)'),
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Frequency penalty change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Frequency penalty change cancelled"))
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if not (-2.0 <= value <= 2.0):
            print(t('Frequency penalty must be between -2.0 and 2.0.'))
            continue

        config.frequency_penalty = value
        print(f"{t('Frequency penalty updated')}: {value}")
        return


def set_presence_penalty():
    """Set presence penalty (-2.0 to 2.0)."""
    current = config.presence_penalty
    print(f"\n{t('Current presence penalty')}: {current}")
    print(t('Presence penalty hint'))
    print(t('Enter a value between -2.0 and 2.0 (dot or comma).'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Presence penalty (-2.0–2.0)'),
                default=str(current)
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Presence penalty change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Presence penalty change cancelled"))
            return

        raw = raw.replace(',', '.')
        try:
            value = float(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        if not (-2.0 <= value <= 2.0):
            print(t('Presence penalty must be between -2.0 and 2.0.'))
            continue

        config.presence_penalty = value
        print(f"{t('Presence penalty updated')}: {value}")
        return


def set_seed():
    """Set seed for determinism (null for random)."""
    current = config.seed
    current_str = str(current) if current is not None else "null"
    print(f"\n{t('Current seed')}: {current_str}")
    print(t('Seed hint'))
    print(t('Enter an integer or null for random.'))

    while True:
        questions = [
            inquirer.Text(
                'value',
                message=t('Seed (e.g., 42 or null)'),
                default=current_str
            )
        ]

        answers = prompt_clean(questions)
        if not answers:
            print(t("Seed change cancelled"))
            return

        raw = str(answers.get('value', '')).strip()
        if raw == "":
            print(t("Seed change cancelled"))
            return

        if raw.lower() in ['null', 'none', '']:
            config.seed = None
            print(t('Seed set to random'))
            return

        try:
            value = int(raw)
        except ValueError:
            print(t('Invalid number format.'))
            continue

        config.seed = value
        print(f"{t('Seed updated')}: {value}")
        return


def set_temperature_old():
    """Set generation temperature (0.0–1.0). DEPRECATED - use generation_parameters_menu."""
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
