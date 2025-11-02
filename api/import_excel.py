"""
从Excel文件导入采购数据
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from app.core.database import engine, init_db
from app.models import PurchaseOrder, Product
from app.utils.excel_handler import parse_excel_orders
from datetime import datetime


def import_from_excel(excel_file_path: str):
    """从Excel文件导入数据"""
    print("=" * 70)
    print("开始从Excel导入数据...")
    print("=" * 70)

    # 检查文件是否存在
    if not os.path.exists(excel_file_path):
        print(f"❌ 错误: 找不到Excel文件: {excel_file_path}")
        return False

    print(f"\n📄 Excel文件: {excel_file_path}")

    # 初始化数据库
    init_db()

    # 读取Excel文件
    try:
        with open(excel_file_path, "rb") as f:
            file_content = f.read()

        print("\n正在解析Excel文件...")
        orders, errors = parse_excel_orders(file_content)

        print(f"✅ 解析完成: 找到 {len(orders)} 条订单")

        if errors:
            print(f"⚠️  解析警告: {len(errors)} 条记录有问题")
            for error in errors[:5]:  # 只显示前5个错误
                print(f"   行 {error['row']}: {error['error']}")
            if len(errors) > 5:
                print(f"   ... 还有 {len(errors) - 5} 个错误")

    except Exception as e:
        print(f"❌ 读取Excel文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 导入数据到数据库
    print("\n开始导入到数据库...")
    with Session(engine) as session:
        success_count = 0
        error_count = 0
        skipped_count = 0

        for order_data in orders:
            try:
                # 检查订单明细是否已存在（订单号+产品名组合）
                # 这样支持一单多品：同一订单号可以有多个不同产品
                existing = session.exec(
                    select(PurchaseOrder).where(
                        PurchaseOrder.order_no == order_data["order_no"],
                        PurchaseOrder.product_name == order_data["product_name"]
                    )
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                # 创建新订单明细
                order = PurchaseOrder(**order_data)
                session.add(order)
                success_count += 1

                if success_count % 50 == 0:
                    session.commit()
                    print(f"  已导入 {success_count} 条订单...")

            except Exception as e:
                error_count += 1
                print(f"  ❌ 导入失败: {str(e)}")
                print(f"     订单数据: {order_data}")
                continue

        # 最终提交
        session.commit()

        print(f"\n订单导入完成:")
        print(f"  ✅ 成功: {success_count}")
        print(f"  ⏭️  跳过(已存在): {skipped_count}")
        print(f"  ❌ 失败: {error_count}")

        # 更新产品统计
        if success_count > 0:
            print("\n正在更新产品统计...")
            update_all_products(session)

        # 显示最终统计
        from sqlmodel import func
        total_orders = session.exec(select(func.count(PurchaseOrder.id))).one()
        total_products = session.exec(select(func.count(Product.id))).one()
        total_amount = session.exec(select(func.sum(PurchaseOrder.purchase_amount))).one()

        print("\n" + "=" * 70)
        print("导入完成!")
        print("=" * 70)
        print(f"订单总数: {total_orders}")
        print(f"产品总数: {total_products}")
        print(f"采购总额: ¥{total_amount:,.2f}" if total_amount else "采购总额: ¥0.00")
        print("=" * 70)

    return success_count > 0


def update_all_products(session: Session):
    """更新所有产品统计"""
    from sqlmodel import func

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
    print(f"  ✅ 更新了 {len(product_names)} 个产品的统计数据")


if __name__ == "__main__":
    # 获取Excel文件路径
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        # 默认使用项目根目录下的Excel文件
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excel_file = os.path.join(project_root, "采购表-2（最新版.xlsx")

    success = import_from_excel(excel_file)
    sys.exit(0 if success else 1)
