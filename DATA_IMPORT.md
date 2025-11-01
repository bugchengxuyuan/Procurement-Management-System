# 数据导入指南

## 📍 数据存储位置

### 数据库文件
```
/home/user/Procurement-Management-System/data/procurement.db
```
- **类型**: SQLite 数据库
- **大小**: 约 268 KB (800条订单 + 101个产品)
- **格式**: SQLite 3.x

### Excel源文件
```
/home/user/Procurement-Management-System/采购表-2（最新版.xlsx
```
- **大小**: 320 KB
- **工作表**: CAISHENDAO, Kitchen maestro
- **数据行**: 约 862 行

---

## 🚀 本地导入完整流程

### 方式一：使用自动化脚本（推荐）

#### 1. 准备Excel文件
将您的采购表Excel文件放在项目根目录：
```bash
/home/user/Procurement-Management-System/采购表-2（最新版.xlsx
```

#### 2. 运行导入脚本
```bash
cd /home/user/Procurement-Management-System
bash import_data.sh
```

**脚本会自动执行以下操作：**
- ✅ 检查Excel文件是否存在
- ✅ 创建数据目录
- ✅ 备份现有数据库（如果存在）
- ✅ 提示是否清空旧数据
- ✅ 运行数据迁移
- ✅ 验证导入结果
- ✅ 显示统计信息

---

### 方式二：手动步骤

#### 1. 准备环境
```bash
cd /home/user/Procurement-Management-System
mkdir -p data
```

#### 2. 备份现有数据（可选）
```bash
# 如果已有数据库，先备份
cp data/procurement.db data/procurement.db.backup.$(date +%Y%m%d_%H%M%S)
```

#### 3. 清空数据库（如果需要重新导入）
```bash
rm -f data/procurement.db
```

#### 4. 运行迁移脚本
```bash
cd api
python3 migrate_data.py
```

**输出示例：**
```
======================================================================
开始迁移数据...
======================================================================

从旧数据库找到 800 条订单
  已迁移 100 条订单...
  已迁移 200 条订单...
  ...
  已迁移 800 条订单...

订单迁移完成:
  成功: 800
  失败: 0

正在更新产品统计...
  更新了 101 个产品的统计数据

======================================================================
迁移完成!
======================================================================
订单总数: 800
产品总数: 101
采购总额: ¥749,678.90
======================================================================
```

#### 5. 验证导入结果
```bash
cd api
python3 << 'EOF'
from sqlmodel import Session, select, func
from app.core.database import engine
from app.models import PurchaseOrder, Product

with Session(engine) as session:
    orders = session.exec(select(func.count(PurchaseOrder.id))).one()
    products = session.exec(select(func.count(Product.id))).one()
    amount = session.exec(select(func.sum(PurchaseOrder.purchase_amount))).one()
    print(f"订单: {orders}, 产品: {products}, 总额: ¥{amount:,.2f}")
EOF
```

---

## 📋 数据导入说明

### 自动生成订单编号

如果Excel中某些行缺少订单编号，系统会自动生成19位数字订单编号：

**生成规则：**
```
订单编号 = 时间戳(13位) + 随机数(4位) + 补齐位(2位)
示例: 3655240347686198464
```

**代码位置：** `api/app/utils/excel_handler.py:19-31`

### 数据映射

Excel列与数据库字段映射：

| Excel列 | 数据库字段 | 说明 |
|---------|-----------|------|
| 日期 | order_date | 订单日期 |
| 初始状态 | order_status | 订单状态 |
| 订单编号 | order_no | 自动生成（如缺失） |
| 产品名称 | product_name | 产品名称 |
| 采购金额 | purchase_amount | 采购金额 |
| 时间 | record_time | 记录时间 |
| 先采后付 | payment_method | 支付方式 |

### 数据验证

导入时会自动验证：
- ❌ 跳过产品名称为空的记录
- ❌ 跳过采购金额为空的记录
- ❌ 跳过订单日期为空的记录
- ✅ 自动生成缺失的订单编号
- ✅ 自动去重（订单编号重复）

