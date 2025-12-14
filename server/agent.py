from datetime import date
import json
import os
from typing import Any, Dict
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
        url = f"{SERVER_URL}/status"
        print(f"  Connecting to: {url}")
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return f"Error connecting to server: {e}"

# --- TODOIST TOOLS ---
@tool
def todoist_get_all_active_tasks() -> dict:
    """
    Retrieves all active, uncompleted tasks from the user's Todoist account.
    Use this to see what the user needs to work on next.
    """
    url = f"{SERVER_URL}/todoist/tasks"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Failed to get Todoist tasks: {e}"

@tool
def todoist_add_new_task(content: str, due_date: str = None) -> dict:
    """
    Adds a new task to the user's Todoist inbox.
    
    Args:
        content: The text content of the task (e.g., 'Buy milk'). REQUIRED.
        due_date: Optional. The due date for the task (e.g., 'YYYY-MM-DD').
    """
    url = f"{SERVER_URL}/todoist/tasks"
    headers = {"Content-Type": "application/json"}
    payload = {"content": content}
    if due_date:
        payload["due_date"] = due_date
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Failed to create Todoist task: {e}"
    
# --- WATER TRACKING TOOLS (ON NOTION) ---
@tool
def log_water_intake(amount_oz: float) -> dict:
    """
    Logs a new water intake entry in fluid ounces (oz) to the user's Notion tracker.
    Use this when the user says they drank water, a glass, or a specific volume.
    
    Args:
        amount_oz: The amount of water consumed in fluid ounces (oz). REQUIRED.
    """
    url = f"{SERVER_URL}/notion/water"
    headers = {"Content-Type": "application/json"}
    payload = {
        "amount_oz": amount_oz,
        "log_date": str(date.today()) # Pass today's date as a string
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Failed to log water: {e}"
    
@tool
def get_today_hydration_status() -> dict:
    """
    Retrieves the total water consumed today and the daily goal status from Notion.
    Use this when the user asks about their water intake, hydration, or goal progress.
    """
    url = f"{SERVER_URL}/notion/water"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Failed to get hydration status: {e}"

#tools list
tools = [
    check_status,
    get_today_hydration_status,
    log_water_intake,
    todoist_add_new_task,
    todoist_get_all_active_tasks
    ]
tools_map = {t.name: t for t in tools}


#init Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
).bind_tools(tools)

#HELPER FUNCTION
def _extract_text_from_message(message_content) -> str:
    """Safely extracts a readable string from the model's message content."""
    if isinstance(message_content, list):
        # Handle the structured list of content blocks
        text_parts = [block['text'] for block in message_content if isinstance(block, dict) and 'text' in block]
        return ' '.join(text_parts)
    # Handle the simple string response
    return str(message_content)

def invoke_agent_with_tools(user_input: str) -> Dict[str, Any]:
    """
    Runs the LLM with the user input, handles tool calls, and returns a structured result for the frontend.
    """
    result = {
        "final_response": None,
        "tool_called": None,
        "tool_call_result": None
    }
    try:
            msg = llm.invoke([HumanMessage(content=user_input)])
            if msg.tool_calls:
                tool_call = msg.tool_calls[0]
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                result["tool_called"] = tool_name
            
                if tool_name in tools_map:
                        tool_result = tools_map[tool_name].invoke(tool_args)
                        result["tool_call_result"] = tool_result
                        tool_summary = json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
                        tool_message_to_llm = f"The user asked: '{user_input}'. The server ran the tool '{tool_name}' and got the following result: {tool_summary}. Now, please give a concise, helpful summary to the user."
                        final_msg = llm.invoke([
                        HumanMessage(content=tool_message_to_llm) 
                        ])
                        result["final_response"] = _extract_text_from_message(final_msg.content)
                else:
                    print(f"Error: Tool {tool_name} not found in tools_map!")
            else:
            # No tool call, just a direct response
                result["final_response"] = _extract_text_from_message(msg.content)
    except Exception as e:
            print(f"Error: {e}")
    return result