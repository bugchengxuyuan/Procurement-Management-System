#!/bin/bash

echo "=========================================="
echo "  采购数据导入脚本"
echo "=========================================="

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

echo "📁 项目目录: $SCRIPT_DIR"

# 检查Excel文件
echo ""
echo "1. 检查Excel文件..."
if [ ! -f "采购表-2（最新版.xlsx" ]; then
    echo "❌ 错误: 找不到Excel文件 '采购表-2（最新版.xlsx'"
    echo "请将Excel文件放在项目根目录: $SCRIPT_DIR"
    echo ""
    echo "提示: 您的Excel文件名可能不同，请修改脚本中的文件名"
    exit 1
fi
echo "✅ 找到Excel文件"

# 检查数据目录
echo ""
echo "2. 检查数据目录..."
mkdir -p data
echo "✅ 数据目录就绪: $SCRIPT_DIR/data/"

# 备份现有数据库（如果存在）
echo ""
echo "3. 备份现有数据..."
if [ -f "data/procurement.db" ]; then
    BACKUP_FILE="data/procurement.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp data/procurement.db "$BACKUP_FILE"
    echo "✅ 已备份到: $BACKUP_FILE"

    # 询问是否清空现有数据
    echo ""
    echo "⚠️  数据库中已有数据，是否清空并重新导入？"
    echo "   当前数据将被保存到备份文件中"
    read -p "   继续? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "❌ 取消导入"
        exit 0
    fi

    # 清空数据库
    rm -f data/procurement.db
    echo "✅ 已清空旧数据"
else
    echo "ℹ️  数据库不存在，将创建新数据库"
fi

# 运行数据导入
echo ""
echo "4. 开始导入数据..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd api || exit 1
python3 import_excel.py

# 检查导入结果
echo ""
echo "5. 验证导入结果..."
python3 << 'PYTHON_SCRIPT'
from sqlmodel import Session, select, func
from app.core.database import engine
from app.models import PurchaseOrder, Product

try:
    with Session(engine) as session:
        order_count = session.exec(select(func.count(PurchaseOrder.id))).one()
        product_count = session.exec(select(func.count(Product.id))).one()
        total_amount = session.exec(select(func.sum(PurchaseOrder.purchase_amount))).one() or 0

        print("\n" + "="*70)
        print("✅ 数据导入成功！")
        print("="*70)
        print(f"📦 订单数量: {order_count}")
        print(f"🏷️  产品数量: {product_count}")
        print(f"💰 采购总额: ¥{total_amount:,.2f}")
        print("="*70)
        print(f"\n📁 数据库位置: data/procurement.db")
        print("="*70)
except Exception as e:
    print(f"\n❌ 验证失败: {e}")
    exit(1)
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "  导入完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "  启动系统: bash start.sh"
echo "  或分别启动："
echo "    后端: cd api && python3 run.py"
echo "    前端: cd web && npm run dev"
echo ""
