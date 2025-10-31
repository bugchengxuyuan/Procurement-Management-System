"""
Product Service - Business logic for product management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from models.product import Product
from models.order import PurchaseOrder


class ProductService:
    """产品服务类"""

    @staticmethod
    def get_products(
        db: Session,
        sort_by: str = "total_purchase_amount",
        sort_order: str = "desc",
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取产品列表

        Args:
            db: Database session
            sort_by: Sort field (total_purchase_amount, total_order_count, avg_unit_price, last_purchase_date)
            sort_order: Sort order (asc/desc)
            search: Search by product name

        Returns:
            Dictionary with total count and items
        """
        query = db.query(Product)

        # Apply search filter
        if search:
            query = query.filter(Product.product_name.like(f"%{search}%"))

        # Get total amount for percentage calculation
        total_amount_result = db.query(func.sum(Product.total_purchase_amount)).scalar()
        total_amount = float(total_amount_result) if total_amount_result else 0

        # Apply sorting
        if hasattr(Product, sort_by):
            sort_column = getattr(Product, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        items = query.all()

        # Add percentage to each product
        products_with_percentage = []
        for product in items:
            product_dict = product.to_dict()
            if total_amount > 0:
                product_dict["percentage"] = round((float(product.total_purchase_amount) / total_amount) * 100, 2)
            else:
                product_dict["percentage"] = 0
            products_with_percentage.append(product_dict)

        return {
            "total": len(products_with_percentage),
            "total_amount": total_amount,
            "items": products_with_percentage,
        }

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """获取产品详情"""
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_product_by_name(db: Session, product_name: str) -> Optional[Product]:
        """根据产品名称获取产品"""
        return db.query(Product).filter(Product.product_name == product_name).first()

    @staticmethod
    def get_product_orders(
        db: Session,
        product_name: str,
        limit: int = 20,
    ) -> List[PurchaseOrder]:
        """
        获取产品的订单历史

        Args:
            db: Database session
            product_name: Product name
            limit: Max number of orders to return

        Returns:
            List of orders
        """
        orders = (
            db.query(PurchaseOrder)
            .filter(PurchaseOrder.product_name == product_name)
            .order_by(PurchaseOrder.order_date.desc())
            .limit(limit)
            .all()
        )

        return orders

    @staticmethod
    def get_product_monthly_trend(
        db: Session,
        product_name: str,
        months: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        获取产品月度采购趋势

        Args:
            db: Database session
            product_name: Product name
            months: Number of months to include

        Returns:
            List of monthly trend data
        """
        # Query monthly stats using SQLite date functions
        query = db.query(
            func.strftime('%Y-%m', PurchaseOrder.order_date).label('month'),
            func.sum(PurchaseOrder.purchase_amount).label('amount'),
            func.count(PurchaseOrder.id).label('count')
        ).filter(
            PurchaseOrder.product_name == product_name
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
    def get_top_products(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取Top产品

        Args:
            db: Database session
            limit: Number of top products

        Returns:
            List of top products
        """
        # Get total amount
        total_amount_result = db.query(func.sum(Product.total_purchase_amount)).scalar()
        total_amount = float(total_amount_result) if total_amount_result else 0

        # Get top products
        products = (
            db.query(Product)
            .order_by(Product.total_purchase_amount.desc())
            .limit(limit)
            .all()
        )

        top_products = []
        for product in products:
            percentage = 0
            if total_amount > 0:
                percentage = round((float(product.total_purchase_amount) / total_amount) * 100, 2)

            top_products.append({
                "product_name": product.product_name,
                "total_amount": float(product.total_purchase_amount),
                "order_count": product.total_order_count,
                "percentage": percentage,
            })

        return top_products
