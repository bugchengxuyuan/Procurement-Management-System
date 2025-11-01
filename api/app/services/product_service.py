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

    return {
        "total": total,
        "page": page,
        "size": page_size,
        "items": products,
    }


def get_product(session: Session, product_id: int) -> Optional[Product]:
    """获取单个产品"""
    return session.get(Product, product_id)


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
