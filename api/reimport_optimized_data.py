"""
从采购表-优化版重新导入数据
"""
import sys
import os

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select, delete
from app.core.database import engine, init_db
from app.models import PurchaseOrder, Product
from app.utils.excel_handler import parse_excel_orders
from datetime import datetime


def reimport_from_optimized_excel(excel_file_path: str, clear_existing: bool = True):
    """从优化版Excel重新导入数据"""
    print("=" * 80)
    print("从采购表-优化版重新导入数据")
    print("=" * 80)

    # 检查文件是否存在
    if not os.path.exists(excel_file_path):
        print(f"❌ 错误: 找不到Excel文件: {excel_file_path}")
        return False

    print(f"\n📄 Excel文件: {excel_file_path}")

    # 初始化数据库
    print("\n正在初始化数据库...")
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

    # 统计解析结果
    payment_status_count = {}
    for order in orders:
        status = order.get('payment_status', '未知')
        payment_status_count[status] = payment_status_count.get(status, 0) + 1

    print(f"\n付款状态分布:")
    for status, count in payment_status_count.items():
        print(f"  - {status}: {count}条")

    # 导入数据到数据库
    with Session(engine) as session:
        # 清空现有数据
        if clear_existing:
            print("\n正在清空现有数据...")

            # 获取当前数据统计
            existing_orders = session.exec(select(PurchaseOrder)).all()
            existing_products = session.exec(select(Product)).all()

            print(f"  当前订单数: {len(existing_orders)}")
            print(f"  当前产品数: {len(existing_products)}")

            # 确认清空
            print("\n⚠️  即将清空所有现有数据，是否继续？")
            print("  输入 'yes' 确认，其他任意键取消：", end=" ")
            confirmation = input().strip().lower()

            if confirmation != 'yes':
                print("❌ 操作已取消")
                return False

            # 删除所有订单
            session.exec(delete(PurchaseOrder))
            session.exec(delete(Product))
            session.commit()

            print("  ✅ 已清空所有数据")

        # 导入新数据
        print("\n开始导入新数据...")
        success_count = 0
        error_count = 0

        for order_data in orders:
            try:
                # 创建新订单
                order = PurchaseOrder(**order_data)
                session.add(order)
                success_count += 1

                if success_count % 100 == 0:
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

        # 付款状态统计
        print("\n数据库中的付款状态分布:")
        for status in ['即时付款', '账期未到', '账期已结']:
            count = session.exec(
                select(func.count(PurchaseOrder.id)).where(
                    PurchaseOrder.payment_status == status
                )
            ).one()
            amount = session.exec(
                select(func.sum(PurchaseOrder.purchase_amount)).where(
                    PurchaseOrder.payment_status == status
                )
            ).one() or 0
            print(f"  - {status}: {count}条, 金额 ¥{amount:,.2f}")

        print("\n" + "=" * 80)
        print("导入完成!")
        print("=" * 80)
        print(f"订单总数: {total_orders}")
        print(f"产品总数: {total_products}")
        print(f"采购总额: ¥{total_amount:,.2f}" if total_amount else "采购总额: ¥0.00")
        print("=" * 80)

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
    # 默认使用项目根目录下的"采购表_优化版.xlsx"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_file = os.path.join(project_root, "采购表_优化版.xlsx")

    # 也可以通过命令行参数指定文件
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]

    success = reimport_from_optimized_excel(excel_file, clear_existing=True)
    sys.exit(0 if success else 1)
