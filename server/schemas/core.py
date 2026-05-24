"""
HDM AI - Core Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List
from datetime import datetime


# ================================================================================================
# AUTH
# ================================================================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ================================================================================================
# OUTBOUND KEYS
# ================================================================================================

class OutboundKeyCreate(BaseModel):
    project: str = Field(default="general")
    name: str = Field(min_length=1, max_length=100)

class OutboundKeyResponse(BaseModel):
    id: str
    project: str
    key_prefix: str
    name: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime] = None
    total_requests: int = 0
    tokens_used: int = 0
    full_key: Optional[str] = None


# ================================================================================================
# INBOUND KEYS
# ================================================================================================

class InboundKeyCreate(BaseModel):
    provider: str = Field(..., pattern="^(openai|anthropic|deepseek|google|erp|crm|database|custom)$")
    name: str = Field(min_length=1, max_length=100)
    api_key: str = Field(min_length=1)
    base_url: Optional[str] = None
    api_structure: Optional[dict] = None

class InboundKeyUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    api_structure: Optional[dict] = None
    is_active: Optional[bool] = None

class InboundKeyResponse(BaseModel):
    id: str
    provider: str
    name: str
    key_prefix: str
    base_url: Optional[str] = None
    api_structure: Optional[dict] = None
    is_active: bool
    is_verified: bool
    last_tested: Optional[datetime] = None
    test_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ================================================================================================
# ADMIN
# ================================================================================================

class AdminKeyCreate(BaseModel):
    user_id: str
    project: str
    name: str = Field(min_length=1, max_length=100)

class AdminKeyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    project: Optional[str] = None


# ================================================================================================
# COMMON
# ================================================================================================

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

class PaginationMeta(BaseModel):
    total: int
    page: int
    pages: int