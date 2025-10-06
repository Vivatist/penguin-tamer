#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Textual меню.
"""

import sys
sys.path.insert(0, 'src')

from penguin_tamer.config_manager import config

print("=" * 60)
print("ПРОВЕРКА КОНФИГУРАЦИИ ДЛЯ TEXTUAL МЕНЮ")
print("=" * 60)

# Проверка LLM
print("\n📋 ДОСТУПНЫЕ LLM:")
llms = config.get_available_llms()
print(f"   Количество: {len(llms)}")
for i, llm_name in enumerate(llms, 1):
    cfg = config.get_llm_config(llm_name) or {}
    current = " ← ТЕКУЩАЯ" if llm_name == config.current_llm else ""
    print(f"   {i}. {llm_name}{current}")
    print(f"      Модель: {cfg.get('model', 'N/A')}")
    print(f"      URL: {cfg.get('api_url', 'N/A')}")

# Проверка параметров
print("\n⚙️  ПАРАМЕТРЫ ГЕНЕРАЦИИ:")
print(f"   Температура: {config.temperature}")
print(f"   Max tokens: {config.max_tokens or 'неограниченно'}")
print(f"   Top P: {config.top_p}")
print(f"   Frequency penalty: {config.frequency_penalty}")
print(f"   Presence penalty: {config.presence_penalty}")
print(f"   Seed: {config.seed or 'случайный'}")

# Проверка контента
print("\n📝 ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ:")
if config.user_content:
    preview = config.user_content[:100] + "..." if len(config.user_content) > 100 else config.user_content
    print(f"   {preview}")
else:
    print("   (пусто)")

# Проверка системных настроек
print("\n🔧 СИСТЕМНЫЕ НАСТРОЙКИ:")
print(f"   Задержка стрима: {config.get('global', 'sleep_time', 0.01)} сек")
print(f"   Частота обновлений: {config.get('global', 'refresh_per_second', 10)} Гц")
print(f"   Режим отладки: {'Включен' if getattr(config, 'debug', False) else 'Выключен'}")

# Проверка языка и темы
print("\n🌐 ЯЗЫК И ТЕМА:")
print(f"   Язык: {getattr(config, 'language', 'en')}")
print(f"   Тема: {getattr(config, 'theme', 'default')}")

print("\n" + "=" * 60)
print("✅ ВСЕ ДАННЫЕ ЗАГРУЖЕНЫ УСПЕШНО")
print("=" * 60)

print("\n🚀 Запуск Textual приложения...")
print("   Нажмите Q или Ctrl+C для выхода")
print("   Используйте Tab для переключения между вкладками")
print("   Используйте стрелки для навигации по таблицам\n")

# Запуск приложения
from penguin_tamer.config_menu import ConfigMenuApp

app = ConfigMenuApp()
app.run()
