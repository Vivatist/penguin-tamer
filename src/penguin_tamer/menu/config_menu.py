#!/usr/bin/env python3
"""
Textual-based configuration menu for Penguin Tamer.
Provides a modern TUI interface with tabs, tables, and live status updates.
"""

import re
import sys
import time
from pathlib import Path

# Add src directory to path for direct execution
if __name__ == "__main__":
    # Файл находится в src/penguin_tamer/menu/config_menu.py
    # Нужно подняться на 3 уровня до src/
    src_path = Path(__file__).parent.parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Markdown,
    Select,
    Static,
    Switch,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.reactive import reactive
from textual.message import Message

from penguin_tamer.config_manager import config
from penguin_tamer.i18n import translator
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.arguments import __version__


class DoubleClickDataTable(DataTable):
    """DataTable with double-click support."""
    
    class DoubleClicked(Message):
        """Message sent when table is double-clicked."""
        def __init__(self, row: int) -> None:
            self.row = row
            super().__init__()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_click_time = 0
        self._last_clicked_row = -1
        self._double_click_threshold = 0.5
    
    def on_click(self, event) -> None:
        """Handle click to detect double-click."""
        current_time = time.time()
        current_row = self.cursor_row
        
        # Check for double-click
        if (current_row == self._last_clicked_row and 
            current_time - self._last_click_time < self._double_click_threshold):
            # Double-click detected!
            if current_row >= 0:
                self.post_message(self.DoubleClicked(current_row))
            # Reset
            self._last_click_time = 0
            self._last_clicked_row = -1
        else:
            # First click
            self._last_click_time = current_time
            self._last_clicked_row = current_row


class ResponsiveButtonRow(Container):
    """Container that adapts button layout based on available width."""
    
    def __init__(self, buttons_data: list, **kwargs):
        super().__init__(**kwargs)
        self.buttons_data = buttons_data  # List of (text, id, variant)
        self._current_layout = 4  # How many buttons fit in first row
    
    def compose(self) -> ComposeResult:
        """Create layout with all buttons in one row aligned to the right."""
        with Horizontal(classes="adaptive-button-row"):
            for text, btn_id, variant in self.buttons_data:
                yield Button(text, id=btn_id, variant=variant)
    
    def on_resize(self, event) -> None:
        """Handle container resize to adapt layout."""
        container_width = self.size.width
        
        # Calculate how many buttons fit: each button ~19 chars (17 content + 2 margins)
        button_width = 19
        buttons_per_row = max(1, container_width // button_width)
        buttons_per_row = min(buttons_per_row, len(self.buttons_data))
        
        # Only rebuild if layout changed
        if buttons_per_row != self._current_layout:
            self._current_layout = buttons_per_row
            self._rebuild_layout()
    
    def _rebuild_layout(self):
        """Rebuild button layout based on how many buttons fit per row."""
        # Remove all children first
        try:
            for child in list(self.children):
                child.remove()
        except Exception:
            pass
        
        buttons_per_row = self._current_layout
        total_buttons = len(self.buttons_data)
        
        # Create rows dynamically
        current_index = 0
        while current_index < total_buttons:
            # Create a new row with spacing between rows
            row_classes = "adaptive-button-row"
            
            row = Horizontal(classes=row_classes)
            self.mount(row)
            
            # Calculate how many buttons in this row
            end_index = min(current_index + buttons_per_row, total_buttons)
            
            # Add buttons to this row
            for text, btn_id, variant in self.buttons_data[current_index:end_index]:
                row.mount(Button(text, id=btn_id, variant=variant))
            
            current_index = end_index


class ConfirmDialog(ModalScreen):
    """Modal dialog for confirmation prompts."""

    def __init__(self, message: str, title: str = "Подтверждение", **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.title_text = title
        self.result = False

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="dialog-title"),
            Static(self.message, classes="dialog-message"),
            Horizontal(
                Button("Да", variant="success", id="yes-btn"),
                Button("Нет", variant="success", id="no-btn"),
                classes="dialog-buttons",
            ),
            classes="dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.result = True
        self.dismiss(self.result)


class InputDialog(ModalScreen):
    """Modal dialog for text input with validation."""

    def __init__(
        self,
        prompt: str,
        title: str = "Ввод",
        default: str = "",
        validator=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.prompt = prompt
        self.title_text = title
        self.default = default
        self.validator = validator
        self.result = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="input-dialog-title"),
            Static(self.prompt, classes="input-dialog-prompt"),
            Input(value=self.default, id="input-field"),
            Horizontal(
                Button("OK", variant="success", id="ok-btn"),
                Button("Отмена", variant="success", id="cancel-btn"),
                classes="input-dialog-buttons",
            ),
            classes="input-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            input_field = self.query_one("#input-field", Input)
            value = input_field.value
            if self.validator and not self.validator(value):
                self.notify("Неверный формат ввода", severity="error")
                return
            self.result = value
        self.dismiss(self.result)


class LLMEditDialog(ModalScreen):
    """Modal dialog for adding or editing LLM with all fields in one screen."""

    def __init__(
        self,
        title: str = "Добавление LLM",
        name: str = "",
        model: str = "",
        api_url: str = "",
        api_key: str = "",
        name_editable: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title_text = title
        self.default_name = name
        self.default_model = model
        self.default_api_url = api_url
        self.default_api_key = api_key
        self.name_editable = name_editable
        self.result = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title_text, classes="llm-dialog-title"),
            Container(
                Static("Название LLM:", classes="llm-field-label"),
                Input(
                    value=self.default_name, 
                    id="llm-name-input",
                    disabled=not self.name_editable,
                    placeholder="Любое, например: GPT-4, Claude, Gemini"
                ),
                Static("Модель:", classes="llm-field-label"),
                Input(
                    value=self.default_model, 
                    id="llm-model-input",
                    placeholder="Например: gpt-4-turbo-preview"
                ),
                Static("API URL:", classes="llm-field-label"),
                Input(
                    value=self.default_api_url, 
                    id="llm-url-input",
                    placeholder="Например: https://api.openai.com/v1"
                ),
                Static("API ключ (необязательно):", classes="llm-field-label"),
                Input(
                    value="",  # Оставляем пустым при редактировании
                    id="llm-key-input",
                    placeholder=f"Текущий: {format_api_key_display(self.default_api_key)}" if self.default_api_key else "Оставьте пустым, если не требуется"
                ),
                classes="llm-fields-container"
            ),
            Horizontal(
                Button("Сохранить", variant="success", id="save-btn"),
                Button("Отмена", variant="success", id="cancel-btn"),
                classes="llm-dialog-buttons",
            ),
            classes="llm-dialog-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            name_input = self.query_one("#llm-name-input", Input)
            model_input = self.query_one("#llm-model-input", Input)
            url_input = self.query_one("#llm-url-input", Input)
            key_input = self.query_one("#llm-key-input", Input)
            
            name = name_input.value.strip()
            model = model_input.value.strip()
            api_url = url_input.value.strip()
            api_key = key_input.value.strip()
            
            # Validation
            if not name:
                self.notify("Название LLM обязательно", severity="error")
                name_input.focus()
                return
            if not model:
                self.notify("Модель обязательна", severity="error")
                model_input.focus()
                return
            if not api_url:
                self.notify("API URL обязателен", severity="error")
                url_input.focus()
                return
            
            self.result = {
                "name": name,
                "model": model,
                "api_url": api_url,
                "api_key": api_key
            }
        self.dismiss(self.result)


class ConfirmDialog(ModalScreen):
    """Диалог подтверждения действия."""
    
    def __init__(self, message: str, title: str = "Подтверждение") -> None:
        super().__init__()
        self.message = message
        self.title = title
        self.result = False
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, classes="input-dialog-title"),
            Static(self.message, classes="input-dialog-prompt"),
            Horizontal(
                Button("Да", variant="error", id="confirm-yes-btn"),
                Button("Отмена", variant="success", id="confirm-no-btn"),
                classes="input-dialog-buttons",
            ),
            classes="input-dialog-container",
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes-btn":
            self.result = True
        self.dismiss(self.result)


