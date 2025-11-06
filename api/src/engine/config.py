"""Configuration management for the API."""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    api_key: str = "dev-api-key-change-in-production"
    api_base_url: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    class Config:
        # Use the .env file in the api directory specifically
        env_file = Path(__file__).parent / ".env"
        env_prefix = "API_"
        # Allow extra fields to prevent validation errors
        extra = "allow"


settings = Settings()
