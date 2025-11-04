"""
迁移到新的付款状态系统

新状态方案：
- 即时付款：订单创建时就付款
- 账期未到：先采后付，还未还款
- 账期已结：先采后付，已还款
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "procurement.db"


def migrate_payment_status(conn):
    """迁移付款状态到新的中文状态值"""
    cursor = conn.cursor()

    print("="*80)
    print("迁移付款状态到新系统")
    print("="*80)

    # 查询当前状态分布
    print("\n【迁移前】当前状态分布:")
    cursor.execute("""
        SELECT
            payment_method,
            payment_status,
            COUNT(*) as count,
            SUM(purchase_amount) as total_amount
        FROM purchase_orders
        GROUP BY payment_method, payment_status
        ORDER BY payment_method, payment_status
    """)

    print(f"\n{'付款方式':15s} | {'付款状态':10s} | {'订单数':>8s} | {'金额':>15s}")
    print("-" * 60)

    for row in cursor.fetchall():
        method, status, count, amount = row
        method_display = method or "NULL"
        status_display = status or "NULL"
        print(f"{method_display:15s} | {status_display:10s} | {count:8d} | ¥{float(amount):>13,.2f}")

    # 执行迁移
    print("\n\n【执行迁移】")
    print("映射规则:")
    print("  - payment_method='已付款' OR payment_method='即时付款' → '即时付款'")
    print("  - payment_method='先采后付' AND payment_status='paid' → '账期已结'")
    print("  - payment_method='先采后付' AND payment_status='unpaid' → '账期未到'")
    print("  - 其他 → '即时付款'（默认）\n")

    # 迁移SQL
    migrations = [
        # 1. 即时付款（已付款的订单）
        {
            'sql': """
                UPDATE purchase_orders
                SET payment_status = '即时付款'
                WHERE payment_method IN ('已付款', '即时付款')
                   OR (payment_method NOT IN ('先采后付') AND payment_status IS NULL)
            """,
            'desc': "即时付款（已付款订单）"
        },
        # 2. 账期已结（先采后付+已付款）
        {
            'sql': """
                UPDATE purchase_orders
                SET payment_status = '账期已结'
                WHERE payment_method = '先采后付'
                  AND payment_status = 'paid'
            """,
            'desc': "账期已结（先采后付已还款）"
        },
        # 3. 账期未到（先采后付+未付款）
        {
            'sql': """
                UPDATE purchase_orders
                SET payment_status = '账期未到'
                WHERE payment_method = '先采后付'
                  AND payment_status = 'unpaid'
            """,
            'desc': "账期未到（先采后付未还款）"
        }
    ]

    for i, migration in enumerate(migrations, 1):
        print(f"{i}. 迁移 {migration['desc']}...")
        cursor.execute(migration['sql'])
        affected = cursor.rowcount
        print(f"   ✅ 更新了 {affected} 条记录")

    conn.commit()

    # 验证迁移结果
    print("\n\n【迁移后】新状态分布:")
    cursor.execute("""
        SELECT
            payment_status,
            COUNT(*) as count,
            SUM(purchase_amount) as total_amount
        FROM purchase_orders
        GROUP BY payment_status
        ORDER BY payment_status
    """)

    print(f"\n{'付款状态':15s} | {'订单数':>8s} | {'金额':>15s}")
    print("-" * 45)

    status_stats = {}
    for row in cursor.fetchall():
        status, count, amount = row
        status_display = status or "NULL"
        print(f"{status_display:15s} | {count:8d} | ¥{float(amount):>13,.2f}")
        status_stats[status] = {'count': count, 'amount': float(amount)}

    # 详细验证
    print("\n\n【详细验证】")

    # 检查账期未到的订单是否有确认收货时间
    cursor.execute("""
        SELECT COUNT(*)
        FROM purchase_orders
        WHERE payment_status = '账期未到'
          AND receive_date IS NULL
    """)

    no_receive_date_count = cursor.fetchone()[0]

    if no_receive_date_count > 0:
        print(f"\n⚠️  警告: 发现 {no_receive_date_count} 单'账期未到'订单缺少确认收货时间")
        print(f"   这些订单无法计算还款日期")
        print(f"   建议检查数据完整性")
    else:
        print(f"\n✅ 所有'账期未到'订单都有确认收货时间")

    # 统计总结
    print("\n\n【统计总结】")
    if '即时付款' in status_stats:
        stats = status_stats['即时付款']
        print(f"  即时付款: {stats['count']}单, ¥{stats['amount']:,.2f}")

    if '账期未到' in status_stats:
        stats = status_stats['账期未到']
        print(f"  账期未到: {stats['count']}单, ¥{stats['amount']:,.2f}")

    if '账期已结' in status_stats:
        stats = status_stats['账期已结']
        print(f"  账期已结: {stats['count']}单, ¥{stats['amount']:,.2f}")

    total_count = sum(s['count'] for s in status_stats.values())
    total_amount = sum(s['amount'] for s in status_stats.values())
    print(f"  ────────────────────────────")
    print(f"  总计: {total_count}单, ¥{total_amount:,.2f}")


def main():
    """主函数"""
    print("="*80)
    print("付款状态系统迁移工具")
    print("="*80)

    # 检查数据库文件
    if not DB_PATH.exists():
        print(f"\n❌ 数据库文件不存在: {DB_PATH}")
        return

    print(f"\n连接数据库: {DB_PATH}")

    # 备份提示
    print("\n⚠️  重要提示:")
    print("  1. 此操作将修改数据库中的付款状态字段")
    print("  2. 建议在执行前备份数据库")
    print("  3. 迁移是单向的，无法自动回滚")
    print("\n是否继续？(y/n): ", end="")

    # 在自动化脚本中跳过确认
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        confirm = 'y'
        print("y (auto mode)")
    else:
        confirm = input().lower()

    if confirm != 'y':
        print("\n❌ 迁移已取消")
        return

    # 执行迁移
    conn = sqlite3.connect(DB_PATH)

    try:
        migrate_payment_status(conn)

        print("\n" + "="*80)
        print("✅ 迁移成功完成！")
        print("="*80)
        print("\n后续步骤:")
        print("  1. 重启后端服务")
        print("  2. 更新前端状态筛选器")
        print("  3. 验证API响应")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        print("\n数据库已回滚，未做任何更改")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
