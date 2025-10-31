"""
Statistics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from database import get_db
from services.statistics_service import StatisticsService

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取Dashboard统计数据"""
    try:
        stats = StatisticsService.get_dashboard_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/monthly-trend")
def get_monthly_trend(
    months: int = Query(6, ge=1, le=24, description="月份数量"),
    db: Session = Depends(get_db),
):
    """获取月度采购趋势"""
    try:
        trend = StatisticsService.get_monthly_trend(db, months=months)
        return trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取月度趋势失败: {str(e)}")


@router.get("/payment-due")
def get_payment_due_orders(
    days_threshold: int = Query(7, ge=1, description="提醒天数阈值"),
    db: Session = Depends(get_db),
):
    """获取即将到期的先采后付订单"""
    try:
        orders = StatisticsService.get_payment_due_orders(db, days_threshold=days_threshold)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取到期订单失败: {str(e)}")


@router.get("/date-range")
def get_date_range_stats(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
):
    """获取指定日期范围的统计数据"""
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="开始日期不能大于结束日期")

        stats = StatisticsService.get_date_range_stats(db, start_date, end_date)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")
