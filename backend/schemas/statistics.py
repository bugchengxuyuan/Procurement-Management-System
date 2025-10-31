"""
Statistics Schemas
"""
from pydantic import BaseModel
from typing import List, Dict


class PaymentDistribution(BaseModel):
    """支付方式分布"""

    count: int
    amount: float


class MonthlyTrend(BaseModel):
    """月度趋势"""

    month: str
    amount: float
    count: int


class TopProduct(BaseModel):
    """Top产品"""

    product_name: str
    total_amount: float
    order_count: int
    percentage: float


class DashboardStats(BaseModel):
    """Dashboard统计数据"""

    total_amount: float
    total_orders: int
    total_products: int
    this_month_amount: float
    this_month_growth: float  # 环比增长率
    payment_distribution: Dict[str, PaymentDistribution]
    monthly_trend: List[MonthlyTrend]
    top_products: List[TopProduct]
