# 采购管理系统优化计划

## 目标
将系统从"基础记录工具"升级为"智能采购助手"

---

## 优先级矩阵

| 功能 | 业务价值 | 开发难度 | 优先级 | 预计工时 |
|------|---------|---------|--------|---------|
| 供应商管理 | ⭐⭐⭐⭐⭐ | 中 | P0 | 3-5天 |
| 智能预警 | ⭐⭐⭐⭐⭐ | 低 | P0 | 2-3天 |
| 采购对比 | ⭐⭐⭐⭐ | 低 | P0 | 2天 |
| 快速下单 | ⭐⭐⭐⭐ | 低 | P0 | 1-2天 |
| 数据看板增强 | ⭐⭐⭐⭐ | 中 | P1 | 2-3天 |
| 移动端适配 | ⭐⭐⭐⭐ | 中 | P1 | 3-4天 |
| 成本分析 | ⭐⭐⭐⭐ | 中 | P1 | 2-3天 |
| 报表增强 | ⭐⭐⭐ | 低 | P1 | 2天 |
| 审批工作流 | ⭐⭐⭐ | 高 | P2 | 5-7天 |
| 数据备份 | ⭐⭐⭐ | 低 | P2 | 1天 |

---

## 第一阶段：核心功能增强（Week 1-2）

### 1. 供应商管理模块

#### 数据模型
```python
class Supplier(SQLModel, table=True):
    """供应商表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)  # 供应商名称
    contact_person: str = Field(max_length=100)  # 联系人
    phone: str = Field(max_length=50)  # 联系电话
    platform: str  # 平台：1688/淘宝/线下
    shop_url: Optional[str]  # 店铺链接
    rating: int = Field(default=5, ge=1, le=5)  # 评分 1-5星
    status: str = Field(default="active")  # active/blacklist/preferred
    total_orders: int = Field(default=0)  # 累计订单数
    total_amount: Decimal = Field(default=0)  # 累计采购额
    last_order_date: Optional[date]  # 最近采购日期
    notes: Optional[str]  # 备注
    created_at: datetime
    updated_at: datetime
```

#### API接口
```
GET    /api/suppliers          # 供应商列表（分页、筛选）
POST   /api/suppliers          # 添加供应商
GET    /api/suppliers/{id}     # 供应商详情
PUT    /api/suppliers/{id}     # 更新供应商
DELETE /api/suppliers/{id}     # 删除供应商
GET    /api/suppliers/{id}/orders  # 供应商订单历史
GET    /api/suppliers/stats    # 供应商统计分析
```

#### 前端页面
- 供应商列表页（卡片视图 + 表格视图）
- 供应商详情页（包含采购历史、趋势图）
- 供应商对比页（多个供应商并排对比）

#### 订单关联
- 在 PurchaseOrder 表添加 `supplier_id` 字段
- 导入Excel时支持供应商映射
- 订单详情显示供应商信息

---

### 2. 智能预警系统

#### 预警类型
```python
class AlertType(str, Enum):
    PAYMENT_DUE = "payment_due"          # 账期到期
    PAYMENT_OVERDUE = "payment_overdue"   # 账期超期
    PRICE_SPIKE = "price_spike"           # 价格异常上涨
    DUPLICATE_ORDER = "duplicate_order"   # 重复订单
    BUDGET_EXCEEDED = "budget_exceeded"   # 预算超支
    LOW_FREQUENCY = "low_frequency"       # 低频产品提醒

class Alert(SQLModel, table=True):
    """预警记录表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    alert_type: AlertType
    severity: str  # low/medium/high/critical
    title: str  # 预警标题
    message: str  # 预警内容
    related_order_id: Optional[int]  # 关联订单
    related_product_name: Optional[str]  # 关联产品
    is_read: bool = Field(default=False)
    is_resolved: bool = Field(default=False)
    created_at: datetime
```

