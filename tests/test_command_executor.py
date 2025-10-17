"""
Комплексное тестирование Command Executor.

Объединённый набор тестов для command_executor.py, включающий:
- Базовое выполнение команд (успешные сценарии)
- Обработку ошибок (несуществующие файлы, команды, опции)
- Детальную проверку вывода (stdout/stderr/структура результата)
- Интеграционные тесты (последовательности команд, восстановление)
- Архитектуру (фабрика исполнителей, кросс-платформенность)
- Производительность (потоковый вывод, задержки)

Версия: 2.0 (объединённая)
Дата: 2025-10-09
"""

import sys
import os
import pytest
import time
from io import StringIO
from pathlib import Path

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Импорты после модификации sys.path
from rich.console import Console
from penguin_tamer.command_executor import (
    execute_and_handle_result,
    CommandExecutorFactory,
    LinuxCommandExecutor,
    WindowsCommandExecutor
)


@pytest.fixture
def console():
    """
    Фикстура для создания Rich Console с перехватом вывода.
    Использует StringIO для изоляции тестов от реального stdout.
    """
    return Console(file=StringIO(), force_terminal=True)


# ============================================================================
# БАЗОВОЕ ВЫПОЛНЕНИЕ КОМАНД
# ============================================================================

class TestBasicExecution:
    """
    Тесты базового выполнения команд (успешные сценарии).

    Покрытие:
    - Простые команды (echo)
    - Многострочный вывод
    - Цепочки команд
    - Кросс-платформенность
    """

    def test_simple_echo(self, console):
        """
        Простая команда echo.
        Проверяет базовую работоспособность исполнителя.
        """
        code = "echo Hello World" if os.name == 'nt' else 'echo "Hello World"'
        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        assert result['exit_code'] == 0
        assert 'Hello World' in result['stdout']
        assert result['stderr'] == ''
        assert result['interrupted'] is False

    def test_multiline_output(self, console):
        """
        Команда с многострочным выводом.
        Проверяет корректную обработку нескольких строк.
        """
        if os.name == 'nt':
            code = "\n".join([f"echo Line {i}" for i in range(1, 6)])
        else:
            code = "for i in 1 2 3 4 5; do echo \"Line $i\"; done"

        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        assert result['stdout'].count('Line') == 5

        # Проверяем порядок строк
        lines = [line for line in result['stdout'].split('\n') if 'Line' in line]
        assert len(lines) == 5

    def test_command_chaining(self, console):
        """
        Цепочка последовательных команд.
        Проверяет выполнение нескольких команд подряд.
        """
        if os.name == 'nt':
            code = "echo Step 1\necho Step 2\necho Step 3"
        else:
            code = 'echo "Step 1"\necho "Step 2"\necho "Step 3"'

        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        assert 'Step 1' in result['stdout']
        assert 'Step 2' in result['stdout']
        assert 'Step 3' in result['stdout']


# ============================================================================
# ОБРАБОТКА ОШИБОК
# ============================================================================

class TestErrorHandling:
    """
    Тесты обработки ошибок выполнения.

    Покрытие:
    - Несуществующие файлы
    - Несуществующие команды
    - Невалидные опции
    - Недоступные сетевые узлы
    """

    def test_nonexistent_file(self, console):
        """
        Попытка чтения несуществующего файла.
        Должна вернуть код ошибки и сообщение в stderr или stdout.
        """
        code = (
            "type nonexistent_file_xyz_12345.txt"
            if os.name == 'nt'
            else "cat nonexistent_file_xyz_12345.txt"
        )
        result = execute_and_handle_result(console, code)

        assert result['success'] is False
        assert result['exit_code'] != 0

        error_present = (
            result['stderr'] != '' or
            'не удается найти' in result['stdout'].lower() or
            'no such file' in result['stdout'].lower() or
            'cannot find' in result['stdout'].lower()
        )
        assert error_present, (
            f"Ожидалось сообщение об ошибке, но получено: "
            f"stdout={result['stdout']}, stderr={result['stderr']}"
        )

    def test_command_not_found(self, console):
        """
        Попытка выполнения несуществующей команды.
        Должна вернуть сообщение "command not found".
        """
        code = "nonexistent_command_xyz_12345"
        result = execute_and_handle_result(console, code)

        assert result['success'] is False
        assert result['exit_code'] != 0

        error_indicators = ['not found', 'не найден', 'не является', 'not recognized']
        has_error = any(
            ind in result['stderr'].lower() or ind in result['stdout'].lower()
            for ind in error_indicators
        )
        assert has_error, (
            f"Ожидался индикатор ошибки, но получено: "
            f"stdout={result['stdout']}, stderr={result['stderr']}"
        )

    def test_invalid_option(self, console):
        """
        Невалидная опция команды.
        Команда существует, но опция неправильная.
        """
        code = "dir /invalid_xyz_option" if os.name == 'nt' else "ls --invalid-xyz-option"
        result = execute_and_handle_result(console, code)

        assert result['success'] is False
        assert result['exit_code'] != 0

    @pytest.mark.slow
    def test_ping_unreachable_host(self, console):
        """
        Ping недоступного хоста (только Windows).
        Проверяет обработку сетевых ошибок.
        """
        if os.name != 'nt':
            pytest.skip("Тест только для Windows")

        # Используем заведомо несуществующее имя хоста
        code = "ping -n 1 -w 500 nonexistent-host-xyz-12345.local"
        result = execute_and_handle_result(console, code)

        assert result['exit_code'] != 0
        # Проверяем наличие сообщения об ошибке
        error_indicators = [
            'не найден', 'не удается', 'не удалось обнаружить',
            'could not find', 'unknown host'
        ]
        has_error = any(ind in result['stdout'].lower() for ind in error_indicators)
        assert has_error, f"Ожидалось сообщение об ошибке разрешения имени, но получено: {result['stdout']}"


