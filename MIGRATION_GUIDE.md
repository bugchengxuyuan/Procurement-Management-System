# 数据库迁移指南 - 添加付款状态字段

## 问题说明

如果您遇到以下错误：
```
sqlite3.OperationalError: no such column: purchase_orders.payment_status
```

这是因为您的本地数据库还没有添加新的付款状态字段。

## 快速修复（3步）

### 方法1：快速迁移脚本（推荐）

1. **进入API目录**
```bash
cd api
```

2. **运行快速迁移脚本**
```bash
python3 add_payment_fields.py
```

3. **重启后端服务**
- 停止当前运行的FastAPI服务（Ctrl+C）
- 重新启动：`python3 -m uvicorn app.main:app --reload`

### 方法2：完整迁移（如果您有1688账单文件）

如果您有11月和12月的1688账单文件：

1. **确保账单文件在项目根目录**
   - `2025-11-04_11-09-46-账单明细导出-1058866.xlsx` (11月账单)
   - `2025-11-04_11-11-12-账单明细导出-1058896.xlsx` (12月账单)

2. **运行完整迁移**
```bash
cd api
python3 migrate_payment_status.py
```

3. **重启后端服务**

## 迁移后的效果

### 快速迁移
- ✅ 添加 `payment_status` 字段
- ✅ 添加 `receive_date` 字段
- ✅ 所有先采后付订单标记为 `unpaid`（未付款）

### 完整迁移
- ✅ 添加 `payment_status` 和 `receive_date` 字段
- ✅ 解析1688账单文件
- ✅ 标记35单为 `unpaid`（未付款）
- ✅ 标记12单为 `paid`（已付款）
- ✅ 设置准确的确认收货时间

## 字段说明

| 字段 | 类型 | 说明 | 可能的值 |
|------|------|------|----------|
| `payment_status` | TEXT | 付款状态 | `unpaid` (未付款)<br>`paid` (已付款)<br>`partial` (部分付款) |
| `receive_date` | DATE | 确认收货时间 | YYYY-MM-DD格式<br>1688账期以此日期计算 |

## 业务逻辑说明

### 还款日计算规则

```
确认收货月份 → 次月8号还款

例子：
- 10月15日确认收货 → 11月8日还款
- 11月3日确认收货 → 12月8日还款
```

### 订单状态

| 状态 | 条件 | 说明 |
|------|------|------|
| ✅ 正常 | 剩余天数 > 7 | 距离还款日超过7天 |
| ⚠️ 即将到期 | 0 < 剩余天数 ≤ 7 | 7天内需要还款 |
| ❌ 已逾期 | 剩余天数 < 0 | 已超过还款日 |

## 常见问题

### Q1: 我找不到数据库文件在哪里？

A: 数据库通常位于以下位置之一：
- `data/procurement.db`（项目根目录下的data文件夹）
- `api/procurement.db`
- `backend/procurement.db`

运行脚本时会自动查找，如果找不到会提示您输入路径。

### Q2: 迁移脚本报错怎么办？

A: 请提供完整的错误信息，可能的原因：
- 数据库文件被占用（关闭正在运行的后端服务）
- 权限问题（使用 `sudo` 或管理员权限运行）
- Python依赖缺失（确保安装了 `pandas` 和 `openpyxl`）

### Q3: 我没有账单文件，可以用吗？

A: 可以！使用**快速迁移脚本**（`add_payment_fields.py`），它会：
- 添加必要的字段
- 将所有先采后付订单标记为未付款
- 系统可以正常运行

之后如果获得账单文件，可以再运行完整迁移来精确标记付款状态。

### Q4: 已经运行过迁移，还能再运行吗？

A: 可以！迁移脚本会检查字段是否已存在：
- 如果已存在，不会重复添加
- 如果需要更新数据，会覆盖现有数据

## 技术细节

### 数据库变更

```sql
-- 添加付款状态字段
ALTER TABLE purchase_orders ADD COLUMN payment_status TEXT;

-- 添加确认收货时间字段
ALTER TABLE purchase_orders ADD COLUMN receive_date DATE;

-- 设置默认值
UPDATE purchase_orders
SET payment_status = 'unpaid'
WHERE payment_method = '先采后付'
  AND payment_status IS NULL;
```

### API变更

`GET /api/statistics/payment-due` 现在：
- 优先查询 `payment_status = 'unpaid'` 的订单
- 使用 `receive_date`（如果存在）计算还款日
- 返回更详细的订单信息

### 向后兼容

代码已添加向后兼容逻辑：
- 如果字段不存在，会降级为查询所有先采后付订单
- 如果 `receive_date` 不存在，使用 `order_date`
- 不会因为字段缺失而报错

## 需要帮助？

如果遇到任何问题，请查看：
1. 后端日志输出
2. 数据库文件权限
3. Python版本（建议3.9+）
4. 必要的Python包：`pandas`, `openpyxl`, `python-dateutil`
