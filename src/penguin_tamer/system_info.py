#!/usr/bin/env python3
import os
import platform
import socket
import sys
import locale
from datetime import datetime
import getpass

from penguin_tamer.i18n import t


def get_system_info_text() -> str:
    """Returns system environment information as readable text.

    Возвращает информацию о рабочем окружении в виде читаемого текста
    """
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

    # Дополнительная полезная информация (быстрое извлечение)
    system_encoding = sys.getdefaultencoding()
    filesystem_encoding = sys.getfilesystemencoding()

    # Локаль системы (безопасно с fallback)
    try:
        system_locale = locale.getdefaultlocale()
        locale_str = f"{system_locale[0] or 'unknown'}, {system_locale[1] or 'unknown'}"
    except Exception:
        locale_str = 'unknown'

    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or os.environ.get('TMPDIR') or '/tmp'

    # Определяем виртуальное окружение Python
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_status = 'Yes (active)' if in_venv else 'No'
    if in_venv:
        venv_path = sys.prefix
    else:
        venv_path = 'N/A'

    cpu_count = os.cpu_count() or 'unknown'
    python_executable = sys.executable

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
- {t("Python Executable")}: {python_executable}
- {t("Virtual Environment")}: {venv_status}
- {t("Virtual Environment Path")}: {venv_path}
- {t("System Encoding")}: {system_encoding}
- {t("Filesystem Encoding")}: {filesystem_encoding}
- {t("System Locale")}: {locale_str}
- {t("Temporary Directory")}: {temp_dir}
- {t("CPU Count")}: {cpu_count}
- {t("Current Time")}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- {t("Shell")}: {shell_name}
- {t("Shell Executable")}: {shell_exec}
- {t("Shell Version")}: {shell_version}
"""
    return info_text.strip()


if __name__ == "__main__":
    print(get_system_info_text())
