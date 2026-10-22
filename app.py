"""Run with: python -m streamlit run app.py"""

import streamlit as st

from config import MODEL_NAME
from ollama_service import ChatbotError, OllamaService


def clear_chat() -> None:
    st.session_state.messages = []
    st.session_state.pending_question = None
    st.session_state.last_error = ""


def main() -> None:
    st.set_page_config(page_title="Local AI Chat", layout="centered")
    # Only fixed, trusted CSS is injected; messages use Streamlit's safe Markdown.
    st.html("""
        <style>
        .stMainBlockContainer { max-width: 800px; padding-top: 3rem; }
        h1 { letter-spacing: -0.03em; }
        [data-testid="stCaptionContainer"] { opacity: 1; color: #526159; }
        [data-testid="stChatInput"] textarea::placeholder { color: #526159; opacity: 1; }
        [data-testid="stChatMessage"] { border-radius: 14px; }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background-color: #e8eee9;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background-color: #f2f3ee;
        }
        ::selection { background-color: #c5e4d4; color: #182b22; }
        @media (max-width: 600px) {
            .stMainBlockContainer { padding-top: 4.5rem; }
        }
        </style>
    """)

    if "messages" not in st.session_state:
        clear_chat()
    service = OllamaService()

    with st.sidebar:
        st.header("Your local assistant")
        st.caption("A small model. A place to ask questions.")
        st.text("Selected model")
        st.code(MODEL_NAME, language=None)
        st.button("Clear chat", on_click=clear_chat, width="stretch")
        if st.button("Check connection", width="stretch"):
            with st.spinner("Checking Ollama…"):
                try:
                    service.check_ready()
                except ChatbotError as error:
                    st.error(str(error))
                else:
                    st.success("Ollama is reachable and the local model is available.")
        with st.expander("First-time setup"):
            st.markdown("Install **Ollama**, then open its app or run:")
            st.code("ollama serve", language="bash")
            st.markdown("In another terminal, download the selected model:")
            st.code(f"ollama pull {MODEL_NAME}", language="bash")
            st.caption("The default 1B model is about 1.3 GB; other models vary. Check the size before downloading. Full instructions are in README.md.")
        st.divider()
        st.caption("Chat history lives in this browser session. Clear it any time. AI answers can be wrong.")

    st.title("Make room for a question.")
    st.markdown(
        "Welcome to **Local AI Chat**. Ask a question, explore an idea, or learn "
        "something new. Ollama runs the AI model on your computer."
    )
    st.caption("Local model · No API key · Session-only history")
    if not st.session_state.messages and st.session_state.pending_question is None:
        st.info('Try: “Explain how a computer learns, using a simple example.”')

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "What would you like to understand?",
        disabled=st.session_state.pending_question is not None,
    )
    if prompt is not None:
        if prompt.strip():
            st.session_state.pending_question = prompt.strip()
            st.session_state.last_error = ""
            st.rerun()
        else:
            st.warning("Type a question before sending it.")

    if st.session_state.pending_question is not None:
        question = st.session_state.pending_question
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            if not st.session_state.last_error:
                with st.spinner("Thinking on your computer… The first reply may take longer."):
                    try:
                        answer = service.get_reply([
                            *st.session_state.messages,
                            {"role": "user", "content": question},
                        ])
                    except ChatbotError as error:
                        st.session_state.last_error = str(error)
                    else:
                        # Save complete pairs only; retries never duplicate a question.
                        st.session_state.messages.extend([
                            {"role": "user", "content": question},
                            {"role": "assistant", "content": answer},
                        ])
                        st.session_state.pending_question = None
                        st.rerun()
            if st.session_state.last_error:
                st.error(st.session_state.last_error)
                retry, discard = st.columns(2)
                if retry.button("Retry", width="stretch"):
                    st.session_state.last_error = ""
                    st.rerun()
                if discard.button("Discard question", width="stretch"):
                    st.session_state.pending_question = None
                    st.session_state.last_error = ""
                    st.rerun()


if __name__ == "__main__":
    main()
