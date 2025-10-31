"""
Product Model
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, func
from database import Base


class Product(Base):
    """产品主数据模型"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_name = Column(String(200), unique=True, nullable=False, index=True, comment="产品名称")
    total_purchase_amount = Column(Numeric(12, 2), nullable=False, default=0, comment="累计采购金额")
    total_order_count = Column(Integer, nullable=False, default=0, comment="累计订单数")
    avg_unit_price = Column(Numeric(10, 2), nullable=False, default=0, comment="平均单价")
    last_purchase_date = Column(Date, nullable=True, comment="最近采购日期")

    # System fields
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Product(name='{self.product_name}', total_amount={self.total_purchase_amount}, orders={self.total_order_count})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "product_name": self.product_name,
            "total_purchase_amount": float(self.total_purchase_amount),
            "total_order_count": self.total_order_count,
            "avg_unit_price": float(self.avg_unit_price),
            "last_purchase_date": self.last_purchase_date.isoformat() if self.last_purchase_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
