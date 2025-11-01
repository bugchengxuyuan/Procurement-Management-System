"""
统计服务
"""
from datetime import date, timedelta
from sqlmodel import Session, select, func
from ..models import PurchaseOrder, Product
from ..core.config import settings


def get_dashboard_stats(session: Session):
    """获取仪表盘统计数据"""
    # 总体统计
    total_stats = session.exec(
        select(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_orders"),
        )
    ).first()

    total_products = session.exec(select(func.count(Product.id))).one()

    # 本月统计
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    this_month_amount = session.exec(
        select(func.sum(PurchaseOrder.purchase_amount)).where(
            PurchaseOrder.order_date >= first_day_of_month
        )
    ).first()

    # 上月统计
    if today.month == 1:
        last_month_start = date(today.year - 1, 12, 1)
        last_month_end = date(today.year - 1, 12, 31)
    else:
        last_month_start = date(today.year, today.month - 1, 1)
        # 本月第一天的前一天
        last_month_end = first_day_of_month - timedelta(days=1)

    last_month_amount = session.exec(
        select(func.sum(PurchaseOrder.purchase_amount)).where(
            PurchaseOrder.order_date >= last_month_start,
            PurchaseOrder.order_date <= last_month_end,
        )
    ).first()

    # 计算环比增长
    this_month_val = float(this_month_amount or 0)
    last_month_val = float(last_month_amount or 0)

    if last_month_val > 0:
        growth = ((this_month_val - last_month_val) / last_month_val) * 100
    else:
        growth = -100 if this_month_val == 0 else 100

    # 支付方式分布
    payment_distribution = {}
    payment_stats = session.exec(
        select(
            PurchaseOrder.payment_method,
            func.count(PurchaseOrder.id).label("count"),
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
        ).group_by(PurchaseOrder.payment_method)
    ).all()

    for method, count, amount in payment_stats:
        payment_distribution[method] = {
            "count": count,
            "amount": float(amount or 0),
        }

    # 月度趋势（最近6个月）
    monthly_trend = []
    trend_stats = session.exec(
        select(
            func.strftime("%Y-%m", PurchaseOrder.order_date).label("month"),
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
            func.count(PurchaseOrder.id).label("count"),
        ).group_by(
            func.strftime("%Y-%m", PurchaseOrder.order_date)
        ).order_by(
            func.strftime("%Y-%m", PurchaseOrder.order_date).desc()
        ).limit(6)
    ).all()

    for month, amount, count in trend_stats:
        monthly_trend.append({
            "month": month,
            "amount": float(amount or 0),
            "count": count,
        })

    # TOP产品
    total_product_amount = session.exec(
        select(func.sum(Product.total_purchase_amount))
    ).one()

    top_products = []
    products = session.exec(
        select(Product).order_by(Product.total_purchase_amount.desc()).limit(5)
    ).all()

    for product in products:
        percentage = 0
        if total_product_amount and total_product_amount > 0:
            percentage = round(
                (float(product.total_purchase_amount) / float(total_product_amount)) * 100,
                2
            )

        top_products.append({
            "product_name": product.product_name,
            "total_amount": float(product.total_purchase_amount),
            "order_count": product.total_order_count,
            "percentage": percentage,
        })

    return {
        "total_amount": float(total_stats[0] or 0),
        "total_orders": total_stats[1] or 0,
        "total_products": total_products,
        "this_month_amount": this_month_val,
        "this_month_growth": round(growth, 1),
        "payment_distribution": payment_distribution,
        "monthly_trend": monthly_trend,
        "top_products": top_products,
    }


def get_payment_due_list(session: Session):
    """获取账期跟踪列表"""
    # 查询所有先采后付订单
    statement = select(PurchaseOrder).where(
        PurchaseOrder.payment_method == "先采后付"
    ).order_by(PurchaseOrder.order_date.desc())

    orders = session.exec(statement).all()

    today = date.today()
    result = []

    for order in orders:
        # 计算到期日期
        due_date = order.order_date + timedelta(days=settings.DEFAULT_PAYMENT_TERM_DAYS)
        days_remaining = (due_date - today).days

        # 判断状态
        if days_remaining < 0:
            status = "overdue"  # 已逾期
        elif days_remaining <= settings.WARNING_DAYS:
            status = "warning"  # 即将到期
        else:
            status = "normal"  # 正常

        result.append({
            "id": order.id,
            "order_no": order.order_no,
            "product_name": order.product_name,
            "purchase_amount": float(order.purchase_amount),
            "order_date": order.order_date,
            "due_date": due_date,
            "days_remaining": days_remaining,
            "status": status,
        })

    return result