---

## 🔧 自定义导入

### 修改Excel文件路径

编辑 `api/migrate_data.py` 第160行：
```python
EXCEL_PATH = "../采购表-2（最新版.xlsx"  # 修改为您的文件路径
```

### 修改工作表名称

如果您的Excel工作表名称不同，编辑 `api/migrate_data.py` 第35行：
```python
df = pd.read_excel(excel_path, sheet_name="CAISHENDAO", header=None)
```

### 修改数据列位置

如果您的Excel数据列位置不同，编辑 `api/migrate_data.py` 第38行：
```python
df_data = df.iloc[7:, 10:17].copy()  # [起始行, 列范围]
```

---

## 📊 导入后验证

### 1. 检查数据库文件
```bash
ls -lh data/procurement.db
```

### 2. 查看数据统计
```bash
cd api
python3 -c "
from sqlmodel import Session, select, func
from app.core.database import engine
from app.models import PurchaseOrder, Product

with Session(engine) as session:
    print('订单数:', session.exec(select(func.count(PurchaseOrder.id))).one())
    print('产品数:', session.exec(select(func.count(Product.id))).one())
    print('总金额:', session.exec(select(func.sum(PurchaseOrder.purchase_amount))).one())
"
```

### 3. 测试API
```bash
# 启动后端
cd api
python3 run.py &

# 等待3秒
sleep 3

# 测试API
curl http://localhost:8000/api/statistics/dashboard
```

---

## ⚠️ 常见问题

### Q1: 导入失败，提示找不到Excel文件
**解决方案：**
```bash
# 检查文件是否存在
ls -lh 采购表-2（最新版.xlsx

# 如果不存在，复制文件到项目根目录
cp /path/to/your/excel.xlsx /home/user/Procurement-Management-System/
```

### Q2: 导入后数据为空
**解决方案：**
```bash
# 检查Excel工作表名称
python3 -c "
import pandas as pd
xl = pd.ExcelFile('采购表-2（最新版.xlsx')
print('工作表:', xl.sheet_names)
"

# 修改 migrate_data.py 中的工作表名称
```

### Q3: 想要重新导入数据
**解决方案：**
```bash
# 删除数据库
rm -f data/procurement.db

# 重新运行导入
cd api
python3 migrate_data.py
```

### Q4: 数据库文件太大
**解决方案：**
```bash
# 压缩数据库
sqlite3 data/procurement.db "VACUUM;"
```

---

## 🔄 数据更新流程

### 增量更新（添加新数据）
使用系统的Excel导入功能：
1. 访问 http://localhost:3000/orders
2. 点击"导入"按钮
3. 选择包含新数据的Excel文件
4. 系统会自动去重并添加新记录

### 完全重新导入
```bash
# 1. 备份现有数据
cp data/procurement.db data/procurement.db.backup

# 2. 删除旧数据库
rm -f data/procurement.db

# 3. 运行导入脚本
bash import_data.sh
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `data/procurement.db` | SQLite数据库文件 |
| `api/migrate_data.py` | 数据迁移脚本 |
| `api/app/utils/excel_handler.py` | Excel处理工具 |
| `import_data.sh` | 一键导入脚本 |
| `采购表-2（最新版.xlsx` | Excel源数据 |

---

## 💡 最佳实践

1. **定期备份** - 每次导入前备份数据库
2. **验证数据** - 导入后检查统计数据是否正确
3. **使用脚本** - 使用 `import_data.sh` 避免手动错误
4. **保留源文件** - 保留原始Excel文件以备后用
5. **测试环境** - 先在测试环境导入，确认无误后再导入生产环境

---

## 🆘 获取帮助

如有问题，请检查：
1. `/tmp/api.log` - 后端日志
2. 控制台输出 - 导入脚本的详细信息
3. `migrate_data.py` - 迁移脚本源代码
