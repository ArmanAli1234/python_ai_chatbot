# Personal Python Chatbot

import os
import warnings
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI


warnings.filterwarnings(
    "ignore",
    message="Direct use of automatic function calling.*"
)

# Load API key
load_dotenv()

# History file
HISTORY_FILE = "chat_history.txt"

# Connect model
model = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    max_output_tokens=1024
)

# Create prompt
prompt = ChatPromptTemplate.from_messages([
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
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

# Output parser
parser = StrOutputParser()

# Connect prompt, model and parser
chain = RunnableSequence(prompt, model, parser)

# Store conversation history in memory
store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Add memory to chain
chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)

# Function to view saved history
def show_history():
    if not os.path.exists(HISTORY_FILE):
        print("\nNo chat history found yet.\n")
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        history = file.read()

    if history.strip():
        print("\n===== YOUR CHAT HISTORY =====\n")
        print(history)
        print("=============================\n")
    else:
        print("\nChat history file is empty.\n")

# Chatbot
print("Python Chatbot Started!")
print("Type 'exit' to stop.")
print("Type 'history' to view saved chats.")
print("Type 'clear' to clear current session memory.\n")

session_id = "python-tutor"

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Tutor: Happy learning, bhai!")
        break

    if question.lower() == "history":
        show_history()
        continue

    if question.lower() == "clear":
        store[session_id] = InMemoryChatMessageHistory()
        print("Tutor: Current session memory cleared!\n")
        continue

    if not question:
        continue

    try:
        answer = chatbot.invoke(
            {"question": question},
            config={
                "configurable": {
                    "session_id": session_id
                }
            }
        )

        print("\nTutor:", answer, "\n")

        # Save question and answer to text file
        with open(HISTORY_FILE, "a", encoding="utf-8") as file:
            file.write(f"You: {question}\n")
            file.write(f"Tutor: {answer}\n")
            file.write("-" * 50 + "\n")

    except Exception as e:
        print("Something went wrong:", e)