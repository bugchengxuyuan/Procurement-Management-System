# 先采后付账单导入系统设计方案

## 📋 业务流程

### 完整数据流转

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 日常采购（订单创建/导入）                                │
│    - 即时付款订单: payment_status = "即时付款"              │
│    - 先采后付订单: payment_status = "账期未到"              │
│      必须有 receive_date (确认收货日期)                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 先采后付管理页面（自动关联）                             │
│    - 查询: payment_status = "账期未到"                      │
│    - 按还款日分组 (receive_date 的次月8号)                  │
│    - 显示账单完整性状态                                     │
│      ✓ 过去月份: 完整（例：11月8日账单，10月已结束）       │
│      ⚠ 当前月份: 不完整（例：12月8日账单，11月进行中）      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 月度结算（账单导入）                                     │
│    - 从1688下载月度账单Excel                                │
│    - 上传到系统                                             │
│    - 系统解析订单号                                         │
│    - 匹配系统中的订单                                       │
│    - 批量更新: payment_status = "账期已结"                  │
│    - 记录实际付款日期                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ 数据库设计

### 简化后的字段结构

```python
class PurchaseOrder(SQLModel, table=True):
    id: int
    order_no: str                          # 订单号（唯一，用于匹配1688账单）
    product_name: str                      # 产品名称
    spec: Optional[str]                    # 规格
    purchase_amount: Decimal               # 采购金额
    supplier: Optional[str]                # 供应商
    order_date: date                       # 下单日期
    receive_date: Optional[date]           # 确认收货日期（先采后付必填）

    # 核心字段：只保留 payment_status
    payment_status: str                    # "即时付款" / "账期未到" / "账期已结"

    # 新增字段
    paid_date: Optional[date]              # 实际付款日期（账期已结时记录）
    bill_import_time: Optional[datetime]   # 账单导入时间

    record_time: datetime
    created_at: datetime
    updated_at: datetime
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `payment_status` | str | 付款状态 | "即时付款"、"账期未到"、"账期已结" |
| `receive_date` | date | 确认收货日期 | 2025-10-15（10月15日确认收货） |
| `paid_date` | date | 实际付款日期 | 2025-11-08（11月8日付款） |
| `bill_import_time` | datetime | 账单导入时间 | 2025-11-08 14:30:00 |

### 移除的字段

```python
# ❌ 移除这两个冗余字段
# order_status: str      # 旧字段，与 payment_status 重复
# payment_method: str    # 旧字段，与 payment_status 重复
```

## 🔧 核心功能设计

### 功能 1: 账单导入服务

#### 1.1 Excel 格式要求

**1688账单Excel 应包含的列**：
- 订单编号（必须，用于匹配）
- 产品名称（可选，用于验证）
- 金额（可选，用于验证）
- 确认收货时间（可选，用于验证）
- 付款时间（可选，记录实际付款日期）

#### 1.2 导入逻辑

```python
# api/app/services/bill_import_service.py

class BillImportService:
    """先采后付账单导入服务"""

    def import_payment_bill(self, excel_file: UploadFile) -> BillImportResult:
        """
        导入1688账单并更新订单状态

        流程：
        1. 解析Excel文件
        2. 提取订单号列表
        3. 在数据库中查找匹配的订单
        4. 验证订单当前状态（必须是"账期未到"）
        5. 批量更新为"账期已结"
        6. 记录付款日期和导入时间
        7. 返回导入结果统计
        """
        pass

    def validate_bill_orders(self, order_nos: List[str]) -> ValidationResult:
        """
        验证账单中的订单

        检查：
        - 订单是否存在
        - 当前状态是否为"账期未到"
        - 是否有 receive_date
        """
        pass

    def mark_orders_as_paid(
        self,
        order_nos: List[str],
        paid_date: date
    ) -> UpdateResult:
        """
        批量标记订单为已付款

        更新：
        - payment_status = "账期已结"
        - paid_date = 实际付款日期
        - bill_import_time = 当前时间
        """
        pass
