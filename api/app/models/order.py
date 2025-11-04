"""
采购订单模型
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Numeric
from pydantic import field_serializer


class PurchaseOrderBase(SQLModel):
    """订单基础字段"""
    order_no: str = Field(index=True, max_length=50)  # 移除unique约束以支持一单多品
    product_name: str = Field(index=True, max_length=200)
    spec: Optional[str] = Field(default=None, index=True, max_length=200)  # 新增：规格字段
    purchase_amount: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    supplier: Optional[str] = Field(default=None, index=True, max_length=300)  # 新增：供应商字段
    order_date: date = Field(index=True)
    order_status: str = Field(index=True, max_length=20)
    payment_method: str = Field(index=True, max_length=20)
    payment_status: Optional[str] = Field(default=None, index=True, max_length=20)  # 付款状态：unpaid/paid/partial
    receive_date: Optional[date] = Field(default=None, index=True)  # 确认收货时间（1688账期按此计算）
    record_time: datetime

    @field_serializer('purchase_amount')
    def serialize_amount(self, value: Decimal) -> float:
        """将Decimal转换为float用于JSON序列化"""
        return float(value)


class PurchaseOrder(PurchaseOrderBase, table=True):
    """采购订单表"""
    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PurchaseOrderCreate(PurchaseOrderBase):
    """创建订单"""
    pass


class PurchaseOrderUpdate(SQLModel):
    """更新订单"""
    product_name: Optional[str] = None
    spec: Optional[str] = None  # 新增：规格字段
    purchase_amount: Optional[Decimal] = None
    supplier: Optional[str] = None  # 新增：供应商字段
    order_date: Optional[date] = None
    order_status: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None  # 付款状态
    receive_date: Optional[date] = None  # 确认收货时间
    record_time: Optional[datetime] = None
