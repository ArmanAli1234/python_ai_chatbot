# PyTutor - Personal Python Programming Tutor

PyTutor is a small chatbot project I built to help learners with Python programming. It uses Streamlit for the chat interface and Google Gemini through LangChain to generate answers.

The idea is to make it easier to ask Python questions, understand concepts, and get help with basic coding problems.

## What it can do

- Answer questions about Python concepts and syntax
- Explain code in simple language
- Help with common programming errors
- Keep messages in the current chat session
- Save chat questions and answers in `chat_history.txt`
- Provide quick prompts for common Python topics
- Clear the current chat and download saved history

## Tools used

- Python
- Streamlit
- LangChain
- Google Gemini API
- `python-dotenv`

## Project files

```text
Python-Personal-Chatbot/
├── app.py
├── .env
├── requirements.txt
├── chat_history.txt
└── README.md
```

`chat_history.txt` is created by the app when chat history is saved. The `.env` file stores the API key and should not be uploaded to GitHub.

## Setup

### 1. Get a Gemini API key

Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).

### 2. Create a virtual environment

Run these commands in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the packages

If you have a `requirements.txt` file:

```powershell
pip install -r requirements.txt
```

Or install the packages directly:

```powershell
pip install streamlit python-dotenv langchain-core langchain-google-genai
```

### 4. Add your API key

Create a `.env` file in the same folder as `app.py` and add your key:

```dotenv
GOOGLE_API_KEY=your_gemini_api_key_here
```

Replace the example value with your actual key. Do not share it or commit the `.env` file to GitHub.

### 5. Run the app

From the project folder, run:

```powershell
python -m streamlit run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Example questions

You can try questions such as:

- What is the difference between a list and a tuple?
- Explain Python list comprehensions with an example.
- Why am I getting a `TypeError`?
- Explain inheritance in Python.
- Give me a Python practice question.

## Common issues

**API key error:** Check that `.env` is in the project folder and the variable name is `GOOGLE_API_KEY`.

**Model not found:** The model configured in `app.py` may not be available to your API account. Check the current model names in the [Gemini API documentation](https://ai.google.dev/gemini-api/docs/models) and update the model name if needed.

**Rate limit error:** Gemini API usage can have quota and rate limits. Check your current limits in Google AI Studio.

**Streamlit warning:** Run the app with `python -m streamlit run app.py`, not `python app.py`.

## Security

Keep your API key and personal chat logs out of public repositories. A simple `.gitignore` file can include:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
chat_history.txt
.streamlit/secrets.toml
```

## Possible improvements

- Add beginner, intermediate, and advanced learning modes
- Add short quizzes and coding exercises
- Improve code formatting in chatbot responses
- Add a way to choose learning topics

---

This project was built as a hands-on way to learn how to connect a language model to a Python application using LangChain and Streamlit.
