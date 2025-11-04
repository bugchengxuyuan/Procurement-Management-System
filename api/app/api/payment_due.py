"""
先采后付按还款日分组API
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from datetime import date as date_type
from typing import Optional

from ..db import get_session
from ..services import payment_due_service

router = APIRouter(prefix="/payment-due", tags=["先采后付管理"])


@router.get("/groups")
def get_payment_due_groups(
    include_paid: bool = Query(False, description="是否包含已付款订单"),
    session: Session = Depends(get_session)
):
    """获取先采后付订单按还款日分组统计

    返回格式：
    [
        {
            "due_date": "2025-11-08",
            "days_remaining": 4,
            "status": "warning",  // overdue/warning/normal
            "status_text": "即将到期（4天后）",
            "total_count": 40,
            "total_amount": 26329.93,
            "unpaid_count": 30,
            "unpaid_amount": 7578.05,
            "paid_count": 10,
            "paid_amount": 18751.88,
            "receive_month_start": "2025-10-02",
            "receive_month_end": "2025-10-31",
            "is_current_month": false,
            "is_incomplete": false,
            "order_ids": [1, 2, 3, ...]
        },
        ...
    ]

    字段说明：
    - is_current_month: 是否包含当月确认收货的订单
    - is_incomplete: 账单是否可能不完整（当月未结束）
    """
    return payment_due_service.get_payment_due_groups(session, include_paid)


@router.get("/groups/{due_date}/detail")
def get_payment_due_group_detail(
    due_date: date_type,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    session: Session = Depends(get_session)
):
    """获取指定还款日的订单详情列表

    Args:
        due_date: 还款日期，格式：YYYY-MM-DD，例如 2025-11-08
        page: 页码
        page_size: 每页数量

    Returns:
        订单详情列表和分页信息
    """
    return payment_due_service.get_payment_due_group_detail(
        session, due_date, page, page_size
    )


@router.post("/groups/{due_date}/mark-paid")
def mark_payment_due_group_as_paid(
    due_date: date_type,
    session: Session = Depends(get_session)
):
    """将指定还款日的所有未付款订单标记为已付款

    Args:
        due_date: 还款日期，格式：YYYY-MM-DD，例如 2025-11-08

    Returns:
        更新结果统计
        {
            "due_date": "2025-11-08",
            "updated_count": 30,
            "updated_amount": 7578.05
        }

    使用场景：
    - 完成还款后，批量标记该还款日的所有订单为已付款
    - 避免逐个订单手动标记
    """
    return payment_due_service.mark_payment_due_group_as_paid(session, due_date)
