# 字段优化方案 - Field Optimization Proposal

## 📋 问题分析

### 当前字段状态

系统目前有**三个相关字段**表示付款/订单状态：

```python
class PurchaseOrder(SQLModel, table=True):
    order_status: str           # 值: "已付款" 或 "先采后付"
    payment_method: str         # 值: "已付款" 或 "先采后付"
    payment_status: str         # 值: "即时付款"、"账期未到"、"账期已结"
```

### 问题点

#### 1. 字段冗余和语义混淆

| 字段 | 原始用途 | 当前值 | 问题 |
|------|---------|--------|------|
| `order_status` | 订单状态 | "已付款"/"先采后付" | ❌ 实际表示的是付款方式，不是订单状态 |
| `payment_method` | 支付方式 | "已付款"/"先采后付" | ❌ 与order_status完全重复 |
| `payment_status` | 付款状态 | "即时付款"/"账期未到"/"账期已结" | ✅ 新字段，语义清晰 |

**核心问题**：
- `order_status` 和 `payment_method` 在旧系统中被误用为表示"是否先采后付"
- 它们的值完全相同，存在数据冗余
- 新的 `payment_status` 字段才是真正符合业务语义的字段

#### 2. 业务语义不匹配

**应该的语义**：
- **订单状态** (Order Status): 待确认、已确认、已发货、已收货、已完成、已取消
- **支付方式** (Payment Method): 支付宝、微信支付、银行转账、货到付款
- **付款状态** (Payment Status): 即时付款、账期未到、账期已结

**当前的语义**：
- **订单状态**: "已付款"/"先采后付" ❌ 这是付款状态，不是订单状态
- **支付方式**: "已付款"/"先采后付" ❌ 这不是支付方式

### 3. 数据一致性要求

用户提出的关键需求：

> "订单管理中所有'账期未到'的数据，应该在先采后付管理中显示，它们之间是有对应的逻辑关系"

**验证点**：
- ✅ 订单管理筛选 `payment_status = '账期未到'`
- ✅ 先采后付管理页面查询 `payment_status = '账期未到'`
- ✅ 两个页面应该显示完全相同的订单

## 💡 解决方案

### 方案A：激进方案 - 移除冗余字段（推荐）

**核心思想**：只保留 `payment_status` 字段

#### 1. 数据库迁移

```python
# 移除 order_status 和 payment_method 字段
# 只保留 payment_status 作为唯一的付款状态字段

class PurchaseOrder(SQLModel, table=True):
    # 移除这两个字段
    # order_status: str
    # payment_method: str

    # 只保留这个
    payment_status: str  # "即时付款"、"账期未到"、"账期已结"
```

**优点**：
- ✅ 消除字段冗余
- ✅ 语义清晰，符合业务逻辑
- ✅ 简化代码和查询逻辑

**缺点**：
- ⚠️ 需要修改所有使用这两个字段的代码
- ⚠️ 可能影响已有的导入/导出逻辑

#### 2. UI 改造

**订单管理页面**：
- 移除"订单状态"和"支付方式"筛选器
- 只保留"付款状态"筛选器（即时付款、账期未到、账期已结）
- 表格只显示"付款状态"列

**先采后付管理页面**：
- 自动显示所有 `payment_status = '账期未到'` 的订单
- 按还款日分组展示

### 方案B：渐进方案 - 重新定义字段含义

**核心思想**：保留字段，但重新定义它们的用途

#### 1. 字段重定义

```python
class PurchaseOrder(SQLModel, table=True):
    # 改为真正的订单履行状态
    order_status: str = Field(default="待确认")
    # 可选值: "待确认"、"已确认"、"已发货"、"已收货"、"已完成"、"已取消"

    # 改为真正的支付方式（可选，可以为空）
    payment_method: Optional[str] = Field(default=None)
    # 可选值: "支付宝"、"微信支付"、"银行转账"、"现金"等

    # 保持不变 - 主要的付款状态字段
    payment_status: str
    # 可选值: "即时付款"、"账期未到"、"账期已结"
```

#### 2. 数据迁移

```python
# 迁移脚本
# 1. 将所有现有订单的 order_status 设置为 "已完成"（因为都是历史订单）
# 2. 将 payment_method 设置为 None（因为旧数据中这个字段被误用）
# 3. payment_status 保持不变

UPDATE purchase_orders
SET order_status = '已完成',
    payment_method = NULL
WHERE order_status IN ('已付款', '先采后付');
```

**优点**：
- ✅ 保留字段，向后兼容
- ✅ 字段语义符合业务实际
- ✅ 为未来扩展订单状态追踪留有空间

**缺点**：
- ⚠️ 旧数据中这两个字段会变成无意义的值
- ⚠️ 仍需修改部分代码逻辑

