import subprocess
import platform
import tempfile
import os
import sys
from abc import ABC, abstractmethod
from rich.console import Console
from aiebash.i18n import t

from aiebash.logger import logger, log_execution_time


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
        pass


# Исполнитель команд для Linux
class LinuxCommandExecutor(CommandExecutor):
    """Исполнитель команд для Linux/Unix систем"""
    
    @log_execution_time
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bash-команды в Linux с выводом в реальном времени"""
        logger.debug(f"Executing bash command: {code_block[:80]}...")
        
        # Используем Popen для вывода в реальном времени
        process = subprocess.Popen(
            code_block,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # Используем байты для корректной работы
        )
        
        # Читаем вывод в реальном времени
        stdout_lines = []
        stderr_lines = []
        
        # Читаем stdout построчно
        if process.stdout:
            for line in process.stdout:
                if line:  # Проверяем, что линия не пустая
                    try:
                        decoded_line = line.decode('utf-8', errors='replace').strip()
                        if decoded_line:  # Игнорируем пустые строки
                            print(decoded_line)  # Выводим в реальном времени
                            stdout_lines.append(decoded_line)
                    except UnicodeDecodeError:
                        # Если UTF-8 не работает, пробуем системную кодировку
                        try:
                            decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
                            if decoded_line:
                                print(decoded_line)
                                stdout_lines.append(decoded_line)
                        except:
                            # В крайнем случае выводим как есть
                            raw_line = line.decode('latin1', errors='replace').strip()
                            if raw_line:
                                print(raw_line)
                                stdout_lines.append(raw_line)
        
        # Читаем stderr построчно
        if process.stderr:
            for line in process.stderr:
                if line:  # Проверяем, что линия не пустая
                    try:
                        decoded_line = line.decode('utf-8', errors='replace').strip()
                        if decoded_line:  # Игнорируем пустые строки
                            print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)  # Выводим ошибки в реальном времени
                            stderr_lines.append(decoded_line)
                    except UnicodeDecodeError:
                        try:
                            decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
                            if decoded_line:
                                print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)
                                stderr_lines.append(decoded_line)
                        except:
                            raw_line = line.decode('latin1', errors='replace').strip()
                            if raw_line:
                                print(t("Error: {line}").format(line=raw_line), file=sys.stderr)
                                stderr_lines.append(raw_line)
        
        # Ждем завершения процесса
        process.wait()
        
        # Создаем объект CompletedProcess для совместимости
        result = subprocess.CompletedProcess(
            args=code_block,
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines) if stdout_lines else '',
            stderr='\n'.join(stderr_lines) if stderr_lines else ''
        )
        
        logger.debug(
            t("Execution result: return code {code}, stdout: {stdout} bytes, stderr: {stderr} bytes").format(
                code=result.returncode,
                stdout=(len(result.stdout) if result.stdout else 0),
                stderr=(len(result.stderr) if result.stderr else 0),
            )
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
        except:
            return line_bytes.decode('latin1', errors='replace').strip()

    @log_execution_time
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл с выводом в реальном времени"""
        # Предобработка кода для Windows
        code = code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        
        logger.debug(f"Preparing Windows command: {code[:80]}...")
        
        # Создаем временный .bat файл с правильной кодировкой
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        logger.debug(f"Created temporary file: {temp_path}")
        
        try:
            with os.fdopen(fd, 'w', encoding='cp1251', errors='replace') as f:
                f.write(code)
            
            # Запускаем с кодировкой консоли Windows и выводом в реальном времени
            logger.info(f"Executing command from file {temp_path}")
            
            process = subprocess.Popen(
                [temp_path],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Используем байты для корректной работы
                creationflags=subprocess.CREATE_NO_WINDOW  # Предотвращаем создание окна консоли
            )
            
            # Читаем вывод в реальном времени
            stdout_lines = []
            stderr_lines = []
            
            # Читаем stdout построчно
            if process.stdout:
                for line in process.stdout:
                    if line:  # Проверяем, что линия не пустая
                        decoded_line = self._decode_line_windows(line)
                        if decoded_line:  # Игнорируем пустые строки
                            print(decoded_line)  # Выводим в реальном времени
                            stdout_lines.append(decoded_line)
            
            # Читаем stderr построчно
            if process.stderr:
                for line in process.stderr:
                    if line:  # Проверяем, что линия не пустая
                        decoded_line = self._decode_line_windows(line)
                        if decoded_line:  # Игнорируем пустые строки
                            print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)  # Выводим ошибки в реальном времени
                            stderr_lines.append(decoded_line)
            
            # Ждем завершения процесса
            process.wait()
            
            # Создаем объект CompletedProcess для совместимости
            result = subprocess.CompletedProcess(
                args=[temp_path],
                returncode=process.returncode,
                stdout='\n'.join(stdout_lines) if stdout_lines else '',
                stderr='\n'.join(stderr_lines) if stderr_lines else ''
            )
            
            logger.debug(
                t("Execution result: return code {code}, stdout: {stdout} bytes, stderr: {stderr} bytes").format(
                    code=result.returncode,
                    stdout=(len(result.stdout) if result.stdout else 0),
                    stderr=(len(result.stderr) if result.stderr else 0),
                )
            )
            return result
        except Exception as e:
            logger.error(f"Error executing Windows command: {e}", exc_info=True)
            raise
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
                logger.debug(f"Temporary file {temp_path} deleted")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {e}")


