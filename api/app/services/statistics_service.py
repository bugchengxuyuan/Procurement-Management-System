"""
统计服务
"""
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional
from sqlmodel import Session, select, func
from ..models import PurchaseOrder, Product
from ..core.config import settings


def get_dashboard_stats(
    session: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """获取仪表盘统计数据

    Args:
        session: 数据库会话
        start_date: 开始日期（可选），用于筛选月度趋势
        end_date: 结束日期（可选），用于筛选月度趋势

    注意：采购总额、订单总数、产品总数等始终显示所有数据，不受时间筛选影响
    """
    # 总体统计（不受时间筛选影响，始终显示所有数据）
    total_stats = session.exec(
        select(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_orders"),
        )
    ).first()

    total_products = session.exec(select(func.count(Product.id))).one()

    # 本月统计（不受时间筛选影响）
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    this_month_amount = session.exec(
        select(func.sum(PurchaseOrder.purchase_amount)).where(
            PurchaseOrder.order_date >= first_day_of_month
        )
    ).first()

    # 上月统计（不受时间筛选影响）
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

    # 支付方式分布（不受时间筛选影响）
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

    # 月度趋势（受时间筛选影响）
    monthly_trend = []

    # 构建月度趋势查询
    trend_query = select(
        func.strftime("%Y-%m", PurchaseOrder.order_date).label("month"),
        func.sum(PurchaseOrder.purchase_amount).label("amount"),
        func.count(PurchaseOrder.id).label("count"),
    )

    # 如果指定了时间范围，则筛选
    if start_date and end_date:
        trend_query = trend_query.where(
            PurchaseOrder.order_date >= start_date,
            PurchaseOrder.order_date <= end_date,
        )
    elif start_date:
        trend_query = trend_query.where(PurchaseOrder.order_date >= start_date)
    elif end_date:
        trend_query = trend_query.where(PurchaseOrder.order_date <= end_date)

    trend_query = trend_query.group_by(
        func.strftime("%Y-%m", PurchaseOrder.order_date)
    ).order_by(
        func.strftime("%Y-%m", PurchaseOrder.order_date).desc()
    )

    # 如果没有指定时间范围，默认显示最近6个月
    if not start_date and not end_date:
        trend_query = trend_query.limit(6)

    trend_stats = session.exec(trend_query).all()

    for month, amount, count in trend_stats:
        monthly_trend.append({
            "month": month,
            "amount": float(amount or 0),
            "count": count,
        })

    # TOP产品（不受时间筛选影响）
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
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    }


def get_payment_due_list(session: Session):
    """获取账期跟踪列表（月结8号逻辑）

    业务规则：
    - 还款日：每月8号
    - 月结原则：本月确认收货，次月8号还款
    - 举例：10月确认收货 → 11月8日还款
    - 优先显示未付款订单（payment_status = 'unpaid'），兼容旧数据
    """
    # 查询先采后付订单
    # 尝试使用 payment_status 过滤，如果字段不存在则查询全部
    try:
        # 优先查询未付款订单
        statement = select(PurchaseOrder).where(
            PurchaseOrder.payment_method == "先采后付",
            PurchaseOrder.payment_status == "unpaid"
        ).order_by(PurchaseOrder.order_date.desc())
        orders = session.exec(statement).all()
    except Exception:
        # 如果 payment_status 字段不存在，查询所有先采后付订单
        statement = select(PurchaseOrder).where(
            PurchaseOrder.payment_method == "先采后付"
        ).order_by(PurchaseOrder.order_date.desc())
        orders = session.exec(statement).all()

    today = date.today()
    result = []

    for order in orders:
        # 计算到期日期（次月8号）
        # 重要：账期按确认收货时间计算，不是订单日期
        try:
            if hasattr(order, 'receive_date') and order.receive_date:
                # 使用确认收货时间
                base_date = order.receive_date
            else:
                # 如果没有确认收货时间，降级使用订单日期
                base_date = order.order_date
        except AttributeError:
            # 如果 receive_date 字段不存在，使用订单日期
            base_date = order.order_date

        # 获取确认收货所在月份的下个月
        next_month = base_date + relativedelta(months=1)
        # 设置为下个月的8号
        due_date = date(next_month.year, next_month.month, settings.PAYMENT_DUE_DAY)

        days_remaining = (due_date - today).days

        # 判断状态
        if days_remaining < 0:
            status = "overdue"  # 已逾期
        elif days_remaining <= settings.WARNING_DAYS:
            status = "warning"  # 即将到期
        else:
            status = "normal"  # 正常

        # 构建结果，兼容新旧字段
        item = {
            "id": order.id,
            "order_no": order.order_no,
            "product_name": order.product_name,
            "supplier": order.supplier,
            "purchase_amount": float(order.purchase_amount),
            "order_date": order.order_date,
            "due_date": due_date,
            "days_remaining": days_remaining,
            "status": status,
        }

        # 添加可选字段
        if hasattr(order, 'receive_date'):
            item["receive_date"] = order.receive_date
        if hasattr(order, 'payment_status'):
            item["payment_status"] = order.payment_status

        result.append(item)

    return result


def get_unique_suppliers(session: Session):
    """获取所有唯一供应商列表"""
    suppliers = session.exec(
        select(PurchaseOrder.supplier)
        .where(PurchaseOrder.supplier.is_not(None))
        .distinct()
        .order_by(PurchaseOrder.supplier)
    ).all()

    return {"suppliers": [s for s in suppliers if s]}


def get_unique_specs(session: Session):
    """获取所有唯一规格列表"""
    specs = session.exec(
        select(PurchaseOrder.spec)
        .where(PurchaseOrder.spec.is_not(None))
        .distinct()
        .order_by(PurchaseOrder.spec)
    ).all()

    return {"specs": [s for s in specs if s]}
