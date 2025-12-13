import os
from dotenv import load_dotenv
import requests

from fastapi import APIRouter, HTTPException
from todoist_api_python.api import TodoistAPI
from pydantic import BaseModel

router = APIRouter()

load_dotenv()
api_key = os.getenv("TODOIST_API_KEY")
if not api_key:
    print("Error: Cannot find TODOIST_API_KEY in .env")
    todoist = None
else:
    todoist = TodoistAPI(api_key)

class TaskInput(BaseModel):
    """Defines the structure for adding a new task."""
    content: str
    due_date: str | None = None
    #TODO: can add other fields here later, like priority

#Get All Tasks
@router.get("/todoist/tasks")
def get_todoist_tasks():
    """
    Get all active tasks from Todoist
    """
    if not todoist:
        raise HTTPException(status_code=500, detail="Todoist API key not configured in .env file.")

    try:
        result = todoist.get_tasks()
        tasks = []
        for task_list in result:
            for task in task_list:
                tasks.append(task)
        clean_tasks = [
            {
                "id": task.id,
                "content:": task.content,
                "due": task.due.string if task.due else "No Date"
            }
            for task in tasks
        ]
        return clean_tasks
    except Exception as e:
        return f"An error occured while getting all tasks: {e}"