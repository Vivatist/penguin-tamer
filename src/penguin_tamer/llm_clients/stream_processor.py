"""
Stream Processor - Общий процессор для обработки потоковых ответов LLM.

Инкапсулирует логику обработки streaming responses от LLM API,
включая обработку ошибок, обработку чанков и управление live display.
"""

import threading
import time
from typing import List, Optional

from rich.live import Live

from penguin_tamer.i18n import t
from penguin_tamer.config_manager import config
from penguin_tamer.error_handlers import ErrorHandler, ErrorContext, ErrorSeverity


class StreamProcessor:
    """Processor for handling streaming LLM responses.

    Encapsulates the logic of processing streaming responses from LLM API,
    including error handling, chunk processing, and live display management.
    """

    def __init__(self, client):
        """Initialize stream processor.

        Args:
            client: Parent LLM client instance (OpenRouterClient, OpenAIClient, etc.)
        """
        self.client = client
        self.interrupted = threading.Event()
        self.reply_parts: List[str] = []
        self.user_input: str = ""  # Store user input to add to context only on success

    def process(self, user_input: str) -> str:
        """Process user input and return AI response.

        Args:
            user_input: User's message text

        Returns:
            Complete AI response text
        """
        # Store user input to add to context only if request succeeds
        self.user_input = user_input

        # Create error handler
        debug_mode = config.get("global", "debug", False)
        error_handler = ErrorHandler(console=self.client.console, debug_mode=debug_mode)

        # Phase 1: Connect and wait for first chunk
        stream, first_chunk = self._connect_and_wait(error_handler)
        if stream is None:
            # Error occurred - don't add user message to context
            return ""

        # Phase 2: Process stream with live display
        try:
            reply = self._stream_with_live_display(stream, first_chunk)
        except KeyboardInterrupt:
            self.interrupted.set()
            # Interrupted - don't add to context
            raise

        # Phase 3: Finalize (will add user message to context if successful)
        return self._finalize_response(reply)

    def _connect_and_wait(self, error_handler: ErrorHandler) -> tuple:
        """Connect to API and wait for first chunk.

        Returns:
            Tuple of (stream, first_chunk) or (None, None) on error
        """
        with self.client._managed_spinner(t('Connecting...')) as status_message:
            try:
                # Send API request with user input (but don't add to permanent context yet)
                api_params = self.client._prepare_api_params(self.user_input)
                stream = self.client._create_stream(api_params)

                # Try to extract rate limit info from stream (if available)
                self.client._extract_rate_limits(stream)

                # Wait for first chunk
                status_message['text'] = t('Ai thinking...')
                first_chunk = self._wait_first_chunk(stream)

                if first_chunk:
                    self.reply_parts.append(first_chunk)

                return stream, first_chunk

            except KeyboardInterrupt:
                self.interrupted.set()
                raise
            except Exception as e:
                self.interrupted.set()
                context = ErrorContext(
                    operation="streaming API request",
                    severity=ErrorSeverity.ERROR,
                    recoverable=True
                )
                error_message = error_handler.handle(e, context)
                self.client.console.print(error_message)
                return None, None

    def _wait_first_chunk(self, stream) -> Optional[str]:
        """Ожидание первого чанка с контентом (используется API-специфичный парсинг)."""
        try:
            for chunk in stream:
                if self.interrupted.is_set():
                    raise KeyboardInterrupt("Stream interrupted")

                # Use client-specific chunk content extraction
                content = self.client._extract_chunk_content(chunk)
                if content:
                    return content
        except (AttributeError, IndexError):
            return None
        return None

    def _stream_with_live_display(self, stream, first_chunk: str) -> str:
        """Process stream with live markdown display.

        Args:
            stream: API response stream
            first_chunk: First chunk of content

        Returns:
            Complete response text
        """
        sleep_time = config.get("global", "sleep_time", 0.01)
        refresh_per_second = config.get("global", "refresh_per_second", 10)
        theme_name = config.get("global", "markdown_theme", "default")

        with Live(
            console=self.client.console,
            refresh_per_second=refresh_per_second,
            auto_refresh=True
        ) as live:
            # Show first chunk
            if first_chunk:
                markdown = self.client._create_markdown(first_chunk, theme_name)
                live.update(markdown)
                # Record first chunk for demo
                if self.client._demo_manager:
                    self.client._demo_manager.record_llm_chunk(first_chunk)

            # Process remaining chunks
            try:
                for chunk in stream:
                    if self.interrupted.is_set():
                        raise KeyboardInterrupt("Stream interrupted")

                    # Use client-specific chunk content extraction
                    text = self.client._extract_chunk_content(chunk)
                    if text:
                        self.reply_parts.append(text)
                        # Record chunk for demo
                        if self.client._demo_manager:
                            self.client._demo_manager.record_llm_chunk(text)
                        full_text = "".join(self.reply_parts)
                        markdown = self.client._create_markdown(full_text, theme_name)
                        live.update(markdown)
                        time.sleep(sleep_time)

                    # Use client-specific usage stats extraction (ВСЕГДА проверяем, не только если нет контента)
                    usage_stats = self.client._extract_usage_stats(chunk)
                    if usage_stats:
                        self.client.total_prompt_tokens += usage_stats.get('prompt_tokens', 0)
                        self.client.total_completion_tokens += usage_stats.get('completion_tokens', 0)
                        self.client.total_requests += 1
            except (AttributeError, IndexError):
                pass

        return "".join(self.reply_parts)

    def _finalize_response(self, reply: str) -> str:
        """Finalize response and update messages.

        Args:
            reply: Complete response text

        Returns:
            Final response text
        """
        # Check for empty response
        if not reply or not reply.strip():
            warning = t('Warning: Empty response received from API.')
            self.client.console.print(f"[dim italic]{warning}[/dim italic]")
            # Empty response is an error - don't add to context
            return ""

        # Success! Add both user message and assistant response to context
        self.client.messages.append({"role": "user", "content": self.user_input})
        self.client.messages.append({"role": "assistant", "content": reply})

        # Debug output if enabled
        self.client._debug_print_if_enabled("response")

        return reply
