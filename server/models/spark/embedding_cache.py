# ====================================================================================================
# server/models/spark/embedding_cache.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, List

class EmbeddingCache(Document):
    content_hash: Indexed(str, unique=True)
    embedding: List[float] = []
    model: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    class Settings: name = "spark_embedding_cache"