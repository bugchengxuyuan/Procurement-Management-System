"""
Product Schemas
"""
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class ProductResponse(BaseModel):
    """产品响应Schema"""

    id: int
    product_name: str
    total_purchase_amount: float
    total_order_count: int
    avg_unit_price: float
    last_purchase_date: Optional[date]
    percentage: Optional[float] = None  # 占总采购额的百分比

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品列表响应Schema"""

    total: int
    items: List[ProductResponse]
