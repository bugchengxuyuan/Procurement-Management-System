"""
Order Schemas for validation
"""
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List


class OrderCreate(BaseModel):
    """订单创建Schema"""

    order_no: str = Field(..., min_length=19, max_length=19, description="订单编号，19位数字")
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    purchase_amount: Decimal = Field(..., description="采购金额")
    order_date: date = Field(..., description="订单日期")
    order_status: str = Field(..., description="订单状态：已付款/先采后付")
    payment_method: str = Field(..., description="支付方式：已付款/先采后付")
    record_time: Optional[datetime] = Field(None, description="记录时间")

    @validator("order_no")
    def validate_order_no(cls, v):
        if not v.isdigit():
            raise ValueError("订单编号必须是19位数字")
        return v

    @validator("order_status")
    def validate_order_status(cls, v):
        if v not in ["已付款", "先采后付"]:
            raise ValueError("订单状态必须是：已付款 或 先采后付")
        return v

    @validator("payment_method")
    def validate_payment_method(cls, v):
        if v not in ["已付款", "先采后付", "先用后付"]:
            raise ValueError("支付方式必须是：已付款、先采后付 或 先用后付")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "order_no": "3655240347686198464",
                "product_name": "高铸胶",
                "purchase_amount": 2880.00,
                "order_date": "2025-10-28",
                "order_status": "已付款",
                "payment_method": "已付款",
            }
        }


class OrderUpdate(BaseModel):
    """订单更新Schema"""

    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    purchase_amount: Optional[Decimal] = None
    order_date: Optional[date] = None
    order_status: Optional[str] = None
    payment_method: Optional[str] = None
    record_time: Optional[datetime] = None

    @validator("order_status")
    def validate_order_status(cls, v):
        if v and v not in ["已付款", "先采后付"]:
            raise ValueError("订单状态必须是：已付款 或 先采后付")
        return v

    @validator("payment_method")
    def validate_payment_method(cls, v):
        if v and v not in ["已付款", "先采后付", "先用后付"]:
            raise ValueError("支付方式必须是：已付款、先采后付 或 先用后付")
        return v


class OrderResponse(BaseModel):
    """订单响应Schema"""

    id: int
    order_no: str
    product_name: str
    purchase_amount: float
    order_date: date
    order_status: str
    payment_method: str
    record_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应Schema"""

    total: int
    page: int
    size: int
    items: List[OrderResponse]
