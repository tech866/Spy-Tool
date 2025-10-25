"""
Configuration settings for the Ad-Intelligence Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ad-Intelligence Platform"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/adspy"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # S3/MinIO
    S3_ENDPOINT: Optional[str] = None  # Use None for AWS S3
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "adspy-thumbs"
    S3_REGION: str = "us-east-1"

    # Security
    API_KEY: Optional[str] = None
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # AI Tagging
    AI_TAGGING_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4-turbo-preview"  # or claude-3-sonnet-20240229

    # Ingestion
    INGEST_INTERVAL_MINUTES: int = 15
    INGEST_MAX_ADS_PER_RUN: int = 200
    INGEST_TIMEOUT_SECONDS: int = 300

    # Platform Flags
    ENABLE_META_ADAPTER: bool = True
    ENABLE_TIKTOK_ADAPTER: bool = True
    ENABLE_YOUTUBE_ADAPTER: bool = True

    # Observability
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
