import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

agent = create_agent(model=model, tools=[], system_prompt="You are a helpful assistant. Be concise and to the point. Understand the user's question and provide a clear and accurate answer. stay professional and courteous in your responses. If you don't know the answer, say you don't know.")

result = agent.invoke(
{
    "messages": [{"role": "user", "content": "Explain machine learning in short"}]
}
)

print(result)