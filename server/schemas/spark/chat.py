# ====================================================================================================
# 1. server/schemas/spark/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatAskRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    language: str = "en"
    data: Optional[dict] = None

class ChatTranslateRequest(BaseModel):
    text: str
    target_language: str
    data: Optional[dict] = None

class ChatRewriteRequest(BaseModel):
    text: str
    style: str = "professional"
    data: Optional[dict] = None

class ChatDraftRequest(BaseModel):
    prompt: str
    tone: str = "casual"
    data: Optional[dict] = None

class ChatExplainRequest(BaseModel):
    text: str
    level: str = "simple"
    data: Optional[dict] = None

class ChatSummarizeRequest(BaseModel):
    text: str
    max_length: int = 200
    data: Optional[dict] = None

class ChatVoiceRequest(BaseModel):
    audio_base64: str
    language: str = "en"
    data: Optional[dict] = None

class ChatEmojiRequest(BaseModel):
    message: str
    count: int = 3
    data: Optional[dict] = None

class ChatAutocompleteRequest(BaseModel):
    partial_text: str
    max_suggestions: int = 3
    data: Optional[dict] = None

class ChatToneRequest(BaseModel):
    text: str
    data: Optional[dict] = None

class ChatFormatRequest(BaseModel):
    text: str
    format_type: str = "markdown"
    data: Optional[dict] = None

class ChatQuoteRequest(BaseModel):
    original_message: str
    reply: str
    data: Optional[dict] = None

class ChatPollRequest(BaseModel):
    topic: str
    options_count: int = 4
    data: Optional[dict] = None

class ChatContextReplyRequest(BaseModel):
    message: str
    context_messages: List[str] = []
    data: Optional[dict] = None