"""
User Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(100), nullable=True, comment="真实姓名")
    role = Column(String(20), nullable=False, default="viewer", comment="角色: admin, purchaser, viewer")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否激活")

    # System fields
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
