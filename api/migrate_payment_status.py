"""
数据库迁移脚本：添加付款状态和确认收货时间字段
"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "procurement.db"

# Bill files
BILL_NOV = Path(__file__).parent.parent / "2025-11-04_11-09-46-账单明细导出-1058866.xlsx"
BILL_DEC = Path(__file__).parent.parent / "2025-11-04_11-11-12-账单明细导出-1058896.xlsx"


def add_columns_if_not_exists(conn):
    """添加新列到数据库（如果不存在）"""
    cursor = conn.cursor()

    # 检查列是否存在
    cursor.execute("PRAGMA table_info(purchase_orders)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'payment_status' not in columns:
        print("添加 payment_status 列...")
        cursor.execute("""
            ALTER TABLE purchase_orders
            ADD COLUMN payment_status TEXT
        """)
        conn.commit()
        print("✅ payment_status 列添加成功")
    else:
        print("✅ payment_status 列已存在")

    if 'receive_date' not in columns:
        print("添加 receive_date 列...")
        cursor.execute("""
            ALTER TABLE purchase_orders
            ADD COLUMN receive_date DATE
        """)
        conn.commit()
        print("✅ receive_date 列添加成功")
    else:
        print("✅ receive_date 列已存在")


def parse_bill_file(file_path):
    """解析账单文件，提取订单号和确认收货时间"""
    print(f"\n读取账单文件: {file_path.name}")

    df = pd.read_excel(file_path)

    # 找到账单明细列表的起始行
    detail_start_row = None
    for i, row in df.iterrows():
        if '账单明细列表' in str(row[0]):
            detail_start_row = i + 1
            break

    if detail_start_row is None:
        print("❌ 未找到账单明细列表")
        return []

    # 提取订单数据
    orders = []
    for i in range(detail_start_row, len(df)):
        row = df.iloc[i]

        # 跳过表头行
        if '订单号' in str(row[0]):
            continue

        # 检查是否有订单号
        order_no = str(row[0])
        if not order_no or order_no == 'nan' or len(order_no) < 10:
            break

        # 提取确认收货时间
        receive_time = row[5]  # 第6列是确认收货时间
        if pd.notna(receive_time):
            # 解析日期时间，只保留日期部分
            if isinstance(receive_time, str):
                receive_date = datetime.strptime(receive_time, '%Y-%m-%d %H:%M:%S').date()
            else:
                receive_date = receive_time.date() if hasattr(receive_time, 'date') else receive_time

            orders.append({
                'order_no': order_no,
                'receive_date': receive_date,
                'product_name': str(row[2]),  # 订单名称
                'amount': float(row[3])  # 支付金额
            })

    print(f"✅ 解析到 {len(orders)} 条订单记录")
    return orders


def update_payment_status(conn, unpaid_orders):
    """更新订单付款状态"""
    cursor = conn.cursor()

    # 首先，将所有先采后付订单标记为已付款
    print("\n更新付款状态...")
    cursor.execute("""
        UPDATE purchase_orders
        SET payment_status = 'paid'
        WHERE payment_method = '先采后付'
    """)

    # 然后，将未付款订单标记为未付款
    unpaid_count = 0
    updated_count = 0

    for order in unpaid_orders:
        order_no = order['order_no']
        receive_date = order['receive_date']

        # 查找匹配的订单
        cursor.execute("""
            SELECT id, order_no, product_name, purchase_amount
            FROM purchase_orders
            WHERE order_no = ? AND payment_method = '先采后付'
        """, (order_no,))

        result = cursor.fetchone()
        if result:
            order_id = result[0]
            # 更新为未付款状态
            cursor.execute("""
                UPDATE purchase_orders
                SET payment_status = 'unpaid',
                    receive_date = ?
                WHERE id = ?
            """, (receive_date, order_id))
            updated_count += 1
            unpaid_count += 1
        else:
            print(f"⚠️  数据库中未找到订单号: {order_no}")

    conn.commit()
    print(f"\n✅ 更新完成:")
    print(f"   - 标记为未付款: {unpaid_count} 单")
    print(f"   - 已更新确认收货时间: {updated_count} 单")

    # 统计结果
    cursor.execute("""
        SELECT payment_status, COUNT(*), SUM(purchase_amount)
        FROM purchase_orders
        WHERE payment_method = '先采后付'
        GROUP BY payment_status
    """)

    print("\n📊 付款状态统计:")
    for row in cursor.fetchall():
        status = row[0] or '未设置'
        count = row[1]
        amount = float(row[2]) if row[2] else 0
        print(f"   - {status}: {count}单, ¥{amount:,.2f}")


def main():
    """主函数"""
    print("="*80)
    print("数据库迁移：添加付款状态跟踪")
    print("="*80)

    # 连接数据库
    print(f"\n连接数据库: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    try:
        # 1. 添加新列
        add_columns_if_not_exists(conn)

        # 2. 解析账单文件
        unpaid_orders = []

        if BILL_NOV.exists():
            orders_nov = parse_bill_file(BILL_NOV)
            unpaid_orders.extend(orders_nov)
        else:
            print(f"⚠️  未找到11月账单文件: {BILL_NOV}")

        if BILL_DEC.exists():
            orders_dec = parse_bill_file(BILL_DEC)
            unpaid_orders.extend(orders_dec)
        else:
            print(f"⚠️  未找到12月账单文件: {BILL_DEC}")

        print(f"\n总计未付款订单: {len(unpaid_orders)} 单")

        # 3. 更新付款状态
        if unpaid_orders:
            update_payment_status(conn, unpaid_orders)
        else:
            print("\n⚠️  未找到任何账单数据")

        print("\n" + "="*80)
        print("✅ 迁移完成！")
        print("="*80)

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