# Фабрика для создания исполнителей команд
class CommandExecutorFactory:
    """Фабрика для создания исполнителей команд в зависимости от ОС"""
    
    @staticmethod
    @log_execution_time
    def create_executor() -> CommandExecutor:
        """
        Создает исполнитель команд в зависимости от текущей ОС
        
        Returns:
            CommandExecutor: Соответствующий исполнитель для текущей ОС
        """
        system = platform.system().lower()
        if system == "windows":
            logger.info("Creating command executor for Windows")
            return WindowsCommandExecutor()
        else:
            logger.info(f"Creating command executor for {system} (using LinuxCommandExecutor)")
            return LinuxCommandExecutor()


@log_execution_time
def run_code_block(console: Console, code_blocks: list, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    
    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока
    """
    logger.info(f"Starting code block #{idx}")
    
    # Проверяем корректность индекса
    if not (1 <= idx <= len(code_blocks)):
        logger.warning(f"Invalid block index: {idx}. Total blocks: {len(code_blocks)}")
        console.print(t("[yellow]Block #{idx} does not exist. Available blocks: 1 to {total}.[/yellow]").format(idx=idx, total=len(code_blocks)))
        return
    
    code = code_blocks[idx - 1]
    logger.debug(f"Block #{idx} content: {code[:100]}...")

    console.print(t("[dim]>>> Running block #{idx}:[/dim]").format(idx=idx))
    console.print(code)
    
    # Получаем исполнитель для текущей ОС
    try:
        executor = CommandExecutorFactory.create_executor()
        
        # Выполняем код через соответствующий исполнитель
        logger.debug("Starting code block execution...")
        console.print(t("[dim]>>> Result:[/dim]").format(idx=idx))
        process = executor.execute(code)
        
        # Выводим только код завершения, поскольку вывод уже был показан в реальном времени
        exit_code = process.returncode
        logger.info(f"Block #{idx} finished with exit code {exit_code}")
        console.print(t("[dim]>>> Exit code: {code}[/dim]").format(code=exit_code))
        
        # Показываем итоговую сводку только если есть stderr или особые случаи
        if process.stderr and not any("Error:" in line for line in process.stderr.split('\n')):
            logger.debug(f"Additional stderr ({len(process.stderr)} chars)")
            console.print(t("[yellow]>>> Error:[/yellow]") + "\n" + process.stderr)
    except Exception as e:
        logger.error(f"Execution error in block #{idx}: {e}", exc_info=True)
        console.print(t("[dim]Script execution error: {error}[/dim]").format(error=e))
