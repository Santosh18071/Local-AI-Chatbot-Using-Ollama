"""Talk to Ollama and translate failures into helpful, safe messages."""

from collections.abc import Sequence
from typing import Literal, TypedDict

from ollama import Client, ResponseError

from config import (
    MODEL_NAME,
    OLLAMA_HOST,
    REQUEST_TIMEOUT_SECONDS,
    SYSTEM_PROMPT,
)


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatbotError(Exception):
    """An error whose message is safe to display in the chat interface."""


class OllamaService:
    def __init__(self, model: str = MODEL_NAME, client: Client | None = None) -> None:
        self.model = model.strip()
        self.client = client if client is not None else Client(
            host=OLLAMA_HOST,
            timeout=REQUEST_TIMEOUT_SECONDS,
            trust_env=False,  # Do not send local traffic through a proxy.
        )

    def _connection_error(self) -> ChatbotError:
        return ChatbotError(
            "Cannot reach Ollama on this computer. If it is not installed, get it "
            "from https://ollama.com/download. Open the Ollama app, or run "
            "`ollama serve` in another terminal, then check the connection or retry your question."
        )

    def _response_error(self, error: ResponseError) -> ChatbotError:
        if error.status_code == 404:
            return ChatbotError(
                f"The selected model ({self.model}) is unavailable. Check the model "
                "name in config.py and run `ollama list`. Download the selected "
                f"model with `ollama pull {self.model}`, then try again. "
                "The default 1B model download is about 1.3 GB; other models vary."
            )
        return ChatbotError(
            "Ollama could not complete the request. The model may need more memory. "
            "Close other applications, check Ollama's terminal, and try again."
        )

    def check_ready(self) -> None:
        """Check the model without downloading it or generating an answer."""
        if not self.model:
            raise ChatbotError("Set MODEL_NAME to a local model name in config.py.")
        if "cloud" in self.model.lower():
            raise ChatbotError("Choose a downloaded local model in config.py. Cloud models are disabled.")
        try:
            self.client.show(self.model)
        except ChatbotError:
            raise
        except ConnectionError:
            raise self._connection_error() from None
        except ResponseError as error:
            raise self._response_error(error) from None
        except Exception:
            raise ChatbotError(
                "Could not check the local model. Restart Ollama and try again. "
                "If the problem continues, reinstall the Python dependencies."
            ) from None

    def get_reply(self, messages: Sequence[ChatMessage]) -> str:
        """Send a copy of the conversation with one leading system instruction."""
        if any(
            message.get("role") not in ("user", "assistant")
            or not isinstance(message.get("content"), str)
            for message in messages
        ):
            raise ChatbotError("The conversation is invalid. Clear the chat and try again.")
        if not messages or not messages[-1]["content"].strip():
            raise ChatbotError("Type a question before sending it.")
        if messages[-1]["role"] != "user":
            raise ChatbotError("The conversation must end with your question.")
        self.check_ready()
        request_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        request_messages.extend(dict(message) for message in messages)
        try:
            response = self.client.chat(
                model=self.model,
                messages=request_messages,
                stream=False,
                options={"num_ctx": 4096},
            )
            # The official response object supports dictionary-style access.
            message = response["message"]
            content = message["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Empty answer")
            return content.strip()
        except ConnectionError:
            raise self._connection_error() from None
        except ResponseError as error:
            raise self._response_error(error) from None
        except Exception:
            raise ChatbotError(
                "No usable answer arrived from Ollama. Try again, or clear the chat "
                "and ask a shorter question. If this repeats, restart Ollama. "
                f"Slow computers may exceed the {REQUEST_TIMEOUT_SECONDS:g}-second request timeout."
            ) from None

