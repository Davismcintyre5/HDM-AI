# ====================================================================================================
# server/models/core.py
# ====================================================================================================
"""
HDM AI - Core Database Models (MongoDB + Beanie ODM)
"""

from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ProjectName(str, Enum):
    GENERAL = "general"
    SMARTPOS = "smartpos"
    SPARK = "spark"
    VIBE = "vibe"
    VAULT = "vault"
    ERP = "erp"
    WIDGET = "widget"


class InboundProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"
    ERP = "erp"
    CRM = "crm"
    DATABASE = "database"
    CUSTOM = "custom"


# ================================================================================================
# USER
# ================================================================================================

class User(Document):
    """User account. Same email can have both user and admin accounts (different roles)."""
    email: str
    username: str
    hashed_password: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    api_keys_count: int = 0
    total_requests: int = 0
    tokens_used: int = 0

    class Settings:
        name = "users"
        indexes = [
            [("email", 1), ("role", 1)],  # Compound: same email OK if different roles
        ]


# ================================================================================================
# OUTBOUND API KEY (Apps call HDM AI)
# ================================================================================================

class APIKey(Document):
    user_id: Indexed(str)
    project: ProjectName
    key_prefix: str
    full_key_hash: str
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    total_requests: int = 0
    tokens_used: int = 0

    class Settings:
        name = "api_keys"


# ================================================================================================
# INBOUND API KEY (HDM AI calls external systems)
# ================================================================================================

class ThirdPartyKey(Document):
    user_id: Indexed(str)
    provider: InboundProvider
    name: str
    encrypted_key: str
    base_url: Optional[str] = None
    api_structure: Optional[dict] = None
    is_active: bool = True
    is_verified: bool = False
    last_tested: Optional[datetime] = None
    test_result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "third_party_keys"


# ================================================================================================
# USAGE LOG
# ================================================================================================

class UsageLog(Document):
    user_id: Optional[str] = None
    project: Optional[str] = None
    endpoint: str
    provider: Optional[str] = None
    model: Optional[str] = None
    tokens_used: int = 0
    response_time_ms: float = 0
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "usage_logs"