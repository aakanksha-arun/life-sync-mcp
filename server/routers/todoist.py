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

#Get All Active Tasks
@router.get("/todoist/tasks")
def get_all_tasks():
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

#TaskModel
class TaskInput(BaseModel):
    """Defines the structure for adding a new task."""
    content: str
    due_date: str | None = None
    #TODO: can add other fields here later, like priority

#Add a new task
@router.post("/todoist/tasks")
def add_new_task(task_input: TaskInput):
    if not todoist:
        raise HTTPException(status_code=500, detail="Todoist API key not configured in .env file.")
    #create task structure
    try:
        task = todoist.add_task(
            content=task_input.content,
            due_string=task_input.due_date,
        )
        return {"status": "success", "task_id": task.id, "content": task.content}
    except Exception as e:
        return f"An error occured while creating a new task: {e}"
    

