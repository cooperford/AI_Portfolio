import os
from functools import lru_cache
from pathlib import Path

from django.conf import settings

try:
    from dotenv import load_dotenv
    from langchain.agents import create_agent
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as exc:
    load_dotenv = None
    create_agent = None
    ChatGoogleGenerativeAI = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


SYSTEM_PROMPT = (
    "You are a helpful assistant. Be concise and to the point. Understand the "
    "user's question and provide a clear and accurate answer. Stay professional "
    "and courteous in your responses. If you don't know the answer, say you "
    "don't know."
)


class ChatbotUnavailableError(Exception):
    pass


def _load_project_env():
    if load_dotenv is None:
        return

    load_dotenv()
    project_env = Path(settings.BASE_DIR) / 'LangChainProject1' / '.env'
    if project_env.exists():
        load_dotenv(project_env, override=False)


@lru_cache(maxsize=1)
def get_agent():
    if IMPORT_ERROR is not None:
        raise ChatbotUnavailableError(
            'LangChain chatbot dependencies are not installed in this environment.'
        ) from IMPORT_ERROR

    _load_project_env()
    if not os.getenv('GEMINI_API_KEY'):
        raise ChatbotUnavailableError('GEMINI_API_KEY is not configured.')

    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0)
    return create_agent(model=model, tools=[], system_prompt=SYSTEM_PROMPT)


def _extract_reply(result):
    messages = result.get('messages', []) if isinstance(result, dict) else []

    for message in reversed(messages):
        content = getattr(message, 'content', None)
        if content:
            return content

    return str(result)


def ask_chatbot(history, user_message):
    messages = history + [{'role': 'user', 'content': user_message}]
    result = get_agent().invoke({'messages': messages})
    return _extract_reply(result)
