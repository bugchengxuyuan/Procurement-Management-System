"""
供应商服务 - 简化版
直接从订单数据聚合统计，无需额外数据表
"""
from typing import Optional
from datetime import date
from sqlmodel import Session, select, func
from ..models import PurchaseOrder


def get_supplier_list(
    session: Session,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    sort_by: str = "total_amount",  # total_amount, order_count, last_order_date
    sort_order: str = "desc",
):
    """获取供应商列表（带统计信息）"""

    # 基础查询：按供应商分组统计
    query = select(
        PurchaseOrder.supplier.label("supplier_name"),
        func.count(PurchaseOrder.id).label("order_count"),
        func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
        func.count(func.distinct(PurchaseOrder.product_name)).label("product_count"),
        func.max(PurchaseOrder.order_date).label("last_order_date"),
        func.min(PurchaseOrder.order_date).label("first_order_date"),
    ).where(
        PurchaseOrder.supplier.is_not(None)
    ).group_by(
        PurchaseOrder.supplier
    )

    # 搜索过滤
    if search:
        query = query.where(PurchaseOrder.supplier.contains(search))

    # 排序
    if sort_by == "total_amount":
        order_col = func.sum(PurchaseOrder.purchase_amount)
    elif sort_by == "order_count":
        order_col = func.count(PurchaseOrder.id)
    elif sort_by == "last_order_date":
        order_col = func.max(PurchaseOrder.order_date)
    else:
        order_col = func.sum(PurchaseOrder.purchase_amount)

    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    # 执行查询获取所有结果（用于计算总数）
    all_results = session.exec(query).all()
    total = len(all_results)

    # 分页
    offset = (page - 1) * page_size
    paginated_results = all_results[offset:offset + page_size]

    # 格式化结果
    items = []
    for row in paginated_results:
        items.append({
            "supplier_name": row.supplier_name,
            "order_count": row.order_count,
            "total_amount": float(row.total_amount or 0),
            "product_count": row.product_count,
            "last_order_date": row.last_order_date.isoformat() if row.last_order_date else None,
            "first_order_date": row.first_order_date.isoformat() if row.first_order_date else None,
        })

    return {
        "total": total,
        "page": page,
        "size": page_size,
        "items": items,
    }


def get_supplier_stats(session: Session, supplier_name: str):
    """获取供应商详细统计"""

    # 基础统计
    basic_stats = session.exec(
        select(
            func.count(PurchaseOrder.id).label("order_count"),
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(func.distinct(PurchaseOrder.product_name)).label("product_count"),
            func.max(PurchaseOrder.order_date).label("last_order_date"),
            func.min(PurchaseOrder.order_date).label("first_order_date"),
        ).where(PurchaseOrder.supplier == supplier_name)
    ).first()

    if not basic_stats or basic_stats.order_count == 0:
        return None

    # 月度趋势（最近12个月）
    monthly_trend = session.exec(
        select(
            func.strftime("%Y-%m", PurchaseOrder.order_date).label("month"),
            func.sum(PurchaseOrder.purchase_amount).label("amount"),
            func.count(PurchaseOrder.id).label("count"),
        ).where(
            PurchaseOrder.supplier == supplier_name
        ).group_by(
            func.strftime("%Y-%m", PurchaseOrder.order_date)
        ).order_by(
            func.strftime("%Y-%m", PurchaseOrder.order_date).desc()
        ).limit(12)
    ).all()

    # 产品列表
    products = session.exec(
        select(
            PurchaseOrder.product_name,
            PurchaseOrder.spec,
            func.count(PurchaseOrder.id).label("order_count"),
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.avg(PurchaseOrder.purchase_amount).label("avg_amount"),
        ).where(
            PurchaseOrder.supplier == supplier_name
        ).group_by(
            PurchaseOrder.product_name,
            PurchaseOrder.spec
        ).order_by(
            func.sum(PurchaseOrder.purchase_amount).desc()
        )
    ).all()

    return {
        "supplier_name": supplier_name,
        "order_count": basic_stats.order_count,
        "total_amount": float(basic_stats.total_amount or 0),
        "product_count": basic_stats.product_count,
        "last_order_date": basic_stats.last_order_date.isoformat() if basic_stats.last_order_date else None,
        "first_order_date": basic_stats.first_order_date.isoformat() if basic_stats.first_order_date else None,

        "monthly_trend": [
            {
                "month": row.month,
                "amount": float(row.amount or 0),
                "count": row.count,
            }
            for row in reversed(list(monthly_trend))  # 反转以显示时间正序
        ],

        "products": [
            {
                "product_name": row.product_name,
                "spec": row.spec,
                "order_count": row.order_count,
                "total_amount": float(row.total_amount or 0),
                "avg_amount": float(row.avg_amount or 0),
            }
            for row in products
        ],
    }


def get_supplier_orders(
    session: Session,
    supplier_name: str,
    page: int = 1,
    page_size: int = 20,
    product_name: Optional[str] = None,
    spec: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """获取供应商的订单列表"""

    # 构建查询
    statement = select(PurchaseOrder).where(
        PurchaseOrder.supplier == supplier_name
    )

    # 过滤条件
    if product_name:
        statement = statement.where(PurchaseOrder.product_name.contains(product_name))
    if spec:
        statement = statement.where(PurchaseOrder.spec == spec)
    if start_date:
        statement = statement.where(PurchaseOrder.order_date >= start_date)
    if end_date:
        statement = statement.where(PurchaseOrder.order_date <= end_date)

    # 排序
    statement = statement.order_by(PurchaseOrder.order_date.desc())

    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # 分页
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    orders = session.exec(statement).all()

    return {
        "total": total,
        "page": page,
        "size": page_size,
        "items": orders,
    }
