"""
HDM AI - General AI File Upload Model
"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional


class FileUpload(Document):
    """Uploaded file metadata."""
    user_id: Indexed(str)
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    path: str
    extracted_text: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "file_uploads"