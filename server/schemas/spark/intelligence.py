# ====================================================================================================
# server/schemas/spark/intelligence.py
# ====================================================================================================
from pydantic import BaseModel, Field

class IntelSentimentRequest(BaseModel):
    text: str

class IntelKeywordsRequest(BaseModel):
    text: str
    count: int = 10

class IntelEntitiesRequest(BaseModel):
    text: str

class IntelReadReceiptRequest(BaseModel):
    message: str
    sender_history: list = []

class IntelUrgencyRequest(BaseModel):
    message: str

class IntelLanguageRequest(BaseModel):
    text: str