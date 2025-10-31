"""
Order Service - Business logic for order management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from models.order import PurchaseOrder
from models.product import Product
from schemas.order import OrderCreate, OrderUpdate


class OrderService:
    """订单服务类"""

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> PurchaseOrder:
        """
        创建订单

        Args:
            db: Database session
            order_data: Order creation data

        Returns:
            Created order object

        Raises:
            ValueError: If order_no already exists
        """
        # Check if order_no already exists
        existing_order = db.query(PurchaseOrder).filter(
            PurchaseOrder.order_no == order_data.order_no
        ).first()

        if existing_order:
            raise ValueError(f"订单编号 {order_data.order_no} 已存在")

        # Create order
        order = PurchaseOrder(
            order_no=order_data.order_no,
            product_name=order_data.product_name,
            purchase_amount=order_data.purchase_amount,
            order_date=order_data.order_date,
            order_status=order_data.order_status,
            payment_method=order_data.payment_method,
            record_time=order_data.record_time or datetime.now(),
        )

        db.add(order)
        db.flush()  # Get the ID without committing

        # Update or create product stats
        OrderService._update_product_stats(db, order_data.product_name)

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[PurchaseOrder]:
        """获取订单详情"""
        return db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

    @staticmethod
    def get_order_by_order_no(db: Session, order_no: str) -> Optional[PurchaseOrder]:
        """根据订单号获取订单"""
        return db.query(PurchaseOrder).filter(PurchaseOrder.order_no == order_no).first()

    @staticmethod
    def get_orders(
        db: Session,
        page: int = 1,
        size: int = 20,
        product_name: Optional[str] = None,
        order_status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        sort_by: str = "order_date",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        获取订单列表（分页）

        Args:
            db: Database session
            page: Page number (starting from 1)
            size: Page size
            product_name: Filter by product name
            order_status: Filter by order status
            payment_method: Filter by payment method
            start_date: Filter by start date
            end_date: Filter by end date
            search: Search by order_no or product_name
            sort_by: Sort field
            sort_order: Sort order (asc/desc)

        Returns:
            Dictionary with total count and items
        """
        query = db.query(PurchaseOrder)

        # Apply filters
        if product_name:
            query = query.filter(PurchaseOrder.product_name == product_name)

        if order_status:
            query = query.filter(PurchaseOrder.order_status == order_status)

        if payment_method:
            query = query.filter(PurchaseOrder.payment_method == payment_method)

        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)

        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)

        if search:
            query = query.filter(
                or_(
                    PurchaseOrder.order_no.like(f"%{search}%"),
                    PurchaseOrder.product_name.like(f"%{search}%"),
                )
            )

        # Get total count
        total = query.count()

        # Apply sorting
        if hasattr(PurchaseOrder, sort_by):
            sort_column = getattr(PurchaseOrder, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * size
        items = query.offset(offset).limit(size).all()

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": items,
        }

    @staticmethod
    def update_order(db: Session, order_id: int, order_data: OrderUpdate) -> Optional[PurchaseOrder]:
        """
        更新订单

        Args:
            db: Database session
            order_id: Order ID
            order_data: Order update data

        Returns:
            Updated order object or None if not found
        """
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

        if not order:
            return None

        old_product_name = order.product_name

        # Update fields
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        db.commit()
        db.refresh(order)

        # Update product stats if product changed
        if "product_name" in update_data and update_data["product_name"] != old_product_name:
            OrderService._update_product_stats(db, old_product_name)
            OrderService._update_product_stats(db, order.product_name)
        else:
            OrderService._update_product_stats(db, order.product_name)

        return order

    @staticmethod
    def delete_order(db: Session, order_id: int) -> bool:
        """
        删除订单

        Args:
            db: Database session
            order_id: Order ID

        Returns:
            True if deleted, False if not found
        """
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

        if not order:
            return False

        product_name = order.product_name

        db.delete(order)
        db.commit()

        # Update product stats
        OrderService._update_product_stats(db, product_name)

        return True

    @staticmethod
    def _update_product_stats(db: Session, product_name: str):
        """
        更新产品统计数据

        Args:
            db: Database session
            product_name: Product name
        """
        # Calculate stats from orders
        stats = db.query(
            func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
            func.count(PurchaseOrder.id).label("total_count"),
            func.avg(PurchaseOrder.purchase_amount).label("avg_price"),
            func.max(PurchaseOrder.order_date).label("last_date"),
        ).filter(PurchaseOrder.product_name == product_name).first()

        # Get or create product
        product = db.query(Product).filter(Product.product_name == product_name).first()

        if not product:
            product = Product(product_name=product_name)
            db.add(product)

        # Update stats
        product.total_purchase_amount = float(stats.total_amount) if stats.total_amount else 0
        product.total_order_count = stats.total_count if stats.total_count else 0
        product.avg_unit_price = float(stats.avg_price) if stats.avg_price else 0
        product.last_purchase_date = stats.last_date

        db.commit()
