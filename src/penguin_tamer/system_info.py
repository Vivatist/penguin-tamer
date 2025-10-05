#!/usr/bin/env python3
import os
import platform
import socket
from datetime import datetime
import getpass

from penguin_tamer.i18n import t

def get_system_info_text() -> str:
    """Returns system environment information as readable text / Возвращает информацию о рабочем окружении в виде читаемого текста"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = t("failed to retrieve") + f" ({e})"

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
{t("System Information")}:
- {t("Operating System")}: {platform.system()} {platform.release()} ({platform.version()})
- {t("Architecture")}: {platform.machine()}
- {t("User")}: {getpass.getuser()}
- {t("Home Directory")}: {os.path.expanduser("~")}
- {t("Current Directory")}: {os.getcwd()}
- {t("Hostname")}: {hostname}
- {t("Local IP Address")}: {local_ip}
- {t("Python Version")}: {platform.python_version()}
- {t("Current Time")}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- {t("Shell")}: {shell_name}
- {t("Shell Executable")}: {shell_exec}
- {t("Shell Version")}: {shell_version}
"""
    return info_text.strip()

if __name__ == "__main__":
    print(get_system_info_text())