```

#### 1.3 API 端点

```python
# api/app/api/payment_due.py

@router.post("/import-bill")
async def import_payment_bill(
    file: UploadFile = File(...),
    paid_date: date = Form(...),  # 实际付款日期
    session: Session = Depends(get_session)
):
    """
    导入1688账单Excel并批量更新订单状态

    参数：
    - file: Excel文件（必须包含"订单编号"列）
    - paid_date: 实际付款日期（例如：2025-11-08）

    返回：
    - success_count: 成功更新的订单数
    - failed_count: 失败的订单数
    - errors: 错误详情
    - not_found: 未找到的订单号列表
    - already_paid: 已经付款的订单号列表
    """
    pass
```

#### 1.4 返回结果

```typescript
interface BillImportResult {
  success_count: number;           // 成功更新的订单数
  failed_count: number;            // 失败的订单数
  not_found_count: number;         // 未找到的订单数
  already_paid_count: number;      // 已经付款的订单数

  success_orders: string[];        // 成功更新的订单号列表
  not_found_orders: string[];      // 未找到的订单号列表
  already_paid_orders: string[];   // 已付款的订单号列表
  errors: Array<{
    order_no: string;
    error: string;
  }>;

  paid_date: string;               // 付款日期
  import_time: string;             // 导入时间
  total_amount: number;            // 总付款金额
}
```

### 功能 2: 账单完整性检测优化

#### 2.1 逻辑优化

```python
def get_payment_due_groups(session: Session, include_paid: bool = False):
    """获取按还款日分组的账期"""

    # ... 分组逻辑 ...

    for due_date, orders_in_group in grouped_orders.items():
        # 获取确认收货月份范围
        receive_dates = [o.receive_date for o in orders_in_group if o.receive_date]
        receive_month_start = min(receive_dates)
        receive_month_end = max(receive_dates)

        # 关键优化：只有当前月份才标记为不完整
        today = date.today()
        receive_month = receive_month_start.replace(day=1)  # 确认收货月份的第一天
        current_month = today.replace(day=1)                # 当前月份的第一天

        is_current_month = (receive_month == current_month)

        # 只有当前月份且月份未结束才标记为不完整
        if is_current_month:
            # 如果今天是11月4日，11月还没结束，账单可能不完整
            is_incomplete = (today.day < 28)  # 通常月底前都可能有新订单
        else:
            # 过去月份的账单都是完整的
            is_incomplete = False

        # 示例：
        # - 今天：2025-11-04
        # - 11月8日账单（10月收货）：receive_month = 2025-10-01 ≠ current_month → complete ✅
        # - 12月8日账单（11月收货）：receive_month = 2025-11-01 = current_month → incomplete ⚠️
```

### 功能 3: 前端账单导入界面

#### 3.1 先采后付管理页面增强

```typescript
// frontend/src/pages/PaymentDue/index.tsx

// 在账期分组表格上方添加"导入账单"按钮
<Card>
  <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
    <h3>按还款日分组</h3>
    <Space>
      <Button
        type="primary"
        icon={<UploadOutlined />}
        onClick={() => setImportModalVisible(true)}
      >
        导入1688账单
      </Button>
      <span>显示已付款账期:</span>
      <Switch checked={includePaid} onChange={setIncludePaid} />
    </Space>
  </div>

  {/* 账期分组表格 */}
</Card>
```

#### 3.2 账单导入 Modal

```typescript
<Modal
  title="导入1688账单"
  open={importModalVisible}
  onCancel={() => setImportModalVisible(false)}
  footer={null}
  width={600}
