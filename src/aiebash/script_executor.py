import subprocess
import platform
import tempfile
import os
import sys
from abc import ABC, abstractmethod
from rich.console import Console

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
        logger.debug(f"Выполнение bash-команды: {code_block[:80]}...")
        
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
                try:
                    decoded_line = line.decode('utf-8', errors='replace').strip()
                    if decoded_line:  # Игнорируем пустые строки
                        print(f"Error: {decoded_line}", file=sys.stderr)  # Выводим ошибки в реальном времени
                        stderr_lines.append(decoded_line)
                except UnicodeDecodeError:
                    try:
                        decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
                        if decoded_line:
                            print(f"Error: {decoded_line}", file=sys.stderr)
                            stderr_lines.append(decoded_line)
                    except:
                        raw_line = line.decode('latin1', errors='replace').strip()
                        if raw_line:
                            print(f"Error: {raw_line}", file=sys.stderr)
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
        
        logger.debug(f"Результат выполнения: код возврата {result.returncode}, "
                    f"stdout: {len(result.stdout) if result.stdout else 0} байт, stderr: {len(result.stderr) if result.stderr else 0} байт")
        return result


# Исполнитель команд для Windows
class WindowsCommandExecutor(CommandExecutor):
    """Исполнитель команд для Windows систем"""
    
    @log_execution_time
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл с выводом в реальном времени"""
        # Предобработка кода для Windows
        code = code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        
        logger.debug(f"Подготовка Windows-команды: {code[:80]}...")
        
        # Создаем временный .bat файл
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        logger.debug(f"Создан временный файл: {temp_path}")
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
            
            # Запускаем с кодировкой консоли Windows и выводом в реальном времени
            logger.info(f"Выполнение команды из файла {temp_path}")
            
            process = subprocess.Popen(
                [temp_path],
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
                    try:
                        decoded_line = line.decode('cp1251', errors='replace').strip()
                        if decoded_line:  # Игнорируем пустые строки
                            print(decoded_line)  # Выводим в реальном времени
                            stdout_lines.append(decoded_line)
                    except UnicodeDecodeError:
                        try:
                            decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
                            if decoded_line:
                                print(decoded_line)
                                stdout_lines.append(decoded_line)
                        except:
                            raw_line = line.decode('latin1', errors='replace').strip()
                            if raw_line:
                                print(raw_line)
                                stdout_lines.append(raw_line)
            
            # Читаем stderr построчно
            if process.stderr:
                for line in process.stderr:
                    try:
                        decoded_line = line.decode('cp1251', errors='replace').strip()
                        if decoded_line:  # Игнорируем пустые строки
                            print(f"Error: {decoded_line}", file=sys.stderr)  # Выводим ошибки в реальном времени
                            stderr_lines.append(decoded_line)
                    except UnicodeDecodeError:
                        try:
                            decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
                            if decoded_line:
                                print(f"Error: {decoded_line}", file=sys.stderr)
                                stderr_lines.append(decoded_line)
                        except:
                            raw_line = line.decode('latin1', errors='replace').strip()
                            if raw_line:
                                print(f"Error: {raw_line}", file=sys.stderr)
                                stderr_lines.append(raw_line)
            
            # Ждем завершения процесса
            process.wait()
            
            # Создаем объект CompletedProcess для совместимости
            result = subprocess.CompletedProcess(
                args=[temp_path],
                returncode=process.returncode,
                stdout='\n'.join(stdout_lines) if stdout_lines else '',
                stderr='\n'.join(stderr_lines) if stderr_lines else ''
            )
            
            logger.debug(f"Результат выполнения: код возврата {result.returncode}, "
                        f"stdout: {len(result.stdout) if result.stdout else 0} байт, stderr: {len(result.stderr) if result.stderr else 0} байт")
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении Windows-команды: {e}", exc_info=True)
            raise
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
                logger.debug(f"Временный файл {temp_path} удален")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {temp_path}: {e}")


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
            logger.info("Создание исполнителя команд для Windows")
            return WindowsCommandExecutor()
        else:
            logger.info(f"Создание исполнителя команд для {system} (используется LinuxCommandExecutor)")
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
    logger.info(f"Запуск блока кода #{idx}")
    
    # Проверяем корректность индекса
    if not (1 <= idx <= len(code_blocks)):
        logger.warning(f"Некорректный индекс блока: {idx}. Доступно блоков: {len(code_blocks)}")
        console.print(f"[yellow]Блок #{idx} не существует. Доступны блоки с 1 по {len(code_blocks)}.[/yellow]")
        return
    
    code = code_blocks[idx - 1]
    logger.debug(f"Содержимое блока #{idx}: {code[:100]}...")

    console.print(f"[dim]>>> Выполняем блок #{idx}:[/dim]")
    console.print(code)
    
    # Получаем исполнитель для текущей ОС
    try:
        executor = CommandExecutorFactory.create_executor()
        
        # Выполняем код через соответствующий исполнитель
        logger.debug("Начало выполнения блока кода...")
        process = executor.execute(code)
        
        # Выводим только код завершения, поскольку вывод уже был показан в реальном времени
        exit_code = process.returncode
        logger.info(f"Блок #{idx} выполнен с кодом {exit_code}")
        console.print(f"[dim]>>> Код завершения: {exit_code}[/dim]")
        
        # Показываем итоговую сводку только если есть stderr или особые случаи
        if process.stderr and not any("Error:" in line for line in process.stderr.split('\n')):
            logger.debug(f"Дополнительный stderr ({len(process.stderr)} символов)")
            console.print(f"[yellow]>>>Error:[/yellow]\n{process.stderr}")
    except Exception as e:
        logger.error(f"Ошибка выполнения блока #{idx}: {e}", exc_info=True)
        console.print(f"[dim]Ошибка выполнения скрипта: {e}[/dim]")
