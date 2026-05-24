# ====================================================================================================
# server/models/widget/conversation.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Document):
    conversation_id: Indexed(str)
    role: MessageRole
    content: str
    tokens_used: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "widget_messages"

class Conversation(Document):
    source: Indexed(str)  # "docusoft" or "hdm_portfolio"
    user_id: Optional[str] = None  # null for public portfolio visitors
    title: str = "Widget Chat"
    is_active: bool = True
    message_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "widget_conversations"