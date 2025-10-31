"""
订单服务层
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models import PurchaseOrder
from ..models.schemas import PurchaseOrderCreate, PurchaseOrderUpdate


class OrderService:
    """订单服务"""

    @staticmethod
    def create_order(db: Session, order: PurchaseOrderCreate) -> PurchaseOrder:
        """创建订单"""
        db_order = PurchaseOrder(**order.model_dump())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def get_order(db: Session, order_id: int) -> Optional[PurchaseOrder]:
        """获取单个订单"""
        return db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

    @staticmethod
    def get_order_by_no(db: Session, order_no: str) -> Optional[PurchaseOrder]:
        """通过订单号获取订单"""
        return db.query(PurchaseOrder).filter(PurchaseOrder.order_no == order_no).first()

    @staticmethod
    def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        shop_name: Optional[str] = None,
        product_name: Optional[str] = None,
        payment_status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[PurchaseOrder], int]:
        """
        获取订单列表（带筛选和分页）

        Returns:
            (订单列表, 总数)
        """
        query = db.query(PurchaseOrder)

        # 应用筛选条件
        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        if shop_name:
            query = query.filter(PurchaseOrder.shop_name == shop_name)
        if product_name:
            query = query.filter(PurchaseOrder.product_name == product_name)
        if payment_status:
            query = query.filter(PurchaseOrder.payment_status == payment_status)
        if search:
            # 模糊搜索：订单号、产品名称
            query = query.filter(
                or_(
                    PurchaseOrder.order_no.like(f"%{search}%"),
                    PurchaseOrder.product_name.like(f"%{search}%")
                )
            )

        # 获取总数
        total = query.count()

        # 排序和分页
        orders = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()

        return orders, total

    @staticmethod
    def update_order(db: Session, order_id: int, order_update: PurchaseOrderUpdate) -> Optional[PurchaseOrder]:
        """更新订单"""
        db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not db_order:
            return None

        # 更新字段
        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)

        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def delete_order(db: Session, order_id: int) -> bool:
        """删除订单"""
        db_order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not db_order:
            return False

        db.delete(db_order)
        db.commit()
        return True

    @staticmethod
    def get_statistics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        shop_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取统计数据"""
        query = db.query(PurchaseOrder)

        # 应用筛选
        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        if shop_name:
            query = query.filter(PurchaseOrder.shop_name == shop_name)

        # 基础统计
        total_amount = query.with_entities(func.sum(PurchaseOrder.purchase_amount)).scalar() or 0
        total_orders = query.count()
        total_products = query.with_entities(func.count(distinct(PurchaseOrder.product_name))).scalar() or 0

        # 按店铺统计
        shop_stats = db.query(
            PurchaseOrder.shop_name,
            func.sum(PurchaseOrder.purchase_amount).label('total_amount'),
            func.count(PurchaseOrder.id).label('order_count')
        ).group_by(PurchaseOrder.shop_name).all()

        # 按支付状态统计
        payment_stats = query.with_entities(
            PurchaseOrder.payment_status,
            func.sum(PurchaseOrder.purchase_amount).label('total_amount'),
            func.count(PurchaseOrder.id).label('order_count')
        ).group_by(PurchaseOrder.payment_status).all()

        return {
            "total_amount": float(total_amount),
            "total_orders": total_orders,
            "total_products": total_products,
            "shop_stats": [
                {
                    "shop_name": stat[0],
                    "total_amount": float(stat[1]),
                    "order_count": stat[2]
                }
                for stat in shop_stats
            ],
            "payment_stats": [
                {
                    "payment_status": stat[0],
                    "total_amount": float(stat[1]),
                    "order_count": stat[2]
                }
                for stat in payment_stats if stat[0]
            ]
        }

    @staticmethod
    def get_product_statistics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        shop_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取产品统计"""
        query = db.query(PurchaseOrder)

        # 应用筛选
        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        if shop_name:
            query = query.filter(PurchaseOrder.shop_name == shop_name)

        # 计算总金额用于百分比
        total_amount = query.with_entities(func.sum(PurchaseOrder.purchase_amount)).scalar() or 0

        # 按产品统计
        product_stats = query.with_entities(
            PurchaseOrder.product_name,
            func.sum(PurchaseOrder.purchase_amount).label('total_amount'),
            func.count(PurchaseOrder.id).label('order_count'),
            func.avg(PurchaseOrder.purchase_amount).label('avg_amount')
        ).group_by(PurchaseOrder.product_name).order_by(func.sum(PurchaseOrder.purchase_amount).desc()).limit(limit).all()

        return [
            {
                "product_name": stat[0],
                "total_amount": float(stat[1]),
                "order_count": stat[2],
                "avg_amount": float(stat[3]),
                "percentage": float(stat[1]) / float(total_amount) * 100 if total_amount > 0 else 0
            }
            for stat in product_stats
        ]

    @staticmethod
    def get_payment_pending_orders(db: Session) -> List[PurchaseOrder]:
        """获取待支付订单（先采后付）"""
        return db.query(PurchaseOrder).filter(
            PurchaseOrder.payment_status.in_(['先采后付', '先用后付'])
        ).order_by(PurchaseOrder.order_date.desc()).all()
