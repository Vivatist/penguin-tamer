"""
Tests for new demo package.

Tests the decoupled demo system with Strategy, Repository, and Facade patterns.
"""

import pytest

from penguin_tamer.demo import (
    DemoManager,
    DemoRecorder,
    DemoPlayer,
    DemoStorage,
    DemoResponse,
    DemoSession,
    UserAction,
    RobotPlaybackStrategy,
    RecordStrategy,
    PlayerFactory,
)


class TestUserAction:
    """Test UserAction factory methods."""

    def test_create_query(self):
        action = UserAction.create_query("What is Python?")
        assert action.type == 'query'
        assert action.value == "What is Python?"

    def test_create_command(self):
        action = UserAction.create_command("ls -la")
        assert action.type == 'command'
        assert action.value == "ls -la"

    def test_create_code_block(self):
        action = UserAction.create_code_block("print('hello')")
        assert action.type == 'code_block'
        assert action.value == "print('hello')"

    def test_to_dict(self):
        action = UserAction.create_query("test")
        d = action.to_dict()
        assert d['type'] == 'query'
        assert d['value'] == 'test'


class TestDemoResponse:
    """Test DemoResponse data model."""

    def test_has_response_content(self):
        response = DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="Hello",
            response="Hi there!",
            chunks=["Hi ", "there!"],
            metadata={},
            user_actions=[]
        )
        assert response.has_response_content() is True

    def test_is_action_only(self):
        response = DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="",
            response="",
            chunks=[],
            metadata={'action_only': True},
            user_actions=[{'type': 'command', 'value': 'ls'}]
        )
        assert response.is_action_only() is True

    def test_to_from_dict(self):
        response = DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="Hello",
            response="Hi",
            chunks=["Hi"],
            metadata={'model': 'gpt-4'},
            user_actions=[{'type': 'query', 'value': 'Hello'}]
        )

        d = response.to_dict()
        restored = DemoResponse.from_dict(d)

        assert restored.user_query == response.user_query
        assert restored.response == response.response
        assert restored.chunks == response.chunks


class TestDemoSession:
    """Test DemoSession aggregate."""

    def test_add_response(self):
        session = DemoSession()
        response = DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="test",
            response="response",
            chunks=[],
            metadata={},
            user_actions=[]
        )

        session.add_response(response)
        assert len(session.responses) == 1
        assert session.responses[0] == response

    def test_clear(self):
        session = DemoSession()
        session.add_response(DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="test",
            response="response",
            chunks=[],
            metadata={},
            user_actions=[]
        ))

        session.clear()
        assert len(session.responses) == 0


class TestDemoStorage:
    """Test DemoStorage repository."""

    def test_save_and_load(self, tmp_path):
        storage = DemoStorage()
        session = DemoSession()

        response = DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="Hello",
            response="Hi",
            chunks=["Hi"],
            metadata={'model': 'test'},
            user_actions=[{'type': 'query', 'value': 'Hello'}]
        )
        session.add_response(response)

        demo_file = tmp_path / "test_demo.json"
        storage.save_session(session, str(demo_file))

        assert demo_file.exists()

        loaded_session = storage.load_session(str(demo_file))
        assert len(loaded_session.responses) == 1
        assert loaded_session.responses[0].user_query == "Hello"

    def test_get_unique_path(self, tmp_path):
        storage = DemoStorage()

        # Create first file
        file1 = tmp_path / "test.json"
        file1.write_text("{}")

        # Get unique path - should add _1
        unique_path = storage.get_unique_path(file1)
        assert "_1.json" in str(unique_path)

    def test_list_sessions(self, tmp_path):
        storage = DemoStorage()

        # Create some demo files
        (tmp_path / "demo1.json").write_text("{}")
        (tmp_path / "demo2.json").write_text("{}")
        (tmp_path / "other.txt").write_text("")

        demos = storage.list_sessions(str(tmp_path))
        assert len(demos) == 2
        assert all(d.endswith('.json') for d in demos)


class TestRecordStrategy:
    """Test recording strategy."""

    def test_add_user_action(self):
        strategy = RecordStrategy()
        strategy.add_user_action('query', 'Hello')

        assert len(strategy.pending_actions) == 1
        assert strategy.pending_actions[0]['type'] == 'query'

    def test_record_response(self):
        strategy = RecordStrategy()
        strategy.add_user_action('query', 'Hello')

        strategy.record_response(
            user_query='Hello',
            response='Hi',
            chunks=['Hi'],
            metadata={'model': 'test'}
        )

        assert len(strategy.session.responses) == 1
        assert strategy.pending_actions == []  # Should be cleared

    def test_record_action_only(self):
        strategy = RecordStrategy()
        strategy.record_action_only('command', 'ls', 'listing files')

        assert len(strategy.session.responses) == 1
        response = strategy.session.responses[0]
        assert response.is_action_only()


