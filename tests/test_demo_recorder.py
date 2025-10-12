#!/usr/bin/env python3
"""
Тесты для системы записи и воспроизведения демо-сессий.
"""

import pytest
import tempfile
import json
from pathlib import Path

from penguin_tamer.demo_recorder import (
    DemoResponse,
    DemoRecorder,
    DemoPlayer,
    DemoManager,
    _resolve_demo_path,
    _add_sequence_number_to_filename
)


class TestDemoResponse:
    """Тесты для DemoResponse."""

    def test_add_sequence_number_to_filename(self):
        """Проверка добавления порядкового номера к имени файла."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "session.json"

            # Первый файл получит номер 1
            result = _add_sequence_number_to_filename(filepath)
            assert result.parent == filepath.parent
            assert result.suffix == filepath.suffix
            assert result.stem == "session_1"

            # Создаём файл, чтобы проверить инкремент
            result.touch()

            # Второй файл получит номер 2
            result2 = _add_sequence_number_to_filename(filepath)
            assert result2.stem == "session_2"

            # Создаём и третий
            result2.touch()
            result3 = _add_sequence_number_to_filename(filepath)
            assert result3.stem == "session_3"

    def test_resolve_demo_path_relative(self):
        """Относительный путь должен разрешаться в директорию конфига."""
        from platformdirs import user_config_dir

        result = _resolve_demo_path("demo_sessions/test.json")
        expected = Path(user_config_dir("penguin-tamer")) / "demo_sessions" / "test.json"

        assert result == expected

    def test_resolve_demo_path_absolute(self):
        """Абсолютный путь должен оставаться без изменений."""
        import platform

        # Используем платформо-зависимый абсолютный путь
        if platform.system() == 'Windows':
            abs_path = Path("C:/temp/demo.json")
        else:
            abs_path = Path("/tmp/demo.json")

        result = _resolve_demo_path(str(abs_path))

        assert result == abs_path

    def test_create_demo_response(self):
        """Создание DemoResponse."""
        response = DemoResponse(
            timestamp="2025-01-01T12:00:00",
            user_query="Hello",
            response="Hi there!",
            chunks=["Hi", " there", "!"],
            metadata={"model": "gpt-4"},
            user_actions=[
                {"type": "query", "value": "Hello", "timestamp": "2025-01-01T12:00:00"}
            ]
        )

        assert response.user_query == "Hello"
        assert response.response == "Hi there!"
        assert len(response.chunks) == 3
        assert len(response.user_actions) == 1

    def test_to_dict(self):
        """Конвертация в словарь."""
        response = DemoResponse(
            timestamp="2025-01-01T12:00:00",
            user_query="Test",
            response="Response",
            chunks=["Res", "ponse"],
            metadata={},
            user_actions=[]
        )

        data = response.to_dict()
        assert data["user_query"] == "Test"
        assert data["response"] == "Response"
        assert data["chunks"] == ["Res", "ponse"]
        assert data["user_actions"] == []

    def test_from_dict(self):
        """Создание из словаря."""
        data = {
            "timestamp": "2025-01-01T12:00:00",
            "user_query": "Test",
            "response": "Response",
            "chunks": ["Res", "ponse"],
            "metadata": {},
            "user_actions": []
        }

        response = DemoResponse.from_dict(data)
        assert response.user_query == "Test"
        assert response.response == "Response"
        assert response.user_actions == []


class TestDemoRecorder:
    """Тесты для DemoRecorder."""

    @pytest.fixture
    def temp_dir(self):
        """Временная директория для тестов."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_record_response(self, temp_dir):
        """Запись ответа."""
        demo_file = temp_dir / "test.json"
        recorder = DemoRecorder(str(demo_file))

        recorder.record_response(
            user_query="Hello",
            response="Hi!",
            chunks=["Hi", "!"],
            metadata={"test": True}
        )

        assert recorder.get_response_count() == 1
        # Файл существует с порядковым номером
        assert recorder.demo_file.exists()
        assert recorder.demo_file.suffix == ".json"
        assert recorder.demo_file.stem == "test_1"  # Первый файл получает номер 1

    def test_multiple_recordings(self, temp_dir):
        """Множественная запись."""
        demo_file = temp_dir / "test.json"
        recorder = DemoRecorder(str(demo_file))

        recorder.record_response("Q1", "A1", ["A", "1"])
        recorder.record_response("Q2", "A2", ["A", "2"])
        recorder.record_response("Q3", "A3", ["A", "3"])

        assert recorder.get_response_count() == 3

    def test_sequence_number_added_to_filename(self, temp_dir):
        """Проверка, что порядковый номер добавляется к имени файла."""
        demo_file = temp_dir / "session.json"

        # Первая запись получит номер 1
        recorder1 = DemoRecorder(str(demo_file))
        assert recorder1.demo_file.stem == "session_1"
        assert recorder1.demo_file.parent == demo_file.parent
        assert recorder1.demo_file.suffix == ".json"
        # Сохраняем, чтобы файл появился на диске
        recorder1.record_response("Q1", "A1", ["A", "1"])

        # Вторая запись получит номер 2 (потому что session_1 уже существует)
        recorder2 = DemoRecorder(str(demo_file))
        assert recorder2.demo_file.stem == "session_2"
        recorder2.record_response("Q2", "A2", ["A", "2"])

        # Третья запись получит номер 3 (потому что session_1 и session_2 существуют)
        recorder3 = DemoRecorder(str(demo_file))
        assert recorder3.demo_file.stem == "session_3"

    def test_clear_responses(self, temp_dir):
        """Очистка записей."""
        demo_file = temp_dir / "test.json"
        recorder = DemoRecorder(str(demo_file))
        recorder.record_response("Q", "A", ["A"])

        assert recorder.get_response_count() == 1
        recorder.clear_responses()
        assert recorder.get_response_count() == 0

    def test_record_user_action_only(self, temp_dir):
        """Запись действия пользователя без ответа LLM."""
        demo_file = temp_dir / "test.json"
        recorder = DemoRecorder(str(demo_file))

        # Записываем действие без ответа LLM
        recorder.record_user_action_only('code_block', '1', 'Exit code: 0, Success: True')

        assert recorder.get_response_count() == 1

        # Проверяем, что файл создан и содержит правильные данные
        assert recorder.demo_file.exists()

        import json
        with open(recorder.demo_file, 'r') as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]['user_query'] == ""
        assert data[0]['response'] == ""
        assert data[0]['metadata']['action_only'] is True
        assert len(data[0]['user_actions']) == 1
        assert data[0]['user_actions'][0]['type'] == 'code_block'
        assert data[0]['user_actions'][0]['value'] == '1'


