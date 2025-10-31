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
        # 读取CAISHENDAO数据 - 使用正确的列位置
        print("\n📊 读取 CAISHENDAO 数据...")

        # 直接读取原始数据，不用header
        df1_raw = pd.read_excel(file_path, sheet_name='CAISHENDAO', header=None)

        # 订单数据在第10-16列（索引从0开始）
        # 从第7行开始（跳过表头和汇总行）
        orders_df1 = df1_raw.iloc[7:, 10:17].copy()
        orders_df1.columns = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', '先采后付']

        # 清理数据
        orders_df1 = orders_df1.dropna(subset=['订单编号', '产品名称'], how='all')
        orders_df1['订单编号'] = orders_df1['订单编号'].astype(str)
        orders_df1 = orders_df1[orders_df1['订单编号'].str.len() > 10]
        orders_df1['采购金额'] = pd.to_numeric(orders_df1['采购金额'], errors='coerce')
        orders_df1 = orders_df1.dropna(subset=['采购金额'])

        orders_df1['店铺'] = 'CAISHENDAO'
        orders_df1 = orders_df1.rename(columns={'先采后付': '支付状态'})

        print(f"   找到 {len(orders_df1)} 条订单")

        # 读取Kitchen maestro数据 - 使用正确的列位置
        print("\n📊 读取 Kitchen maestro 数据...")

        # 直接读取原始数据，不用header
        df2_raw = pd.read_excel(file_path, sheet_name='Kitchen maestro', header=None)

        # 订单数据也在第10-16列（索引从0开始）
        # 从第7行开始（跳过表头和汇总行）
        orders_df2 = df2_raw.iloc[7:, 10:17].copy()
        orders_df2.columns = ['日期', '初始状态', '订单编号', '产品名称', '采购金额', '时间', '采购方式']

        # 清理数据
        orders_df2 = orders_df2.dropna(subset=['订单编号', '产品名称'], how='all')
        orders_df2['订单编号'] = orders_df2['订单编号'].astype(str)
        orders_df2 = orders_df2[orders_df2['订单编号'].str.len() > 10]
        orders_df2['采购金额'] = pd.to_numeric(orders_df2['采购金额'], errors='coerce')
        orders_df2 = orders_df2.dropna(subset=['采购金额'])

        orders_df2['店铺'] = 'Kitchen maestro'
        orders_df2 = orders_df2.rename(columns={'采购方式': '支付状态'})

        print(f"   找到 {len(orders_df2)} 条订单")

        # 合并数据
        all_orders = pd.concat([orders_df1, orders_df2], ignore_index=True)
        print(f"\n📦 总计 {len(all_orders)} 条订单（合并前）")

        # ⭐ 数据清理（不去重 - 一个订单可以有多个产品）
        # 先清理无效数据
        all_orders = all_orders.dropna(subset=['订单编号', '产品名称', '采购金额'])

        # 统计订单明细
        unique_orders = all_orders['订单编号'].nunique()
        total_items = len(all_orders)
        print(f"\n📦 订单统计:")
        print(f"   唯一订单数: {unique_orders}")
        print(f"   订单明细数: {total_items}")
        print(f"   平均每单产品数: {total_items/unique_orders:.2f}")

        # 按订单号+产品名称去重（防止完全重复的记录）
        dup_count = all_orders.duplicated(subset=['订单编号', '产品名称']).sum()
        if dup_count > 0:
            print(f"\n⚠️  发现 {dup_count} 条完全重复的订单明细")
            all_orders = all_orders.drop_duplicates(subset=['订单编号', '产品名称'], keep='last')
            print(f"   去重后: {len(all_orders)} 条明细")

        print(f"\n📦 准备导入 {len(all_orders)} 条订单明细")

        # 清空现有数据
        db.query(PurchaseOrder).delete()
        db.commit()
        print("✅ 已清空现有数据")

        # 导入数据
        imported_count = 0
        error_count = 0
        skipped_count = 0

        for idx, row in all_orders.iterrows():
            try:
                # 二次验证数据有效性
                if pd.isna(row['采购金额']) or pd.isna(row['订单编号']) or pd.isna(row['产品名称']):
                    skipped_count += 1
                    continue

                # 创建订单对象
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

                # 每50条提交一次（减小批次避免大事务）
                if imported_count % 50 == 0:
                    try:
                        db.commit()
                        print(f"   已导入 {imported_count} 条...")
                    except Exception as commit_error:
                        print(f"   ⚠️  提交失败，回滚并继续: {commit_error}")
                        db.rollback()
                        error_count += 1

            except Exception as e:
                error_count += 1
                print(f"   ⚠️  第 {idx} 行处理失败: {str(e)[:100]}")
                db.rollback()
                continue

        # 提交剩余数据
        try:
            db.commit()
            print(f"   最终提交完成")
        except Exception as e:
            print(f"   ⚠️  最终提交失败: {e}")
            db.rollback()

        print(f"\n✅ 导入完成!")
        print(f"   成功: {imported_count} 条")
        print(f"   跳过: {skipped_count} 条")
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