class TestDemoRecorder:
    """Test DemoRecorder."""

    def test_start_stop_recording(self, tmp_path):
        demo_file = tmp_path / "test.json"
        recorder = DemoRecorder(str(demo_file))

        recorder.start_recording()
        assert recorder.is_recording()

        recorder.record_response('Hello', 'Hi', ['Hi'], {'model': 'test'})

        result = recorder.stop_recording()
        assert result is True
        assert demo_file.exists()

    def test_record_response(self, tmp_path):
        demo_file = tmp_path / "test.json"
        recorder = DemoRecorder(str(demo_file))
        recorder.start_recording()

        recorder.add_user_action('query', 'Hello')
        recorder.record_response(
            user_query='Hello',
            response='Hi there!',
            chunks=['Hi ', 'there!'],
            metadata={'model': 'test'}
        )

        session = recorder.get_session()
        assert len(session.responses) == 1
        assert session.responses[0].user_query == 'Hello'


class TestDemoPlayer:
    """Test DemoPlayer."""

    def test_load_and_play(self, tmp_path):
        # Create a demo file first
        demo_file = tmp_path / "test.json"
        session = DemoSession()
        session.add_response(DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="Hello",
            response="Hi",
            chunks=["Hi"],
            metadata={},
            user_actions=[{'type': 'query', 'value': 'Hello'}]
        ))

        storage = DemoStorage()
        storage.save_session(session, str(demo_file))

        # Now test player
        player = DemoPlayer(demo_file=str(demo_file))
        assert player.is_loaded()
        assert player.has_more_responses()

        response = player.play_next_response()
        assert response is not None
        assert response.user_query == "Hello"

    def test_player_factory(self, tmp_path):
        # Create demo file
        demo_file = tmp_path / "test.json"
        session = DemoSession()
        session.add_response(DemoResponse(
            timestamp="2024-01-01T12:00:00",
            user_query="Test",
            response="Response",
            chunks=["Response"],
            metadata={},
            user_actions=[]
        ))

        storage = DemoStorage()
        storage.save_session(session, str(demo_file))

        # Test factory methods
        player1 = PlayerFactory.create_simple_player(str(demo_file))
        assert player1.strategy is not None

        player2 = PlayerFactory.create_robot_player(str(demo_file))
        assert player2.strategy is not None
        assert isinstance(player2.strategy, RobotPlaybackStrategy)


class TestDemoManager:
    """Test DemoManager facade."""

    def test_recording_mode(self, tmp_path):
        demo_file = tmp_path / "test.json"
        manager = DemoManager(mode='record', demo_file=str(demo_file))

        assert manager.is_recording()
        assert not manager.is_playing()

        manager.add_user_action('query', 'Hello')
        manager.record_response('Hello', 'Hi', ['Hi'], {})

        manager.stop()
        assert demo_file.exists()

    def test_playback_mode(self, tmp_path):
        # Create demo file first
        demo_file = tmp_path / "test.json"
        recorder = DemoRecorder(str(demo_file))
        recorder.start_recording()
        recorder.add_user_action('query', 'Hello')
        recorder.record_response('Hello', 'Hi', ['Hi'], {})
        recorder.stop_recording()

        # Now test playback
        manager = DemoManager(mode='play', demo_file=str(demo_file))

        assert manager.is_playing()
        assert not manager.is_recording()
        assert manager.has_more_responses()

        response = manager.play_next_response()
        assert response is not None
        assert response.user_query == 'Hello'

    def test_robot_mode(self, tmp_path):
        # Create demo file
        demo_file = tmp_path / "test.json"
        recorder = DemoRecorder(str(demo_file))
        recorder.start_recording()
        recorder.add_user_action('query', 'Test')
        recorder.record_response('Test', 'Response', ['Response'], {})
        recorder.stop_recording()

        # Test robot mode
        manager = DemoManager(mode='robot', demo_file=str(demo_file))

        assert manager.is_robot_mode()
        assert manager.is_playing()

        action = manager.get_next_user_action()
        assert action is not None
        assert action['type'] == 'query'

    def test_context_manager(self, tmp_path):
        demo_file = tmp_path / "test.json"

        with DemoManager(mode='record', demo_file=str(demo_file)) as manager:
            manager.record_response('Hello', 'Hi', ['Hi'], {})

        # File should be saved after exit
        assert demo_file.exists()

    def test_off_mode(self):
        manager = DemoManager(mode='off')

        assert not manager.is_recording()
        assert not manager.is_playing()
        assert not manager.is_robot_mode()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
