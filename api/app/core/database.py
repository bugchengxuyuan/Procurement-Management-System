"""
数据库配置和连接管理
"""
from sqlmodel import SQLModel, create_engine, Session
from .config import settings


# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)


def init_db():
    """初始化数据库表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话（依赖注入）"""
    with Session(engine) as session:
        yield session
