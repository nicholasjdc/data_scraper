import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    fred_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env file
    )


# Global settings instance
settings = Settings()

# Fallback to environment variable if not in .env file
if not settings.fred_api_key:
    settings.fred_api_key = os.getenv("FRED_API_KEY")

if not settings.alpha_vantage_api_key:
    settings.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

