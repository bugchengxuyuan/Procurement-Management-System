"""
Excel数据导入工具
"""
import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy import func

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.database import SessionLocal, init_db
from backend.models import PurchaseOrder


def clean_and_import_excel(file_path: str):
    """
    从Excel文件导入数据到数据库

    Args:
        file_path: Excel文件路径
    """
    print("🚀 开始导入数据...")

    # 初始化数据库
    init_db()
    print("✅ 数据库表已创建")

    db = SessionLocal()

    try:
        # 读取CAISHENDAO数据
        print("\n📊 读取 CAISHENDAO 数据...")
        df1 = pd.read_excel(file_path, sheet_name='CAISHENDAO', skiprows=6)
        order_columns = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', '先采后付']
        orders_df1 = df1[order_columns].copy()
        orders_df1 = orders_df1.dropna(subset=['订单编号', '产品名称'])
        orders_df1 = orders_df1[orders_df1['订单编号'].astype(str).str.len() > 10]
        orders_df1['店铺'] = 'CAISHENDAO'
        orders_df1 = orders_df1.rename(columns={'先采后付': '支付状态'})

        print(f"   找到 {len(orders_df1)} 条订单")

        # 读取Kitchen maestro数据
        print("\n📊 读取 Kitchen maestro 数据...")
        df2 = pd.read_excel(file_path, sheet_name='Kitchen maestro', skiprows=6)
        order_columns2 = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', '采购方式']
        orders_df2 = df2[order_columns2].copy()
        orders_df2 = orders_df2.dropna(subset=['订单编号', '产品名称'])
        orders_df2 = orders_df2[orders_df2['订单编号'].astype(str).str.len() > 10]
        orders_df2['采购金额'] = pd.to_numeric(orders_df2['采购金额'], errors='coerce')
        orders_df2 = orders_df2.dropna(subset=['采购金额'])
        orders_df2['店铺'] = 'Kitchen maestro'
        orders_df2 = orders_df2.rename(columns={'采购方式': '支付状态'})

        print(f"   找到 {len(orders_df2)} 条订单")

        # 合并数据
        all_orders = pd.concat([orders_df1, orders_df2], ignore_index=True)
        print(f"\n📦 总计 {len(all_orders)} 条订单待导入")

        # 清空现有数据
        db.query(PurchaseOrder).delete()
        db.commit()
        print("✅ 已清空现有数据")

        # 导入数据
        imported_count = 0
        error_count = 0

        for idx, row in all_orders.iterrows():
            try:
                # 跳过采购金额为NaN或无效的行
                if pd.isna(row['采购金额']) or pd.isna(row['订单编号']) or pd.isna(row['产品名称']):
                    error_count += 1
                    continue

                order = PurchaseOrder(
                    order_no=str(row['订单编号']),
                    product_name=str(row['产品名称']),
                    purchase_amount=float(row['采购金额']),
                    order_date=pd.to_datetime(row['日期']) if pd.notna(row['日期']) else None,
                    order_time=pd.to_datetime(row['时间']) if pd.notna(row['时间']) else None,
                    initial_status=str(row['初始状态']) if pd.notna(row['初始状态']) else None,
                    payment_status=str(row['支付状态']) if pd.notna(row['支付状态']) else None,
                    shop_name=str(row['店铺'])
                )
                db.add(order)
                imported_count += 1

                # 每100条提交一次
                if imported_count % 100 == 0:
                    db.commit()
                    print(f"   已导入 {imported_count} 条...")

            except Exception as e:
                error_count += 1
                print(f"   ⚠️  第 {idx} 行导入失败: {e}")
                db.rollback()  # 回滚失败的事务
                continue

        # 提交剩余数据
        db.commit()

        print(f"\n✅ 导入完成!")
        print(f"   成功: {imported_count} 条")
        print(f"   失败: {error_count} 条")

        # 统计信息
        total_orders = db.query(PurchaseOrder).count()
        total_amount = db.query(func.sum(PurchaseOrder.purchase_amount)).scalar() or 0
        total_products = db.query(PurchaseOrder.product_name).distinct().count()

        print(f"\n📈 数据库统计:")
        print(f"   订单总数: {total_orders}")
        print(f"   采购总额: ¥{total_amount:,.2f}")
        print(f"   产品种类: {total_products}")

    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Excel文件路径
    excel_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "采购表-2（最新版.xlsx"
    )

    if os.path.exists(excel_file):
        clean_and_import_excel(excel_file)
    else:
        print(f"❌ 文件不存在: {excel_file}")
