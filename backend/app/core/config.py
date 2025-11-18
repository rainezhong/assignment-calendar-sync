"""
Core configuration using Pydantic settings.
Loads from environment variables and .env file.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Assignment Calendar Sync API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006",  # Expo
        "http://localhost:19000",  # Expo web
    ]

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # AI Services
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def async_database_url(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")


# Global settings instance
settings = Settings()
