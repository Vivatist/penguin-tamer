#!/usr/bin/env python3
"""
Интеграционные тесты для автоматической локализации user_content в ConfigManager.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from penguin_tamer.config_manager import ConfigManager
from penguin_tamer.i18n_content import DEFAULT_USER_CONTENT


class TestConfigLanguageSwitch:
    """Тесты переключения языка с автоматической локализацией user_content."""

    @pytest.fixture
    def temp_config_dir(self):
        """Создаёт временную директорию для конфига."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def config_manager(self, temp_config_dir, monkeypatch):
        """Создаёт ConfigManager с временной директорией."""
        # Копируем default_config.yaml во временную директорию
        default_config_path = Path(__file__).parent.parent / "src" / "penguin_tamer" / "default_config.yaml"
        temp_default_config = temp_config_dir / "default_config.yaml"

        if default_config_path.exists():
            shutil.copy2(default_config_path, temp_default_config)

        # Патчим путь к дефолтному конфигу
        def mock_init(self, app_name="penguin-tamer"):
            self.app_name = app_name
            self.user_config_dir = temp_config_dir
            self.user_config_path = self.user_config_dir / "config.yaml"
            self._default_config_path = temp_default_config
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            self._ensure_config_exists()
            self._config = self._load_config()

        monkeypatch.setattr(ConfigManager, "__init__", mock_init)
        return ConfigManager()

    def test_default_language_creates_localized_content(self, config_manager):
        """При создании конфига user_content должен быть на системном языке."""
        # При инициализации устанавливается язык системы
        current_lang = config_manager.language
        user_content = config_manager.user_content

        # Проверяем что content соответствует языку
        expected_content = DEFAULT_USER_CONTENT.get(current_lang, DEFAULT_USER_CONTENT["en"])
        assert user_content.strip() == expected_content.strip()

    def test_switch_language_updates_default_content(self, config_manager):
        """При смене языка дефолтный user_content должен обновляться."""
        # Устанавливаем английский
        config_manager.set_language("en")
        assert config_manager.user_content.strip() == DEFAULT_USER_CONTENT["en"].strip()

        # Переключаемся на русский
        config_manager.set_language("ru")
        assert config_manager.user_content.strip() == DEFAULT_USER_CONTENT["ru"].strip()

        # Обратно на английский
        config_manager.set_language("en")
        assert config_manager.user_content.strip() == DEFAULT_USER_CONTENT["en"].strip()

    def test_switch_language_preserves_custom_content(self, config_manager):
        """При смене языка кастомный user_content должен сохраняться."""
        custom_content = "My custom system message that I don't want to lose"

        # Устанавливаем кастомный контент
        config_manager.user_content = custom_content

        # Переключаем язык
        config_manager.set_language("ru")

        # Контент должен остаться тем же
        assert config_manager.user_content == custom_content

        # И при обратном переключении тоже
        config_manager.set_language("en")
        assert config_manager.user_content == custom_content

    def test_partial_modification_preserves_content(self, config_manager):
        """Даже небольшое изменение должно защитить контент от автоперевода."""
        # Берём дефолтный английский и добавляем текст
        modified_content = DEFAULT_USER_CONTENT["en"] + "\nP.S. Be extra helpful!"
        config_manager.user_content = modified_content

        # Переключаем язык
        config_manager.set_language("ru")

        # Изменённый контент должен сохраниться
        assert config_manager.user_content == modified_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
