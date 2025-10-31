"""
订单管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import math

from ..database import get_db
from ..models.schemas import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    OrderListResponse,
    StatisticsResponse,
    ProductStatsResponse
)
from ..services import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=PurchaseOrderResponse, summary="创建订单")
def create_order(order: PurchaseOrderCreate, db: Session = Depends(get_db)):
    """创建新订单"""
    # 检查订单号是否已存在
    existing = OrderService.get_order_by_no(db, order.order_no)
    if existing:
        raise HTTPException(status_code=400, detail="订单号已存在")

    return OrderService.create_order(db, order)


@router.get("/", response_model=OrderListResponse, summary="获取订单列表")
def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=500, description="每页数量"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    shop_name: Optional[str] = Query(None, description="店铺名称"),
    product_name: Optional[str] = Query(None, description="产品名称"),
    payment_status: Optional[str] = Query(None, description="支付状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """
    获取订单列表（支持分页和筛选）

    - **page**: 页码，从1开始
    - **page_size**: 每页数量
    - **start_date**: 开始日期筛选
    - **end_date**: 结束日期筛选
    - **shop_name**: 店铺筛选
    - **product_name**: 产品筛选
    - **payment_status**: 支付状态筛选
    - **search**: 关键词搜索（订单号、产品名称）
    """
    skip = (page - 1) * page_size

    orders, total = OrderService.get_orders(
        db=db,
        skip=skip,
        limit=page_size,
        start_date=start_date,
        end_date=end_date,
        shop_name=shop_name,
        product_name=product_name,
        payment_status=payment_status,
        search=search
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return {
        "total": total,
        "orders": orders,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{order_id}", response_model=PurchaseOrderResponse, summary="获取订单详情")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """根据ID获取订单详情"""
    order = OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}", response_model=PurchaseOrderResponse, summary="更新订单")
def update_order(order_id: int, order_update: PurchaseOrderUpdate, db: Session = Depends(get_db)):
    """更新订单信息"""
    order = OrderService.update_order(db, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.delete("/{order_id}", summary="删除订单")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """删除订单"""
    success = OrderService.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="订单不存在")
    return {"message": "订单已删除", "order_id": order_id}


@router.get("/statistics/summary", response_model=StatisticsResponse, summary="获取统计摘要")
def get_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    shop_name: Optional[str] = Query(None, description="店铺名称"),
    db: Session = Depends(get_db)
):
    """
    获取统计摘要数据

    - 采购总额
    - 订单总数
    - 产品种类数
    - 按店铺统计
    - 按支付状态统计
    """
    return OrderService.get_statistics(db, start_date, end_date, shop_name)


@router.get("/statistics/products", response_model=List[ProductStatsResponse], summary="获取产品统计")
def get_product_statistics(
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    shop_name: Optional[str] = Query(None, description="店铺名称"),
    limit: int = Query(50, ge=1, le=500, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取产品统计数据

    - 产品名称
    - 采购总额
    - 订单数量
    - 平均金额
    - 占比
    """
    return OrderService.get_product_statistics(db, start_date, end_date, shop_name, limit)


@router.get("/payment/pending", response_model=List[PurchaseOrderResponse], summary="获取待支付订单")
def get_payment_pending_orders(db: Session = Depends(get_db)):
    """获取所有待支付订单（先采后付、先用后付）"""
    return OrderService.get_payment_pending_orders(db)
