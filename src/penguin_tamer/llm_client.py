import threading
from typing import List, Dict
import time
from penguin_tamer.text_utils import format_api_key_display
from penguin_tamer.i18n import t
from penguin_tamer.config_manager import config
from penguin_tamer.themes import get_code_theme
from penguin_tamer.debug import debug_print_messages

# Ленивый импорт Rich
_markdown = None
_live = None


def _get_markdown():
    global _markdown
    if _markdown is None:
        from rich.markdown import Markdown
        _markdown = Markdown
    return _markdown


def _create_markdown(text: str, theme_name: str = "default"):
    """
    Создаёт Markdown объект с правильной темой для блоков кода.
    
    Args:
        text: Текст в формате Markdown
        theme_name: Название темы
    
    Returns:
        Markdown объект с применённой темой
    """
    Markdown = _get_markdown()
    code_theme = get_code_theme(theme_name)
    return Markdown(text, code_theme=code_theme)

def _get_live():
    global _live
    if _live is None:
        from rich.live import Live
        _live = Live
    return _live

# Ленивый импорт OpenAI (самый тяжелый модуль)
_openai_client = None


def _get_openai_client():
    """Ленивый импорт OpenAI клиента"""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI
    return _openai_client


class OpenRouterClient:

    def _spinner(self, stop_spinner: threading.Event, status_message: dict) -> None:
        """Визуальный индикатор работы ИИ с динамическим статусом.
        status_message - словарь с ключом 'text' для обновления сообщения.
        """
        try:
            with self.console.status("[dim]" + status_message.get('text', t('Ai thinking...')) + "[/dim]", spinner="dots", spinner_style="dim") as status:
                while not stop_spinner.is_set():
                    # Обновляем статус, если он изменился
                    current_text = status_message.get('text', t('Ai thinking...'))
                    status.update(f"[dim]{current_text}[/dim]")
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def __init__(self, console, api_key: str, api_url: str, model: str,
                 system_message: List[dict[str, str]],
                 temperature: float = 0.7,
                 max_tokens: int = None,
                 top_p: float = 0.95,
                 frequency_penalty: float = 0.0,
                 presence_penalty: float = 0.0,
                 stop: list = None,
                 seed: int = None):
        self.console = console
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.seed = seed
        self.messages: List[Dict[str, str]] = system_message.copy()
        self._client = None  # Ленивая инициализация

    @property
    def client(self):
        """Ленивая инициализация OpenAI клиента"""
        if self._client is None:
            self._client = _get_openai_client()(api_key=self.api_key, base_url=self.api_url)
        return self._client


    def ask_stream(self, user_input: str, educational_prompt: list = []) -> str:
        """Потоковый режим с сохранением контекста и обработкой Markdown в реальном времени"""
        # Показ спиннера в отдельном потоке с динамическим статусом
        stop_spinner = threading.Event()
        status_message = {'text': t('Sending request...')}
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner, status_message), daemon=True)
        spinner_thread.start()

        self.messages.extend(educational_prompt)
        self.messages.append({"role": "user", "content": user_input})
        reply_parts = []

        # Debug mode: показываем структуру запроса
        import os
        if os.getenv("PT_DEBUG") == "1" or config.get("global", "debug_mode", False):
            stop_spinner.set()  # Останавливаем спиннер для чистого вывода
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.1)
            debug_print_messages(
                self.messages, 
                model=self.model, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=self.stop,
                seed=self.seed,
                phase="request"
            )
            # Перезапускаем спиннер
            stop_spinner.clear()
            spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner, status_message), daemon=True)
            spinner_thread.start()
        
        # Флаг прерывания для потока
        interrupted = threading.Event()
        
        try:
            # Фаза 1: Отправка запроса
            # Подготавливаем параметры API
            api_params = {
                "model": self.model,
                "messages": self.messages,
                "temperature": self.temperature,
                "stream": True
            }
            
            # Добавляем опциональные параметры только если они заданы
            if self.max_tokens is not None:
                api_params["max_tokens"] = self.max_tokens
            if self.top_p is not None and self.top_p != 1.0:
                api_params["top_p"] = self.top_p
            if self.frequency_penalty != 0.0:
                api_params["frequency_penalty"] = self.frequency_penalty
            if self.presence_penalty != 0.0:
                api_params["presence_penalty"] = self.presence_penalty
            if self.stop is not None:
                api_params["stop"] = self.stop
            if self.seed is not None:
                api_params["seed"] = self.seed
            
            stream = self.client.chat.completions.create(**api_params)

            # Фаза 2: Ожидание ответа от модели
            status_message['text'] = t('Ai thinking...')
            
            # Ждем первый чанк с контентом перед запуском Live
            first_content_chunk = None
            for chunk in stream:
                if interrupted.is_set():
                    raise KeyboardInterrupt("Stream interrupted")
                if chunk.choices[0].delta.content:
                    first_content_chunk = chunk.choices[0].delta.content
                    reply_parts.append(first_content_chunk)
                    break
            
            # Останавливаем спиннер после получения первого чанка
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.1)

            sleep_time = config.get("global", "sleep_time", 0.01)
            refresh_per_second = config.get("global", "refresh_per_second", 10)
            theme_name = config.get("global", "markdown_theme", "default")
            
            # Используем Live для динамического обновления отображения с Markdown
            with _get_live()(console=self.console, refresh_per_second=refresh_per_second, auto_refresh=True) as live:
                # Показываем первый чанк
                if first_content_chunk:
                    markdown = _create_markdown(first_content_chunk, theme_name)
                    live.update(markdown)
                
                # Продолжаем обрабатывать остальные чанки
                for chunk in stream:
                    if interrupted.is_set():
                        raise KeyboardInterrupt("Stream interrupted")
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        reply_parts.append(text)
                        # Объединяем все части и обрабатываем как Markdown
                        full_text = "".join(reply_parts)
                        markdown = _create_markdown(full_text, theme_name)
                        live.update(markdown)
                        time.sleep(sleep_time)  # Небольшая задержка для плавности обновления
            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})
            
            # Debug mode: показываем структуру ответа
            import os
            if os.getenv("PT_DEBUG") == "1" or config.get("global", "debug_mode", False):
                debug_print_messages(
                    self.messages,  # Показываем все сообщения включая новый ответ
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=self.stop,
                    seed=self.seed,
                    phase="response"
                )
            
            return reply

        except KeyboardInterrupt:
            # Устанавливаем флаг прерывания
            interrupted.set()
            # Останавливаем спиннер
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)
            raise
        except Exception as e:
            # Останавливаем спиннер в случае ошибки
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join(timeout=0.3)
            raise
  


    def __str__(self) -> str:
        """Человекочитаемое представление клиента со всеми полями.

        Примечание: значение `api_key` маскируется (видны только последние 4 символа),
        а сложные объекты выводятся кратко.
        """

        items = {}
        for k, v in self.__dict__.items():
            if k == 'api_key':
                items[k] = format_api_key_display(v)
            elif k == 'messages' or k == 'console' or k == '_client':
                continue
            else:
                try:
                    items[k] = v
                except Exception:
                    items[k] = f"<unrepr {type(v).__name__}>"

        parts = [f"{self.__class__.__name__}("]
        for key, val in items.items():
            parts.append(f"  {key}={val!r},")
        parts.append(")")
        return "\n".join(parts)
