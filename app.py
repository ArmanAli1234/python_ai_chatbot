import os
import warnings
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

warnings.filterwarnings("ignore", message="Direct use of automatic function calling.*")
load_dotenv()

HISTORY_FILE = "chat_history.txt"
SESSION_ID = "python-tutor"

# ---------- Page setup ----------
st.set_page_config(page_title="Python Tutor", page_icon="🐍", layout="centered")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 820px;}
    .hero {
        padding: 1.4rem 1.6rem; border-radius: 16px; margin-bottom: 1.2rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #4f46e5 55%, #7c3aed 100%);
        color: #fff;
    }
    .hero h1 {margin: 0; font-size: 1.7rem; font-weight: 700; color: #fff;}
    .hero p {margin: .3rem 0 0; opacity: .9; font-size: .95rem;}
    [data-testid="stChatMessage"] {border-radius: 14px; padding: .7rem 1rem;}
    div.stButton > button {border-radius: 10px; width: 100%;}
    footer, #MainMenu {visibility: hidden;}
    </style>
    <div class="hero">
        <h1>🐍 Python Tutor</h1>
        <p>Your personal Python programming tutor, with simple explanations and code examples.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = InMemoryChatMessageHistory()
if "pending" not in st.session_state:
    st.session_state.pending = None

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    model_name = st.text_input("Model", value="gemini-3.8-flash")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.05)
    max_tokens = st.slider("Max output tokens", 256, 4096, 1024, 128)

    st.divider()
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = InMemoryChatMessageHistory()
        st.rerun()

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            saved = f.read()
        if saved.strip():
            st.download_button(
                "⬇️ Download history",
                saved,
                file_name="chat_history.txt",
                use_container_width=True,
            )
            with st.expander("📜 Saved history"):
                st.text(saved)
            if st.button("🗑️ Delete saved history", use_container_width=True):
                os.remove(HISTORY_FILE)
                st.rerun()

    st.divider()
    st.caption(f"Messages in session: {len(st.session_state.messages)}")


# ---------- Chain ----------
@st.cache_resource(show_spinner=False)
def build_chain(model_name: str, temperature: float, max_tokens: int):
    model = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_output_tokens=max_tokens,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are my personal Python programming tutor.

                Rules:
                1. Answer only Python programming-related questions.
                2. Explain concepts in easy language.
                3. Give code examples wherever useful.
                4. If a question is unrelated to Python,
                   politely say that you only answer Python questions.
                5. Never invent code behavior.
                """,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )
    return prompt | model | StrOutputParser()


def get_chatbot():
    chain = build_chain(model_name, temperature, max_tokens)
    return RunnableWithMessageHistory(
        chain,
        lambda _sid: st.session_state.memory,
        input_messages_key="question",
        history_messages_key="chat_history",
    )


def save_to_file(question: str, answer: str):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}]\n")
        f.write(f"You: {question}\nTutor: {answer}\n")
        f.write("-" * 50 + "\n")


# ---------- API key check ----------
if not os.getenv("GOOGLE_API_KEY"):
    st.error("`GOOGLE_API_KEY` not found. Add it to your `.env` file and restart the app.")
    st.stop()

# ---------- Chat history render ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🐍"):
        st.markdown(msg["content"])

# ---------- Suggestion chips (only on empty chat) ----------
if not st.session_state.messages:
    st.markdown("##### 💡 Try asking")
    suggestions = [
        "What is the difference between a list and a tuple?",
        "Explain decorators with a simple example",
        "How do I write a list comprehension?",
        "What are generators and yield?",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sugg_{i}"):
            st.session_state.pending = s
            st.rerun()

# ---------- Input ----------
typed = st.chat_input("Ask a Python question...")
question = typed or st.session_state.pending
st.session_state.pending = None

if question:
    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🐍"):
        try:
            stream = get_chatbot().stream(
                {"question": question},
                config={"configurable": {"session_id": SESSION_ID}},
            )
            answer = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            save_to_file(question, answer)
        except Exception as e:
            st.error(f"Something went wrong: {e}")