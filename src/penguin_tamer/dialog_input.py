#!/usr/bin/env python3
"""Модуль для оформления ввода в диалоговом режиме."""
from pathlib import Path
from prompt_toolkit.history import FileHistory
from penguin_tamer.utils.lazy_import import lazy_import


# Ленивые импорты prompt_toolkit через декоратор
@lazy_import
def get_prompt_toolkit():
    """Ленивый импорт prompt_toolkit компонентов"""
    from prompt_toolkit import HTML, prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.layout.processors import Processor, Transformation
    return {
        'HTML': HTML,
        'prompt': prompt,
        'Style': Style,
        'Processor': Processor,
        'Transformation': Transformation
    }


class FilteredFileHistory(FileHistory):
    """История команд с фильтрацией чисел (номеров блоков кода)"""

    def append_string(self, string: str) -> None:
        """Добавляет строку в историю, игнорируя чистые числа"""
        # Игнорируем строки, которые являются только числами
        if string.strip().isdigit():
            return
        # Также игнорируем команды выхода
        if string.strip().lower() in ['exit', 'quit', 'q']:
            return
        # Для всех остальных команд вызываем родительский метод
        super().append_string(string)


class DialogInputFormatter:
    """Класс для оформления ввода в диалоговом режиме с подсветкой синтаксиса"""

    def __init__(self, history_file_path: Path):
        """
        Инициализация форматтера ввода

        Args:
            history_file_path: Путь к файлу истории команд
        """
        # Получаем компоненты prompt_toolkit
        pt = get_prompt_toolkit()
        Style = pt['Style']
        Processor = pt['Processor']
        Transformation = pt['Transformation']

        # Используем FilteredFileHistory вместо FileHistory
        self.history = FilteredFileHistory(str(history_file_path))
        self.style = Style.from_dict({
            "prompt": "bold fg:#e07333",    # Оранжевый основной цвет
            "dot": "fg:gray",               # Серая точка
            "command": "fg:#007c6e",        # Бирюзовый для команд после точки
            "text": "",                     # Стандартный цвет консоли
        })

        # Создаем процессор для real-time подсветки
        class DotCommandProcessor(Processor):
            """Процессор для real-time подсветки команд с точкой"""

            def apply_transformation(self, transformation_input):
                """Применяет трансформацию к вводу"""
                text = transformation_input.document.text

                if text.startswith('.') and len(text) > 0:
                    # Создаем форматированный текст для команд с точкой
                    formatted_fragments = [
                        ('class:dot', '.'),
                        ('class:command', text[1:])
                    ]
                else:
                    # Обычный текст
                    formatted_fragments = [('class:text', text)]

                return Transformation(
                    formatted_fragments,
                    source_to_display=lambda i: i,
                    display_to_source=lambda i: i
                )

        self.dot_processor = DotCommandProcessor()

    def get_input(self, console, has_code_blocks: bool = False, t=None) -> str:
        """
        Получить ввод пользователя с оформлением и подсветкой

        Args:
            console: Консоль для вывода
            has_code_blocks: Есть ли блоки кода в последнем ответе
            t: Функция перевода (опциональна)

        Returns:
            Введенная пользователем строка
        """
        # Получаем компоненты prompt_toolkit
        pt = get_prompt_toolkit()
        HTML = pt['HTML']
        prompt = pt['prompt']

        # Если функция перевода не передана, используем заглушку
        if t is None:
            def t(x):
                return x

        # Выбираем placeholder в зависимости от наличия блоков кода
        if has_code_blocks:
            placeholder = HTML(
                t("<i><gray>Number of the code block to execute or "
                  "the next question... Ctrl+C - exit</gray></i>")
            )
        else:
            placeholder = HTML(t("<i><gray>Your question... Ctrl+C - exit</gray></i>"))

        # Создаем кастомную функцию для динамической подсветки
        def get_prompt_tokens():
            """Возвращает токены промпта с подсветкой в зависимости от введенного текста"""
            return [("class:prompt", ">>> ")]

        # Пытаемся использовать prompt_toolkit, если не получается - fallback на input()
        try:
            # Настраиваем параметры prompt с процессором для подсветки
            prompt_kwargs = {
                'placeholder': placeholder,
                'history': self.history,
                'style': self.style,
                'multiline': False,
                'wrap_lines': True,
                'enable_history_search': True,
                'input_processors': [self.dot_processor]  # Добавляем процессор для real-time подсветки
            }

            user_input = prompt(get_prompt_tokens, **prompt_kwargs)

        except Exception:
            # Fallback на стандартный input() если prompt_toolkit не работает
            console.print("[dim]>>> [/dim]", end="")
            user_input = input().strip()

        return user_input
