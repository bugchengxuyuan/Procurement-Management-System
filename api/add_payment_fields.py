"""
快速迁移脚本：添加付款状态字段
适用于本地开发环境
"""
import sqlite3
from pathlib import Path

# Database path - 根据实际情况调整
DB_PATHS = [
    Path(__file__).parent.parent / "data" / "procurement.db",  # Linux/服务器
    Path.home() / "Procurement-Management-System" / "data" / "procurement.db",  # Mac/本地
]


def find_database():
    """查找数据库文件"""
    for db_path in DB_PATHS:
        if db_path.exists():
            return db_path

    # 如果都不存在，询问用户
    print("未找到数据库文件，请输入数据库路径：")
    custom_path = input().strip()
    return Path(custom_path)


def add_columns(conn):
    """添加新列到数据库"""
    cursor = conn.cursor()

    # 检查列是否存在
    cursor.execute("PRAGMA table_info(purchase_orders)")
    columns = [col[1] for col in cursor.fetchall()]

    changes_made = False

    if 'payment_status' not in columns:
        print("添加 payment_status 列...")
        cursor.execute("""
            ALTER TABLE purchase_orders
            ADD COLUMN payment_status TEXT
        """)
        changes_made = True
        print("✅ payment_status 列添加成功")
    else:
        print("✅ payment_status 列已存在")

    if 'receive_date' not in columns:
        print("添加 receive_date 列...")
        cursor.execute("""
            ALTER TABLE purchase_orders
            ADD COLUMN receive_date DATE
        """)
        changes_made = True
        print("✅ receive_date 列添加成功")
    else:
        print("✅ receive_date 列已存在")

    if changes_made:
        conn.commit()

        # 设置默认值：所有先采后付订单标记为未付款
        print("\n设置默认值...")
        cursor.execute("""
            UPDATE purchase_orders
            SET payment_status = 'unpaid'
            WHERE payment_method = '先采后付'
              AND payment_status IS NULL
        """)
        conn.commit()

        # 统计
        cursor.execute("""
            SELECT COUNT(*), SUM(purchase_amount)
            FROM purchase_orders
            WHERE payment_method = '先采后付'
              AND payment_status = 'unpaid'
        """)
        count, total = cursor.fetchone()
        total = float(total) if total else 0
        print(f"✅ 标记 {count} 单先采后付订单为未付款，总金额: ¥{total:,.2f}")


def main():
    """主函数"""
    print("="*80)
    print("快速迁移：添加付款状态字段")
    print("="*80)

    # 查找数据库
    db_path = find_database()

    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return

    print(f"\n连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        add_columns(conn)

        print("\n" + "="*80)
        print("✅ 迁移完成！")
        print("="*80)
        print("\n提示：如果您有1688账单文件，可以运行 migrate_payment_status.py")
        print("     来精确标记哪些订单已付款，哪些未付款。")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
