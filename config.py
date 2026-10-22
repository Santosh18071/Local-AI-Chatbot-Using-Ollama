"""Change the model and the assistant's instructions in this one file."""

MODEL_NAME = "llama3.2:1b"
# A loopback address keeps requests on this computer, regardless of OLLAMA_HOST.
OLLAMA_HOST = "http://127.0.0.1:11434"
REQUEST_TIMEOUT_SECONDS = 180.0
SYSTEM_PROMPT = (
    "You are a patient, helpful assistant. Give clear, accurate, beginner-friendly "
    "answers. Explain unfamiliar terms, use small examples when useful, and say "
    "when you are unsure. Never pretend to have browsed the internet or used tools."
)

