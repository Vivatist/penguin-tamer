#!/usr/bin/env python3
"""
Тестовый скрипт для проверки настраиваемых размеров чанков в демо-системе.
"""

import yaml
from pathlib import Path

# Проверяем конфигурацию демо
config_path = Path("src/penguin_tamer/demo_system/config_demo.yaml")

if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    playback = config.get('playback', {})
    chunk_min = playback.get('chunk_size_min')
    chunk_max = playback.get('chunk_size_max')
    
    print("✅ Конфигурация демо загружена успешно!")
    print(f"   Минимальный размер чанка: {chunk_min}")
    print(f"   Максимальный размер чанка: {chunk_max}")
    
    # Проверяем валидность значений
    if chunk_min and chunk_max and chunk_min > 0 and chunk_max >= chunk_min:
        print("✅ Параметры валидны!")
        
        # Показываем, как будет выглядеть диапазон
        chunk_range = list(range(chunk_min, chunk_max + 1))
        print(f"   Диапазон размеров чанков: {chunk_range}")
    else:
        print("❌ Ошибка: Некорректные значения параметров!")
else:
    print("❌ Файл конфигурации не найден!")
