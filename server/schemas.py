from pydantic import BaseModel, Field
from datetime import date

# --- Notion x Water Log Schemas ---
class WaterLogInput(BaseModel):
    """Defines the structure for logging water"""
    amount_oz: float
    log_date: date = Field(default_factory=date.today)

class WaterLogSummary(BaseModel):
    """Defines the structure for output of a water log summary."""
    date: str
    total_intake_oz: float
    goal_oz: float
    progress_percentage: float

# --- Todoist Schemas ---
class TaskInput(BaseModel):
    """Defines the structure for adding a new task."""
    content: str
    due_date: str | None = None
    #TODO: can add other fields here later, like priority

# --- Agent Core Schemas ---
class ChatInput(BaseModel):
    """Defines the structure for the chat interface with the Agent"""
    message: str