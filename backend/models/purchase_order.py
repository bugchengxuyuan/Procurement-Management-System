"""
采购订单数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base


class PurchaseOrder(Base):
    """采购订单明细模型 - 每条记录是订单中的一个产品"""
    __tablename__ = "purchase_orders"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 订单基本信息（一个订单可以有多个产品，所以不设置unique）
    order_no = Column(String(50), index=True, nullable=False, comment="订单编号")
    product_name = Column(String(200), index=True, nullable=False, comment="产品名称")
    purchase_amount = Column(Float, nullable=False, comment="采购金额")

    # 日期信息
    order_date = Column(DateTime, index=True, comment="订单日期")
    order_time = Column(DateTime, comment="订单时间")

    # 状态信息
    initial_status = Column(String(50), comment="初始状态")
    payment_status = Column(String(50), index=True, comment="支付状态")

    # 店铺信息
    shop_name = Column(String(100), index=True, comment="店铺名称")

    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    # 创建复合索引以提高查询性能
    # 添加复合唯一索引：订单号+产品名称保证唯一
    __table_args__ = (
        Index('idx_date_shop', 'order_date', 'shop_name'),
        Index('idx_product_shop', 'product_name', 'shop_name'),
        Index('idx_payment_shop', 'payment_status', 'shop_name'),
        Index('idx_order_product', 'order_no', 'product_name', unique=True),
    )

    def __repr__(self):
        return f"<PurchaseOrder(order_no={self.order_no}, product={self.product_name}, amount={self.purchase_amount})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "product_name": self.product_name,
            "purchase_amount": self.purchase_amount,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "order_time": self.order_time.isoformat() if self.order_time else None,
            "initial_status": self.initial_status,
            "payment_status": self.payment_status,
            "shop_name": self.shop_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
