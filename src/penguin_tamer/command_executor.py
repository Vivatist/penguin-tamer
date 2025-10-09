import subprocess
import platform
import tempfile
import os
from abc import ABC, abstractmethod
from rich.console import Console
from penguin_tamer.i18n import t


# Абстрактный базовый класс для исполнителей команд
class CommandExecutor(ABC):
    """Базовый интерфейс для исполнителей команд разных ОС"""

    @abstractmethod
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """
        Выполняет блок кода и возвращает результат

        Args:
            code_block (str): Блок кода для выполнения

        Returns:
            subprocess.CompletedProcess: Результат выполнения команды
        """


# Исполнитель команд для Linux
class LinuxCommandExecutor(CommandExecutor):
    """Исполнитель команд для Linux/Unix систем"""

    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bash-команды в Linux с выводом в реальном времени"""
        import threading

        # Используем Popen для вывода в реальном времени
        process = subprocess.Popen(
            code_block,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Используем текстовый режим для автоматического декодирования
        )

        # Буферы для накопления вывода
        stdout_lines = []
        stderr_lines = []

        # Функция для чтения stderr в отдельном потоке
        def read_stderr():
            if process.stderr:
                for line in process.stderr:
                    stderr_lines.append(line.rstrip('\n'))

        # Запускаем поток для чтения stderr
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        # Читаем stdout построчно в основном потоке и сразу выводим
        try:
            if process.stdout:
                for line in process.stdout:
                    line_clean = line.rstrip('\n')
                    stdout_lines.append(line_clean)
                    print(line_clean)  # Выводим сразу!

            # Ждем завершения процесса
            process.wait()

            # Даем потоку stderr время завершиться
            stderr_thread.join(timeout=1)

        except KeyboardInterrupt:
            # Если получили Ctrl+C, завершаем процесс и пробрасываем исключение
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            # Ждем поток stderr
            stderr_thread.join(timeout=1)
            raise

        # Создаем объект CompletedProcess для совместимости
        result = subprocess.CompletedProcess(
            args=code_block,
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines),
            stderr='\n'.join(stderr_lines)
        )

        return result


# Исполнитель команд для Windows
class WindowsCommandExecutor(CommandExecutor):
    """Исполнитель команд для Windows систем"""

    def _decode_line_windows(self, line_bytes: bytes) -> str:
        """Безопасное декодирование строки в Windows с учетом разных кодировок"""
        # Список кодировок для попытки декодирования в Windows
        encodings = ['cp866', 'cp1251', 'utf-8', 'ascii']

        for encoding in encodings:
            try:
                decoded = line_bytes.decode(encoding, errors='strict')
                return decoded.strip()
            except UnicodeDecodeError:
                continue

        # Если ничего не сработало, используем замену с ошибками
        try:
            return line_bytes.decode('utf-8', errors='replace').strip()
        except Exception:
            return line_bytes.decode('latin1', errors='replace').strip()

    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл с выводом в реальном времени"""
        import threading

        # Предобработка кода для Windows - отключаем echo для предотвращения дублирования команд
        code = '@echo off\n' + code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')

        # Создаем временный .bat файл с правильной кодировкой
        fd, temp_path = tempfile.mkstemp(suffix='.bat')

        try:
            with os.fdopen(fd, 'w', encoding='cp866', errors='replace') as f:
                f.write(code)

            # Запускаем команду
            process = subprocess.Popen(
                [temp_path],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Используем байты для корректной работы с кодировками
                creationflags=subprocess.CREATE_NO_WINDOW  # Предотвращаем создание окна консоли
            )

            # Буферы для накопления вывода
            stdout_lines = []
            stderr_lines = []

            # Функция для чтения stderr в отдельном потоке
            def read_stderr():
                if process.stderr:
                    for line in process.stderr:
                        if line:
                            decoded = self._decode_line_windows(line)
                            if decoded:
                                stderr_lines.append(decoded)

            # Запускаем поток для чтения stderr
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()

            # Читаем stdout построчно в основном потоке и сразу выводим
            try:
                if process.stdout:
                    for line in process.stdout:
                        if line:
                            decoded = self._decode_line_windows(line)
                            if decoded:
                                stdout_lines.append(decoded)
                                print(decoded)  # Выводим сразу!

                # Ждем завершения процесса
                process.wait()

                # Даем потоку stderr время завершиться
                stderr_thread.join(timeout=1)

            except KeyboardInterrupt:
                # Если получили Ctrl+C, завершаем процесс и пробрасываем исключение
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                # Ждем поток stderr
                stderr_thread.join(timeout=1)
                raise

            # Создаем объект CompletedProcess для совместимости
            result = subprocess.CompletedProcess(
                args=[temp_path],
                returncode=process.returncode,
                stdout='\n'.join(stdout_lines),
                stderr='\n'.join(stderr_lines)
            )

            return result
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
            except Exception:
                pass


