#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического ребрендинга проекта ai-ebash
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List

class ProjectRebranding:
    """Класс для автоматического ребрендинга проекта"""
    
    def __init__(self, old_name: str, new_name: str, old_cmd: str, new_cmd: str):
        self.old_name = old_name  # ai-ebash
        self.new_name = new_name  # penguin-tamer
        self.old_package = old_name.replace('-', '_')  # ai_ebash
        self.new_package = new_name.replace('-', '_')  # penguin_tamer
        self.old_module = 'penguin_tamer'  # старый модуль
        self.new_module = 'penguin_tamer'  # новый модуль penguin_tamer
        self.old_cmd = old_cmd  # ai
        self.new_cmd = new_cmd  # pt
        
    def get_files_to_update(self) -> List[Path]:
        """Получает список файлов для обновления"""
        files = []
        
        # Python файлы
        for py_file in Path('.').rglob('*.py'):
            if 'venv' not in str(py_file) and '__pycache__' not in str(py_file):
                files.append(py_file)
        
        # Конфигурационные файлы
        config_files = [
            'pyproject.toml',
            'setup.cfg', 
            'setup.py',
            'README.md',
            'MANIFEST.in',
            '.github/workflows/*.yml',
            '.github/workflows/*.yaml', 
            'debian/control',
            'debian/changelog',
        ]
        
        for pattern in config_files:
            files.extend(Path('.').glob(pattern))
            
        # JSON файлы локализации
        for json_file in Path('.').rglob('*.json'):
            if 'locales' in str(json_file):
                files.append(json_file)
                
        return files
    
    def update_file_content(self, file_path: Path) -> bool:
        """Обновляет содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Замены в зависимости от типа файла
            if file_path.suffix == '.py':
                content = self._update_python_file(content)
            elif file_path.name == 'pyproject.toml':
                content = self._update_pyproject(content)
            elif file_path.name == 'setup.cfg':
                content = self._update_setup_cfg(content)
            elif file_path.name == 'README.md':
                content = self._update_readme(content)
            elif file_path.suffix in ['.yml', '.yaml']:
                content = self._update_github_actions(content)
            elif 'debian' in str(file_path):
                content = self._update_debian_files(content)
            else:
                content = self._update_generic_file(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"Ошибка обновления {file_path}: {e}")
            
        return False
    
    def _update_python_file(self, content: str) -> str:
        """Обновляет Python файлы"""
        # Импорты
        content = re.sub(r'\bfrom penguin_tamer\b', f'from {self.new_module}', content)
        content = re.sub(r'\bimport penguin_tamer\b', f'import {self.new_module}', content)
        
        # Пути к пакетам
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
    
    def _update_pyproject(self, content: str) -> str:
        """Обновляет pyproject.toml"""
        content = re.sub(r'name = "ai-ebash"', f'name = "{self.new_name}"', content)
        content = re.sub(r'ai = "penguin_tamer.__main__:main"', f'{self.new_cmd} = "{self.new_module}.__main__:main"', content)
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
    
    def _update_setup_cfg(self, content: str) -> str:
        """Обновляет setup.cfg"""
        content = re.sub(r'name = ai-ebash', f'name = {self.new_name}', content)
        content = re.sub(r'ai = penguin_tamer.__main__:main', f'{self.new_cmd} = {self.new_module}.__main__:main', content)
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
        
    def _update_readme(self, content: str) -> str:
        """Обновляет README.md"""
        content = re.sub(r'\bai-ebash\b', self.new_name, content, flags=re.IGNORECASE)
        content = re.sub(r'\baiebash\b', self.new_module, content, flags=re.IGNORECASE)
        content = re.sub(r'`ai `', f'`{self.new_cmd} `', content)
        content = re.sub(r'`ai\b', f'`{self.new_cmd}', content)
        
        # Обновляем описания
        content = re.sub(r'Console utility for integrating artificial intelligence into a Linux terminal', 
                        'Penguin Tamer - AI-powered terminal assistant for Linux systems', content)
        content = re.sub(r'AI-eBash', 'Penguin Tamer', content)
        
        return content
        
    def _update_github_actions(self, content: str) -> str:
        """Обновляет GitHub Actions"""
        content = re.sub(r'\bai-ebash\b', self.new_name, content)
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
        
    def _update_debian_files(self, content: str) -> str:
        """Обновляет Debian файлы"""
        content = re.sub(r'\bai-ebash\b', self.new_name, content)
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
        
    def _update_generic_file(self, content: str) -> str:
        """Обновляет остальные файлы"""
        content = re.sub(r'\bai-ebash\b', self.new_name, content)
        content = re.sub(r'\baiebash\b', self.new_module, content)
        
        return content
    
    def rename_directories(self) -> bool:
        """Переименовывает директории"""
        src_old = Path('src/penguin_tamer')
        src_new = Path(f'src/{self.new_module}')
        
        if src_old.exists():
            try:
                shutil.move(str(src_old), str(src_new))
                print(f"✅ Переименована папка: {src_old} → {src_new}")
                return True
            except Exception as e:
                print(f"❌ Ошибка переименования папки: {e}")
                return False
        return True
    
    def run_rebranding(self) -> None:
        """Запускает полный ребрендинг"""
        print(f"🚀 Начинаем ребрендинг: {self.old_name} → {self.new_name}")
        print(f"📦 Пакет: {self.old_module} → {self.new_module}")  
        print(f"⚡ Команда: {self.old_cmd} → {self.new_cmd}")
        print()
        
        # Получаем файлы для обновления
        files = self.get_files_to_update()
        print(f"📄 Найдено файлов для обновления: {len(files)}")
        
        # Обновляем содержимое файлов
        updated_count = 0
        for file_path in files:
            if self.update_file_content(file_path):
                print(f"✅ Обновлен: {file_path}")
                updated_count += 1
            
        print(f"\n📝 Обновлено файлов: {updated_count}")
        
        # Переименовываем директории
        print("\n📁 Переименование директорий...")
        self.rename_directories()
        
        print(f"\n🎉 Ребрендинг завершен!")
        print("\n📋 Следующие шаги:")
        print("1. Проверьте изменения в git")
        print("2. Протестируйте сборку пакета") 
        print("3. Создайте новый репозиторий на GitHub")
        print("4. Опубликуйте на PyPI под новым названием")


def main():
    """Основная функция для запуска ребрендинга"""
    print("� Скрипт ребрендинга проекта ai-ebash → Penguin Tamer")
    print("=" * 60)
    
    # Заданные параметры для Penguin Tamer
    OLD_NAME = "ai-ebash"
    NEW_NAME = "penguin-tamer"
    OLD_CMD = "ai"
    NEW_CMD = "pt"
    
    print(f"🎯 Коммерческое название: Penguin Tamer")
    print(f"📦 PyPI пакет: {NEW_NAME}")
    print(f"🐍 Python модуль: penguin_tamer")
    print(f"⚡ Команда: {NEW_CMD}")
    print(f"🐙 GitHub repo: {NEW_NAME}")
    
    print(f"\n🚀 Запускаем автоматический ребрендинг {OLD_NAME} → {NEW_NAME}...")
    
    # Создаем резервную копию
    backup_dir = f"backup_{OLD_NAME}"
    if not Path(backup_dir).exists():
        try:
            shutil.copytree('.', backup_dir, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'venv', '.venv'))
            print(f"💾 Создана резервная копия в: {backup_dir}")
        except Exception as e:
            print(f"⚠️ Не удалось создать резервную копию: {e}")
    
    # Запускаем ребрендинг
    rebrander = ProjectRebranding(OLD_NAME, NEW_NAME, OLD_CMD, NEW_CMD)
    rebrander.run_rebranding()


if __name__ == "__main__":
    main()