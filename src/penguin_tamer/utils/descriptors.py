"""Дескрипторы для упрощения работы с конфигурацией.

Этот модуль предоставляет дескрипторы для автоматического создания
property в классах конфигурации, устраняя необходимость в boilerplate коде.
"""

from typing import Any, Optional


class ConfigProperty:
    """Дескриптор для автоматического создания property конфигурации.

    Автоматически генерирует getter и setter для параметров конфигурации,
    избавляя от необходимости писать повторяющийся код @property/@setter.

    Example:
        >>> class ConfigManager:
        ...     temperature = ConfigProperty("global", "temperature", 0.8, "Температура генерации")
        ...     max_tokens = ConfigProperty("global", "max_tokens", None, "Максимум токенов")
        ...
        >>> config = ConfigManager()
        >>> temp = config.temperature  # Вызывает get("global", "temperature", 0.8)
        >>> config.temperature = 0.9   # Вызывает set("global", "temperature", 0.9)
    """

    def __init__(
        self,
        section: str,
        key: str,
        default: Any = None,
        doc: Optional[str] = None
    ):
        """Инициализация дескриптора конфигурации.

        Args:
            section: Секция конфигурации (например, 'global', 'logging')
                    Пустая строка "" означает top-level ключ
            key: Ключ в секции (или top-level ключ если section пустая)
            default: Значение по умолчанию
            doc: Описание параметра для документации
        """
        self.section = section
        self.key = key
        self.default = default
        # Генерируем документацию
        if doc:
            self.__doc__ = doc
        elif section:
            self.__doc__ = f"Configuration property: {section}.{key}"
        else:
            self.__doc__ = f"Configuration property: {key}"
        self.name = None  # Будет установлено в __set_name__

    def __set_name__(self, owner, name):
        """Магический метод Python 3.6+ для получения имени атрибута.

        Вызывается автоматически при создании класса.
        """
        self.name = name

    def __get__(self, obj, objtype=None):
        """Getter для property.

        Args:
            obj: Экземпляр класса (ConfigManager)
            objtype: Тип класса

        Returns:
            Значение из конфигурации или дескриптор сам по себе при доступе через класс
        """
        if obj is None:
            # Доступ через класс, а не через экземпляр
            return self

        # Top-level ключ (language, и т.д.)
        if not self.section:
            try:
                return obj._config.get(self.key, self.default)
            except Exception:
                return self.default

        # Обычный ключ в секции
        return obj.get(self.section, self.key, self.default)

    def __set__(self, obj, value):
        """Setter для property.

        Args:
            obj: Экземпляр класса (ConfigManager)
            value: Новое значение для установки
        """
        # Top-level ключ
        if not self.section:
            try:
                obj._config[self.key] = value
                obj._save_config()
            except Exception:
                pass
            return

        # Обычный ключ в секции
        obj.set(self.section, self.key, value)

    def __repr__(self):
        """Представление дескриптора для отладки."""
        return (
            f"ConfigProperty(section={self.section!r}, key={self.key!r}, "
            f"default={self.default!r})"
        )
