"""
供应商API路由 - 简化版
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..core.database import get_session
from ..services import supplier_service

router = APIRouter()


@router.get("/list")
def get_supplier_list(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    sort_by: str = "total_amount",
    sort_order: str = "desc",
    session: Session = Depends(get_session),
):
    """获取供应商列表（带统计）

    sort_by: total_amount, order_count, last_order_date
    sort_order: desc, asc
    """
    return supplier_service.get_supplier_list(
        session, page, page_size, search, sort_by, sort_order
    )


@router.get("/{supplier_name}/stats")
def get_supplier_stats(
    supplier_name: str,
    session: Session = Depends(get_session),
):
    """获取供应商详细统计"""
    stats = supplier_service.get_supplier_stats(session, supplier_name)
    if not stats:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return stats


@router.get("/{supplier_name}/orders")
def get_supplier_orders(
    supplier_name: str,
    page: int = 1,
    page_size: int = 20,
    product_name: Optional[str] = None,
    spec: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: Session = Depends(get_session),
):
    """获取供应商的订单列表"""
    return supplier_service.get_supplier_orders(
        session,
        supplier_name,
        page,
        page_size,
        product_name,
        spec,
        start_date,
        end_date,
    )