#### 预警规则引擎
```python
# 定时任务（每天凌晨执行）
async def check_alerts():
    # 1. 账期预警
    check_payment_due_alerts()

    # 2. 价格异常检测
    check_price_spike_alerts()

    # 3. 重复订单检测（24小时内）
    check_duplicate_order_alerts()

    # 4. 预算超支检测
    check_budget_alerts()
```

#### 前端展示
- 顶部通知中心（小红点提醒）
- 预警列表页（可筛选、标记已读）
- Dashboard 预警卡片

---

### 3. 采购对比功能

#### 产品价格历史图表
```typescript
// 使用 @ant-design/charts 的 Line 图表
<Line
  data={priceHistory}
  xField="date"
  yField="price"
  seriesField="supplier"
  annotations={[
    {
      type: 'line',
      start: ['min', avgPrice],
      end: ['max', avgPrice],
      text: { content: '平均价格', position: 'end' }
    }
  ]}
/>
```

#### 价格对比卡片
```
┌───────────────────────────────────────┐
│ 水槽扳手 - 采购分析                     │
├───────────────────────────────────────┤
│ 📊 价格趋势                            │
│   最低: ¥5.20 (2024-03-15, 供应商A)   │
│   最高: ¥7.80 (2024-08-20, 供应商B)   │
│   当前: ¥6.50 (2024-11-02, 供应商C)   │
│   平均: ¥6.12                          │
│                                        │
│ 💡 建议                                │
│   • 当前价格高于平均 6.2%              │
│   • 供应商A价格最优                    │
│   • 建议等待促销或更换供应商            │
│                                        │
│ 📈 采购频率                            │
│   每月平均: 9.5 次                     │
│   上次采购: 5天前                      │
│   预计下次: 25天后                     │
└───────────────────────────────────────┘
```

---

### 4. 快速下单功能

#### 常用产品模板
```typescript
// 前端页面：订单创建页
<Card title="常用产品快捷下单">
  <Space wrap>
    {favoriteProducts.map(product => (
      <Card.Grid key={product.id} hoverable>
        <div className="quick-order-card">
          <h4>{product.name}</h4>
          <p>上次: ¥{product.lastPrice}</p>
          <Button
            type="primary"
            onClick={() => quickOrder(product)}
          >
            快速下单
          </Button>
        </div>
      </Card.Grid>
    ))}
  </Space>
</Card>
```

#### 历史订单复制
```typescript
// 订单列表添加"复制"按钮
<Button
  icon={<CopyOutlined />}
  onClick={() => duplicateOrder(record)}
>
  复制订单
</Button>
```

#### 1688链接解析（可选）
```python
@router.post("/parse-1688-link")
async def parse_1688_order_link(url: str):
    """解析1688订单链接，提取订单信息"""
    # 使用正则表达式提取订单号
    # 返回解析结果供前端填充表单
    return {
        "order_no": "提取的订单号",
        "product_name": "提取的产品名",
        # ...
    }
```

---

## 第二阶段：体验优化（Week 3-4）

### 5. Dashboard增强

#### 新增卡片
```
┌──────────────────────┐ ┌──────────────────────┐
│ 本月 vs 上月          │ │ 成本趋势预测         │
│ 采购额: ↑ 12.5%      │ │ 下月预计: ¥85,342    │
│ 订单数: ↓ 5.3%       │ │ 环比: ↑ 8.2%         │
└──────────────────────┘ └──────────────────────┘

┌──────────────────────┐ ┌──────────────────────┐
│ 成本TOP3产品          │ │ 待办事项             │
│ 1. 高铸胶 (23.4%)    │ │ • 5个订单即将到期    │
│ 2. 水槽扳手 (18.2%)  │ │ • 3个价格异常        │
│ 3. 白色鞋胶 (12.1%)  │ │ • 2个重复订单        │
└──────────────────────┘ └──────────────────────┘
```

#### 时间段对比功能
```typescript
<RangePicker.RangePicker
  picker="month"
  onChange={handleCompare}
  placeholder={['开始月份', '结束月份']}
/>
// 显示两个时间段的采购数据对比
```

