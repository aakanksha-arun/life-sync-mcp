from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import agent
import schemas

router = APIRouter(
    prefix="/agent",
    tags=["Agent Core"]
)

@router.post("/chat")
def handle_agent_chat(input: schemas.ChatInput) -> Dict[str, Any]:
    """
    Primary endpoint for client-side chat interaction.
    """
    return agent.invoke_agent_with_tools(input.message)