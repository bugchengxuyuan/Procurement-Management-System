"""
产品API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..core.database import get_session
from ..services import product_service

router = APIRouter()


@router.get("")
def get_products(
    page: int = 1,
    page_size: int = 100,
    search: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """获取产品列表"""
    return product_service.get_products(session, page, page_size, search)


@router.get("/{product_id}")
def get_product(product_id: int, session: Session = Depends(get_session)):
    """获取产品详情"""
    product = product_service.get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.get("/name/{product_name}/orders")
def get_product_orders(product_name: str, session: Session = Depends(get_session)):
    """获取产品的所有订单"""
    return product_service.get_product_orders(session, product_name)


@router.get("/name/{product_name}/trend")
def get_product_trend(product_name: str, session: Session = Depends(get_session)):
    """获取产品月度趋势"""
    return product_service.get_product_monthly_trend(session, product_name)
