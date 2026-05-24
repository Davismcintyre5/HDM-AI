# ====================================================================================================
# server/config.py
# ====================================================================================================
"""
HDM AI - Application Configuration
Loaded from .env | Production & Development Ready
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # ================================================================================================
    # APP
    # ================================================================================================
    APP_NAME: str = "HDM AI"
    VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("PORT", 5002))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ================================================================================================
    # JWT
    # ================================================================================================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 1))

    # ================================================================================================
    # DATABASES
    # ================================================================================================
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ================================================================================================
    # AI PROVIDERS
    # ================================================================================================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")

    # ================================================================================================
    # PROJECT API KEYS (Server-to-Server)
    # ================================================================================================
    HDM_GENERAL_KEY: str = os.getenv("HDM_GENERAL_KEY", "")
    HDM_SMARTPOS_KEY: str = os.getenv("HDM_SMARTPOS_KEY", "")
    HDM_SPARK_KEY: str = os.getenv("HDM_SPARK_KEY", "")
    HDM_VIBE_KEY: str = os.getenv("HDM_VIBE_KEY", "")
    HDM_VAULT_KEY: str = os.getenv("HDM_VAULT_KEY", "")
    HDM_ERP_KEY: str = os.getenv("HDM_ERP_KEY", "")
    HDM_WIDGET_KEY: str = os.getenv("HDM_WIDGET_KEY", "")

    # ================================================================================================
    # RATE LIMITING
    # ================================================================================================
    RATE_LIMIT_GLOBAL: int = int(os.getenv("RATE_LIMIT_GLOBAL", 1000))
    RATE_LIMIT_PER_USER: int = int(os.getenv("RATE_LIMIT_PER_USER", 30))

    # ================================================================================================
    # CORS
    # ================================================================================================
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:19006",
    )

    # ================================================================================================
    # FILE UPLOADS
    # ================================================================================================
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", 10))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    # ================================================================================================
    # LOGGING
    # ================================================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", 7))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


# Singleton
settings = Settings()