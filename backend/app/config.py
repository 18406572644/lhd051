from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "花语集 - 干花标本管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/dried_flowers.db"

    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
