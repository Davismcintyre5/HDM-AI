"""
HDM AI - General AI Conversation & Message Models
"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Document):
    """Individual message in a conversation."""
    conversation_id: Indexed(str)
    role: MessageRole
    content: str
    tokens_used: int = 0
    model: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"


class Conversation(Document):
    """Multi-turn conversation."""
    user_id: Indexed(str)
    title: str = "New Conversation"
    interface: str = "client"  # client, admin, mobile
    is_active: bool = True
    message_count: int = 0
    total_tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message: Optional[str] = None

    class Settings:
        name = "conversations"