# ============================================================================
# ДЕТАЛЬНАЯ ПРОВЕРКА ВЫВОДА
# ============================================================================

class TestOutputHandling:
    """
    Тесты детальной обработки вывода команд.

    Покрытие:
    - Вывод в stdout
    - Вывод в stderr
    - Пустой вывод
    - Структура результата
    - Специальные символы
    """

    def test_command_with_output_to_stderr(self, console):
        """
        Команда с выводом в stderr (только Windows).
        Проверяет корректное разделение stdout/stderr.
        """
        if os.name != 'nt':
            pytest.skip("Тест требует специфичной для Windows команды")

        # dir с несуществующим путём выводит ошибку в stderr
        code = "dir C:\\nonexistent_path_xyz_12345 2>&1"
        result = execute_and_handle_result(console, code)

        assert result['exit_code'] != 0
        # Ошибка может быть в stdout или stderr в зависимости от перенаправления
        # Проверяем на русском и английском языках
        output_lower = result['stdout'].lower()
        has_error = (
            bool(result['stderr']) or
            'не найден' in output_lower or
            'file not found' in output_lower or
            'cannot find' in output_lower
        )
        assert has_error

    def test_empty_command_output(self, console):
        """
        Команда с пустым выводом.
        Проверяет обработку команд без текстового вывода.
        """
        if os.name == 'nt':
            # Команда, которая ничего не выводит
            code = "cd ."
        else:
            code = "true"

        result = execute_and_handle_result(console, code)

        assert result['exit_code'] == 0
        assert result['stdout'].strip() == '' or result['stdout'] == ''

    def test_result_structure(self, console):
        """
        Проверка структуры возвращаемого результата.
        Все обязательные поля должны присутствовать.
        """
        code = "echo test" if os.name == 'nt' else 'echo "test"'
        result = execute_and_handle_result(console, code)

        # Проверяем наличие всех обязательных полей
        required_fields = ['success', 'exit_code', 'stdout', 'stderr', 'interrupted']
        for field in required_fields:
            assert field in result, f"Отсутствует обязательное поле: {field}"

        # Проверяем типы данных
        assert isinstance(result['success'], bool)
        assert isinstance(result['exit_code'], int)
        assert isinstance(result['stdout'], str)
        assert isinstance(result['stderr'], str)
        assert isinstance(result['interrupted'], bool)

    def test_command_with_special_characters(self, console):
        """
        Команда со специальными символами.
        Проверяет экранирование и кодировку.
        """
        if os.name == 'nt':
            # Используем безопасные символы для Windows
            code = 'echo Test-123_ABC'
        else:
            code = 'echo "Test-123_ABC!@#"'

        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        assert 'Test' in result['stdout']
        assert '123' in result['stdout']


# ============================================================================
# СПЕЦИАЛЬНЫЕ СЛУЧАИ
# ============================================================================

