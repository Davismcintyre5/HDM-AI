# ====================================================================================================
# HDM AI Engine - config.py
# Stateless AI Server | No DB | No Auth | Optional Redis
# ====================================================================================================

import os
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # App
    APP_NAME: str = "HDM AI Engine"
    VERSION: str = "2.0.0"
    PORT: int = int(os.getenv("PORT", 5002))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_URL: str = os.getenv("APP_URL", "")

    # Redis (optional — completely disabled if REDIS_ENABLED=false)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # AI Provider Fallback Keys (used when MERN is unreachable)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_ERP: str = os.getenv("GROQ_API_KEY_ERP", "")
    GROQ_API_KEY_SMARTPOS: str = os.getenv("GROQ_API_KEY_SMARTPOS", "")
    GROQ_API_KEY_SPARK: str = os.getenv("GROQ_API_KEY_SPARK", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # MERN Internal Connection
    MERN_INTERNAL_URL: str = os.getenv("MERN_INTERNAL_URL", "http://localhost:5000")
    MERN_INTERNAL_SECRET: str = os.getenv("MERN_INTERNAL_SECRET", "dev-secret-change-me")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()