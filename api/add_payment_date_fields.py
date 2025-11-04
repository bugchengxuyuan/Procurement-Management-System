#!/usr/bin/env python3
"""
添加付款日期相关字段

新增字段：
- paid_date: 实际付款日期（当订单状态变为"账期已结"时记录）
- bill_import_time: 账单导入时间（记录何时从1688导入账单）
"""

import sqlite3
import os
from pathlib import Path


def get_db_path():
    """获取数据库文件路径"""
    # 尝试多个可能的路径
    possible_paths = [
        '../data/procurement.db',  # data目录（首选）
        '../backend/procurement.db',  # backend目录
        'procurement.db',  # 当前目录
        '../procurement.db',  # 上级目录
        'api/procurement.db',  # api目录
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path

    # 如果都不存在，返回默认路径
    return '../data/procurement.db'


def migrate():
    """执行数据库迁移"""
    db_path = get_db_path()

    print(f"📁 数据库路径: {db_path}")

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("   请确保数据库文件存在后再运行此脚本")
        return False

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(purchase_orders)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"📊 当前表结构包含 {len(columns)} 个字段")

        # 添加 paid_date 字段
        if 'paid_date' not in columns:
            print("➕ 添加 paid_date 字段...")
            cursor.execute("""
                ALTER TABLE purchase_orders
                ADD COLUMN paid_date DATE
            """)
            print("   ✅ paid_date 字段添加成功")
        else:
            print("   ⏭️  paid_date 字段已存在，跳过")

        # 添加 bill_import_time 字段
        if 'bill_import_time' not in columns:
            print("➕ 添加 bill_import_time 字段...")
            cursor.execute("""
                ALTER TABLE purchase_orders
                ADD COLUMN bill_import_time TIMESTAMP
            """)
            print("   ✅ bill_import_time 字段添加成功")
        else:
            print("   ⏭️  bill_import_time 字段已存在，跳过")

        # 创建索引
        print("📑 创建索引...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS ix_purchase_orders_paid_date
                ON purchase_orders (paid_date)
            """)
            print("   ✅ paid_date 索引创建成功")
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  索引可能已存在: {e}")

        # 提交更改
        conn.commit()
        print("\n✅ 数据库迁移完成！")

        # 显示最终字段列表
        cursor.execute("PRAGMA table_info(purchase_orders)")
        columns_after = cursor.fetchall()

        print(f"\n📋 更新后的字段列表 (共 {len(columns_after)} 个字段):")
        for col in columns_after:
            col_id, col_name, col_type, not_null, default, pk = col
            flags = []
            if pk:
                flags.append("PRIMARY KEY")
            if not_null:
                flags.append("NOT NULL")
            if default:
                flags.append(f"DEFAULT {default}")

            flag_str = f" ({', '.join(flags)})" if flags else ""
            print(f"   - {col_name}: {col_type}{flag_str}")

        return True

    except sqlite3.Error as e:
        print(f"\n❌ 数据库错误: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def verify_migration():
    """验证迁移结果"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n🔍 验证迁移结果...")

        # 检查新字段
        cursor.execute("PRAGMA table_info(purchase_orders)")
        columns = {row[1]: row for row in cursor.fetchall()}

        required_fields = ['paid_date', 'bill_import_time']
        all_present = all(field in columns for field in required_fields)

        if all_present:
            print("✅ 所有新字段都已成功添加")
            return True
        else:
            missing = [f for f in required_fields if f not in columns]
            print(f"❌ 缺少字段: {', '.join(missing)}")
            return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("添加付款日期相关字段到数据库")
    print("=" * 60)
    print()

    if migrate():
        verify_migration()
        print("\n" + "=" * 60)
        print("迁移成功完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("迁移失败，请检查错误信息")
        print("=" * 60)
