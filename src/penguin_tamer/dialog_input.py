#!/usr/bin/env python3
"""Модуль для оформления ввода в диалоговом режиме."""
from pathlib import Path


def _ensure_prompt_toolkit():
    """Ленивый импорт prompt_toolkit"""
    global _prompt_toolkit_imported
    if '_prompt_toolkit_imported' not in globals() or not _prompt_toolkit_imported:
        global HTML, prompt, FileHistory, Style, Processor, Transformation
        from prompt_toolkit import HTML, prompt
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style
        from prompt_toolkit.layout.processors import Processor, Transformation
        globals()['_prompt_toolkit_imported'] = True


class DialogInputFormatter:
    """Класс для оформления ввода в диалоговом режиме с подсветкой синтаксиса"""
    
    def __init__(self, history_file_path: Path):
        """
        Инициализация форматтера ввода
        
        Args:
            history_file_path: Путь к файлу истории команд
        """
        _ensure_prompt_toolkit()
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style
        from prompt_toolkit.layout.processors import Processor, Transformation
        
        self.history = FileHistory(str(history_file_path))
        self.style = Style.from_dict({
            "prompt": "bold fg:green",
            "dot": "fg:gray",        # Серая точка
            "command": "fg:cyan",    # Светло-синий текст команды
            "text": "",              # Стандартный цвет консоли
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
        from prompt_toolkit import HTML, prompt
        
        # Если функция перевода не передана, используем заглушку
        if t is None:
            t = lambda x: x
        
        # Выбираем placeholder в зависимости от наличия блоков кода
        if has_code_blocks:
            placeholder = HTML(t("<i><gray>Number of the code block to execute or the next question... Ctrl+C - exit</gray></i>"))
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
                
        except Exception as e:
            # Fallback на стандартный input() если prompt_toolkit не работает
            console.print("[dim]>>> [/dim]", end="")
            user_input = input().strip()
        
        return user_input
