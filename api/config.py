"""Configuration management for the API."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    api_key: str = "dev-api-key-change-in-production"
    api_base_url: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "API_"


settings = Settings()
