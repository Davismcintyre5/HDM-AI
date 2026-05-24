# ====================================================================================================
# server/models/erp/file_extraction.py
# ====================================================================================================
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional

class FileExtraction(Document):
    tenant_id: Indexed(str)
    filename: str
    file_type: str
    extracted_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "erp_file_extractions"