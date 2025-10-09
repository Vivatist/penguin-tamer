#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Единая точка запуска всех тестов.

Использование:
    python run_tests.py           # Все тесты
    python run_tests.py --fast    # Только быстрые
    python run_tests.py --cov     # С покрытием кода
"""

import subprocess
import sys
import argparse
import io


# Настройка вывода для Windows
if sys.platform == 'win32':
    # Принудительная UTF-8 для stdout
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def run_pytest(args_list):
    """Запускает pytest с указанными аргументами"""
    cmd = [sys.executable, '-m', 'pytest', 'tests/'] + args_list
    # Используем простой ASCII вместо Unicode символов
    print(f"Running: {' '.join(cmd)}\n", flush=True)
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(description='Запуск тестов')
    parser.add_argument('--fast', action='store_true', help='Только быстрые тесты')
    parser.add_argument('--cov', action='store_true', help='С покрытием кода')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')

    args = parser.parse_args()

    pytest_args = []

    if args.fast:
        pytest_args.extend(['-m', 'fast'])

    if args.cov:
        pytest_args.extend([
            '--cov=src/penguin_tamer',
            '--cov-report=term',
            '--cov-report=html'
        ])

    if args.verbose:
        pytest_args.append('-vv')
    else:
        pytest_args.append('-v')

    return run_pytest(pytest_args)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTesting interrupted")
        sys.exit(130)
