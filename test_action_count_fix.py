#!/usr/bin/env python3
"""
Тест для проверки правильности работы action_count в robot mode.
Проверяет, что второе действие корректно использует first_action_pause.
"""

from io import StringIO
from unittest.mock import Mock, patch
from penguin_tamer.demo.robot_presenter import RobotPresenter
from penguin_tamer.demo.timing import RobotTimingConfig


def test_action_count_with_skip():
    """Проверка, что action_count инкрементируется правильно."""

    # Create mock objects
    console = Mock()
    demo_manager = Mock()
    t = lambda x: x

    # Create timing config with known values
    timing = RobotTimingConfig(
        first_action_pause=5.0,  # Большое значение для первого действия
        between_actions_range=(1.0, 1.5),  # Меньшие значения для остальных
    )

    presenter = RobotPresenter(console, demo_manager, t, timing)

    # Проверяем начальное состояние
    assert presenter.action_count == 0, "action_count должен быть 0 в начале"

    # Первое действие с skip_user_input=True (не должно увеличивать счётчик)
    action1 = {'type': 'query', 'value': 'First question'}
    demo_manager.play_next_response.return_value = None

    presenter.present_action(action1, has_code_blocks=False, skip_user_input=True)

    assert presenter.action_count == 0, "action_count не должен увеличиться при skip_user_input=True"

    # Второе действие с skip_user_input=False (должно увеличить счётчик до 1)
    action2 = {'type': 'query', 'value': 'Second question'}
    demo_manager.get_typing_strategy.return_value = None

    with patch('time.sleep'):  # Mock sleep to speed up test
        presenter.present_action(action2, has_code_blocks=False, skip_user_input=False)

    assert presenter.action_count == 1, "action_count должен стать 1 после первого показа ввода"

    # Третье действие (должно увеличить счётчик до 2)
    action3 = {'type': 'query', 'value': 'Third question'}

    with patch('time.sleep'):
        presenter.present_action(action3, has_code_blocks=False, skip_user_input=False)

    assert presenter.action_count == 2, "action_count должен стать 2 после второго показа ввода"

    print("✓ Все проверки пройдены!")
    print(f"  Первое действие (skip=True): action_count не изменился")
    print(f"  Второе действие (skip=False): action_count = 1 (первая пауза)")
    print(f"  Третье действие (skip=False): action_count = 2 (обычная пауза)")


if __name__ == '__main__':
    test_action_count_with_skip()
