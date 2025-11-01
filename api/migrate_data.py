"""
数据迁移脚本 - 从旧数据库迁移到新系统
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select, func
from app.core.database import engine, init_db
from app.models import PurchaseOrder, Product


def migrate_from_old_database():
    """从旧数据库迁移数据"""
    print("=" * 70)
    print("开始迁移数据...")
    print("=" * 70)

    # 初始化新数据库
    init_db()

    # 连接旧数据库
    old_db_path = "../backend/procurement.db"
    if not os.path.exists(old_db_path):
        old_db_path = "../data/procurement.db"

    if not os.path.exists(old_db_path):
        print(f"错误: 找不到旧数据库文件")
        return

    import sqlite3
    old_conn = sqlite3.connect(old_db_path)
    old_cursor = old_conn.cursor()

    # 获取旧数据
    old_cursor.execute("SELECT * FROM purchase_orders")
    old_orders = old_cursor.fetchall()

    # 获取列名
    old_cursor.execute("PRAGMA table_info(purchase_orders)")
    columns = [col[1] for col in old_cursor.fetchall()]

    print(f"\n从旧数据库找到 {len(old_orders)} 条订单")

    # 迁移数据到新数据库
    with Session(engine) as session:
        success_count = 0
        error_count = 0

        for row in old_orders:
            try:
                # 构建订单字典
                order_dict = dict(zip(columns, row))

                # 检查订单是否已存在
                existing = session.exec(
                    select(PurchaseOrder).where(
                        PurchaseOrder.order_no == order_dict["order_no"]
                    )
                ).first()

                if existing:
                    continue

                # 转换日期类型
                from datetime import datetime, date
                order_date = order_dict["order_date"]
                if isinstance(order_date, str):
                    order_date = datetime.strptime(order_date, "%Y-%m-%d").date()

                record_time = order_dict["record_time"]
                if isinstance(record_time, str):
                    record_time = datetime.strptime(record_time, "%Y-%m-%d %H:%M:%S.%f")

                # 创建新订单
                order = PurchaseOrder(
                    order_no=order_dict["order_no"],
                    product_name=order_dict["product_name"],
                    purchase_amount=order_dict["purchase_amount"],
                    order_date=order_date,
                    order_status=order_dict["order_status"],
                    payment_method=order_dict["payment_method"],
                    record_time=record_time,
                )

                session.add(order)
                success_count += 1

                if success_count % 100 == 0:
                    session.commit()
                    print(f"  已迁移 {success_count} 条订单...")

            except Exception as e:
                error_count += 1
                print(f"  错误: {str(e)}")
                continue

        # 最终提交
        session.commit()

        print(f"\n订单迁移完成:")
        print(f"  成功: {success_count}")
        print(f"  失败: {error_count}")

        # 更新产品统计
        print("\n正在更新产品统计...")
        update_all_products(session)

        # 显示最终统计
        total_orders = session.exec(select(func.count(PurchaseOrder.id))).one()
        total_products = session.exec(select(func.count(Product.id))).one()
        total_amount = session.exec(select(func.sum(PurchaseOrder.purchase_amount))).one()

        print("\n" + "=" * 70)
        print("迁移完成!")
        print("=" * 70)
        print(f"订单总数: {total_orders}")
        print(f"产品总数: {total_products}")
        print(f"采购总额: ¥{total_amount:,.2f}")
        print("=" * 70)

    old_conn.close()


def update_all_products(session: Session):
    """更新所有产品统计"""
    # 获取所有产品名称
    product_names = session.exec(
        select(PurchaseOrder.product_name).distinct()
    ).all()

    for product_name in product_names:
        # 计算统计数据
        stats = session.exec(
            select(
                func.sum(PurchaseOrder.purchase_amount).label("total_amount"),
                func.count(PurchaseOrder.id).label("total_count"),
                func.avg(PurchaseOrder.purchase_amount).label("avg_price"),
                func.max(PurchaseOrder.order_date).label("last_date"),
            ).where(PurchaseOrder.product_name == product_name)
        ).first()

        # 获取或创建产品
        product = session.exec(
            select(Product).where(Product.product_name == product_name)
        ).first()

        if not product:
            product = Product(product_name=product_name)
            session.add(product)

        # 更新统计
        product.total_purchase_amount = float(stats[0]) if stats[0] else 0
        product.total_order_count = stats[1] if stats[1] else 0
        product.avg_unit_price = float(stats[2]) if stats[2] else 0
        product.last_purchase_date = stats[3]

    session.commit()
    print(f"  更新了 {len(product_names)} 个产品的统计数据")


if __name__ == "__main__":
    migrate_from_old_database()
