"""
统计API路由
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from ..core.database import get_session
from ..services import statistics_service

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(
    start_date: Optional[date] = Query(None, description="开始日期，用于筛选月度趋势"),
    end_date: Optional[date] = Query(None, description="结束日期，用于筛选月度趋势"),
    session: Session = Depends(get_session)
):
    """获取仪表盘统计数据

    注意：采购总额、订单总数等始终显示所有数据，不受时间筛选影响
    时间筛选只影响月度采购趋势图表
    """
    return statistics_service.get_dashboard_stats(session, start_date, end_date)


@router.get("/payment-due")
def get_payment_due(session: Session = Depends(get_session)):
    """获取账期跟踪列表"""
    return statistics_service.get_payment_due_list(session)


@router.get("/suppliers")
def get_suppliers(session: Session = Depends(get_session)):
    """获取所有供应商列表"""
    return statistics_service.get_unique_suppliers(session)


@router.get("/specs")
def get_specs(session: Session = Depends(get_session)):
    """获取所有规格列表"""
    return statistics_service.get_unique_specs(session)
