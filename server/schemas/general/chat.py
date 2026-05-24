"""
HDM AI - General AI Chat Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    interface: str = Field(default="client", pattern="^(client|admin|mobile)$")
    feature: str = Field(default="chat")
    search_enabled: bool = False
    deep_think: bool = False


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    suggestions: List[str] = []
    tokens_used: int = 0
    external_data_used: bool = False
    deep_think_used: bool = False
    files_analyzed: int = 0


class ConversationResponse(BaseModel):
    id: str
    title: str
    message_count: int
    last_message: Optional[str] = None
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    tokens_used: int
    timestamp: str