class InfoPanel(VerticalScroll):
    """Information panel showing detailed help for current tab and widgets with Markdown support."""
    
    content_text = reactive("")

    def compose(self) -> ComposeResult:
        """Create markdown viewer."""
        yield Markdown(id="info-markdown")

    def on_mount(self) -> None:
        """Panel mounted - will show help when first tab is activated."""
        pass
    
    def watch_content_text(self, new_text: str) -> None:
        """Update display when content changes."""
        try:
            md_widget = self.query_one("#info-markdown", Markdown)
            # Convert Rich markup to Markdown
            markdown_text = self._rich_to_markdown(new_text)
            md_widget.update(markdown_text)
        except Exception:
            pass
    
    def _rich_to_markdown(self, rich_text: str) -> str:
        """Convert Rich markup to Markdown."""
        # Replace Rich bold cyan headers with Markdown headers
        text = rich_text.replace("[bold cyan]", "## ").replace("[/bold cyan]", "")
        # Replace Rich bold with Markdown bold
        text = text.replace("[bold]", "**").replace("[/bold]", "**")
        # Replace Rich dim with Markdown italic
        text = text.replace("[dim]", "*").replace("[/dim]", "*")
        # Remove other Rich tags
        text = re.sub(r'\[/?[^\]]+\]', '', text)
        return text

    def show_tab_help(self, tab_id: str) -> None:
        """Show general help for a tab."""
        tab_help = {
            "tab-general": """# ОБЩИЕ НАСТРОЙКИ

Основная информация о системе и управление языковыми моделями.

---

## Системная информация

**Версия ПО** — текущая установленная версия Penguin Tamer

**Папка конфига** — расположение файла `config.yaml` с настройками:
- Windows: `%USERPROFILE%\\.config\\penguin-tamer\\penguin-tamer\\`
- Linux/Mac: `~/.config/penguin-tamer/penguin-tamer/`

**Папка бинарника** — директория с исполняемым файлом Python

**Language** — текущий язык меню и сообщений. *Изменение требует перезапуска приложения.*

---

## Управление LLM

Управление языковыми моделями для генерации текста.

### Текущая LLM
Модель, которая будет использоваться для всех запросов через команду `pt`.

### Доступные операции

- **Выбрать** — установить выбранную модель как текущую
- **Добавить** — добавить новую LLM с параметрами подключения
- **Изменить** — изменить параметры существующей модели
- **Удалить** — удалить модель из списка

### Параметры LLM

| Параметр | Описание | Пример |
|----------|----------|--------|
| **Название** | Уникальное имя модели | `GPT-4`, `Claude` |
| **Модель** | Идентификатор модели | `gpt-4`, `claude-3-opus` |
| **API URL** | Адрес эндпоинта API | `https://api.openai.com/v1` |
| **API ключ** | Ключ доступа к API | `sk-...` |

> 💡 **Совет:** Для быстрого переключения дважды кликните на нужную модель в таблице.""",

            "tab-params": """# ПАРАМЕТРЫ ГЕНЕРАЦИИ

Настройка поведения языковой модели при генерации текста.

---

## Temperature (Температура)

**Диапазон:** 0.0 - 2.0 | **По умолчанию:** 0.8

Контролирует креативность и случайность ответов:

- **0.0-0.3** — Детерминированные, точные ответы  
  *Идеально для:* технических задач, извлечения данных

- **0.4-0.7** — Сбалансированные ответы  
  *Идеально для:* общего использования, Q&A

- **0.8-1.5** — Креативные, разнообразные ответы  
  *Идеально для:* brainstorming, генерация идей

- **1.6-2.0** — Очень креативные (может быть непредсказуемо)

---

## Max Tokens (Максимум токенов)

**Диапазон:** 1 - ∞ | **По умолчанию:** без ограничений

Ограничивает длину ответа модели:

- **100 токенов** ≈ 75 слов ≈ 1-2 параграфа
- **500 токенов** ≈ 375 слов ≈ 1 страница
- **2000 токенов** ≈ 1500 слов ≈ 3-4 страницы

*Оставьте пустым для неограниченной длины ответа.*

---

## Top P (Nucleus Sampling)

**Диапазон:** 0.0 - 1.0 | **По умолчанию:** 0.95

Альтернативный способ контроля случайности. Модель выбирает из топ-N% наиболее вероятных токенов.

> 💡 **Совет:** Меняйте **либо** `temperature` **либо** `top_p`, но не оба одновременно.

---

## Frequency Penalty (Штраф за частоту)

**Диапазон:** -2.0 до 2.0 | **По умолчанию:** 0.0

Уменьшает вероятность повторения одних и тех же токенов:

- **0.3-0.5** — Лёгкое уменьшение повторов *(рекомендуется)*
- **1.0-2.0** — Сильное избегание повторов

---

## Presence Penalty (Штраф за присутствие)

**Диапазон:** -2.0 до 2.0 | **По умолчанию:** 0.0

Увеличивает вероятность обсуждения новых тем. Наказывает за сам факт упоминания токена (в отличие от frequency_penalty, который наказывает за частоту).

---

## Seed (Детерминизм)

**Тип:** целое число или пусто | **По умолчанию:** случайно

Обеспечивает воспроизводимость результатов. Одинаковый seed с теми же параметрами даст идентичный ответ.

*Используйте для:* тестирования, отладки промптов, демонстраций

---

## Рекомендации

Начните с **defaults** и постепенно настраивайте

Меняйте **один параметр за раз** для понимания влияния

Используйте **debug mode** для анализа запросов

> Подробнее: [LLM_PARAMETERS_GUIDE.md](docs/LLM_PARAMETERS_GUIDE.md)""",

            "tab-content": """# ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ

Дополнительный контекст, автоматически добавляемый ко всем запросам.

---

## Назначение

Используйте это поле для **системных промптов** и **инструкций**, которые должны автоматически применяться к каждому вашему запросу к LLM.

Это позволяет:
- Задать роль и стиль общения ассистента
- Определить формат ответов
- Добавить специфический контекст для ваших задач

---

## Примеры использования

### Роль ассистента
```
Ты - опытный программист Python. 
Всегда давай подробные объяснения с примерами кода.
```

### Формат ответов
```
Отвечай кратко и по делу. 
Используй маркированные списки и заголовки.
```

### Стиль общения
```
Общайся дружелюбно и неформально, 
используй примеры из жизни для объяснения сложных концепций.
```

### Специализация
```
Ты специализируешься на веб-разработке 
с фокусом на React и TypeScript.
```

---

## Рекомендации

**Будьте конкретны** — чёткие инструкции дают лучшие результаты

**Тестируйте** — проверьте, как модель реагирует на ваш промпт

**Итерируйте** — улучшайте промпт на основе результатов

> 💡 **Совет:** Хороший системный промпт может значительно улучшить качество и релевантность ответов модели.""",

            "tab-system": """# СИСТЕМНЫЕ НАСТРОЙКИ

Настройки производительности и поведения приложения.

---

## Задержка стрима (0.001-0.1 сек)

Пауза между порциями текста при потоковой генерации.

| Значение | Режим | Описание |
|----------|-------|----------|
| **0.001-0.01** | Быстрый | Мгновенное отображение |
| **0.02-0.05** | Оптимальный | Рекомендуется |
| **0.06-0.1** | Медленный | Легче читать в реальном времени |

---

## Частота обновлений (1-60 Гц)

Скорость обновления интерфейса.

| Частота | Нагрузка | Описание |
|---------|----------|----------|
| **1-10 Гц** | Низкая | Меньше нагрузка на CPU |
| **10-30 Гц** | Средняя | Рекомендуется |
| **30-60 Гц** | Высокая | Очень плавно, больше нагрузка |

---

## Режим отладки

Включает подробное логирование для диагностики:

- Информация о запросах к API
- Логирование всех параметров
- Отображение токенов и времени выполнения
- Детали ошибок и предупреждения

**Когда использовать:**
- Диагностика проблем с подключением
- Проверка параметров запросов
- Оптимизация производительности
- Отладка промптов

---

## Рекомендации

**Стандартные значения** (подходят для большинства случаев):
- Задержка стрима: `0.01`
- Частота обновлений: `10`
- Режим отладки: `ВЫКЛ`

> 💡 **Совет:** Включите debug mode, если испытываете проблемы с ответами LLM.""",

            "tab-appearance": """# НАСТРОЙКИ ИНТЕРФЕЙСА

Внешний вид и визуальное оформление приложения.

---

## Цветовая схема

Выбор темы оформления терминала:

### Доступные темы

| Тема | Описание | Особенности |
|------|----------|-------------|
| **Классический** | Стандартная тема Textual | Нейтральная, универсальная |
| **Monokai** | Тёмная с контрастом | Яркие акценты на тёмном фоне |
| **Dracula** | Популярная тёмная | Мягкие фиолетовые тона |
| **Nord** | Холодные северные | Приглушённые синие оттенки |

---

## Применение изменений

**Изменение темы требует перезапуска приложения**

После выбора темы:
1. Закройте меню настроек (`Q` или `Ctrl+C`)
2. Перезапустите: `pt --settings`
3. Тема будет применена

---

## Примечание

**Language** (English/Русский) находится в разделе **Общие**.

> 💡 **Совет:** Выберите тему, комфортную для ваших глаз при длительной работе. Тёмные темы (Monokai, Dracula, Nord) меньше утомляют зрение.""",
        }
        
        content = tab_help.get(tab_id, f"[bold red]Информация для вкладки {tab_id} не найдена[/bold red]")
        self.content_text = content

    def show_help(self, widget_id: str) -> None:
        """Show detailed help for specific widget."""
        help_texts = {
            "temp-input": """[bold cyan]ТЕМПЕРАТУРА[/bold cyan]

Контролирует креативность и случайность ответов.

[bold]Диапазон:[/bold] 0.0 - 2.0

[bold]Низкие значения (0.0-0.5):[/bold]
• Более предсказуемые ответы
• Подходит для технических задач
• Факты и точность

[bold]Средние значения (0.6-1.0):[/bold]
• Баланс креативности и точности
• Подходит для большинства задач

[bold]Высокие значения (1.1-2.0):[/bold]
• Очень креативные ответы
• Подходит для творческих задач
• Может быть менее точным""",
            "max-tokens-input": """[bold cyan]МАКСИМУМ ТОКЕНОВ[/bold cyan]

Ограничивает длину генерируемого ответа.

[bold]Значения:[/bold]
• Пусто или 0 = без ограничений
• Число > 0 = максимальное количество токенов

[bold]Примерно:[/bold]
• 100 токенов ≈ 75 слов
• 500 токенов ≈ 375 слов
• 1000 токенов ≈ 750 слов

[bold]Рекомендации:[/bold]
• Короткие ответы: 100-300
• Средние ответы: 500-1000
• Длинные ответы: 1500-3000""",
            "top-p-input": """[bold cyan]TOP P (Nucleus Sampling)[/bold cyan]

Контролирует разнообразие выбора слов.

[bold]Диапазон:[/bold] 0.0 - 1.0

[bold]Как работает:[/bold]
Модель выбирает из топ N% наиболее вероятных токенов.

[bold]Низкие значения (0.1-0.5):[/bold]
• Более консервативный выбор
• Предсказуемые ответы

[bold]Средние значения (0.6-0.9):[/bold]
• Баланс разнообразия
• Рекомендуется для большинства задач

[bold]Высокие значения (0.95-1.0):[/bold]
• Максимальное разнообразие
• Более неожиданные ответы""",
            "freq-penalty-input": """[bold cyan]ШТРАФ ЧАСТОТЫ[/bold cyan]

Снижает повторение одних и тех же слов.

[bold]Диапазон:[/bold] -2.0 до 2.0

[bold]Отрицательные значения:[/bold]
• Поощряет повторения
• Редко используется

[bold]Нулевое значение (0.0):[/bold]
• Без штрафов
• По умолчанию

[bold]Положительные значения:[/bold]
• 0.1-0.5: легкое снижение повторов
• 0.6-1.0: заметное снижение
• 1.1-2.0: сильное снижение (может быть неестественным)""",
            "presence-penalty-input": """[bold cyan]ШТРАФ ПРИСУТСТВИЯ[/bold cyan]

Поощряет обсуждение новых тем.

[bold]Диапазон:[/bold] -2.0 до 2.0

[bold]Отрицательные значения:[/bold]
• Фокус на текущей теме
• Глубокое обсуждение

[bold]Нулевое значение (0.0):[/bold]
• Естественное поведение
• По умолчанию

[bold]Положительные значения:[/bold]
• 0.1-0.5: легкое разнообразие тем
• 0.6-1.0: заметное разнообразие
• 1.1-2.0: максимальное разнообразие (может терять фокус)""",
            "seed-input": """[bold cyan]SEED (Зерно генерации)[/bold cyan]

Обеспечивает воспроизводимость результатов.

[bold]Значения:[/bold]
• Пусто или 0 = случайная генерация
• Любое число = фиксированный seed

[bold]Применение:[/bold]
• Тестирование: один и тот же seed даст одинаковые результаты
• Отладка: воспроизведение проблем
• Эксперименты: сравнение разных параметров

[bold]Примечание:[/bold]
Одинаковый seed с одинаковыми параметрами даст идентичный ответ.""",
            "stream-delay-input": """[bold cyan]ЗАДЕРЖКА СТРИМА[/bold cyan]

Пауза между порциями текста при потоковой генерации.

[bold]Диапазон:[/bold] 0.001 - 0.1 секунд

[bold]Малые значения (0.001-0.01):[/bold]
• Быстрое отображение
• Может мерцать

[bold]Средние значения (0.02-0.05):[/bold]
• Комфортная скорость
• Рекомендуется

[bold]Большие значения (0.06-0.1):[/bold]
• Медленное отображение
• Легче читать в реальном времени""",
            "refresh-rate-input": """[bold cyan]ЧАСТОТА ОБНОВЛЕНИЙ[/bold cyan]

Скорость обновления интерфейса.

[bold]Диапазон:[/bold] 1-60 Гц (обновлений в секунду)

[bold]Низкие значения (1-10):[/bold]
• Меньше нагрузка на систему
• Может быть менее плавным

[bold]Средние значения (10-30):[/bold]
• Оптимальный баланс
• Рекомендуется (10 по умолчанию)

[bold]Высокие значения (30-60):[/bold]
• Очень плавный интерфейс
• Больше нагрузка на CPU""",
            "debug-switch": """[bold cyan]РЕЖИМ ОТЛАДКИ[/bold cyan]

Включает подробное логирование.

[bold]Выключен (OFF):[/bold]
• Обычный режим работы
• Только важные сообщения
• Рекомендуется для повседневного использования

[bold]Включен (ON):[/bold]
• Подробная информация о запросах
• Логирование параметров
• Отображение токенов и времени выполнения
• Полезно для диагностики проблем

[bold]Применение:[/bold]
• Разработка и тестирование
• Поиск проблем с API
• Анализ производительности""",
            "language-select": """[bold cyan]ЯЗЫК ИНТЕРФЕЙСА[/bold cyan]

Выбор языка меню и сообщений.

[bold]Доступные языки:[/bold]
• English (en)
• Русский (ru)

[bold]Что изменится:[/bold]
• Язык меню
• Системные сообщения
• Подсказки и описания

[bold]Примечание:[/bold]
Язык общения с LLM зависит от вашего промпта, а не от этой настройки.""",
            "theme-select": """[bold cyan]ТЕМА ОФОРМЛЕНИЯ[/bold cyan]

Выбор цветовой схемы интерфейса.

[bold]Доступные темы:[/bold]
• Классический (default) - стандартная тема
• Monokai - тёмная с контрастными акцентами
• Dracula - популярная тёмная тема
• Nord - холодные северные тона

[bold]Выбор темы влияет на:[/bold]
• Цвета интерфейса
• Контрастность текста
• Общее восприятие

[bold]Рекомендация:[/bold]
Выберите тему, которая комфортна для ваших глаз.""",
        }
        content = help_texts.get(widget_id, f"[bold yellow]Подсказка для {widget_id} не найдена[/bold yellow]")
        self.content_text = content