class TestDemoPlayer:
    """Тесты для DemoPlayer."""

    @pytest.fixture
    def demo_file_with_data(self):
        """Файл с тестовыми данными."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            data = [
                {
                    "timestamp": "2025-01-01T12:00:00",
                    "user_query": "Query 1",
                    "response": "Response 1",
                    "chunks": ["Res", "ponse", " 1"],
                    "metadata": {"model": "test"}
                },
                {
                    "timestamp": "2025-01-01T12:01:00",
                    "user_query": "Query 2",
                    "response": "Response 2",
                    "chunks": ["Res", "ponse", " 2"],
                    "metadata": {"model": "test"}
                }
            ]
            json.dump(data, f)
            temp_path = Path(f.name)

        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_load_responses(self, demo_file_with_data):
        """Загрузка записей из файла."""
        player = DemoPlayer(str(demo_file_with_data))

        assert player.get_total_responses() == 2
        assert player.has_more_responses()

    def test_play_next_response(self, demo_file_with_data):
        """Воспроизведение следующего ответа."""
        player = DemoPlayer(str(demo_file_with_data))

        response1 = player.play_next_response()
        assert response1 is not None
        assert response1.user_query == "Query 1"
        assert response1.response == "Response 1"

        response2 = player.play_next_response()
        assert response2 is not None
        assert response2.user_query == "Query 2"

    def test_has_more_responses(self, demo_file_with_data):
        """Проверка наличия ответов."""
        player = DemoPlayer(str(demo_file_with_data))

        assert player.has_more_responses()
        player.play_next_response()
        assert player.has_more_responses()
        player.play_next_response()
        assert not player.has_more_responses()

    def test_create_chunk_generator(self, demo_file_with_data):
        """Создание генератора чанков."""
        player = DemoPlayer(str(demo_file_with_data))
        response = player.play_next_response()

        chunks = list(player.create_chunk_generator(response, chunk_delay=0))
        assert chunks == ["Res", "ponse", " 1"]

    def test_reset(self, demo_file_with_data):
        """Сброс позиции воспроизведения."""
        player = DemoPlayer(str(demo_file_with_data))

        player.play_next_response()
        player.play_next_response()
        assert not player.has_more_responses()

        player.reset()
        assert player.has_more_responses()
        assert player.get_current_position() == 0


class TestDemoManager:
    """Тесты для DemoManager."""

    @pytest.fixture
    def temp_file(self):
        """Временный файл."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_user_actions_tracking(self, temp_file):
        """Отслеживание действий пользователя."""
        manager = DemoManager("record", str(temp_file))

        # Добавляем действия
        manager.add_user_action('command', '.ls')
        manager.add_user_action('code_block', '1')
        manager.add_user_action('query', 'What is this?')

        # Получаем и очищаем
        actions = manager.get_and_clear_user_actions()
        assert len(actions) == 3
        assert actions[0]['type'] == 'command'
        assert actions[0]['value'] == '.ls'
        assert actions[1]['type'] == 'code_block'
        assert actions[1]['value'] == '1'
        assert actions[2]['type'] == 'query'
        assert actions[2]['value'] == 'What is this?'

        # Буфер должен быть очищен
        actions = manager.get_and_clear_user_actions()
        assert len(actions) == 0

    def test_record_mode(self, temp_file):
        """Режим записи."""
        manager = DemoManager("record", str(temp_file))

        assert manager.is_recording()
        assert not manager.is_playing()
        assert manager.is_enabled()
        assert manager.get_recorder() is not None
        assert manager.get_player() is None

    def test_play_mode(self, temp_file):
        """Режим воспроизведения."""
        # Создаём файл с данными
        data = [{
            "timestamp": "2025-01-01T12:00:00",
            "user_query": "Q",
            "response": "A",
            "chunks": ["A"],
            "metadata": {},
            "user_actions": []
        }]
        with open(temp_file, 'w') as f:
            json.dump(data, f)

        manager = DemoManager("play", str(temp_file))

        assert not manager.is_recording()
        assert manager.is_playing()
        assert manager.is_enabled()
        assert manager.get_recorder() is None
        assert manager.get_player() is not None

    def test_off_mode(self, temp_file):
        """Выключенный режим."""
        manager = DemoManager("off", str(temp_file))

        assert not manager.is_recording()
        assert not manager.is_playing()
        assert not manager.is_enabled()
        assert manager.get_recorder() is None
        assert manager.get_player() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
