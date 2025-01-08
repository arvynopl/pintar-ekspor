# backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # JWT settings
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # Environment settings
    ENV: str = "development"  # Added this line - defaults to "development"
    
    # CORS settings
    ALLOWED_ORIGINS: str = "*"  # Default to allow all in development
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pintar Ekspor"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()