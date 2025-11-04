"""
产品服务
"""
from typing import Optional
from sqlmodel import Session, select, func
from ..models import Product, PurchaseOrder


def update_product_stats(session: Session, product_name: str):
    """更新产品统计数据"""
    # 查询该产品的统计数据
    stats = session.exec(
        select(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_count"),
            func.avg(PurchaseOrder.purchase_amount).label("avg_price"),
            func.max(PurchaseOrder.order_date).label("last_date"),
        ).where(PurchaseOrder.product_name == product_name)
    ).first()

    # 获取或创建产品记录
    product = session.exec(
        select(Product).where(Product.product_name == product_name)
    ).first()

    if not product:
        product = Product(product_name=product_name)
        session.add(product)

    # 更新统计数据
    product.total_purchase_amount = float(stats[0]) if stats[0] else 0
    product.total_order_count = stats[1] if stats[1] else 0
    product.avg_unit_price = float(stats[2]) if stats[2] else 0
    product.last_purchase_date = stats[3]

    session.add(product)
    session.commit()


def get_products(
    session: Session,
    page: int = 1,
    page_size: int = 100,
    search: Optional[str] = None,
):
    """获取产品列表"""
    statement = select(Product)

    if search:
        statement = statement.where(Product.product_name.contains(search))

    statement = statement.order_by(Product.total_purchase_amount.desc())

    # 总数
    count_statement = select(func.count()).select_from(statement.subquery())
    total = session.exec(count_statement).one()

    # 分页
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    products = session.exec(statement).all()

    # 计算总金额
    total_amount = sum(p.total_purchase_amount for p in products)

    # 为每个产品添加百分比
    items = []
    for product in products:
        product_dict = {
            "id": product.id,
            "product_name": product.product_name,
            "total_purchase_amount": product.total_purchase_amount,
            "total_order_count": product.total_order_count,
            "avg_unit_price": product.avg_unit_price,
            "last_purchase_date": product.last_purchase_date.isoformat() if product.last_purchase_date else None,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
            "percentage": round((product.total_purchase_amount / total_amount * 100) if total_amount > 0 else 0, 2)
        }
        items.append(product_dict)

    return {
        "total": total,
        "page": page,
        "size": page_size,
        "total_amount": total_amount,
        "items": items,
    }


def get_product(session: Session, product_id: int):
    """获取产品详情（包括订单历史和月度趋势）"""
    product = session.get(Product, product_id)
    if not product:
        return None

    # 获取最近订单
    recent_orders = session.exec(
        select(PurchaseOrder)
        .where(PurchaseOrder.product_name == product.product_name)
        .order_by(PurchaseOrder.order_date.desc())
        .limit(10)
    ).all()

    # 获取月度趋势
    monthly_trend = get_product_monthly_trend(session, product.product_name)

    return {
        "product": product,
        "recent_orders": recent_orders,
        "monthly_trend": monthly_trend,
    }


def get_product_orders(session: Session, product_name: str):
    """获取产品的所有订单"""
    statement = select(PurchaseOrder).where(
        PurchaseOrder.product_name == product_name
    ).order_by(PurchaseOrder.order_date.desc())

    return session.exec(statement).all()


def get_product_monthly_trend(session: Session, product_name: str):
    """获取产品月度趋势"""
    statement = select(
        func.strftime("%Y-%m", PurchaseOrder.order_date).label("month"),
        func.sum(PurchaseOrder.purchase_amount).label("amount"),
        func.count(PurchaseOrder.id).label("count"),
    ).where(
        PurchaseOrder.product_name == product_name
    ).group_by(
        func.strftime("%Y-%m", PurchaseOrder.order_date)
    ).order_by(
        func.strftime("%Y-%m", PurchaseOrder.order_date).desc()
    ).limit(12)

    results = session.exec(statement).all()

    return [
        {"month": r[0], "amount": float(r[1]), "count": r[2]}
        for r in results
    ]
