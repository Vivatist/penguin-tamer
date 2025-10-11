#!/usr/bin/env python3
"""
Система записи и воспроизведения демо-сессий LLM.

Позволяет записывать реальные ответы LLM и затем воспроизводить их
для демонстрации, создавая полностью реалистичную имитацию работы.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from platformdirs import user_config_dir


def _simulate_human_typing(text: str, console=None, style: str = None) -> None:
    """
    Эмулирует печать текста человеком с реалистичными задержками.

    Args:
        text: Текст для печати
        console: Rich console для вывода (опционально)
        style: Стиль Rich для текста (например, 'bold', 'dim', '#007c6e')
    """
    import random

    for char in text:
        if console:
            if style:
                console.print(f"[{style}]{char}[/{style}]", end='', highlight=False)
            else:
                console.print(char, end='', highlight=False)
        else:
            print(char, end='', flush=True)

        # Неравномерные задержки, имитирующие быструю печать человека
        if char == ' ':
            # Пробелы печатаются быстрее
            delay = random.uniform(0.05, 0.15)
        elif char in '.,!?;:':
            # После пунктуации небольшая пауза
            delay = random.uniform(0.15, 0.3)
        elif char.isupper():
            # Заглавные буквы чуть медленнее
            delay = random.uniform(0.08, 0.18)
        else:
            # Обычные символы
            delay = random.uniform(0.05, 0.12)

        # Редкие "заминки" (как будто человек задумался)
        if random.random() < 0.05:  # 5% шанс
            delay += random.uniform(0.2, 0.5)

        time.sleep(delay)


def _add_sequence_number_to_filename(filepath: Path) -> Path:
    """
    Добавляет порядковый номер к имени файла перед расширением.
    Находит следующий свободный номер, проверяя существующие файлы.

    Args:
        filepath: Путь к файлу

    Returns:
        Path: Путь с добавленным порядковым номером

    Example:
        demo.json -> demo_1.json (если demo_1.json не существует)
        demo.json -> demo_2.json (если demo_1.json уже существует)
    """
    stem = filepath.stem  # Имя без расширения
    suffix = filepath.suffix  # Расширение с точкой
    parent = filepath.parent

    # Ищем следующий доступный номер
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
        # Защита от бесконечного цикла (маловероятно, но на всякий случай)
        if counter > 10000:
            # Если дошли до 10000, используем временную метку
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{stem}_{timestamp}{suffix}"
            return parent / new_name


def _resolve_demo_path(demo_file: str, app_name: str = "penguin-tamer") -> Path:
    """
    Разрешает путь к демо-файлу относительно директории конфигурации пользователя.

    Args:
        demo_file: Имя файла или относительный путь
        app_name: Имя приложения для определения директории конфига

    Returns:
        Path: Полный путь к демо-файлу в директории конфигурации
    """
    # Если путь абсолютный - используем как есть
    demo_path = Path(demo_file)
    if demo_path.is_absolute():
        return demo_path

    # Иначе - относительно директории конфигурации пользователя
    config_dir = Path(user_config_dir(app_name))
    return config_dir / demo_file


@dataclass
class DemoResponse:
    """Записанный ответ LLM для демонстрации."""

    timestamp: str  # ISO формат времени записи
    user_query: str  # Запрос пользователя
    response: str  # Полный ответ LLM
    chunks: List[str]  # Список чанков для реалистичного воспроизведения
    metadata: Dict[str, Any]  # Дополнительная информация (модель, температура и т.д.)
    user_actions: Optional[List[Dict[str, str]]] = None  # История действий пользователя перед этим ответом

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DemoResponse':
        """Создание из словаря."""
        return cls(**data)


class DemoRecorder:
    """
    Записывает ответы LLM в файл для последующего воспроизведения.

    Формат файла: JSON с массивом записанных ответов.
    """

    def __init__(self, demo_file: str):
        """
        Инициализация рекордера.

        Args:
            demo_file: Имя файла или путь к файлу для записи.
                      Если путь относительный - будет создан в директории конфига пользователя.
                      К имени файла автоматически добавляется порядковый номер.
        """
        # Добавляем порядковый номер к имени файла
        base_path = _resolve_demo_path(demo_file)
        self.demo_file = _add_sequence_number_to_filename(base_path)
        self.responses: List[DemoResponse] = []

        # Новая запись всегда начинается с пустого списка
        # (не загружаем существующие записи, так как у каждой записи уникальное имя)

    def _save_responses(self) -> None:
        """Сохраняет все записи в файл."""
        # Создаём директорию если не существует
        self.demo_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.demo_file, 'w', encoding='utf-8') as f:
            data = [resp.to_dict() for resp in self.responses]
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_response(
        self,
        user_query: str,
        response: str,
        chunks: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        user_actions: Optional[List[Dict[str, str]]] = None
    ) -> None:
        """
        Записывает ответ LLM.

        Args:
            user_query: Запрос пользователя к LLM
            response: Полный ответ LLM
            chunks: Список чанков (для реалистичного воспроизведения)
            metadata: Дополнительная информация (модель, параметры и т.д.)
            user_actions: Список действий пользователя перед этим ответом
                         (команды через точку, номера блоков и т.д.)
        """
        demo_response = DemoResponse(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            response=response,
            chunks=chunks,
            metadata=metadata or {},
            user_actions=user_actions or []
        )

        self.responses.append(demo_response)
        self._save_responses()

    def record_user_action_only(
        self,
        action_type: str,
        action_value: str,
        context: str = ""
    ) -> None:
        """
        Записывает действие пользователя без ответа LLM.
        Используется для команд через точку и выбора блоков кода.

        Args:
            action_type: Тип действия ('command', 'code_block')
            action_value: Значение действия
            context: Контекстная информация (результат выполнения)
        """
        demo_response = DemoResponse(
            timestamp=datetime.now().isoformat(),
            user_query="",  # Нет запроса к LLM
            response="",  # Нет ответа LLM
            chunks=[],
            metadata={'action_only': True, 'context': context},
            user_actions=[{
                'type': action_type,
                'value': action_value,
                'timestamp': datetime.now().isoformat()
            }]
        )

        self.responses.append(demo_response)
        self._save_responses()

    def get_response_count(self) -> int:
        """Возвращает количество записанных ответов."""
        return len(self.responses)

    def clear_responses(self) -> None:
        """Очищает все записанные ответы."""
        self.responses = []
        self._save_responses()


class DemoPlayer:
    """
    Воспроизводит записанные ответы LLM с имитацией потоковой передачи.

    Эмулирует реальную работу LLM: спиннер, чанки, задержки.
    """

    def __init__(self, demo_file: str, spinner_delay: float = 1.0):
        """
        Инициализация плеера.

        Args:
            demo_file: Имя файла или путь к файлу с записями.
                      Если путь относительный - будет искаться в директории конфига пользователя.
            spinner_delay: Задержка перед началом вывода (секунды)
        """
        self.demo_file = _resolve_demo_path(demo_file)
        self.spinner_delay = spinner_delay
        self.responses: List[DemoResponse] = []
        self.current_index = 0
        self.current_action_index = 0  # Индекс текущего действия в user_actions

        # Загружаем записи
        self._load_responses()

    def _load_responses(self) -> None:
        """Загружает записи из файла."""
        if not self.demo_file.exists():
            raise FileNotFoundError(f"Демо-файл не найден: {self.demo_file}")

        try:
            with open(self.demo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.responses = [DemoResponse.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Некорректный формат демо-файла: {e}")

    def has_more_responses(self) -> bool:
        """Проверяет, есть ли ещё непроигранные ответы."""
        return self.current_index < len(self.responses)

    def get_spinner_delay(self) -> float:
        """Возвращает задержку спиннера."""
        return self.spinner_delay

    def play_next_response(self, user_query: str = None) -> Optional[DemoResponse]:
        """
        Получает следующий записанный ответ.

        В robot mode НЕ увеличивает current_index, так как это делает get_next_user_action().
        Возвращает ответ для текущего current_index, если он еще не был воспроизведен.

        Args:
            user_query: Запрос пользователя (игнорируется, но принимается для совместимости)

        Returns:
            DemoResponse или None если ответы закончились или ответ пустой
        """
        if not self.has_more_responses():
            return None

        response = self.responses[self.current_index]

        # Возвращаем None для записей с action_only=true (нет ответа для воспроизведения)
        if response.metadata.get('action_only'):
            return None

        # Проверяем, есть ли реальный ответ для воспроизведения
        if not response.response or not response.chunks:
            return None

        # Возвращаем ответ БЕЗ увеличения current_index
        # Индекс будет увеличен в get_next_user_action() при переходе к следующей записи
        return response

    def create_chunk_generator(
        self,
        response: DemoResponse,
        chunk_delay: float = 0.01
    ) -> Iterator[str]:
        """
        Создаёт генератор для потоковой выдачи чанков.

        Args:
            response: Записанный ответ
            chunk_delay: Задержка между чанками (секунды)

        Yields:
            Чанки текста
        """
        for chunk in response.chunks:
            yield chunk
            if chunk_delay > 0:
                time.sleep(chunk_delay)

    def create_mock_stream(self, response: DemoResponse) -> Iterator[object]:
        """
        Создаёт мок-объект потока в формате OpenAI API.

        Имитирует структуру ответа от OpenAI для совместимости
        с существующим кодом обработки потока.

        Args:
            response: Записанный ответ

        Yields:
            Объекты с структурой как у OpenAI chunk
        """
        # Создаём мок-объекты для имитации OpenAI API response
        class MockDelta:
            def __init__(self, content: str):
                self.content = content

        class MockChoice:
            def __init__(self, delta: MockDelta):
                self.delta = delta

        class MockChunk:
            def __init__(self, content: str):
                self.choices = [MockChoice(MockDelta(content))]

        for chunk in response.chunks:
            yield MockChunk(chunk)
            time.sleep(0.01)  # Небольшая задержка для реалистичности

    def reset(self) -> None:
        """Сбрасывает счётчик на начало."""
        self.current_index = 0
        self.current_action_index = 0

    def get_total_responses(self) -> int:
        """Возвращает общее количество записей."""
        return len(self.responses)

    def get_current_position(self) -> int:
        """Возвращает текущую позицию воспроизведения."""
        return self.current_index

    def get_next_user_action(self) -> Optional[Dict[str, str]]:
        """
        Получает следующее действие пользователя из текущей или следующих записей.
        Используется в режиме robot для автоматического ввода.
        Отслеживает позицию в списке user_actions для возврата всех действий.

        Returns:
            Словарь с типом и значением действия, или None если действий больше нет
        """
        # Ищем следующее действие, начиная с текущей позиции
        response_idx = self.current_index
        action_idx = self.current_action_index

        while response_idx < len(self.responses):
            response = self.responses[response_idx]

            if response.user_actions:
                # Ищем действие начиная с action_idx
                while action_idx < len(response.user_actions):
                    action = response.user_actions[action_idx]
                    if action['type'] in ('command', 'code_block', 'query'):
                        # Нашли действие - обновляем позицию для следующего вызова
                        action_idx += 1

                        # Обновляем позицию в объекте
                        self.current_index = response_idx
                        self.current_action_index = action_idx

                        return action

                    action_idx += 1

            # Переходим к следующей записи
            response_idx += 1
            action_idx = 0  # Начинаем с первого действия в новой записи

        return None


class DemoManager:
    """
    Управляющий класс для работы с демо-режимом.

    Автоматически выбирает режим (запись/воспроизведение/выкл)
    на основе конфигурации.
    """

    def __init__(self, demo_mode: str, demo_file: str, spinner_delay: float = 1.0):
        """
        Инициализация менеджера.

        Args:
            demo_mode: Режим работы ('record', 'play', 'robot', 'off')
            demo_file: Путь к файлу демо-записей
            spinner_delay: Задержка спиннера в режиме play/robot (секунды)
        """
        self.demo_mode = demo_mode.lower()
        self.demo_file = demo_file
        self.spinner_delay = spinner_delay

        self.recorder: Optional[DemoRecorder] = None
        self.player: Optional[DemoPlayer] = None
        self.pending_user_actions: List[Dict[str, str]] = []  # Буфер для действий пользователя

        # Инициализируем нужный компонент
        if self.demo_mode == 'record':
            self.recorder = DemoRecorder(demo_file)
        elif self.demo_mode in ('play', 'robot'):
            self.player = DemoPlayer(demo_file, spinner_delay)

    def add_user_action(self, action_type: str, action_value: str) -> None:
        """
        Добавляет действие пользователя в буфер.

        Args:
            action_type: Тип действия ('command', 'code_block', 'query')
            action_value: Значение действия
        """
        self.pending_user_actions.append({
            'type': action_type,
            'value': action_value,
            'timestamp': datetime.now().isoformat()
        })

    def get_and_clear_user_actions(self) -> List[Dict[str, str]]:
        """
        Получает накопленные действия пользователя и очищает буфер.

        Returns:
            Список действий пользователя
        """
        actions = self.pending_user_actions.copy()
        self.pending_user_actions.clear()
        return actions

    def is_recording(self) -> bool:
        """Проверка, идёт ли запись."""
        return self.demo_mode == 'record'

    def is_playing(self) -> bool:
        """Проверка, идёт ли воспроизведение (play или robot)."""
        return self.demo_mode in ('play', 'robot')

    def is_robot_mode(self) -> bool:
        """Проверка, включен ли режим робота (автоматический ввод)."""
        return self.demo_mode == 'robot'

    def is_enabled(self) -> bool:
        """Проверка, включен ли демо-режим."""
        return self.demo_mode in ('record', 'play', 'robot')

    def get_recorder(self) -> Optional[DemoRecorder]:
        """Получить рекордер (если в режиме записи)."""
        return self.recorder

    def get_player(self) -> Optional[DemoPlayer]:
        """Получить плеер (если в режиме воспроизведения)."""
        return self.player
