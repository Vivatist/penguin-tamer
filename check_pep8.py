#!/usr/bin/env python3
"""
Простая проверка соответствия PEP8 для основных файлов проекта
"""
import ast
import os
from pathlib import Path


def check_pep8_compliance(file_path):
    """Проверяет базовые правила PEP8 для Python файла"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Ошибка чтения файла: {e}"]
    
    # Проверка длины строк (PEP8: max 79 символов)
    for i, line in enumerate(lines, 1):
        if len(line.rstrip()) > 79:
            issues.append(f"Строка {i}: превышена длина ({len(line.rstrip())} символов): {line.strip()[:50]}...")
    
    # Проверка пустых строк в конце
    content = ''.join(lines)
    if content.endswith('\n\n\n'):
        issues.append("Слишком много пустых строк в конце файла")
    
    # Проверка синтаксиса
    try:
        ast.parse(content)
    except SyntaxError as e:
        issues.append(f"Синтаксическая ошибка: {e}")
    
    return issues


def main():
    """Проверяет все Python файлы в проекте"""
    src_dir = Path(__file__).parent / "src" / "aiebash"
    python_files = list(src_dir.glob("*.py"))
    
    total_issues = 0
    
    print("Проверка соответствия PEP8...")
    print("=" * 50)
    
    for py_file in python_files:
        if py_file.name.startswith('__'):
            continue
            
        issues = check_pep8_compliance(py_file)
        
        if issues:
            print(f"\nERR {py_file.name}:")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
        else:
            print(f"OK  {py_file.name}")
    
    print("\n" + "=" * 50)
    if total_issues == 0:
        print("Все файлы соответствуют базовым правилам PEP8!")
    else:
        print(f"Найдено проблем: {total_issues}")
    
    return total_issues


if __name__ == "__main__":
    exit(main())