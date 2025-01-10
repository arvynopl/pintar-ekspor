# backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import List

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/pintar_ekspor")
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

    # Environment settings
    ENV: str = os.getenv("ENV", "development")

    # CORS settings - Changed to use string parsing instead of direct List typing
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,https://pintar-ekspor-frontend.vercel.app"
    )
    ALLOWED_HOSTS: str = os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,pintar-ekspor-production.up.railway.app"
    )

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pintar Ekspor"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # FinTrackIt configuration (for email service)
    FINTRACKIT_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

    # Method to get origins as list
    def get_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Method to get hosts as list
    def get_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

@lru_cache()
def get_settings():
    return Settings()