### 方案C：保守方案 - 保留但隐藏

**核心思想**：数据库保留字段，但UI完全不显示

#### 1. 数据库层面

```python
# 保持字段不变，但标记为废弃
class PurchaseOrder(SQLModel, table=True):
    order_status: str       # DEPRECATED: 旧字段，仅用于兼容
    payment_method: str     # DEPRECATED: 旧字段，仅用于兼容
    payment_status: str     # 主字段
```

#### 2. UI层面

**完全移除** `order_status` 和 `payment_method` 的显示和筛选：
- 订单管理页面只显示"付款状态"
- 导入导出时自动转换

**优点**：
- ✅ 最小改动
- ✅ 完全向后兼容
- ✅ UI清晰，用户不困惑

**缺点**：
- ⚠️ 数据库中仍有冗余字段
- ⚠️ 维护成本增加

## 🎯 推荐方案

### 综合建议：方案A（激进方案）

**理由**：
1. 系统还在早期阶段，重构成本较低
2. 用户已经明确了新的字段语义（"采购表-优化版"）
3. 消除冗余可以避免未来的维护问题
4. 代码逻辑更清晰

### 实施步骤

#### Phase 1: 后端清理

**1.1 创建迁移脚本**

```python
# api/migrate_remove_legacy_fields.py

"""
移除 order_status 和 payment_method 字段
只保留 payment_status 作为唯一的状态字段
"""

from sqlmodel import Session, select
from app.core.database import engine
from app.models.order import PurchaseOrder

def migrate():
    # 1. 验证所有订单都有 payment_status
    with Session(engine) as session:
        statement = select(PurchaseOrder).where(
            PurchaseOrder.payment_status == None
        )
        orders_without_status = session.exec(statement).all()

        if orders_without_status:
            print(f"错误: {len(orders_without_status)} 个订单没有 payment_status")
            return False

    # 2. 使用 ALTER TABLE 移除字段（需要备份）
    print("警告: 即将移除 order_status 和 payment_method 字段")
    print("请确保已经备份数据库！")

    # SQLite 不支持 DROP COLUMN，需要重建表
    # 这里只是示意，实际需要更复杂的迁移

    return True
```

**1.2 更新模型定义**

```python
# api/app/models/order.py

class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_no: str = Field(unique=True, index=True, max_length=20)
    product_name: str = Field(index=True, max_length=200)
    spec: Optional[str] = Field(default=None, max_length=100)
    purchase_amount: Decimal = Field(max_digits=10, decimal_places=2)
    supplier: Optional[str] = Field(default=None, index=True, max_length=200)
    order_date: date = Field(index=True)
    receive_date: Optional[date] = Field(default=None, index=True)

    # 只保留这个字段
    payment_status: str = Field(index=True, max_length=20)
    # 可选值: "即时付款"、"账期未到"、"账期已结"

    record_time: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

**1.3 更新所有API**

```python
# 移除所有对 order_status 和 payment_method 的引用
# 只使用 payment_status

# 例如：订单列表过滤
def get_orders(params: OrderListParams):
    statement = select(PurchaseOrder)

    # 移除
    # if params.order_status:
    #     statement = statement.where(PurchaseOrder.order_status == params.order_status)
    # if params.payment_method:
    #     statement = statement.where(PurchaseOrder.payment_method == params.payment_method)

    # 只保留
    if params.payment_status:
        statement = statement.where(PurchaseOrder.payment_status == params.payment_status)
```

#### Phase 2: 前端清理

**2.1 更新订单列表页面**

```typescript
// frontend/src/pages/OrderList/index.tsx

// 移除"订单状态"和"支付方式"筛选器
// 只保留"付款状态"筛选器

<Row gutter={16}>
  <Col span={6}>
    <Form.Item name="product_name" label="产品名称">
      <Input placeholder="请输入产品名称" />
    </Form.Item>
  </Col>
  <Col span={6}>
    <Form.Item name="supplier" label="供应商">
      <Input placeholder="请输入供应商" />
    </Form.Item>
  </Col>
  <Col span={6}>
    {/* 只保留付款状态 */}
    <Form.Item name="payment_status" label="付款状态">
      <Select placeholder="请选择" allowClear>
        <Select.Option value="即时付款">即时付款</Select.Option>
        <Select.Option value="账期未到">账期未到</Select.Option>
        <Select.Option value="账期已结">账期已结</Select.Option>
      </Select>
    </Form.Item>
  </Col>
  <Col span={6}>
    <Form.Item name="dateRange" label="日期范围">
      <RangePicker style={{ width: '100%' }} />
    </Form.Item>
  </Col>
</Row>
```

**2.2 更新表格列**

```typescript
// 移除"订单状态"和"支付方式"列
// 只保留"付款状态"列

