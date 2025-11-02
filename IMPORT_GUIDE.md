# 数据导入指南

## 快速开始

### 方法一：使用导入脚本（推荐）

```bash
bash import_data.sh
```

这个脚本会：
1. 检查 Excel 文件是否存在
2. 自动备份现有数据库
3. 清空旧数据并导入新数据
4. 验证导入结果

### 方法二：手动导入

```bash
# 1. 重置数据库（如果遇到错误）
python3 api/reset_database.py

# 2. 导入数据
python3 api/import_excel.py
```

## 常见问题

### ❌ 错误：UNIQUE constraint failed: purchase_orders.order_no

**原因：** 您的数据库使用的是旧版本的表结构，不支持"一单多品"功能。

**解决方案：**

```bash
# 重置数据库
python3 api/reset_database.py

# 重新导入
python3 api/import_excel.py
```

或者直接运行：

```bash
bash import_data.sh
```

### 📝 关于"一单多品"

系统现在支持同一订单号包含多个不同产品，例如：

```
订单号: 2428407734977198464
  - 粘鞋胶（黄色）: ¥116.15
  - 鞋面修补胶（蓝白）: ¥116.15
  - 白色英文鞋胶: ¥116.15
```

这是通过移除订单号的唯一性约束实现的。系统现在使用"订单号+产品名"的组合来判断是否重复。

### 📊 Excel 文件要求

1. **文件位置：** 项目根目录下的 `采购表-2（最新版.xlsx`
2. **采购金额列：** 必须是数值，不能是公式
3. **必填字段：**
   - 日期
   - 产品名称
   - 采购金额

如果某些单元格使用了公式，导入前请：
1. 选中采购金额列
2. 复制
3. 右键 → 选择性粘贴 → 数值

### 🔧 手动重置数据库

如果需要完全清空数据库：

```bash
# 备份（可选）
cp data/procurement.db data/procurement.db.backup

# 删除数据库
rm -f data/procurement.db

# 导入数据（会自动创建新数据库）
python3 api/import_excel.py
```

### 📈 验证导入结果

导入完成后，系统会显示：

```
订单总数: 856
产品总数: 113
采购总额: ¥778,380.12
```

您也可以手动验证一单多品订单：

```bash
cd api
python3 << 'EOF'
from sqlmodel import Session, select, func
from app.core.database import engine
from app.models import PurchaseOrder

with Session(engine) as session:
    result = session.exec(
        select(
            PurchaseOrder.order_no,
            func.count(PurchaseOrder.id).label("count")
        )
        .group_by(PurchaseOrder.order_no)
        .having(func.count(PurchaseOrder.id) > 1)
    ).all()

    print(f"一单多品订单数: {len(result)}")
    for order_no, count in result[:3]:
        print(f"  {order_no}: {count}个产品")
EOF
```

## 数据库位置

- **数据库文件：** `data/procurement.db`
- **备份文件：** `data/procurement.db.backup_*`

## 获取帮助

如果遇到其他问题，请检查：

1. Python 版本是否正确 (`python3 --version`)
2. 依赖是否安装 (`pip install -r api/requirements.txt`)
3. Excel 文件路径是否正确
4. 数据目录是否有写权限
