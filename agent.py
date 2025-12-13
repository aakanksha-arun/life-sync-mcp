import os
import requests
from dotenv import load_dotenv

#LangChain Imports
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

#setup
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("Error: Cannot find GOOGLE_API_KEY in .env")
    exit(1)

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

#define tools
@tool
def check_status():
    """
    Checks the user's current status.
    """
    try:
        status_url = f"{SERVER_URL}/status"
        print(f"  Connecting to: {status_url}")

        response = requests.get(status_url)
        return response.json()
    except Exception as e:
        return f"Error connecting to server: {e}"

#tools list
tools = [check_status]
tools_map = {t.name: t for t in tools}


#init Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
).bind_tools(tools)

#main loop
def run_chat():
    print("Life Sync Agent is ready! (Type 'quit' to exit)")
    while True:
        user_input = input("\n You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        try:
            msg = llm.invoke([HumanMessage(content=user_input)])
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                print(f" AI calling: {tool_name} with args: {tool_args}")

                #lookup tool in tools_map
                if tool_name in tools_map:
                    tool_result = tools_map[tool_name].invoke(tool_args)
                    print(f"Result from Server: {tool_result}")
                else:
                    print(f"Error: Tool {tool_name} not found in tools_map!")
            else:
                content = msg.content
                if isinstance(content, list):
                    text_parts = [block['text'] for block in content if 'text' in block]
                    print(f"Life Sync says: {' '.join(text_parts)}")
                else:
                    print(f"Life Sync says: {content}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_chat()