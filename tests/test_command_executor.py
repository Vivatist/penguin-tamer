"""
Комплексное тестирование Command Executor.

Объединяет все тесты для command_executor.py в один файл.
"""

import sys
import os
import pytest
import time
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rich.console import Console
from penguin_tamer.command_executor import (
    execute_and_handle_result,
    CommandExecutorFactory,
    LinuxCommandExecutor,
    WindowsCommandExecutor
)


@pytest.fixture
def console():
    """Фикстура для создания Rich Console"""
    return Console()


class TestSuccessfulExecution:
    """Тесты успешного выполнения команд"""
    
    def test_simple_echo(self, console):
        """Простая команда echo"""
        code = "echo Hello World" if os.name == 'nt' else 'echo "Hello World"'
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == True
        assert result['exit_code'] == 0
        assert 'Hello World' in result['stdout']
        assert result['stderr'] == ''
        assert result['interrupted'] == False
    
    def test_multiline_output(self, console):
        """Команда с многострочным выводом"""
        if os.name == 'nt':
            code = "\n".join([f"echo Line {i}" for i in range(1, 6)])
        else:
            code = "for i in 1 2 3 4 5; do echo \"Line $i\"; done"
        
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == True
        assert result['stdout'].count('Line') == 5
    
    def test_command_chaining(self, console):
        """Цепочка команд"""
        if os.name == 'nt':
            code = "echo Step 1\necho Step 2\necho Step 3"
        else:
            code = 'echo "Step 1"\necho "Step 2"\necho "Step 3"'
        
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == True
        assert 'Step 1' in result['stdout']
        assert 'Step 2' in result['stdout']
        assert 'Step 3' in result['stdout']


class TestExecutionErrors:
    """Тесты ошибок выполнения"""
    
    def test_nonexistent_file(self, console):
        """Попытка чтения несуществующего файла"""
        code = "type nonexistent_file_xyz.txt" if os.name == 'nt' else "cat nonexistent_file_xyz.txt"
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == False
        assert result['exit_code'] != 0
        
        error_present = (
            result['stderr'] != '' or 
            'не удается найти' in result['stdout'].lower() or
            'no such file' in result['stdout'].lower()
        )
        assert error_present
    
    def test_command_not_found(self, console):
        """Несуществующая команда"""
        code = "nonexistent_command_xyz_123"
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == False
        assert result['exit_code'] != 0
        
        error_indicators = ['not found', 'не найден', 'не является', 'not recognized']
        has_error = any(
            ind in result['stderr'].lower() or ind in result['stdout'].lower()
            for ind in error_indicators
        )
        assert has_error
    
    def test_invalid_option(self, console):
        """Невалидная опция команды"""
        code = "dir /invalid_xyz" if os.name == 'nt' else "ls --invalid-xyz"
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == False
        assert result['exit_code'] != 0


class TestStreamingOutput:
    """Тесты потокового вывода в реальном времени"""
    
    def test_delayed_output(self, console):
        """Команда с задержками - проверка потокового вывода"""
        if os.name == 'nt':
            code = """echo Start
ping -n 2 127.0.0.1 > nul
echo Middle
ping -n 2 127.0.0.1 > nul
echo End"""
        else:
            code = """echo "Start"
sleep 1
echo "Middle"
sleep 1
echo "End"
"""
        
        start_time = time.time()
        result = execute_and_handle_result(console, code)
        elapsed = time.time() - start_time
        
        assert result['success'] == True
        assert 'Start' in result['stdout']
        assert 'Middle' in result['stdout']
        assert 'End' in result['stdout']
        assert elapsed >= 1.5, f"Должна быть задержка минимум 1.5s, было {elapsed:.1f}s"


class TestSpecialCases:
    """Специальные случаи"""
    
    def test_empty_command(self, console):
        """Пустая команда"""
        result = execute_and_handle_result(console, "")
        assert result['exit_code'] == 0
    
    def test_unicode_cyrillic(self, console):
        """Кириллица и Unicode"""
        code = 'echo Привет мир!' if os.name == 'nt' else 'echo "Привет мир!"'
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == True
        has_cyrillic = any(c in result['stdout'] for c in 'Привет')
        assert has_cyrillic or 'Привет' in result['stdout']


class TestExecutorFactory:
    """Тесты фабрики исполнителей"""
    
    def test_creates_correct_executor(self):
        """Правильный исполнитель для текущей ОС"""
        executor = CommandExecutorFactory.create_executor()
        
        assert executor is not None
        
        if os.name == 'nt':
            assert isinstance(executor, WindowsCommandExecutor)
        else:
            assert isinstance(executor, LinuxCommandExecutor)


# Маркеры для быстрых тестов
@pytest.mark.fast
class TestQuickSmoke:
    """Быстрые smoke-тесты"""
    
    def test_basic_echo(self, console):
        """Базовая проверка работоспособности"""
        code = "echo test" if os.name == 'nt' else 'echo "test"'
        result = execute_and_handle_result(console, code)
        
        assert result['success'] == True
        assert result['exit_code'] == 0
        assert 'test' in result['stdout']
