"""
Products API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas.product import ProductResponse, ProductListResponse
from services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
def get_products(
    sort_by: str = Query("total_purchase_amount", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序"),
    search: Optional[str] = Query(None, description="搜索产品名称"),
    db: Session = Depends(get_db),
):
    """获取产品列表"""
    result = ProductService.get_products(
        db,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )
    return result


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取产品详情"""
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    # Get product orders
    orders = ProductService.get_product_orders(db, product.product_name, limit=20)

    # Get monthly trend
    monthly_trend = ProductService.get_product_monthly_trend(db, product.product_name, months=6)

    return {
        "product": product.to_dict(),
        "recent_orders": [order.to_dict() for order in orders],
        "monthly_trend": monthly_trend,
    }


@router.get("/name/{product_name}")
def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    """根据产品名称获取产品"""
    product = ProductService.get_product_by_name(db, product_name)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product.to_dict()
