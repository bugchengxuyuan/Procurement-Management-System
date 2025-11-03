"""
订单服务
"""
from typing import Optional
from datetime import date
from sqlmodel import Session, select, func, or_
from ..models import PurchaseOrder, PurchaseOrderCreate, PurchaseOrderUpdate
from .product_service import update_product_stats


def create_order(session: Session, order: PurchaseOrderCreate) -> PurchaseOrder:
    """创建订单"""
    db_order = PurchaseOrder.model_validate(order)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    # 更新产品统计
    update_product_stats(session, db_order.product_name)

    return db_order


def get_orders(
    session: Session,
    page: int = 1,
    page_size: int = 20,
    product_name: Optional[str] = None,
    spec: Optional[str] = None,
    supplier: Optional[str] = None,
    order_status: Optional[str] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
):
    """获取订单列表"""
    # 构建查询
    statement = select(PurchaseOrder)

    # 过滤条件
    if product_name:
        statement = statement.where(PurchaseOrder.product_name == product_name)
    if spec:
        statement = statement.where(PurchaseOrder.spec == spec)
    if supplier:
        statement = statement.where(PurchaseOrder.supplier == supplier)
    if order_status:
        statement = statement.where(PurchaseOrder.order_status == order_status)
    if payment_method:
        statement = statement.where(PurchaseOrder.payment_method == payment_method)
    if start_date:
        statement = statement.where(PurchaseOrder.order_date >= start_date)
    if end_date:
        statement = statement.where(PurchaseOrder.order_date <= end_date)
    if search:
        statement = statement.where(
            or_(
                PurchaseOrder.order_no.contains(search),
                PurchaseOrder.product_name.contains(search),
                PurchaseOrder.spec.contains(search),
                PurchaseOrder.supplier.contains(search),
            )
        )

    # 排序
    statement = statement.order_by(PurchaseOrder.created_at.desc())

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


def get_order(session: Session, order_id: int) -> Optional[PurchaseOrder]:
    """获取单个订单"""
    return session.get(PurchaseOrder, order_id)


def update_order(
    session: Session, order_id: int, order_update: PurchaseOrderUpdate
) -> Optional[PurchaseOrder]:
    """更新订单"""
    db_order = session.get(PurchaseOrder, order_id)
    if not db_order:
        return None

    old_product_name = db_order.product_name

    # 更新字段
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    # 更新产品统计
    update_product_stats(session, db_order.product_name)
    if old_product_name != db_order.product_name:
        update_product_stats(session, old_product_name)

    return db_order


def delete_order(session: Session, order_id: int) -> bool:
    """删除订单"""
    db_order = session.get(PurchaseOrder, order_id)
    if not db_order:
        return False

    product_name = db_order.product_name

    session.delete(db_order)
    session.commit()

    # 更新产品统计
    update_product_stats(session, product_name)

    return True
