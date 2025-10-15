import subprocess
import platform
import tempfile
import os
import threading
from abc import ABC, abstractmethod
from rich.console import Console
from penguin_tamer.i18n import t


# === Базовый класс с Template Method паттерном ===

class BaseCommandExecutor(ABC):
    """Базовый исполнитель с общей логикой выполнения команд.

    Использует Template Method паттерн для устранения дублирования кода между
    платформами. Общая логика управления потоками, вывода и обработки ошибок
    находится здесь, а специфичные для ОС детали делегируются подклассам.
    """

    @abstractmethod
    def _create_process(self, code_block: str) -> subprocess.Popen:
        """Создает процесс для выполнения команды (специфично для ОС).

        Args:
            code_block: Код для выполнения

        Returns:
            subprocess.Popen: Созданный процесс
        """
        pass

    @abstractmethod
    def _decode_line(self, line: bytes) -> str:
        """Декодирует байты в строку (специфично для ОС).

        Args:
            line: Байты для декодирования

        Returns:
            str: Декодированная строка
        """
        pass

    def _cleanup(self, process: subprocess.Popen) -> None:
        """Очищает ресурсы после выполнения (опционально переопределяется).

        Args:
            process: Процесс для очистки
        """
        pass

    def _start_stderr_thread(
        self,
        process: subprocess.Popen,
        stderr_lines: list
    ) -> threading.Thread:
        """Запускает поток для чтения stderr.

        Args:
            process: Процесс для чтения
            stderr_lines: Список для накопления строк stderr

        Returns:
            threading.Thread: Запущенный поток
        """
        def read_stderr():
            if process.stderr:
                for line in process.stderr:
                    decoded = self._decode_line(line)
                    if decoded:
                        stderr_lines.append(decoded)

        thread = threading.Thread(target=read_stderr, daemon=True)
        thread.start()
        return thread

    def _process_stdout(
        self,
        process: subprocess.Popen,
        stdout_lines: list,
        output_callback=None
    ) -> None:
        """Обрабатывает stdout в реальном времени.

        Args:
            process: Процесс для чтения
            stdout_lines: Список для накопления строк stdout
            output_callback: Optional callback function to call for each line
        """
        if process.stdout:
            for line in process.stdout:
                decoded = self._decode_line(line)
                if decoded:
                    stdout_lines.append(decoded)
                    print(decoded)  # Выводим сразу!
                    if output_callback:
                        # Добавляем \n для правильного воспроизведения
                        output_callback(decoded + '\n')

    def _terminate_process(self, process: subprocess.Popen) -> None:
        """Завершает процесс при прерывании.

        Args:
            process: Процесс для завершения
        """
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    def _create_result(
        self,
        process: subprocess.Popen,
        stdout_lines: list,
        stderr_lines: list
    ) -> subprocess.CompletedProcess:
        """Создает объект CompletedProcess с результатами.

        Args:
            process: Завершенный процесс
            stdout_lines: Строки stdout
            stderr_lines: Строки stderr

        Returns:
            subprocess.CompletedProcess: Результат выполнения
        """
        return subprocess.CompletedProcess(
            args=getattr(process.args, '__iter__', lambda: [process.args])(),
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines),
            stderr='\n'.join(stderr_lines)
        )

    def execute(self, code_block: str, output_callback=None) -> subprocess.CompletedProcess:
        """Шаблонный метод выполнения команды.

        Определяет общий алгоритм выполнения, делегируя специфичные
        детали подклассам через абстрактные методы.

        Args:
            code_block: Блок кода для выполнения
            output_callback: Optional callback function to call for each output line

        Returns:
            subprocess.CompletedProcess: Результат выполнения команды
        """
        process = self._create_process(code_block)
        stdout_lines, stderr_lines = [], []

        # Запускаем поток для stderr
        stderr_thread = self._start_stderr_thread(process, stderr_lines)

        try:
            # Обрабатываем stdout в основном потоке
            self._process_stdout(process, stdout_lines, output_callback)

            # Ждем завершения процесса
            process.wait()

            # Даем потоку stderr время завершиться
            stderr_thread.join(timeout=1)

        except KeyboardInterrupt:
            # Обрабатываем Ctrl+C
            self._terminate_process(process)
            stderr_thread.join(timeout=1)
            raise

        finally:
            # Очищаем ресурсы
            self._cleanup(process)

        return self._create_result(process, stdout_lines, stderr_lines)


