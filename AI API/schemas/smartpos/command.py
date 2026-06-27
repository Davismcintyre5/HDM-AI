# ====================================================================================================
# server/schemas/smartpos/command.py
# ====================================================================================================
from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1)
    business_id: str
    parameters: dict = {}

class CommandResponse(BaseModel):
    success: bool
    intent: str = ""
    result: str = ""