"""
Pydantic数据模式定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PurchaseOrderBase(BaseModel):
    """订单基础模式"""
    order_no: str = Field(..., description="订单编号")
    product_name: str = Field(..., description="产品名称")
    purchase_amount: float = Field(..., gt=0, description="采购金额")
    order_date: Optional[datetime] = Field(None, description="订单日期")
    order_time: Optional[datetime] = Field(None, description="订单时间")
    initial_status: Optional[str] = Field(None, description="初始状态")
    payment_status: Optional[str] = Field(None, description="支付状态")
    shop_name: str = Field(..., description="店铺名称")


class PurchaseOrderCreate(PurchaseOrderBase):
    """创建订单模式"""
    pass


class PurchaseOrderUpdate(BaseModel):
    """更新订单模式"""
    product_name: Optional[str] = None
    purchase_amount: Optional[float] = None
    order_date: Optional[datetime] = None
    order_time: Optional[datetime] = None
    initial_status: Optional[str] = None
    payment_status: Optional[str] = None
    shop_name: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """订单响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_amount: float = Field(..., description="采购总额")
    total_orders: int = Field(..., description="订单总数")
    total_products: int = Field(..., description="产品种类数")
    shop_stats: List[dict] = Field(default_factory=list, description="按店铺统计")
    payment_stats: List[dict] = Field(default_factory=list, description="按支付状态统计")


class ProductStatsResponse(BaseModel):
    """产品统计响应"""
    product_name: str
    total_amount: float
    order_count: int
    avg_amount: float
    percentage: float


class DateRangeQuery(BaseModel):
    """日期范围查询"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    shop_name: Optional[str] = None
    product_name: Optional[str] = None
    payment_status: Optional[str] = None


class OrderListResponse(BaseModel):
    """订单列表响应"""
    total: int
    orders: List[PurchaseOrderResponse]
    page: int
    page_size: int
    total_pages: int


class ImportResponse(BaseModel):
    """导入响应"""
    success: bool
    message: str
    imported_count: int
    error_count: int
    total_amount: float
    total_products: int
