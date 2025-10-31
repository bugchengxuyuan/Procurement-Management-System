"""
Purchase Order Model
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, func
from database import Base


class PurchaseOrder(Base):
    """采购订单模型"""

    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    product_name = Column(String(200), nullable=False, index=True, comment="产品名称")
    purchase_amount = Column(Numeric(10, 2), nullable=False, comment="采购金额")
    order_date = Column(Date, nullable=False, index=True, comment="订单日期")
    order_status = Column(String(20), nullable=False, index=True, comment="订单状态")
    payment_method = Column(String(20), nullable=False, index=True, comment="支付方式")
    record_time = Column(DateTime, nullable=False, comment="记录时间")

    # System fields
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建人ID")

    def __repr__(self):
        return f"<PurchaseOrder(order_no='{self.order_no}', product='{self.product_name}', amount={self.purchase_amount})>"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "product_name": self.product_name,
            "purchase_amount": float(self.purchase_amount),
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "order_status": self.order_status,
            "payment_method": self.payment_method,
            "record_time": self.record_time.isoformat() if self.record_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