# === Платформо-специфичные реализации ===

class LinuxCommandExecutor(BaseCommandExecutor):
    """Исполнитель команд для Linux/Unix систем."""

    def _create_process(self, code_block: str) -> subprocess.Popen:
        """Создает bash процесс для Linux."""
        return subprocess.Popen(
            code_block,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Текстовый режим для автоматического декодирования
        )

    def _decode_line(self, line: bytes | str) -> str:
        """Декодирует строку в Linux (простая логика)."""
        if isinstance(line, str):
            return line.rstrip('\n')
        return line.decode('utf-8', errors='replace').rstrip('\n')


class WindowsCommandExecutor(BaseCommandExecutor):
    """Исполнитель команд для Windows систем."""

    def __init__(self):
        """Инициализация с поддержкой временных файлов."""
        self._temp_file = None

    def _create_process(self, code_block: str) -> subprocess.Popen:
        """Создает cmd процесс через временный .bat файл для Windows."""
        # Предобработка кода для Windows
        code = '@echo off\n' + code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')

        # Создаем временный .bat файл
        fd, self._temp_file = tempfile.mkstemp(suffix='.bat')

        with os.fdopen(fd, 'w', encoding='cp866', errors='replace') as f:
            f.write(code)

        return subprocess.Popen(
            [self._temp_file],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # Байтовый режим для корректной работы с кодировками
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def _decode_line(self, line: bytes) -> str:
        """Декодирует строку в Windows с учетом множества кодировок."""
        if isinstance(line, str):
            return line.strip()

        # Список кодировок для Windows
        encodings = ['cp866', 'cp1251', 'utf-8', 'ascii']

        for encoding in encodings:
            try:
                return line.decode(encoding, errors='strict').strip()
            except UnicodeDecodeError:
                continue

        # Fallback с заменой ошибок
        try:
            return line.decode('utf-8', errors='replace').strip()
        except Exception:
            return line.decode('latin1', errors='replace').strip()

    def _cleanup(self, process: subprocess.Popen) -> None:
        """Удаляет временный .bat файл."""
        if self._temp_file:
            try:
                os.unlink(self._temp_file)
            except Exception:
                pass
            finally:
                self._temp_file = None


# === Фабрика ===
class CommandExecutorFactory:
    """Фабрика для создания исполнителей команд в зависимости от ОС"""

    @staticmethod
    def create_executor() -> BaseCommandExecutor:
        """
        Создает исполнитель команд в зависимости от текущей ОС

        Returns:
            BaseCommandExecutor: Соответствующий исполнитель для текущей ОС
        """
        system = platform.system().lower()
        if system == "windows":
            return WindowsCommandExecutor()
        else:
            return LinuxCommandExecutor()


def execute_and_handle_result(console: Console, code: str, demo_manager=None) -> dict:
    """
    Выполняет блок кода и обрабатывает результаты выполнения.

    Args:
        console (Console): Консоль для вывода
        code (str): Код для выполнения
        demo_manager: Optional demo manager for recording output with timing

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

        # Setup callback for recording if in demo mode
        output_callback = None
        if demo_manager and hasattr(demo_manager, 'record_command_chunk'):
            def record_chunk(chunk):
                demo_manager.record_command_chunk(chunk)
            output_callback = record_chunk

        try:
            process = executor.execute(code, output_callback=output_callback)

            # Сохраняем результаты
            result['exit_code'] = process.returncode
            result['stdout'] = process.stdout
            result['stderr'] = process.stderr
            result['success'] = process.returncode == 0

            # Выводим код завершения
            console.print(t("[dim]>>> Exit code: {code}[/dim]").format(code=process.returncode))

            # Показываем stderr если есть
            if process.stderr:
                console.print(t("[dim italic]>>> Error:[/dim italic]"))
                console.print(f"[dim italic]{process.stderr}[/dim italic]")

        except KeyboardInterrupt:
            # Перехватываем Ctrl+C во время выполнения команды
            result['interrupted'] = True
            console.print(t("[dim]>>> Command interrupted by user (Ctrl+C)[/dim]"))

    except Exception as e:
        result['stderr'] = str(e)
        console.print(t("[dim]Script execution error: {error}[/dim]").format(error=e))

    return result


def run_code_block(console: Console, code_blocks: list, idx: int, demo_manager=None) -> dict:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.

    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока
        demo_manager: Optional demo manager for recording output with timing

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
    return execute_and_handle_result(console, code, demo_manager)
