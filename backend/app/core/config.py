import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "HireShield Backend"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Frontend origin for CORS
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Database connection URL (defaults to SQLite for local development, can be set to PostgreSQL)
    DATABASE_URL: str = "sqlite:///./hireshield.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = [self.FRONTEND_URL]
        # Also include common local dev variations
        for origin in ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]:
            if origin not in origins:
                origins.append(origin)
        return origins


settings = Settings()