class ConfigMenuApp(App):
    """Main Textual configuration application."""
    
    # Flag to prevent notifications during initialization
    _initialized = False

    CSS = """
    Screen {
        layout: horizontal;
    }

    #left-panel {
        width: 65%;
        border: solid #1e2a30;
        padding: 1;
    }

    #right-panel {
        width: 35%;
        border: solid #1e2a30;
        padding: 1;
        margin-left: 1;
    }

    TabPane {
        padding: 0;
    }

    .tab-header {
        padding: 0 0 1 0;
        margin-bottom: 1;
    }

    .system-info-panel {
        width: 100%;
        padding: 1 2;
        margin-bottom: 2;
        background: $panel;
        border: solid $primary;
    }

    .section-header {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    .setting-group {
        margin-bottom: 1;
        padding: 0;
    }


    .setting-row {
        height: 3;
        align: left middle;
        margin-bottom: 1;
        margin-top: 1;
    }

    .setting-spacer {
        height: 1;
    }

    .flexible-spacer {
        height: 1fr;
    }

    #reset-settings-btn {
        dock: left;
    }

    .param-label {
        width: 40%;
        color: $text;
        text-style: bold;
        padding-right: 2;
    }

    .param-control {
        width: 60%;
    }

    .param-description {
        margin-bottom: 0;
        color: $text-muted;
        text-style: italic;
    }

    .param-current {
        margin-bottom: 0;
        color: $success;
        text-style: bold;
    }

    .current-llm-panel {
        height: 3;
        width: 100%;
        background: $success;
        color: $text;
        text-style: bold;
        content-align: center middle;
        margin-bottom: 1;
    }

    DataTable {
        height: auto;
        max-height: 15;
        margin-bottom: 0;
        border: solid $primary;
    }

.button-row {
    margin-bottom: 0;
    margin-top: 0;
    min-height: 3;
    height: auto;
    align: right top;
}

.reset-button-row {
    height: auto;
    align: left top;
    margin-top: 2;
    margin-bottom: 0;
}

.adaptive-button-row {
    height: auto;
    align: right top;
    margin-bottom: 1;
}

.adaptive-button-row Button {
    margin-right: 1;
    min-width: 16;
}

    TextArea {
        height: 12;
        margin-bottom: 1;
    }

    Input {
        width: 1fr;
        text-align: right;
    }

    .param-control Input {
        width: 100%;
        margin: 0;
        text-align: right;
    }

    .param-control Switch {
        width: auto;
    }
    
    Switch {
        width: auto;
    }

    .param-control Select {
        width: 100%;
        margin: 0;
        text-align: right;
    }

    .setting-button {
        min-width: 12;
    }

    /* Dialog styles */
    .dialog-container {
        width: 60;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    .dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .dialog-message {
        width: 100%;
        margin-bottom: 2;
        text-align: center;
    }

    .dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    .dialog-buttons Button {
        margin: 0 2;
        min-width: 10;
    }

    .input-dialog-container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    ConfirmDialog {
        align: center middle;
    }

    .input-dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .input-dialog-prompt {
        width: 100%;
        margin-bottom: 1;
    }

    .input-dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    .input-dialog-buttons Button {
        margin: 0 2;
        min-width: 10;
    }

    /* LLM Edit Dialog */
    .llm-dialog-container {
        width: 80;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    LLMEditDialog {
        align-horizontal: center;
        align-vertical: middle;
    }

    .llm-dialog-title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .llm-fields-container {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    .llm-field-label {
        width: 100%;
        margin-top: 1;
        margin-bottom: 0;
        color: $text;
    }

    .llm-fields-container Input {
        width: 100%;
        margin-bottom: 1;
    }

    .llm-fields-container Input > .input--placeholder {
        color: $text 30%;
        text-style: italic;
    }

    .llm-dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    .llm-dialog-buttons Button {
        margin: 0 2;
        min-width: 15;
    }

    /* Button color overrides */
    Button.-primary {
        background: #e07333;
        color: white;
        border: tall #e07333;
    }

    Button.-primary:hover {
        background: #c86529;
        border: tall #c86529;
    }

    Button.-success {
        background: #007c6e;
        color: white;
        border: tall #007c6e;
    }

    Button.-success:hover {
        background: #006558;
        border: tall #006558;
    }

    Button.-warning {
        background: #ffd8b9;
        color: #1e2a30;
        border: tall #ffd8b9;
    }

    Button.-warning:hover {
        background: #ffc89f;
        border: tall #ffc89f;
    }

    Button.-error {
        background: #ff5555;
        color: white;
        border: tall #ff5555;
    }

    Button.-error:hover {
        background: #ff3333;
        border: tall #ff3333;
    }

    Button.-default {
        background: #1e2a30;
        color: #e07333;
        border: tall #e07333;
    }

    Button.-default:hover {
        background: #2a3640;
        border: tall #e07333;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Выход", priority=True),
        Binding("ctrl+c", "quit", "Выход"),
        Binding("f1", "help", "Помощь"),
        Binding("ctrl+r", "refresh_status", "Обновить"),
    ]

    TITLE = "Penguin Tamer - Конфигурация"
    SUB_TITLE = "Управление настройками ИИ"

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        with Horizontal():
            # Left panel with tabs
            with Vertical(id="left-panel"):
                with TabbedContent():
                    # Tab 1: General Settings (Общие)
                    with TabPane("Общие", id="tab-general"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ОБЩИЕ НАСТРОЙКИ[/bold]\n"
                                "[dim]Системная информация и управление LLM[/dim]",
                                classes="tab-header",
                            )
                            
                            # System Info
                            config_dir = Path(config.config_path).parent if hasattr(config, 'config_path') else Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
                            bin_path = Path(sys.executable).parent
                            current_llm = config.current_llm or "Не выбрана"
                            
                            yield Static(
                                f"[bold]Версия ПО:[/bold] {__version__}\n"
                                f"[bold]Папка конфига:[/bold] {config_dir}\n"
                                f"[bold]Папка бинарника:[/bold] {bin_path}\n\n"
                                f"[bold]Текущая LLM:[/bold] [green]{current_llm}[/green]",
                                classes="system-info-panel",
                                id="system-info-display"
                            )
                            
                            # Language setting
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Language\n[dim]Перезапуск после изменения[/dim]",
                                    classes="param-label"
                                )
                                current_lang_val = getattr(config, "language", "en")
                                yield Select(
                                    [("English", "en"), ("Русский", "ru")],
                                    value=current_lang_val,
                                    id="language-select",
                                    allow_blank=False,
                                    classes="param-control"
                                )
                            
                            yield Static("")
                            yield Static(
                                "[bold]Добавленные нейросети[/bold]\n"
                                "[dim]Выберите какую нейросеть использовать, или добавьте свою[/dim]"
                            )
                            llm_dt = DoubleClickDataTable(id="llm-table", show_header=True, cursor_type="row")
                            yield llm_dt
                            yield Static("")
                            yield ResponsiveButtonRow(
                                buttons_data=[
                                    ("Выбрать", "select-llm-btn", "success"),
                                    ("Добавить", "add-llm-btn", "success"),
                                    ("Изменить", "edit-llm-btn", "success"),
                                    ("Удалить", "delete-llm-btn", "error"),
                                ],
                                classes="button-row"
                            )

                    # Tab 2: User Content
                    with TabPane("Контент", id="tab-content"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ПОЛЬЗОВАТЕЛЬСКИЙ КОНТЕНТ[/bold]\n"
                                "[dim]Дополнительный контекст для всех запросов[/dim]",
                                classes="tab-header",
                            )
                            yield TextArea(text=config.user_content, id="content-textarea")
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "Сохранить",
                                    id="save-content-btn",
                                    variant="success",
                                )

                    # Tab 3: Generation Parameters
                    with TabPane("Генерация", id="tab-params"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]ПАРАМЕТРЫ ГЕНЕРАЦИИ[/bold]\n"
                                "[dim]Настройка поведения ИИ (нажмите Enter для сохранения)[/dim]",
                                classes="tab-header",
                            )

                            # Temperature
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Температура\n[dim]Креативность (0.0-2.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.temperature), 
                                    id="temp-input",
                                    placeholder="0.0-2.0",
                                    classes="param-control"
                                )

                            # Max Tokens
                            max_tokens_str = (
                                str(config.max_tokens)
                                if config.max_tokens
                                else "неограниченно"
                            )
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Максимум токенов\n[dim]Длина ответа[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=max_tokens_str, 
                                    id="max-tokens-input",
                                    placeholder="число или 'null'",
                                    classes="param-control"
                                )

                            # Top P
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Top P\n[dim]Nucleus sampling (0.0-1.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.top_p), 
                                    id="top-p-input",
                                    placeholder="0.0-1.0",
                                    classes="param-control"
                                )

                            # Frequency Penalty
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Штраф частоты\n[dim]Снижает повторения (-2.0 до 2.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.frequency_penalty),
                                    id="freq-penalty-input",
                                    placeholder="-2.0 до 2.0",
                                    classes="param-control"
                                )

                            # Presence Penalty
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Штраф присутствия\n[dim]Разнообразие тем (-2.0 до 2.0)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(config.presence_penalty),
                                    id="pres-penalty-input",
                                    placeholder="-2.0 до 2.0",
                                    classes="param-control"
                                )

                            # Seed
                            seed_str = str(config.seed) if config.seed else "случайный"
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Seed\n[dim]Для воспроизводимости[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=seed_str, 
                                    id="seed-input",
                                    placeholder="число или 'null'",
                                    classes="param-control"
                                )

                    # Tab 4: System Settings

                    with TabPane("Система", id="tab-system"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]СИСТЕМНЫЕ НАСТРОЙКИ[/bold]\n"
                                "[dim]Поведение приложения (нажмите Enter для сохранения)[/dim]",
                                classes="tab-header",
                            )

                            # Stream Delay
                            stream_delay = config.get("global", "sleep_time", 0.01)
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Задержка стрима\n[dim]Пауза между частями (0.001-0.1)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(stream_delay), 
                                    id="stream-delay-input",
                                    placeholder="0.001-0.1",
                                    classes="param-control"
                                )

                            # Refresh Rate
                            refresh_rate = config.get("global", "refresh_per_second", 10)
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Частота обновлений\n[dim]Обновление интерфейса (1-60 Гц)[/dim]",
                                    classes="param-label"
                                )
                                yield Input(
                                    value=str(refresh_rate), 
                                    id="refresh-rate-input",
                                    placeholder="1-60",
                                    classes="param-control"
                                )

                            # Debug Mode
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Режим отладки\n[dim]Подробная информация о запросах[/dim]",
                                    classes="param-label"
                                )
                                with Container(classes="param-control"):
                                    yield Switch(
                                        value=getattr(config, "debug", False),
                                        id="debug-switch"
                                    )
                            
                            # Reset Settings Button
                            yield Static("")
                            with Horizontal(classes="button-row"):
                                yield Button(
                                    "Сброс настроек",
                                    id="reset-settings-btn",
                                    variant="error",
                                )
                            
                            # Flexible spacer AFTER button to fill remaining space
                            yield Static("", classes="flexible-spacer")

                    # Tab 5: Interface

                    with TabPane("Интерфейс", id="tab-appearance"):
                        with VerticalScroll():
                            yield Static(
                                "[bold]НАСТРОЙКИ ИНТЕРФЕЙСА[/bold]\n"
                                "[dim]Внешний вид приложения (изменения сохраняются автоматически)[/dim]",
                                classes="tab-header",
                            )

                            # Theme
                            current_theme = getattr(config, "theme", "default")
                            with Horizontal(classes="setting-row"):
                                yield Static(
                                    "Цветовая схема\n[dim]Перезапуск после изменения[/dim]",
                                    classes="param-label"
                                )
                                yield Select(
                                    [
                                        ("Классический", "default"),
                                        ("Monokai", "monokai"),
                                        ("Dracula", "dracula"),
                                        ("Nord", "nord"),
                                    ],
                                    value=current_theme,
                                    id="theme-select",
                                    allow_blank=False,
                                    classes="param-control"
                                )

            # Right panel with info
            with Vertical(id="right-panel"):
                with VerticalScroll():
                    yield InfoPanel(id="info-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app."""
        self._initialized = False
        self.update_llm_tables()
        # Set flag after initialization to enable notifications and tab switching
        def finish_init():
            self._initialized = True
            # Show help for first tab
            panel = self.query_one("#info-panel", InfoPanel)
            panel.show_tab_help("tab-general")
        
        self.set_timer(0.2, finish_init)
    
    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab change to update info panel."""
        # Ensure we're initialized
        if not getattr(self, '_initialized', False):
            return
            
        try:
            panel = self.query_one("#info-panel", InfoPanel)
            # Extract actual tab ID from the event
            raw_id = event.tab.id
            
            # Format is "--content-tab-tab-system", we need "tab-system"
            # Remove "--content-" prefix first
            if raw_id and raw_id.startswith("--content-"):
                tab_id = raw_id[len("--content-"):]
                # If it has duplicate "tab-tab-", fix it
                if tab_id.startswith("tab-tab-"):
                    tab_id = tab_id[4:]  # Remove one "tab-"
            else:
                tab_id = raw_id
            
            panel.show_tab_help(tab_id)
        except Exception as e:
            self.notify(f"Ошибка: {e}", severity="error")
    
    def on_focus(self, event) -> None:
        """Show help when any widget gets focus."""
        widget = event.widget
        widget_id = getattr(widget, 'id', None)
        
        if widget_id and isinstance(widget, (Input, Select, Switch)):
            panel = self.query_one(InfoPanel)
            panel.show_help(widget_id)
    
    def on_blur(self, event) -> None:
        """Restore config when widget loses focus."""
        widget = event.widget
        
        if isinstance(widget, (Input, Select, Switch)):
            # Get current tab and show its help
            tabs = self.query_one(TabbedContent)
            current_tab = tabs.active
            panel = self.query_one(InfoPanel)
            panel.show_tab_help(current_tab)
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch state changes."""
        if event.switch.id == "debug-switch":
            config.debug = event.value
            config.save()
            self.refresh_status()
            status = "включен" if event.value else "выключен"
            self.notify(f"Режим отладки {status}", severity="information")
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        # Skip notifications during initialization
        if not self._initialized:
            return
            
        select_id = event.select.id
        
        if select_id == "language-select" and event.value != Select.BLANK:
            self.set_language(str(event.value))
        elif select_id == "theme-select" and event.value != Select.BLANK:
            self.set_theme(str(event.value))

    def update_llm_tables(self, keep_cursor_position: bool = False) -> None:
        """Update LLM table with current data.
        
        Args:
            keep_cursor_position: If True, try to keep cursor on the same row
        """
        current = config.current_llm
        llms = config.get_available_llms()

        # Update unified LLM table
        llm_table = self.query_one("#llm-table", DataTable)
        
        # Save cursor position
        old_cursor_row = llm_table.cursor_row if keep_cursor_position else -1
        old_llm_name = None
        if old_cursor_row >= 0:
            try:
                row = llm_table.get_row_at(old_cursor_row)
                old_llm_name = str(row[1])  # Название LLM
            except:
                pass
        
        llm_table.clear(columns=True)
        llm_table.add_columns("", "Название", "Модель", "API URL")
        
        new_cursor_row = 0
        for idx, llm_name in enumerate(llms):
            cfg = config.get_llm_config(llm_name) or {}
            is_current = "✓" if llm_name == current else ""
            llm_table.add_row(
                is_current,
                llm_name,
                cfg.get("model", "N/A"),
                cfg.get("api_url", "N/A"),
            )
            # Запоминаем новую позицию для старой LLM
            if old_llm_name and llm_name == old_llm_name:
                new_cursor_row = idx
        
        # Восстанавливаем позицию курсора и highlight
        if keep_cursor_position and old_llm_name and len(llms) > 0:
            try:
                # Устанавливаем cursor_coordinate для правильного highlight
                llm_table.cursor_coordinate = (new_cursor_row, 0)
            except:
                try:
                    # Альтернативный способ
                    llm_table.move_cursor(row=new_cursor_row, animate=False)
                except:
                    pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input fields."""
        input_id = event.input.id
        
        # Parameters
        if input_id == "temp-input":
            self.set_temperature()
        elif input_id == "max-tokens-input":
            self.set_max_tokens()
        elif input_id == "top-p-input":
            self.set_top_p()
        elif input_id == "freq-penalty-input":
            self.set_frequency_penalty()
        elif input_id == "pres-penalty-input":
            self.set_presence_penalty()
        elif input_id == "seed-input":
            self.set_seed()
        # System
        elif input_id == "stream-delay-input":
            self.set_stream_delay()
        elif input_id == "refresh-rate-input":
            self.set_refresh_rate()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id

        # Reset Settings
        if btn_id == "reset-settings-btn":
            self.action_reset_settings()

        # LLM Management
        elif btn_id == "select-llm-btn":
            self.select_current_llm()

        # LLM Management
        elif btn_id == "add-llm-btn":
            self.add_llm()
        elif btn_id == "edit-llm-btn":
            self.edit_llm()
        elif btn_id == "delete-llm-btn":
            self.delete_llm()

        # User Content
        elif btn_id == "save-content-btn":
            self.save_user_content()
    
    def on_double_click_data_table_double_clicked(self, event: DoubleClickDataTable.DoubleClicked) -> None:
        """Handle double-click on DataTable."""
        self.select_current_llm()

    # LLM Methods
    def select_current_llm(self) -> None:
        """Select current LLM from table."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM из списка", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)
        config.current_llm = llm_name
        config.save()
        self.update_llm_tables(keep_cursor_position=True)  # Сохраняем позицию курсора
        
        # Update system info panel with new current LLM
        config_dir = Path(config.config_path).parent if hasattr(config, 'config_path') else Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
        bin_path = Path(sys.executable).parent
        system_info_display = self.query_one("#system-info-display", Static)
        system_info_display.update(
            f"[bold]Версия ПО:[/bold] {__version__}\n"
            f"[bold]Папка конфига:[/bold] {config_dir}\n"
            f"[bold]Папка бинарника:[/bold] {bin_path}\n\n"
            f"[bold]Текущая LLM:[/bold] [green]{llm_name}[/green]"
        )
        
        self.refresh_status()
        self.notify(f"Текущая LLM: {llm_name}", severity="information")

    def add_llm(self) -> None:
        """Add new LLM."""
        def handle_result(result):
            if result:
                config.add_llm(
                    result["name"], 
                    result["model"], 
                    result["api_url"], 
                    result["api_key"]
                )
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"LLM '{result['name']}' добавлена", severity="information")

        self.push_screen(
            LLMEditDialog(title="Добавление LLM"),
            handle_result
        )

    def edit_llm(self) -> None:
        """Edit selected LLM."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM для редактирования", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)
        cfg = config.get_llm_config(llm_name) or {}

        def handle_result(result):
            if result:
                # Если API ключ не был изменен (пустой), оставляем старый
                api_key_to_save = result["api_key"] if result["api_key"] else cfg.get("api_key", "")
                config.update_llm(
                    llm_name,
                    model=result["model"],
                    api_url=result["api_url"],
                    api_key=api_key_to_save
                )
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"LLM '{llm_name}' обновлена", severity="information")

        self.push_screen(
            LLMEditDialog(
                title=f"Редактирование {llm_name}",
                name=llm_name,
                model=cfg.get("model", ""),
                api_url=cfg.get("api_url", ""),
                api_key=cfg.get("api_key", ""),
                name_editable=False  # При редактировании имя не меняется
            ),
            handle_result
        )

    def delete_llm(self) -> None:
        """Delete selected LLM."""
        table = self.query_one("#llm-table", DataTable)
        if table.cursor_row < 0:
            self.notify("Выберите LLM для удаления", severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        llm_name = str(row[1])  # Название во втором столбце (после галочки)

        if llm_name == config.current_llm:
            self.notify("Нельзя удалить текущую LLM", severity="error")
            return

        def handle_confirm(confirm):
            if confirm:
                config.remove_llm(llm_name)
                self.update_llm_tables()
                self.refresh_status()
                self.notify(f"LLM '{llm_name}' удалена", severity="information")

        self.push_screen(
            ConfirmDialog(f"Удалить LLM '{llm_name}'?", title="Подтверждение"),
            handle_confirm,
        )

    # Parameter Methods
    def set_temperature(self) -> None:
        """Set temperature parameter."""
        input_field = self.query_one("#temp-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 2.0:
                config.temperature = value
                config.save()
                self.refresh_status()
                self.notify(f"Температура: {value}", severity="information")
            else:
                self.notify("Температура должна быть от 0.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_max_tokens(self) -> None:
        """Set max tokens parameter."""
        input_field = self.query_one("#max-tokens-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.max_tokens = None
            config.save()
            self.refresh_status()
            self.notify("Максимум токенов: без ограничений", severity="information")
        else:
            try:
                num_value = int(value)
                if num_value > 0:
                    config.max_tokens = num_value
                    config.save()
                    self.refresh_status()
                    self.notify(f"Максимум токенов: {num_value}", severity="information")
                else:
                    self.notify("Должно быть положительным", severity="error")
            except ValueError:
                self.notify("Неверный числовой формат", severity="error")

    def set_top_p(self) -> None:
        """Set top_p parameter."""
        input_field = self.query_one("#top-p-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.0 <= value <= 1.0:
                config.top_p = value
                config.save()
                self.refresh_status()
                self.notify(f"Top P: {value}", severity="information")
            else:
                self.notify("Top P должен быть от 0.0 до 1.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_frequency_penalty(self) -> None:
        """Сет frequency penalty."""
        input_field = self.query_one("#freq-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.frequency_penalty = value
                config.save()
                self.refresh_status()
                self.notify(f"Штраф частоты: {value}", severity="information")
            else:
                self.notify("Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_presence_penalty(self) -> None:
        """Set presence penalty."""
        input_field = self.query_one("#pres-penalty-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if -2.0 <= value <= 2.0:
                config.presence_penalty = value
                config.save()
                self.refresh_status()
                self.notify(f"Штраф присутствия: {value}", severity="information")
            else:
                self.notify("Должно быть от -2.0 до 2.0", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_seed(self) -> None:
        """Set seed parameter."""
        input_field = self.query_one("#seed-input", Input)
        value = input_field.value.strip().lower()
        if value in ["null", "none", ""]:
            config.seed = None
            config.save()
            self.refresh_status()
            self.notify("Seed: случайный", severity="information")
        else:
            try:
                num_value = int(value)
                config.seed = num_value
                config.save()
                self.refresh_status()
                self.notify(f"Seed: {num_value}", severity="information")
            except ValueError:
                self.notify("Неверный числовой формат", severity="error")

    # User Content Methods
    def save_user_content(self) -> None:
        """Save user content."""
        text_area = self.query_one("#content-textarea", TextArea)
        config.user_content = text_area.text
        config.save()
        self.refresh_status()
        self.notify("Контент сохранён", severity="information")

    def reset_user_content(self) -> None:
        """Reset user content."""

        def handle_confirm(confirm):
            if confirm:
                config.user_content = ""
                text_area = self.query_one("#content-textarea", TextArea)
                text_area.text = ""
                self.refresh_status()
                self.notify("Контент сброшен", severity="information")

        self.push_screen(
            ConfirmDialog("Сбросить пользовательский контент?"), handle_confirm
        )

    # System Settings Methods
    def set_stream_delay(self) -> None:
        """Set stream delay."""
        input_field = self.query_one("#stream-delay-input", Input)
        try:
            value = float(input_field.value.replace(",", "."))
            if 0.001 <= value <= 0.1:
                config.set("global", "sleep_time", value)
                self.refresh_status()
                self.notify(f"Задержка стрима: {value} сек", severity="information")
            else:
                self.notify("Должно быть от 0.001 до 0.1", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    def set_refresh_rate(self) -> None:
        """Set refresh rate."""
        input_field = self.query_one("#refresh-rate-input", Input)
        try:
            value = int(input_field.value)
            if 1 <= value <= 60:
                config.set("global", "refresh_per_second", value)
                self.refresh_status()
                self.notify(f"Частота обновлений: {value} Гц", severity="information")
            else:
                self.notify("Должно быть от 1 до 60", severity="error")
        except ValueError:
            self.notify("Неверный числовой формат", severity="error")

    # Language & Theme Methods
    def set_language(self, lang: str) -> None:
        """Set interface language."""
        setattr(config, "language", lang)
        config.save()
        translator.set_language(lang)
        self.refresh_status()
        lang_name = "English" if lang == "en" else "Русский"
        self.notify(f"Язык: {lang_name}", severity="information")

    def set_theme(self, theme: str) -> None:
        """Set interface theme."""
        setattr(config, "theme", theme)
        config.save()
        self.refresh_status()
        theme_names = {
            "default": "Классический",
            "monokai": "Monokai",
            "dracula": "Dracula",
            "nord": "Nord",
        }
        theme_name = theme_names.get(theme, theme)
        self.notify(f"Тема: {theme_name}", severity="information")

    # Utility Methods
    def refresh_status(self) -> None:
        """Refresh info panel to show current tab help."""
        tabs = self.query_one(TabbedContent)
        current_tab = tabs.active
        info_panel = self.query_one("#info-panel", InfoPanel)
        info_panel.show_tab_help(current_tab)

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Q или Ctrl+C - выход\n"
            "F1 - помощь\n"
            "Ctrl+R - обновить статус\n"
            "Все изменения сохраняются автоматически",
            title="Помощь",
            severity="information",
        )

    def action_refresh_status(self) -> None:
        """Refresh status action."""
        self.refresh_status()
        self.notify("Статус обновлён", severity="information")
    
    def action_reset_settings(self) -> None:
        """Сброс настроек к значениям по умолчанию."""
        message = (
            "Внимание! Все настройки, включая API ключи,\n"
            "будут сброшены к настройкам по умолчанию.\n\n"
            "Продолжить?"
        )
        
        def handle_confirm(result):
            if result:
                try:
                    # Загружаем default_config.yaml
                    default_config_path = Path(__file__).parent / "default_config.yaml"
                    
                    if not default_config_path.exists():
                        self.notify("Файл default_config.yaml не найден", severity="error")
                        return
                    
                    # Читаем содержимое default_config.yaml
                    with open(default_config_path, 'r', encoding='utf-8') as f:
                        default_content = f.read()
                    
                    # Записываем в пользовательский конфиг
                    config_path = Path(config.config_path) if hasattr(config, 'config_path') else Path.home() / ".config" / "penguin-tamer" / "penguin-tamer" / "config.yaml"
                    
                    # Создаем директорию если не существует
                    config_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Записываем default конфиг
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    
                    # Перезагружаем конфигурацию
                    config.reload()
                    
                    # Обновляем все отображаемые значения
                    self.update_all_inputs()
                    self.update_llm_tables()
                    
                    self.notify("Настройки успешно сброшены к значениям по умолчанию", severity="information")
                    
                except Exception as e:
                    self.notify(f"Ошибка при сбросе настроек: {e}", severity="error")
        
        self.push_screen(ConfirmDialog(message, "Сброс настроек"), handle_confirm)
    
    def update_all_inputs(self) -> None:
        """Обновляет все поля ввода значениями из конфига."""
        try:
            # Обновляем параметры генерации
            temp_input = self.query_one("#temp-input", Input)
            temp_input.value = str(config.temperature)
            
            max_tokens_input = self.query_one("#max-tokens-input", Input)
            max_tokens_str = str(config.max_tokens) if config.max_tokens else "неограниченно"
            max_tokens_input.value = max_tokens_str
            
            top_p_input = self.query_one("#top-p-input", Input)
            top_p_input.value = str(config.top_p)
            
            freq_penalty_input = self.query_one("#freq-penalty-input", Input)
            freq_penalty_input.value = str(config.frequency_penalty)
            
            pres_penalty_input = self.query_one("#pres-penalty-input", Input)
            pres_penalty_input.value = str(config.presence_penalty)
            
            seed_input = self.query_one("#seed-input", Input)
            seed_str = str(config.seed) if config.seed else "случайный"
            seed_input.value = seed_str
            
            # Обновляем системные настройки
            stream_delay_input = self.query_one("#stream-delay-input", Input)
            stream_delay = config.get("global", "sleep_time", 0.01)
            stream_delay_input.value = str(stream_delay)
            
            refresh_rate_input = self.query_one("#refresh-rate-input", Input)
            refresh_rate = config.get("global", "refresh_per_second", 10)
            refresh_rate_input.value = str(refresh_rate)
            
            debug_switch = self.query_one("#debug-switch", Switch)
            debug_switch.value = getattr(config, "debug", False)
            
            # Обновляем контент
            content_textarea = self.query_one("#content-textarea", TextArea)
            content_textarea.text = config.user_content
            
            # Обновляем язык
            language_select = self.query_one("#language-select", Select)
            current_lang = getattr(config, "language", "en")
            language_select.value = current_lang
            
            # Обновляем тему
            theme_select = self.query_one("#theme-select", Select)
            current_theme = getattr(config, "theme", "default")
            theme_select.value = current_theme
            
            # Обновляем панель с системной информацией и текущей LLM
            config_dir = Path(config.config_path).parent if hasattr(config, 'config_path') else Path.home() / ".config" / "penguin-tamer" / "penguin-tamer"
            bin_path = Path(sys.executable).parent
            current_llm = config.current_llm or "Не выбрана"
            
            system_info_display = self.query_one("#system-info-display", Static)
            system_info_display.update(
                f"[bold]Версия ПО:[/bold] {__version__}\n"
                f"[bold]Папка конфига:[/bold] {config_dir}\n"
                f"[bold]Папка бинарника:[/bold] {bin_path}\n\n"
                f"[bold]Текущая LLM:[/bold] [green]{current_llm}[/green]"
            )
            
        except Exception as e:
            # Некоторые виджеты могут быть не найдены, это нормально
            pass


def main_menu():
    """Entry point for running the config menu."""
    try:
        app = ConfigMenuApp()
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске меню настроек: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_menu()
