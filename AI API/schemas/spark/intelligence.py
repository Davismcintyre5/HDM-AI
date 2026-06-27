# ====================================================================================================
# 3. server/schemas/spark/intelligence.py
# ====================================================================================================
from pydantic import BaseModel, Field
from typing import Optional

class IntelSentimentRequest(BaseModel):
    text: str
    data: Optional[dict] = None

class IntelKeywordsRequest(BaseModel):
    text: str
    count: int = 10
    data: Optional[dict] = None

class IntelEntitiesRequest(BaseModel):
    text: str
    data: Optional[dict] = None

class IntelReadReceiptRequest(BaseModel):
    message: str
    sender_history: list = []
    data: Optional[dict] = None

class IntelUrgencyRequest(BaseModel):
    message: str
    data: Optional[dict] = None

class IntelLanguageRequest(BaseModel):
    text: str
    data: Optional[dict] = None