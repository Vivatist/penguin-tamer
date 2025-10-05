import subprocess
import platform
import tempfile
import os
import sys
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
        pass


# Исполнитель команд для Linux
class LinuxCommandExecutor(CommandExecutor):
    """Исполнитель команд для Linux/Unix систем"""
    
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bash-команды в Linux с выводом в реальном времени"""
        
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
        
        # # Читаем stderr построчно
        # if process.stderr:
        #     for line in process.stderr:
        #         if line:  # Проверяем, что линия не пустая
        #             try:
        #                 decoded_line = line.decode('utf-8', errors='replace').strip()
        #                 if decoded_line:  # Игнорируем пустые строки
        #                     print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)  # Выводим ошибки в реальном времени
        #                     stderr_lines.append(decoded_line)
        #             except UnicodeDecodeError:
        #                 try:
        #                     decoded_line = line.decode(sys.getdefaultencoding(), errors='replace').strip()
        #                     if decoded_line:
        #                         print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)
        #                         stderr_lines.append(decoded_line)
        #                 except:
        #                     raw_line = line.decode('latin1', errors='replace').strip()
        #                     if raw_line:
        #                         print(t("Error: {line}").format(line=raw_line), file=sys.stderr)
        #                         stderr_lines.append(raw_line)
        
        # Ждем завершения процесса с обработкой прерывания
        try:
            process.wait()
        except KeyboardInterrupt:
            # Если получили Ctrl+C, завершаем процесс и пробрасываем исключение
            try:
                process.terminate()
                process.wait(timeout=5)  # Ждем 5 секунд на корректное завершение
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            # Пробрасываем KeyboardInterrupt дальше для обработки в execute_and_handle_result
            raise
        
        # Создаем объект CompletedProcess для совместимости
        result = subprocess.CompletedProcess(
            args=code_block,
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines) if stdout_lines else '',
            stderr='\n'.join(stderr_lines) if stderr_lines else ''
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

    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл с выводом в реальном времени"""
        # Предобработка кода для Windows - отключаем echo для предотвращения дублирования команд
        code = '@echo off\n' + code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        
        
        # Создаем временный .bat файл с правильной кодировкой
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        
        try:
            with os.fdopen(fd, 'w', encoding='cp1251', errors='replace') as f:
                f.write(code)
            
            # Запускаем с кодировкой консоли Windows и выводом в реальном времени
            
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
            
            # Читаем stderr построчно (только собираем, не выводим сразу)
            if process.stderr:
                for line in process.stderr:
                    if line:  # Проверяем, что линия не пустая
                        decoded_line = self._decode_line_windows(line)
                        if decoded_line:  # Игнорируем пустые строки
                            stderr_lines.append(decoded_line)  # Только собираем ошибки для итоговой сводки
            
            # Ждем завершения процесса с обработкой прерывания
            try:
                process.wait()
            except KeyboardInterrupt:
                # Если получили Ctrl+C, завершаем процесс и пробрасываем исключение
                try:
                    process.terminate()
                    process.wait(timeout=5)  # Ждем 5 секунд на корректное завершение
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                # Пробрасываем KeyboardInterrupt дальше для обработки в execute_and_handle_result
                raise
            
            # Создаем объект CompletedProcess для совместимости
            result = subprocess.CompletedProcess(
                args=[temp_path],
                returncode=process.returncode,
                stdout='\n'.join(stdout_lines) if stdout_lines else '',
                stderr='\n'.join(stderr_lines) if stderr_lines else ''
            )
            
            return result
        except Exception as e:
            raise
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
            except Exception as e:
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


def execute_and_handle_result(console: Console, code: str) -> None:
    """
    Выполняет блок кода и обрабатывает результаты выполнения.
    
    Args:
        console (Console): Консоль для вывода
        code (str): Код для выполнения
    """
    # Получаем исполнитель для текущей ОС
    try:
        executor = CommandExecutorFactory.create_executor()
        
        # Выполняем код через соответствующий исполнитель
        console.print(t("[dim]>>> Result:[/dim]"))
        
        try:
            process = executor.execute(code)
            
            # Выводим только код завершения, поскольку вывод уже был показан в реальном времени
            exit_code = process.returncode
            console.print(t("[dim]>>> Exit code: {code}[/dim]").format(code=exit_code))
            
            # Показываем итоговую сводку только если есть stderr или особые случаи
            if process.stderr and not any("Error:" in line for line in process.stderr.split('\n')):
                console.print(t("[yellow]>>> Error:[/yellow]") + "\n" + process.stderr)
                
        except KeyboardInterrupt:
            # Перехватываем Ctrl+C во время выполнения команды
            console.print(t("[dim]>>> Command interrupted by user (Ctrl+C)[/dim]"))
            
    except Exception as e:
        console.print(t("[dim]Script execution error: {error}[/dim]").format(error=e))


def run_code_block(console: Console, code_blocks: list, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    
    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока
    """
    
    # Проверяем корректность индекса
    if not (1 <= idx <= len(code_blocks)):
        console.print(t("[yellow]Block #{idx} does not exist. Available blocks: 1 to {total}.[/yellow]").format(idx=idx, total=len(code_blocks)))
        return
    
    code = code_blocks[idx - 1]

    console.print(t("[dim]>>> Running block #{idx}:[/dim]").format(idx=idx))
    console.print(code)
    
    # Выполняем код и обрабатываем результат
    execute_and_handle_result(console, code)
