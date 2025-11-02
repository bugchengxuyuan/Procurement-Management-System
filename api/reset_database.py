"""
重置数据库脚本
用于删除旧数据库并重新创建表结构
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db
from app.core.config import DATA_DIR


def reset_database():
    """重置数据库"""
    db_path = DATA_DIR / "procurement.db"

    print("=" * 80)
    print("数据库重置工具")
    print("=" * 80)

    # 检查数据库是否存在
    if db_path.exists():
        # 备份现有数据库
        backup_name = f"procurement.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = DATA_DIR / backup_name

        print(f"\n📦 备份现有数据库...")
        print(f"   从: {db_path}")
        print(f"   到: {backup_path}")

        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"   ✅ 备份完成")

        # 删除现有数据库
        print(f"\n🗑️  删除旧数据库...")
        db_path.unlink()
        print(f"   ✅ 已删除")
    else:
        print(f"\n📝 数据库不存在，将创建新数据库")

    # 重新创建数据库
    print(f"\n🔨 创建新数据库...")
    init_db()
    print(f"   ✅ 数据库表结构已创建")

    print("\n" + "=" * 80)
    print("✅ 数据库重置完成！")
    print("=" * 80)
    print("\n下一步：运行以下命令导入数据")
    print("  python3 api/import_excel.py")
    print()


if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
