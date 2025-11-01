"""
API路由
"""
from fastapi import APIRouter
from .orders import router as orders_router
from .products import router as products_router
from .statistics import router as statistics_router
from .excel_io import router as excel_router

api_router = APIRouter()

api_router.include_router(orders_router, prefix="/orders", tags=["订单管理"])
api_router.include_router(products_router, prefix="/products", tags=["产品管理"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["数据统计"])
api_router.include_router(excel_router, prefix="/excel", tags=["Excel导入导出"])

__all__ = ["api_router"]
