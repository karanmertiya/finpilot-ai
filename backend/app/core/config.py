import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinPilot AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "finpilot-insecure-dev-secret-key-32chars-minimum-prod-override!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./finpilot.db"

    # AI Configuration
    LLM_PROVIDER: str = "gemini"  # gemini, openai, anthropic, mock
    LLM_MODEL: str = "gemini-1.5-flash"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Embeddings
    EMBEDDING_PROVIDER: str = "local"  # local, gemini, openai
    EMBEDDING_MODEL: str = "text-embedding-004"
    SIMILARITY_THRESHOLD: float = 0.35
    MAX_RETRIEVAL_CHUNKS: int = 4

    # Agent constraints
    MAX_AGENT_STEPS: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60

    # Documents & Uploads
    MAX_UPLOAD_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".csv"]

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
