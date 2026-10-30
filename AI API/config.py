# ====================================================================================================
# HDM AI Engine — config.py
# ====================================================================================================

import os
from pydantic_settings import BaseSettings
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

    # Redis (optional)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # AI Provider Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_LEARN: str = os.getenv("GROQ_API_KEY_LEARN", "")
    GROQ_API_KEY_COMPLETION: str = os.getenv("GROQ_API_KEY_COMPLETION", "")
    GROQ_API_KEY_COMPLETION_BACKUP: str = os.getenv("GROQ_API_KEY_COMPLETION_BACKUP", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # MERN Internal
    MERN_INTERNAL_URL: str = os.getenv("MERN_INTERNAL_URL", "http://localhost:5000")
    MERN_INTERNAL_SECRET: str = os.getenv("MERN_INTERNAL_SECRET", "dev-secret-change-me")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()