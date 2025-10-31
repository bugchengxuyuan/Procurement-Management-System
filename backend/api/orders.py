"""
Orders API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """创建订单"""
    try:
        order = OrderService.create_order(db, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.get("", response_model=OrderListResponse)
def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    product_name: Optional[str] = Query(None, description="产品名称"),
    order_status: Optional[str] = Query(None, description="订单状态"),
    payment_method: Optional[str] = Query(None, description="支付方式"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("order_date", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序"),
    db: Session = Depends(get_db),
):
    """获取订单列表"""
    result = OrderService.get_orders(
        db,
        page=page,
        size=size,
        product_name=product_name,
        order_status=order_status,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return result


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """获取订单详情"""
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_data: OrderUpdate, db: Session = Depends(get_db)):
    """更新订单"""
    order = OrderService.update_order(db, order_id, order_data)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """删除订单"""
    success = OrderService.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"message": "订单删除成功"}
