"""
订单API路由
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..core.database import get_session
from ..models import PurchaseOrderCreate, PurchaseOrderUpdate
from ..services import order_service

router = APIRouter()


@router.post("")
def create_order(
    order: PurchaseOrderCreate,
    session: Session = Depends(get_session),
):
    """创建订单"""
    return order_service.create_order(session, order)


@router.get("")
def get_orders(
    page: int = 1,
    page_size: int = 20,
    product_name: Optional[str] = None,
    spec: Optional[str] = None,
    supplier: Optional[str] = None,
    payment_status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """获取订单列表"""
    return order_service.get_orders(
        session,
        page,
        page_size,
        product_name,
        spec,
        supplier,
        payment_status,
        start_date,
        end_date,
        search,
    )


@router.get("/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)):
    """获取订单详情"""
    order = order_service.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}")
def update_order(
    order_id: int,
    order_update: PurchaseOrderUpdate,
    session: Session = Depends(get_session),
):
    """更新订单"""
    order = order_service.update_order(session, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)):
    """删除订单"""
    success = order_service.delete_order(session, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"message": "删除成功"}