>
  <Alert
    message="导入说明"
    description={
      <div>
        <p>1. 从1688下载月度账单Excel文件</p>
        <p>2. Excel必须包含"订单编号"列</p>
        <p>3. 系统会自动匹配订单并标记为"账期已结"</p>
        <p>4. 只能导入状态为"账期未到"的订单</p>
      </div>
    }
    type="info"
    showIcon
    style={{ marginBottom: 16 }}
  />

  <Form onFinish={handleImportBill}>
    <Form.Item
      name="paid_date"
      label="实际付款日期"
      rules={[{ required: true, message: '请选择付款日期' }]}
    >
      <DatePicker style={{ width: '100%' }} />
    </Form.Item>

    <Form.Item
      name="file"
      label="账单文件"
      rules={[{ required: true, message: '请上传账单文件' }]}
    >
      <Upload
        beforeUpload={(file) => {
          setUploadFile(file);
          return false;
        }}
        accept=".xlsx,.xls"
        maxCount={1}
      >
        <Button icon={<UploadOutlined />}>选择Excel文件</Button>
      </Upload>
    </Form.Item>

    <Form.Item>
      <Button
        type="primary"
        htmlType="submit"
        loading={importing}
        block
      >
        开始导入
      </Button>
    </Form.Item>
  </Form>
</Modal>
```

#### 3.3 导入结果展示

```typescript
// 导入完成后显示详细结果
<Modal
  title="账单导入结果"
  open={resultModalVisible}
  onOk={() => setResultModalVisible(false)}
  width={800}
>
  <Result
    status={result.failed_count === 0 ? "success" : "warning"}
    title={`成功导入 ${result.success_count} 个订单`}
    subTitle={`付款日期: ${result.paid_date}，总金额: ¥${result.total_amount.toFixed(2)}`}
  />

  <Descriptions bordered column={2}>
    <Descriptions.Item label="成功更新">{result.success_count} 单</Descriptions.Item>
    <Descriptions.Item label="未找到订单">{result.not_found_count} 单</Descriptions.Item>
    <Descriptions.Item label="已付款订单">{result.already_paid_count} 单</Descriptions.Item>
    <Descriptions.Item label="导入时间">{result.import_time}</Descriptions.Item>
  </Descriptions>

  {result.not_found_orders.length > 0 && (
    <Alert
      message="未找到的订单"
      description={
        <div style={{ maxHeight: 200, overflow: 'auto' }}>
          {result.not_found_orders.map(no => <div key={no}>{no}</div>)}
        </div>
      }
      type="warning"
      showIcon
      style={{ marginTop: 16 }}
    />
  )}
</Modal>
```

## 🔄 完整业务场景示例

### 场景：11月8日结算10月份订单

#### 1. 初始状态（11月4日）

**先采后付管理页面显示**：

```
┌─────────────────────────────────────────────────────────┐
│ 2025年11月08日还款账期  [即将到期（4天后）]             │
├─────────────────────────────────────────────────────────┤
│ 确认收货时段: 2025-10-02 至 2025-10-31                  │
│ 订单数量: 30单（未付: 30 / 已付: 0）                    │
│ 金额统计: 总额 ¥7,578.05                                │
│ [查看详情(30)] [标记付款]                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 2025年12月08日还款账期  [34天后]  ⚠️ 账单未完整        │
├─────────────────────────────────────────────────────────┤
│ 确认收货时段: 2025-11-01 至 2025-11-04                  │
│ 订单数量: 5单（未付: 5 / 已付: 0）                      │
│ 金额统计: 总额 ¥5,949.15                                │
│ [查看详情(5)] [标记付款]                                │
└─────────────────────────────────────────────────────────┘
```

注意：
- ✅ 11月8日账单（10月收货）：**完整**（10月已结束）
- ⚠️ 12月8日账单（11月收货）：**不完整**（11月进行中，今天才4号）

#### 2. 11月8日：从1688下载账单并导入

**用户操作**：
1. 点击"导入1688账单"按钮
2. 选择付款日期：2025-11-08
3. 上传从1688下载的"11月账单.xlsx"
4. 点击"开始导入"

**系统处理**：
```python
# 解析Excel，提取订单号
order_nos = ["4846615021115878222", "4845306422504878222", ...]

