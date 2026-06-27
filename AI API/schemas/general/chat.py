"""
HDM AI Engine - General AI Chat Schemas
Stateless — MERN sends full context per request
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    # Required
    message: str = Field(..., min_length=1, max_length=10000)
    
    # MERN-passed context
    user_id: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None  # Full conversation history
    data: Optional[Dict[str, Any]] = None  # External/business data
    
    # AI configuration
    provider: Optional[str] = "groq"  # "groq" or "gemini"
    model: Optional[str] = None  # Override default model
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    
    # Features
    search_enabled: Optional[bool] = False
    deep_think: Optional[bool] = False
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    tokens_used: int = 0
    provider: str
    external_data_used: bool = False
    deep_think_used: bool = False
    files_analyzed: int = 0
    suggestions: List[str] = []


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