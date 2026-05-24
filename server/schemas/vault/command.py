# ====================================================================================================
# server/schemas/vault/command.py
# ====================================================================================================
from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    user_id: str
    command: str = Field(..., min_length=1)

class CommandResponse(BaseModel):
    intent: str
    success: bool
    result: str = ""