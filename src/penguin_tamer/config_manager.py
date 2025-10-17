#!/usr/bin/env python3
"""
Новый менеджер конфигурации для приложения penguin-tamer.

ОСОБЕННОСТИ:
- Автоматическое создание config.yaml из default_config.yaml при первом запуске
- Удобные свойства для доступа к основным настройкам
- Полная поддержка YAML формата
- Безопасная работа с файлами конфигурации

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

# Базовое использование
from config_manager import config

# Чтение настроек
current_llm = config.current_llm
temperature = config.temperature
user_content = config.user_content

# Изменение настроек
config.temperature = 0.7
config.stream_mode = True
config.user_content = "Новый контент"

# Работа с LLM
available_llms = config.get_available_llms()
current_config = config.get_current_llm_config()

# Добавление новой LLM
config.add_llm("My LLM", "gpt-4", "https://api.example.com/v1", "api-key")

# Сброс к настройкам по умолчанию
config.reset_to_defaults()
"""

import yaml
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List
from platformdirs import user_config_dir

# Добавляем путь к модулю для прямого запуска
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from penguin_tamer.i18n import detect_system_language
from penguin_tamer.i18n_content import get_default_user_content, is_default_user_content
from penguin_tamer.utils.descriptors import ConfigProperty


class ConfigManager:
    """
    Менеджер конфигурации для управления настройками приложения.

    Автоматически создает файл конфигурации из шаблона default_config.yaml,
    если пользовательский config.yaml не существует.
    """

    def __init__(self, app_name: str = "penguin-tamer"):
        """
        Инициализация менеджера конфигурации.

        Args:
            app_name: Имя приложения для определения директории конфигурации
        """
        self.app_name = app_name
        self.user_config_dir = Path(user_config_dir(app_name))
        self.user_config_path = self.user_config_dir / "config.yaml"
        self._default_config_path = Path(__file__).parent / "default_config.yaml"

        # Создаем директорию если не существует
        self.user_config_dir.mkdir(parents=True, exist_ok=True)

        # Автоматически создаем конфигурацию из шаблона если нужно
        self._ensure_config_exists()

        # Загружаем конфигурацию
        self._config = self._load_config()

    def _ensure_config_exists(self) -> None:
        """
        Убеждается, что файл конфигурации существует.
        Если config.yaml не найден, копирует default_config.yaml с сохранением комментариев.
        """
        if not self.user_config_path.exists():
            if self._default_config_path.exists():
                try:
                    # Копируем default_config.yaml в user config
                    shutil.copy2(self._default_config_path, self.user_config_path)
                    
                    # Определяем системный язык и локализованный контент
                    sys_lang = detect_system_language(["en", "ru"]) or "en"
                    localized_content = get_default_user_content(sys_lang)
                    
                    # Читаем скопированный файл как текст для сохранения комментариев
                    with open(self.user_config_path, 'r', encoding='utf-8') as f:
                        config_text = f.read()
                    
                    # Заменяем язык (первая строка с "language:")
                    import re
                    config_text = re.sub(
                        r'^language:\s*\w+',
                        f'language: {sys_lang}',
                        config_text,
                        count=1,
                        flags=re.MULTILINE
                    )
                    
                    # Заменяем user_content (многострочное значение)
                    # Ищем строку "user_content:" и заменяем её значение
                    config_text = re.sub(
                        r'(user_content:\s*)[^\n]+',
                        f'\\1{localized_content}',
                        config_text,
                        count=1
                    )
                    
                    # Сохраняем изменённый файл с комментариями
                    with open(self.user_config_path, 'w', encoding='utf-8') as f:
                        f.write(config_text)
                        
                except Exception as e:
                    raise RuntimeError(f"Не удалось создать файл конфигурации: {e}")
            else:
                raise FileNotFoundError(f"Файл шаблона конфигурации не найден: {self._default_config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из YAML файла.

        Returns:
            Dict[str, Any]: Загруженная конфигурация
        """
        try:
            with open(self.user_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Ошибка загрузки конфигурации: {e}")
            return {}

    def _save_config(self) -> None:
        """
        Сохраняет текущую конфигурацию в YAML файл.
        """
        try:
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    self._config,
                    f,
                    indent=2,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False
                )
        except Exception as e:
            raise RuntimeError(f"Не удалось сохранить конфигурацию: {e}")

    def reload(self) -> None:
        """
        Перезагружает конфигурацию из файла.
        """
        self._config = self._load_config()

    def save(self) -> None:
        """
        Сохраняет текущую конфигурацию в файл.
        """
        self._save_config()

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Получает значение из конфигурации.

        Args:
            section: Секция конфигурации (например, 'global', 'logging')
            key: Ключ в секции (если None, возвращает всю секцию)
            default: Значение по умолчанию

        Returns:
            Значение из конфигурации или default
        """
        section_data = self._config.get(section, {})

        if key is None:
            return section_data

        return section_data.get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Устанавливает значение в конфигурации.

        Args:
            section: Секция конфигурации
            key: Ключ в секции
            value: Новое значение
        """
        if section not in self._config:
            self._config[section] = {}

        self._config[section][key] = value
        self._save_config()

    def update_section(self, section: str, data: Dict[str, Any]) -> None:
        """
        Обновляет всю секцию конфигурации.

        Args:
            section: Секция для обновления
            data: Новые данные секции
        """
        self._config[section] = data
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """
        Возвращает всю конфигурацию.

        Returns:
            Dict[str, Any]: Полная конфигурация
        """
        return self._config.copy()

    # === Удобные методы для работы с конкретными настройками (через дескрипторы) ===

    # Основные параметры генерации
    temperature = ConfigProperty("global", "temperature", 0.7, "Температура генерации ответов")
    max_tokens = ConfigProperty("global", "max_tokens", None, "Максимум токенов в ответе")
    top_p = ConfigProperty("global", "top_p", 0.95, "Nucleus sampling (top_p)")
    frequency_penalty = ConfigProperty("global", "frequency_penalty", 0.0, "Штраф за повторы")
    presence_penalty = ConfigProperty("global", "presence_penalty", 0.0, "Штраф за упоминание")
    seed = ConfigProperty("global", "seed", None, "Seed для детерминизма")

    # Top-level параметры
    language = ConfigProperty("", "language", "en", "UI язык")

    # Дополнительные параметры
    debug = ConfigProperty("global", "debug", False, "Debug mode enabled/disabled")
    theme = ConfigProperty("global", "theme", "default", "Current markdown/code theme")
    user_content = ConfigProperty("global", "user_content", "", "Пользовательский контент для всех LLM")

    @property
    def current_llm(self) -> str:
        """Текущая выбранная LLM (custom logic due to naming)."""
        return self.get("global", "current_LLM", "")

    @current_llm.setter
    def current_llm(self, value: str) -> None:
        """Устанавливает текущую LLM."""
        self.set("global", "current_LLM", value)

    def get_available_llms(self) -> List[str]:
        """
        Возвращает список доступных LLM.

        Returns:
            List[str]: Список имен LLM
        """
        supported_llms = self.get("supported_LLMs")
        if isinstance(supported_llms, dict):
            return list(supported_llms.keys())
        return []

    def get_llm_config(self, llm_name: str) -> Dict[str, Any]:
        """
        Возвращает конфигурацию конкретной LLM.

        Args:
            llm_name: Имя LLM

        Returns:
            Dict[str, Any]: Конфигурация LLM
        """
        supported_llms = self.get("supported_LLMs")
        if isinstance(supported_llms, dict):
            return supported_llms.get(llm_name, {})
        return {}

    def get_current_llm_config(self) -> Dict[str, Any]:
        """
        Возвращает конфигурацию текущей LLM.

        Returns:
            Dict[str, Any]: Конфигурация текущей LLM
        """
        return self.get_llm_config(self.current_llm)

    def get_llm_effective_config(self, llm_name: str) -> Dict[str, Any]:
        """
        Возвращает эффективную конфигурацию LLM с данными от провайдера.
        
        Args:
            llm_name: Имя LLM
        
        Returns:
            Dict с полями: provider, model, api_url, api_key, client_name
        """
        llm_config = self.get_llm_config(llm_name)
        if not llm_config:
            return {}
        
        provider_name = llm_config.get("provider", "")
        providers = self.get("supported_Providers") or {}
        provider_config = providers.get(provider_name, {})
        
        return {
            "provider": provider_name,
            "model": llm_config.get("model", ""),
            "api_url": provider_config.get("api_url", ""),
            "api_key": provider_config.get("api_key", ""),
            "client_name": provider_config.get("client_name", "openrouter")  # Дефолт для совместимости
        }

    def get_current_llm_effective_config(self) -> Dict[str, Any]:
        """
        Возвращает эффективную конфигурацию текущей LLM.
        
        Returns:
            Dict с полями: provider, model, api_url, api_key
        """
        return self.get_llm_effective_config(self.current_llm)

    def _generate_llm_id(self) -> str:
        """
        Генерирует уникальный ID для новой LLM.
        
        Returns:
            str: ID в формате "llm_N"
        """
        supported_llms = self.get("supported_LLMs") or {}
        
        # Находим максимальный номер среди существующих ID
        max_num = 0
        for llm_id in supported_llms.keys():
            if llm_id.startswith("llm_"):
                try:
                    num = int(llm_id.split("_")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue
        
        # Возвращаем следующий номер
        return f"llm_{max_num + 1}"

    def add_llm(self, provider: str, model: str) -> str:
        """
        Добавляет новую LLM с автоматически сгенерированным ID.

        Args:
            provider: Провайдер
            model: Модель LLM
            
        Returns:
            str: Сгенерированный ID новой LLM
        """
        supported_llms = self.get("supported_LLMs") or {}
        
        # Генерируем уникальный ID
        llm_id = self._generate_llm_id()

        supported_llms[llm_id] = {
            "provider": provider,
            "model": model
        }

        self.update_section("supported_LLMs", supported_llms)
        return llm_id

    def update_llm(self, llm_id: str, provider: str = None, model: str = None) -> None:
        """
        Обновляет конфигурацию LLM.

        Args:
            llm_id: ID LLM для обновления
            provider: Новый провайдер (опционально)
            model: Новая модель (опционально)
        """
        supported_llms = self.get("supported_LLMs") or {}

        if llm_id not in supported_llms:
            raise ValueError(f"LLM с ID '{llm_id}' не найдена")

        # Создаем копию текущей конфигурации
        current_config = supported_llms[llm_id].copy()

        if provider is not None:
            current_config["provider"] = provider
        if model is not None:
            current_config["model"] = model

        # Обновляем всю секцию supported_LLMs
        supported_llms[llm_id] = current_config
        self.update_section("supported_LLMs", supported_llms)

    def remove_llm(self, llm_id: str) -> None:
        """
        Удаляет LLM.

        Args:
            llm_id: ID LLM для удаления
        """
        supported_llms = self.get("supported_LLMs") or {}

        if llm_id not in supported_llms:
            raise ValueError(f"LLM с ID '{llm_id}' не найдена")

        del supported_llms[llm_id]
        self.update_section("supported_LLMs", supported_llms)

    def reset_to_defaults(self) -> None:
        """
        Сбрасывает конфигурацию к настройкам по умолчанию.
        """
        if self._default_config_path.exists():
            shutil.copy2(self._default_config_path, self.user_config_path)
            self.reload()
        else:
            raise FileNotFoundError("Файл с настройками по умолчанию не найден")

    def set_language(self, new_language: str) -> None:
        """
        Устанавливает новый язык и автоматически локализует user_content,
        если он не был изменён пользователем.

        Args:
            new_language: Новый код языка ('en', 'ru', и т.д.)
        """
        current_user_content = self.user_content

        # Проверяем, был ли user_content изменён пользователем
        # (сравниваем с дефолтным значением любого языка)
        is_default = is_default_user_content(current_user_content)

        # Обновляем язык
        self.language = new_language

        # Если user_content не был изменён пользователем, локализуем его
        if is_default:
            new_user_content = get_default_user_content(new_language)
            self.user_content = new_user_content

    @property
    def config_path(self) -> Path:
        """Путь к файлу конфигурации."""
        return self.user_config_path

    @property
    def default_config_path(self) -> Path:
        """Путь к файлу с настройками по умолчанию."""
        return self._default_config_path

    def __repr__(self) -> str:
        return f"ConfigManager(app_name='{self.app_name}', config_path='{self.user_config_path}')"


# Глобальный экземпляр для удобства использования
config = ConfigManager()


if __name__ == "__main__":
    # Пример использования
    print("=== Тестирование ConfigManager ===")

    # Показываем текущие настройки
    print(f"Текущая LLM: {config.current_llm}")
    print(f"Температура: {config.temperature}")
    print(f"Язык: {config.language}")
    print(f"Доступные LLM: {config.get_available_llms()}")

    # Показываем конфигурацию текущей LLM
    current_llm_config = config.get_current_llm_config()
    print(f"Конфигурация текущей LLM: {current_llm_config}")

    # Показываем пути
    print(f"\nПуть к конфигурации: {config.config_path}")

    print("\n✅ ConfigManager работает корректно!")
