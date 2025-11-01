"""
统计API路由
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..core.database import get_session
from ..services import statistics_service

router = APIRouter()


@router.get("/dashboard")
def get_dashboard(session: Session = Depends(get_session)):
    """获取仪表盘统计数据"""
    return statistics_service.get_dashboard_stats(session)


@router.get("/payment-due")
def get_payment_due(session: Session = Depends(get_session)):
    """获取账期跟踪列表"""
    return statistics_service.get_payment_due_list(session)