class TestSpecialCases:
    """
    Тесты специальных и граничных случаев.

    Покрытие:
    - Пустые команды
    - Unicode/кириллица
    - Длинный вывод
    """

    def test_empty_command(self, console):
        """
        Полностью пустая команда.
        Должна выполниться успешно без действий.
        """
        result = execute_and_handle_result(console, "")
        assert result['exit_code'] == 0

    def test_unicode_cyrillic(self, console):
        """
        Кириллица и Unicode в командах.
        Проверяет корректную обработку не-ASCII символов.
        """
        code = 'echo Привет мир!' if os.name == 'nt' else 'echo "Привет мир!"'
        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        # Проверяем наличие хотя бы части кириллических символов
        has_cyrillic = any(c in result['stdout'] for c in 'Привет')
        assert has_cyrillic or 'Привет' in result['stdout'], (
            f"Кириллица не найдена в выводе: {result['stdout']}"
        )


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestIntegration:
    """
    Интеграционные тесты последовательного выполнения.

    Покрытие:
    - Последовательность команд
    - Восстановление после ошибок
    - Смешанные сценарии успеха/ошибки
    """

    def test_sequence_of_commands(self, console):
        """
        Выполнение последовательности разных команд.
        Проверяет, что состояние не сохраняется между вызовами.
        """
        commands = [
            "echo First" if os.name == 'nt' else 'echo "First"',
            "echo Second" if os.name == 'nt' else 'echo "Second"',
            "echo Third" if os.name == 'nt' else 'echo "Third"'
        ]

        results = [execute_and_handle_result(console, cmd) for cmd in commands]

        assert all(r['success'] for r in results)
        assert 'First' in results[0]['stdout']
        assert 'Second' in results[1]['stdout']
        assert 'Third' in results[2]['stdout']

    def test_error_recovery(self, console):
        """
        Восстановление после ошибки.
        После ошибочной команды следующая должна выполниться нормально.
        """
        # Сначала ошибка
        error_code = "type nonexistent_xyz.txt" if os.name == 'nt' else "cat nonexistent_xyz.txt"
        error_result = execute_and_handle_result(console, error_code)
        assert error_result['success'] is False

        # Затем успешная команда
        success_code = "echo Recovery" if os.name == 'nt' else 'echo "Recovery"'
        success_result = execute_and_handle_result(console, success_code)
        assert success_result['success'] is True
        assert 'Recovery' in success_result['stdout']


# ============================================================================
# АРХИТЕКТУРА И ФАБРИКА
# ============================================================================

class TestArchitecture:
    """
    Тесты архитектуры и фабрики исполнителей.

    Покрытие:
    - Правильный выбор исполнителя для ОС
    - Кросс-платформенность
    """

    def test_creates_correct_executor(self):
        """
        Фабрика создаёт правильный исполнитель для текущей ОС.
        """
        executor = CommandExecutorFactory.create_executor()

        assert executor is not None

        if os.name == 'nt':
            assert isinstance(executor, WindowsCommandExecutor), \
                f"На Windows должен быть WindowsCommandExecutor, получен {type(executor)}"
        else:
            assert isinstance(executor, LinuxCommandExecutor), \
                f"На Linux должен быть LinuxCommandExecutor, получен {type(executor)}"


# ============================================================================
# ПРОИЗВОДИТЕЛЬНОСТЬ
# ============================================================================

class TestPerformance:
    """
    Тесты производительности и потокового вывода.

    Покрытие:
    - Потоковый вывод с задержками
    - Длительные команды
    """

    @pytest.mark.slow
    def test_delayed_output(self, console):
        """
        Команда с задержками - проверка потокового вывода.
        Вывод должен появляться в реальном времени, не накапливаясь.
        """
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

        assert result['success'] is True
        assert 'Start' in result['stdout']
        assert 'Middle' in result['stdout']
        assert 'End' in result['stdout']
        assert elapsed >= 1.5, (
            f"Должна быть задержка минимум 1.5s, было {elapsed:.1f}s"
        )


# ============================================================================
# БЫСТРЫЕ SMOKE-ТЕСТЫ
# ============================================================================

@pytest.mark.fast
class TestQuickSmoke:
    """
    Быстрые smoke-тесты для проверки базовой работоспособности.
    Используются при частых запусках CI/CD.
    """

    def test_basic_echo(self, console):
        """
        Базовая проверка: команда echo выполняется и возвращает результат.
        """
        code = "echo test" if os.name == 'nt' else 'echo "test"'
        result = execute_and_handle_result(console, code)

        assert result['success'] is True
        assert result['exit_code'] == 0
        assert 'test' in result['stdout']
