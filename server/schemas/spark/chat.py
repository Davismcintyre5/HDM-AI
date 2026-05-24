# ====================================================================================================
# server/schemas/spark/chat.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatAskRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    language: str = "en"

class ChatTranslateRequest(BaseModel):
    text: str
    target_language: str

class ChatRewriteRequest(BaseModel):
    text: str
    style: str = "professional"

class ChatDraftRequest(BaseModel):
    prompt: str
    tone: str = "casual"

class ChatExplainRequest(BaseModel):
    text: str
    level: str = "simple"

class ChatSummarizeRequest(BaseModel):
    text: str
    max_length: int = 200

class ChatVoiceRequest(BaseModel):
    audio_base64: str
    language: str = "en"

class ChatEmojiRequest(BaseModel):
    message: str
    count: int = 3

class ChatAutocompleteRequest(BaseModel):
    partial_text: str
    max_suggestions: int = 3

class ChatToneRequest(BaseModel):
    text: str

class ChatFormatRequest(BaseModel):
    text: str
    format_type: str = "markdown"

class ChatQuoteRequest(BaseModel):
    original_message: str
    reply: str

class ChatPollRequest(BaseModel):
    topic: str
    options_count: int = 4

class ChatContextReplyRequest(BaseModel):
    message: str
    context_messages: List[str] = []