const columns: ColumnsType<Order> = [
  { title: '订单日期', dataIndex: 'order_date', ... },
  { title: '订单编号', dataIndex: 'order_no', ... },
  { title: '产品名称', dataIndex: 'product_name', ... },
  { title: '采购金额', dataIndex: 'purchase_amount', ... },
  { title: '供应商', dataIndex: 'supplier', ... },
  { title: '确认收货日期', dataIndex: 'receive_date', ... },
  // 只保留付款状态
  {
    title: '付款状态',
    dataIndex: 'payment_status',
    render: (status: string) => getPaymentStatusTag(status),
  },
  { title: '操作', ... },
];
```

**2.3 更新数据接口**

```typescript
// frontend/src/services/order.ts

export interface Order {
  id: number;
  order_no: string;
  product_name: string;
  spec?: string | null;
  purchase_amount: number;
  supplier?: string | null;
  order_date: string;
  receive_date?: string | null;
  // 移除这两个
  // order_status: string;
  // payment_method: string;
  // 只保留
  payment_status: string;
  record_time: string;
  created_at: string;
  updated_at: string;
}

export interface OrderListParams {
  page?: number;
  size?: number;
  product_name?: string;
  spec?: string;
  supplier?: string;
  // 移除
  // order_status?: string;
  // payment_method?: string;
  // 只保留
  payment_status?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}
```

#### Phase 3: 导入导出兼容

**3.1 Excel 导入**

```python
# 如果Excel中有"订单状态"或"支付方式"列，自动转换为 payment_status

def map_legacy_status(old_value: str) -> str:
    """将旧的状态值转换为新的 payment_status"""
    if old_value in ['已付款', '即时付款']:
        return '即时付款'
    elif old_value == '先采后付':
        return '账期未到'  # 默认为未到账期
    else:
        return '即时付款'  # 默认
```

**3.2 Excel 导出**

```python
# 导出时只包含 payment_status 列
# 列名："付款状态"
```

## 🔄 数据一致性验证

### 确保订单管理和先采后付管理页面数据一致

#### 1. 后端查询逻辑

**订单管理页面**（筛选"账期未到"）：
```python
# GET /api/orders?payment_status=账期未到
statement = select(PurchaseOrder).where(
    PurchaseOrder.payment_status == "账期未到"
)
```

**先采后付管理页面**：
```python
# GET /api/payment-due/groups
statement = select(PurchaseOrder).where(
    PurchaseOrder.payment_status == "账期未到"
)
```

✅ **两个页面使用相同的查询条件，保证数据一致性**

#### 2. 前端验证

可以添加一个链接，从订单管理跳转到先采后付管理：

```typescript
// 在订单管理页面添加提示
{filteredCount > 0 && (
  <Alert
    message={`找到 ${filteredCount} 个账期未到的订单`}
    description={
      <span>
        这些订单将在先采后付管理页面按还款日分组显示。
        <a onClick={() => navigate('/payment-due')}>前往查看</a>
      </span>
    }
    type="info"
    showIcon
  />
)}
```

## 📊 影响评估

### 需要修改的文件

#### 后端 (8个文件)
- ✅ `api/app/models/order.py` - 模型定义
- ✅ `api/app/api/orders.py` - 订单API
- ✅ `api/app/services/statistics_service.py` - 统计服务
- ✅ `api/app/services/import_service.py` - 导入服务
- ✅ `api/app/services/export_service.py` - 导出服务
- ✅ 数据库迁移脚本
- ✅ API文档更新
- ✅ 测试用例更新

#### 前端 (4个文件)
- ✅ `frontend/src/services/order.ts` - 接口定义
- ✅ `frontend/src/pages/OrderList/index.tsx` - 订单列表页
- ✅ `frontend/src/pages/Dashboard/index.tsx` - 统计面板（如果有相关图表）
- ✅ 其他使用这些字段的组件

### 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 数据丢失 | 高 | 迁移前完整备份数据库 |
| 代码遗漏 | 中 | 全局搜索所有引用点 |
| 用户困惑 | 低 | UI已经使用新术语 |

## ✅ 实施清单

- [ ] 1. 备份当前数据库
- [ ] 2. 全局搜索 `order_status` 和 `payment_method` 的所有引用
- [ ] 3. 创建数据库迁移脚本（如需要）
- [ ] 4. 更新后端模型和API
- [ ] 5. 更新前端接口和页面
- [ ] 6. 更新导入导出逻辑
- [ ] 7. 测试数据一致性
- [ ] 8. 更新文档
- [ ] 9. 部署到生产环境

---

**创建时间**: 2025-11-04
**建议优先级**: 高（应尽快实施以避免混淆）
