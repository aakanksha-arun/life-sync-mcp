from todoist_api_python.api import TodoistAPI
from fastapi import HTTPException
import config, schemas

# Initialize Client
try:
    if config.TODOIST_API_KEY:
        client = TodoistAPI(config.TODOIST_API_KEY)
    else:
        client = None
        print("Todoist API Key missing.")
except Exception as e:
    client = None
    print(f"Todoist client failed: {e}")

#GET ALL TASKS
def get_all_tasks():
    if not client:
        raise HTTPException(status_code=500, detail="Todoist Client not initialized")
    
    try:
        result = client.get_tasks()
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
        raise HTTPException(status_code=500, detail=f"Todoist Error: {str(e)}")

#CREATE NEW TASK
def create_task(task_input: schemas.TaskInput):
    if not client:
        raise HTTPException(status_code=500, detail="Todoist Client not initialized")
    
    try:
        task = client.add_task(
            content=task_input.content,
            due_string=task_input.due_date, #TODO: Fix date format. Not reflecting on fetch
        )
        return {"status": "success", "task_id": task.id, "content": task.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Todoist Error: {str(e)}")