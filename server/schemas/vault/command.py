# server/schemas/vault/command.py
from pydantic import BaseModel, Field
from typing import Optional

class CommandRequest(BaseModel):
    user_id: str
    command: str = Field(..., min_length=1)
    data: Optional[dict] = None

class CommandResponse(BaseModel):
    intent: str
    success: bool
    result: str = ""