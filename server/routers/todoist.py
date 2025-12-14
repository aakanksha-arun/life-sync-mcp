import schemas
from services import todoist_svc
from fastapi import APIRouter

router = APIRouter(
    prefix="/todoist",
    tags=["Todoist"]
)

#Get All Active Tasks
@router.get("/tasks")
def get_all_tasks():
    """
    Get all active tasks from Todoist
    """
    return todoist_svc.get_all_tasks()

#Add a new task
@router.post("/tasks")
def add_new_task(task_input: schemas.TaskInput):
    return todoist_svc.create_task(task_input)
    

