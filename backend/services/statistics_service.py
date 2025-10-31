"""
Statistics Service - Business logic for statistics and analytics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from models.order import PurchaseOrder
from models.product import Product
from dateutil.relativedelta import relativedelta


class StatisticsService:
    """统计服务类"""

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        获取Dashboard统计数据

        Args:
            db: Database session

        Returns:
            Dashboard statistics
        """
        # Total stats
        total_stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_orders"),
        ).first()

        total_amount = float(total_stats.total_amount) if total_stats.total_amount else 0
        total_orders = total_stats.total_orders if total_stats.total_orders else 0

        # Total products
        total_products = db.query(func.count(Product.id)).scalar() or 0

        # This month stats
        today = date.today()
        first_day_this_month = date(today.year, today.month, 1)

        this_month_stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
        ).filter(
            PurchaseOrder.order_date >= first_day_this_month
        ).first()

        this_month_amount = float(this_month_stats.amount) if this_month_stats.amount else 0

        # Last month stats for growth calculation
        first_day_last_month = first_day_this_month - relativedelta(months=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)

        last_month_stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
        ).filter(
            and_(
                PurchaseOrder.order_date >= first_day_last_month,
                PurchaseOrder.order_date <= last_day_last_month,
            )
        ).first()

        last_month_amount = float(last_month_stats.amount) if last_month_stats.amount else 0

        # Calculate growth rate
        if last_month_amount > 0:
            this_month_growth = round(((this_month_amount - last_month_amount) / last_month_amount) * 100, 2)
        else:
            this_month_growth = 0

        # Payment distribution
        payment_dist = db.query(
            PurchaseOrder.payment_method,
            func.count(PurchaseOrder.id).label("count"),
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
        ).group_by(PurchaseOrder.payment_method).all()

        payment_distribution = {}
        for item in payment_dist:
            payment_distribution[item.payment_method] = {
                "count": item.count,
                "amount": float(item.amount),
            }

        # Monthly trend (last 6 months)
        monthly_trend = StatisticsService.get_monthly_trend(db, months=6)

        # Top 5 products
        from services.product_service import ProductService
        top_products = ProductService.get_top_products(db, limit=5)

        return {
            "total_amount": total_amount,
            "total_orders": total_orders,
            "total_products": total_products,
            "this_month_amount": this_month_amount,
            "this_month_growth": this_month_growth,
            "payment_distribution": payment_distribution,
            "monthly_trend": monthly_trend,
            "top_products": top_products,
        }

    @staticmethod
    def get_monthly_trend(db: Session, months: int = 6) -> List[Dict[str, Any]]:
        """
        获取月度采购趋势

        Args:
            db: Database session
            months: Number of months to include

        Returns:
            List of monthly trend data
        """
        # Query monthly stats
        query = db.query(
            func.strftime('%Y-%m', PurchaseOrder.order_date).label('month'),
            func.sum(PurchaseOrder.purchase_amount).label('amount'),
            func.count(PurchaseOrder.id).label('count')
        ).group_by(
            func.strftime('%Y-%m', PurchaseOrder.order_date)
        ).order_by(
            func.strftime('%Y-%m', PurchaseOrder.order_date).desc()
        ).limit(months)

        results = query.all()

        trends = []
        for result in reversed(results):
            trends.append({
                "month": result.month,
                "amount": float(result.amount),
                "count": result.count,
            })

        return trends

    @staticmethod
    def get_payment_due_orders(db: Session, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """
        获取即将到期的先采后付订单

        Args:
            db: Database session
            days_threshold: Days threshold for warning

        Returns:
            List of orders with due date information
        """
        # Get all 先采后付 orders
        orders = db.query(PurchaseOrder).filter(
            PurchaseOrder.payment_method == "先采后付"
        ).all()

        today = date.today()
        result = []

        for order in orders:
            # Calculate due date (30 days after order date)
            from config import settings
            due_date = order.order_date + timedelta(days=settings.DEFAULT_PAYMENT_TERM_DAYS)
            days_remaining = (due_date - today).days

            # Determine status
            if days_remaining < 0:
                status = "overdue"  # 已逾期
            elif days_remaining <= days_threshold:
                status = "warning"  # 即将到期
            else:
                status = "normal"  # 正常

            result.append({
                "order_id": order.id,
                "order_no": order.order_no,
                "product_name": order.product_name,
                "purchase_amount": float(order.purchase_amount),
                "order_date": order.order_date,
                "due_date": due_date,
                "days_remaining": days_remaining,
                "status": status,
            })

        # Sort by days_remaining (ascending)
        result.sort(key=lambda x: x["days_remaining"])

        return result

    @staticmethod
    def get_date_range_stats(
        db: Session,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        获取指定日期范围的统计数据

        Args:
            db: Database session
            start_date: Start date
            end_date: End date

        Returns:
            Statistics for the date range
        """
        stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_orders"),
            func.avg(PurchaseOrder.purchase_amount).label("avg_amount"),
        ).filter(
            and_(
                PurchaseOrder.order_date >= start_date,
                PurchaseOrder.order_date <= end_date,
            )
        ).first()

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_amount": float(stats.total_amount) if stats.total_amount else 0,
            "total_orders": stats.total_orders if stats.total_orders else 0,
            "avg_order_amount": float(stats.avg_amount) if stats.avg_amount else 0,
        }
