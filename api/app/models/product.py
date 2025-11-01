"""
产品模型
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Numeric


class Product(SQLModel, table=True):
    """产品统计表"""
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str = Field(index=True, unique=True, max_length=200)
    total_purchase_amount: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    total_order_count: int = Field(default=0)
    avg_unit_price: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    last_purchase_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
