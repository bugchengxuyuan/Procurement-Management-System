"""
Configuration settings for the Procurement Management System
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "采购管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./procurement.db"
    # For production, use PostgreSQL:
    # DATABASE_URL: str = "postgresql://user:password@localhost/procurement_system"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Business Logic
    DEFAULT_PAYMENT_TERM_DAYS: int = 30  # 先采后付默认账期
    PAYMENT_DUE_WARNING_DAYS: int = 7  # 到期前提醒天数

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
