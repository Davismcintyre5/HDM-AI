# ====================================================================================================
# server/schemas/widget/__init__.py
# ====================================================================================================
from .chat import ChatRequest, ChatResponse
from .system import HealthResponse

__all__ = ["ChatRequest", "ChatResponse", "HealthResponse"]