from openai import OpenAI
from openai import RateLimitError, APIError, OpenAIError
from typing import List, Dict


class OpenRouterChat:
    def __init__(self, api_key: str, api_url: str, model: str,
                 system_context: str = "You are a helpful assistant.",
                 temperature: float = 0.7):
        self.client = OpenAI(api_key=api_key, base_url=api_url)
        self.model = model
        self.temperature = temperature
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_context}
        ]

    def ask(self, user_input: str) -> str:
        """Обычный (не потоковый) режим с сохранением контекста"""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature
            )

            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})

            # токены
            usage = response.usage
            if usage:
                print(f"[TOKENS] input={usage.prompt_tokens}, "
                      f"output={usage.completion_tokens}, "
                      f"total={usage.total_tokens}")

            return reply

        except RateLimitError:
            print("Ошибка: слишком частые запросы (RateLimit). Попробуйте позже.")
        except APIError as e:
            print(f"Ошибка API: {e}")
        except OpenAIError as e:
            print(f"Ошибка клиента OpenAI: {e}")

        return "Ошибка при получении ответа."

    def ask_stream(self, user_input: str) -> str:
        """Потоковый режим с сохранением контекста"""
        self.messages.append({"role": "user", "content": user_input})

        reply_parts = []
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                stream=True
            )

            print("AI: ", end="", flush=True)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    reply_parts.append(text)
                    print(text, end="", flush=True)
            print()

            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})

            # В потоковом режиме usage иногда приходит в конце
            # но в SDK openai stream не всегда отдает usage
            # Поэтому можно потом сделать отдельный запрос к usage-метрикам

            return reply

        except RateLimitError:
            print("Ошибка: слишком частые запросы (RateLimit). Попробуйте позже.")
        except APIError as e:
            print(f"Ошибка API: {e}")
        except OpenAIError as e:
            print(f"Ошибка клиента OpenAI: {e}")

        return "Ошибка при получении ответа."
