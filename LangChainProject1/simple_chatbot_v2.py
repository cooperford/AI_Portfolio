import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0)

agent = create_agent(model=model, tools=[], system_prompt="You are a helpful assistant. Be concise and to the point. Understand the user's question and provide a clear and accurate answer. stay professional and courteous in your responses. If you don't know the answer, say you don't know.")


#create history

chat_history = []

print("Welcome to the chatbot! Type 'exit' to end the conversation.\n")


while True:
    user_input = input("You: ".strip())
    print()
    if user_input.lower() == 'exit':
        print("Assistant: Goodbye!")
        break
    
    messages = chat_history + [{"role": "user", "content": user_input}]
    result = agent.invoke({'messages':messages})

    try:
        reply = result[messages[-1]['content']]
    except Exception as e:
        reply = str(e)

    print(f"Assistant: {reply}\n")
    print("-" * 60)

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": reply})


    print(result)