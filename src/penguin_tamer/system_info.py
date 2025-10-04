#!/usr/bin/env python3
import os
import platform
import socket
from datetime import datetime
import getpass

def get_system_info_text() -> str:
    """Возвращает информацию о рабочем окружении в виде читаемого текста"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = f"не удалось получить ({e})"

    # Определяем shell без медленных вызовов subprocess
    shell_exec = os.environ.get('SHELL') or os.environ.get('COMSPEC') or os.environ.get('TERMINAL') or ''
    shell_name = os.path.basename(shell_exec) if shell_exec else 'unknown'
    
    # Быстрое определение версии shell без subprocess вызовов
    shell_version = 'unknown'
    if shell_exec and os.path.exists(shell_exec):
        # Определяем версию только по известным паттернам, без вызова процесса
        if 'cmd.exe' in shell_exec.lower():
            shell_version = 'Windows Command Line'
        elif 'powershell.exe' in shell_exec.lower():
            shell_version = 'Windows PowerShell'
        elif 'pwsh' in shell_exec.lower():
            shell_version = 'PowerShell Core'
        elif 'bash' in shell_exec.lower():
            shell_version = 'Bash shell'
        elif 'zsh' in shell_exec.lower():
            shell_version = 'Z shell'
        # Для остальных случаев оставляем 'unknown' чтобы не тратить время на subprocess

    info_text = f"""
Сведения о системе:
- Операционная система: {platform.system()} {platform.release()} ({platform.version()})
- Архитектура: {platform.machine()}
- Пользователь: {getpass.getuser()}
- Домашняя папка: {os.path.expanduser("~")}
- Текущий каталог: {os.getcwd()}
- Имя хоста: {hostname}
- Локальный IP-адрес: {local_ip}
- Версия Python: {platform.python_version()}
- Текущее время: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Shell: {shell_name}
- Shell executable: {shell_exec}
- Shell version: {shell_version}
"""
    return info_text.strip()

if __name__ == "__main__":
    print(get_system_info_text())
