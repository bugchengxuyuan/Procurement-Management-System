"""
应用配置
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "采购管理系统"
    APP_VERSION: str = "2.0.0"

    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/procurement.db"

    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 业务配置
    PAYMENT_DUE_DAY: int = 8  # 先采后付月结还款日（每月8号）
    WARNING_DAYS: int = 7  # 到期提醒天数（提前7天预警）

    class Config:
        env_file = ".env"


settings = Settings()
