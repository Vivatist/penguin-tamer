#!/usr/bin/env python3
import os
import platform
import socket
from datetime import datetime
import getpass
import os
import subprocess

def get_system_info_text() -> str:
    """Возвращает информацию о рабочем окружении в виде читаемого текста"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = f"не удалось получить ({e})"

    # Определяем shell
    shell_exec = os.environ.get('SHELL') or os.environ.get('COMSPEC') or os.environ.get('TERMINAL') or ''
    shell_name = os.path.basename(shell_exec) if shell_exec else 'unknown'
    shell_version = 'unknown'
    if shell_exec:
        # Попробуем получить версию через --version, иначе специфичные команды
        try:
            out = subprocess.check_output([shell_exec, '--version'], stderr=subprocess.STDOUT, encoding='utf-8', timeout=2)
            shell_version = out.strip().splitlines()[0]
        except Exception:
            # powershell/pwsh variant
            try:
                if 'powershell' in shell_name.lower() or 'pwsh' in shell_name.lower():
                    out = subprocess.check_output([shell_exec, '-Command', '$PSVersionTable.PSVersion.ToString()'], stderr=subprocess.STDOUT, encoding='utf-8', timeout=2)
                    shell_version = out.strip().splitlines()[0]
            except Exception:
                shell_version = 'unknown'

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