---

### 6. 移动端适配

#### 响应式布局优化
```css
/* 关键断点 */
@media (max-width: 768px) {
  .order-card {
    grid-template-columns: 1fr;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
```

#### 移动端专用功能
- 底部导航栏（订单/统计/我的）
- 手势操作（左滑删除）
- 扫码下单（调用摄像头）

---

### 7. 成本分析工具

#### 成本分布饼图
```typescript
<Pie
  data={costDistribution}
  angleField="amount"
  colorField="product"
  label={{
    type: 'outer',
    content: '{name} {percentage}'
  }}
  interactions={[
    { type: 'element-active' }
  ]}
/>
```

#### 成本趋势分析
- 周环比、月环比、年同比
- 成本上升/下降产品排行
- 成本预测（基于历史数据的线性回归）

---

### 8. 报表增强

#### 月度采购汇总报告
```python
@router.get("/reports/monthly-summary")
async def generate_monthly_report(
    year: int,
    month: int,
    session: Session = Depends(get_session)
):
    """生成月度采购汇总报告"""
    # 1. 总体数据
    # 2. 分类数据（按产品、供应商）
    # 3. 趋势分析
    # 4. 异常提醒
    # 导出为PDF或Excel
```

#### 自定义报表模板
- 用户可选择字段
- 自定义排序和分组
- 保存报表模板

---

## 第三阶段：高级功能（Week 5+）

### 9. 审批工作流

#### 状态机
```
草稿 → 待审批 → 已批准 → 已采购 → 已入库
              ↓
            已拒绝
```

#### 权限管理
```python
class Role(str, Enum):
    ADMIN = "admin"           # 管理员
    PURCHASER = "purchaser"   # 采购员
    APPROVER = "approver"     # 审批人
    FINANCE = "finance"       # 财务
    VIEWER = "viewer"         # 查看者
```

---

### 10. AI辅助功能（可选）

#### 采购预测
```python
# 基于历史数据预测下月采购需求
def predict_next_month_demand(product_name: str):
    """使用简单的移动平均预测"""
    # 获取过去6个月的采购量
    # 计算移动平均
    # 考虑季节性因素
    return predicted_quantity
```

#### 价格异常检测
```python
def detect_price_anomaly(product_name: str, price: float):
    """检测价格是否异常"""
    # 获取历史价格
    # 计算均值和标准差
    # 如果超过2个标准差，则为异常
    return is_anomaly
```

---

## 技术债务清理

### 当前需要改进的地方
1. ✅ 添加用户认证和权限管理
2. ✅ 实现审计日志
3. ✅ 优化数据库查询（添加适当的索引）
4. ✅ 添加API文档（Swagger完善）
5. ✅ 前端错误处理统一化
6. ✅ 添加单元测试和集成测试

---

## 预期效果

### 优化前
- 基础的订单记录和查询
- 手动计算账期
- 无供应商管理
- 静态报表

### 优化后
- 智能采购助手
- 自动预警提醒
- 供应商评估和对比
- 数据驱动的采购决策
- 移动办公支持
- 自动化报表生成

---

## 投资回报分析

| 优化项 | 节省时间/天 | 降低成本 | ROI |
|-------|-----------|---------|-----|
| 供应商管理 | 30min | 5-10% | 高 |
| 智能预警 | 1h | 避免逾期 | 高 |
| 采购对比 | 20min | 3-5% | 中 |
| 快速下单 | 1h | 效率↑ | 中 |
| 移动端 | 2h | 便利性↑ | 中 |

**总计：每天节省约 4.5 小时，采购成本降低 5-15%**

---

## 下一步行动

1. **评审优先级** - 根据实际业务需求调整优先级
2. **技术选型确认** - 确认使用的技术栈和工具
3. **开始开发** - 从第一阶段的核心功能开始
4. **持续迭代** - 小步快跑，快速验证

---

*最后更新: 2025-11-02*