# Фабрика для создания исполнителей команд
class CommandExecutorFactory:
    """Фабрика для создания исполнителей команд в зависимости от ОС"""

    @staticmethod
    def create_executor() -> CommandExecutor:
        """
        Создает исполнитель команд в зависимости от текущей ОС

        Returns:
            CommandExecutor: Соответствующий исполнитель для текущей ОС
        """
        system = platform.system().lower()
        if system == "windows":
            return WindowsCommandExecutor()
        else:
            return LinuxCommandExecutor()


def execute_and_handle_result(console: Console, code: str) -> dict:
    """
    Выполняет блок кода и обрабатывает результаты выполнения.

    Args:
        console (Console): Консоль для вывода
        code (str): Код для выполнения

    Returns:
        dict: Результат выполнения с ключами:
            - 'success': bool - успешность выполнения
            - 'exit_code': int - код возврата
            - 'stdout': str - стандартный вывод
            - 'stderr': str - вывод ошибок
            - 'interrupted': bool - прервано ли выполнение
    """
    result = {
        'success': False,
        'exit_code': -1,
        'stdout': '',
        'stderr': '',
        'interrupted': False
    }

    # Получаем исполнитель для текущей ОС
    try:
        executor = CommandExecutorFactory.create_executor()

        # Выполняем код через соответствующий исполнитель
        console.print(t("[dim]>>> Result:[/dim]"))

        try:
            process = executor.execute(code)

            # Сохраняем результаты
            result['exit_code'] = process.returncode
            result['stdout'] = process.stdout
            result['stderr'] = process.stderr
            result['success'] = process.returncode == 0

            # Выводим код завершения
            console.print(t("[dim]>>> Exit code: {code}[/dim]").format(code=process.returncode))

            # Показываем stderr если есть
            if process.stderr:
                console.print(t("[yellow]>>> Error:[/yellow]"))
                console.print(process.stderr)

        except KeyboardInterrupt:
            # Перехватываем Ctrl+C во время выполнения команды
            result['interrupted'] = True
            console.print(t("[dim]>>> Command interrupted by user (Ctrl+C)[/dim]"))

    except Exception as e:
        result['stderr'] = str(e)
        console.print(t("[dim]Script execution error: {error}[/dim]").format(error=e))

    return result


def run_code_block(console: Console, code_blocks: list, idx: int) -> dict:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.

    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока

    Returns:
        dict: Результат выполнения (см. execute_and_handle_result)
    """

    # Проверяем корректность индекса
    if not (1 <= idx <= len(code_blocks)):
        console.print(
            t("[yellow]Block #{idx} does not exist. Available blocks: 1 to {total}.[/yellow]")
            .format(idx=idx, total=len(code_blocks))
        )
        return {
            'success': False,
            'exit_code': -1,
            'stdout': '',
            'stderr': 'Block index out of range',
            'interrupted': False
        }

    code = code_blocks[idx - 1]

    console.print(t("[dim]>>> Running block #{idx}:[/dim]").format(idx=idx))
    console.print(code)

    # Выполняем код и обрабатываем результат
    return execute_and_handle_result(console, code)