# 查找匹配订单（30单）
matched_orders = session.exec(
    select(PurchaseOrder).where(
        PurchaseOrder.order_no.in_(order_nos),
        PurchaseOrder.payment_status == "账期未到"
    )
).all()  # 找到 30单

# 批量更新
for order in matched_orders:
    order.payment_status = "账期已结"
    order.paid_date = date(2025, 11, 8)
    order.bill_import_time = datetime.now()
    order.updated_at = datetime.now()

session.commit()
```

**导入结果**：
```
✅ 成功导入 30 个订单
   付款日期: 2025-11-08
   总金额: ¥7,578.05

   成功更新: 30 单
   未找到订单: 0 单
   已付款订单: 0 单
```

#### 3. 导入后状态

**先采后付管理页面** (默认不显示已付款):

```
┌─────────────────────────────────────────────────────────┐
│ 2025年12月08日还款账期  [30天后]  ⚠️ 账单未完整        │
├─────────────────────────────────────────────────────────┤
│ 确认收货时段: 2025-11-01 至 2025-11-04                  │
│ 订单数量: 5单（未付: 5 / 已付: 0）                      │
│ 金额统计: 总额 ¥5,949.15                                │
│ [查看详情(5)] [标记付款]                                │
└─────────────────────────────────────────────────────────┘

(11月8日的账期已付款，默认不显示)
```

**开启"显示已付款账期"后**：

```
┌─────────────────────────────────────────────────────────┐
│ 2025年11月08日还款账期  [已付款] ✅                     │
├─────────────────────────────────────────────────────────┤
│ 确认收货时段: 2025-10-02 至 2025-10-31                  │
│ 订单数量: 30单（未付: 0 / 已付: 30）                    │
│ 金额统计: 总额 ¥7,578.05 (已付: ¥7,578.05)             │
│ 付款日期: 2025-11-08                                    │
│ [查看详情(30)]                                          │
└─────────────────────────────────────────────────────────┘
```

## 📊 数据库迁移

### 步骤 1: 添加新字段

```sql
-- 添加实际付款日期字段
ALTER TABLE purchase_orders ADD COLUMN paid_date DATE;

-- 添加账单导入时间字段
ALTER TABLE purchase_orders ADD COLUMN bill_import_time TIMESTAMP;
```

### 步骤 2: 移除冗余字段（可选）

```sql
-- SQLite 不支持 DROP COLUMN，需要重建表
-- 这里暂时保留字段，但不在代码中使用
-- 或者创建新表迁移数据后删除旧表
```

## 🎯 实施优先级

### Phase 1: 核心功能 (高优先级)
1. ✅ 添加 `paid_date` 和 `bill_import_time` 字段
2. ✅ 实现账单导入服务
3. ✅ 优化 `is_incomplete` 逻辑
4. ✅ 创建导入API端点

### Phase 2: UI实现 (高优先级)
1. ✅ 前端账单导入Modal
2. ✅ 导入结果展示
3. ✅ 移除前端对 order_status 和 payment_method 的引用

### Phase 3: 字段清理 (中优先级)
1. ⚠️ 移除后端对 order_status 和 payment_method 的引用
2. ⚠️ 数据库字段清理（可选，暂时保留向后兼容）

## ✅ 验证清单

- [ ] 账单导入功能正常工作
- [ ] 批量更新订单状态成功
- [ ] is_incomplete 逻辑正确（过去月份=完整，当前月份=不完整）
- [ ] 导入结果准确（成功/失败/未找到统计）
- [ ] 前端UI清晰易用
- [ ] 订单管理和先采后付管理数据一致
- [ ] 已付款账期可正确显示/隐藏

---

**创建时间**: 2025-11-04
**设计版本**: v1.0
