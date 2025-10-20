"""
Settings
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
SERVICE_PREFIX = os.getenv("SERVICE_PREFIX", "pjecz_casiopea_api_oauth2")


class Settings(BaseSettings):
    """Settings"""

    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "pjecz_casiopea")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_USER: str = os.getenv("DB_USER", "")
    ORIGINS: str = os.getenv("ORIGINS", "http://127.0.0.1:3000,http://localhost:3000")
    TZ: str = os.getenv("TZ", "America/Mexico_City")

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Change the order of precedence of settings sources"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
