# 供应商管理系统设计方案

## 📋 概述

基于现有的采购数据（800条订单，55个供应商），设计全面的供应商管理功能，提供供应商信息管理、采购分析、绩效评估等功能。

## 🎯 核心功能

### 1. 供应商列表页面 (Supplier List)

**功能特性：**
- 供应商基本信息展示（名称、联系方式、地址等）
- 采购统计卡片：
  - 订单总数
  - 采购总金额
  - 合作产品种类
  - 平均订单金额
  - 最近采购日期
- 供应商筛选和搜索
- 排序功能（按金额、订单数、最近采购日期）
- 快速查看TOP供应商

**列表字段：**
```
| 供应商名称 | 订单数 | 采购总额 | 产品种类 | 最近采购 | 平均单价 | 操作 |
```

**操作按钮：**
- 查看详情
- 编辑信息
- 查看订单历史
- 绩效分析

---

### 2. 供应商详情页面 (Supplier Detail)

**顶部概览卡片：**
```
┌─────────────────────────────────────────────────────────────┐
│ 供应商名称：义乌市豫丹新材料有限公司                              │
│ 联系方式：138xxxx1234 | 邮箱：supplier@example.com           │
│ 地址：浙江省义乌市...                                          │
│                                                             │
│ [采购总额]      [订单数量]      [产品种类]      [合作时长]    │
│ ¥397,211.77      291           11种          23个月        │
└─────────────────────────────────────────────────────────────┘
```

**Tab页面：**

**Tab 1: 订单历史**
- 该供应商的所有订单列表
- 支持按产品、规格、日期筛选
- 显示订单详情

**Tab 2: 产品分析**
- 从该供应商采购的产品列表
- 每个产品的：
  - 采购次数
  - 总金额
  - 平均单价
  - 价格趋势图

**Tab 3: 采购趋势**
- 月度采购金额趋势图
- 订单数量趋势
- 季节性分析

**Tab 4: 绩效评估**
- 价格稳定性：价格波动率
- 交付稳定性：订单频率
- 产品多样性：提供的产品种类
- 占比分析：在总采购中的占比

---

### 3. 供应商对比分析 (Supplier Comparison)

**功能：**
- 选择2-5个供应商进行对比
- 对比维度：
  - 采购金额对比
  - 订单数量对比
  - 产品种类对比
  - 价格竞争力（同产品不同供应商价格对比）
  - 合作稳定性

**可视化：**
- 雷达图：多维度评分对比
- 柱状图：金额和数量对比
- 折线图：价格趋势对比

---

## 🎨 UI重新设计方案

### 整体布局改进

**当前问题：**
- 顶部导航栏简单，功能入口不够清晰
- 没有供应商管理入口
- 数据分析功能分散

**改进方案：**

#### 1. 侧边栏导航 (推荐)

```
┌────────────┬───────────────────────────────────────┐
│  Logo      │         采购管理系统                    │
├────────────┼───────────────────────────────────────┤
│            │                                        │
│ 📊 仪表盘   │                                        │
│            │                                        │
│ 📦 订单管理 │         主内容区域                      │
│  ├ 订单列表 │                                        │
│  ├ 新建订单 │                                        │
│  └ 导入导出 │                                        │
│            │                                        │
│ 🏢 供应商   │                                        │
│  ├ 供应商列表│                                        │
│  ├ 供应商对比│                                        │
│  └ 绩效分析 │                                        │
│            │                                        │
│ 📈 产品分析 │                                        │
│            │                                        │
│ 💰 账期跟踪 │                                        │
│            │                                        │
│ ⚙️  设置    │                                        │
└────────────┴───────────────────────────────────────┘
```

#### 2. 顶部导航 + Tab (备选)

保留当前顶部导航，添加供应商管理Tab

---

### 仪表盘改进 (Dashboard v2)

**新增供应商统计卡片：**

```
┌────────────────┬────────────────┬────────────────┬────────────────┐
│ 采购总额        │ 订单总数        │ 产品总数        │ 供应商总数       │
│ ¥780,830.27    │ 800            │ 80             │ 55             │
│ ↑ 12.5%        │ ↑ 8.3%         │ ↑ 5.2%         │ ↑ 3            │
└────────────────┴────────────────┴────────────────┴────────────────┘

┌─────────────────────────────────┬─────────────────────────────────┐
│ TOP 5 供应商（按采购金额）         │  采购月度趋势                     │
│                                 │                                 │
│ 1. 义乌市豫丹... ¥397,211 (50%)  │  ┌─────────────────────────┐   │
│ 2. 义乌市蓝启... ¥124,734 (16%)  │  │     📊 折线图/柱状图      │   │
│ 3. 义乌市物佳... ¥98,657 (13%)   │  │                         │   │
│ 4. 深圳市泰穆... ¥32,477 (4%)    │  └─────────────────────────┘   │
│ 5. 金华市联赢... ¥29,246 (4%)    │                                 │
│                                 │                                 │
│ [查看全部供应商]                  │  [自定义时间范围]                │
└─────────────────────────────────┴─────────────────────────────────┘

┌─────────────────────────────────┬─────────────────────────────────┐
│ 供应商分布（按订单数）              │  产品采购分布                     │
│                                 │                                 │
│  ┌───────────────────────┐      │  ┌───────────────────────┐      │
│  │   📊 饼图/环形图        │      │  │   📊 树图/旭日图        │      │
│  │                       │      │  │                       │      │
│  └───────────────────────┘      │  └───────────────────────┘      │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

### 订单列表改进

**1. 添加供应商筛选：**

```
[快速搜索] [产品名称▼] [规格▼] [供应商▼] [订单状态▼] [支付方式▼] [日期范围]

[查询] [重置] [导入] [导出] [新建订单]
```

**2. 表格列调整：**

```
| ☑ | 日期 | 订单号 | 产品 | 规格 | 金额 | 供应商 | 状态 | 支付方式 | 操作 |
```

供应商列可点击，跳转到供应商详情页

**3. 批量操作：**
- 批量修改供应商
- 批量导出
- 批量修改状态

---

## 💾 数据模型设计

### Supplier (供应商表)

```python
class Supplier(SQLModel, table=True):
    """供应商信息表"""
    __tablename__ = "suppliers"

    id: int = Field(primary_key=True)

    # 基本信息
    name: str = Field(index=True, max_length=300, unique=True)  # 供应商名称
    contact_person: Optional[str] = Field(default=None, max_length=100)  # 联系人
    phone: Optional[str] = Field(default=None, max_length=50)  # 联系电话
    email: Optional[str] = Field(default=None, max_length=100)  # 邮箱
    address: Optional[str] = Field(default=None, max_length=500)  # 地址

    # 业务信息
    code: Optional[str] = Field(default=None, max_length=50)  # 供应商编号
    category: Optional[str] = Field(default=None, max_length=100)  # 供应商类别
    credit_rating: Optional[str] = Field(default=None, max_length=20)  # 信用评级
    payment_terms: Optional[str] = Field(default=None, max_length=200)  # 付款条款

    # 统计字段（由订单数据自动计算）
    total_orders: int = Field(default=0)  # 订单总数
    total_amount: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))  # 采购总额
    product_count: int = Field(default=0)  # 产品种类数
    first_order_date: Optional[date] = Field(default=None)  # 首次合作日期
    last_order_date: Optional[date] = Field(default=None)  # 最近采购日期

    # 备注
    notes: Optional[str] = Field(default=None)  # 备注

    # 状态
    status: str = Field(default="active")  # active, inactive

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### SupplierProduct (供应商-产品关联表)

```python
class SupplierProduct(SQLModel, table=True):
    """供应商提供的产品"""
    __tablename__ = "supplier_products"

    id: int = Field(primary_key=True)
    supplier_id: int = Field(foreign_key="suppliers.id", index=True)
    product_name: str = Field(index=True, max_length=200)
    spec: Optional[str] = Field(default=None, max_length=200)

    # 统计信息（从订单自动计算）
    order_count: int = Field(default=0)
    total_amount: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    avg_price: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    last_purchase_date: Optional[date] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

---

## 🔧 API设计

### 供应商管理

```
GET    /api/suppliers              # 获取供应商列表（支持筛选、排序、分页）
GET    /api/suppliers/{id}         # 获取供应商详情
POST   /api/suppliers              # 创建供应商
PUT    /api/suppliers/{id}         # 更新供应商信息
DELETE /api/suppliers/{id}         # 删除供应商

GET    /api/suppliers/{id}/orders  # 获取供应商的订单历史
GET    /api/suppliers/{id}/products # 获取供应商的产品列表
GET    /api/suppliers/{id}/stats   # 获取供应商统计数据
GET    /api/suppliers/{id}/trend   # 获取供应商采购趋势

GET    /api/suppliers/compare      # 供应商对比（支持多个ID）
GET    /api/suppliers/sync         # 从订单同步供应商数据（自动创建）
```

### 统计分析

```
GET    /api/statistics/suppliers/top        # TOP供应商排行
GET    /api/statistics/suppliers/distribution # 供应商分布
GET    /api/statistics/suppliers/performance  # 供应商绩效分析
```

---

## 📱 前端页面结构

```
frontend/src/pages/
├── Dashboard/           # 仪表盘（改进）
├── OrderList/          # 订单列表（改进）
├── SupplierList/       # 供应商列表 (NEW)
│   ├── index.tsx
│   ├── components/
│   │   ├── SupplierCard.tsx      # 供应商卡片
│   │   ├── SupplierFilter.tsx    # 筛选组件
│   │   └── TopSuppliers.tsx      # TOP供应商组件
├── SupplierDetail/     # 供应商详情 (NEW)
│   ├── index.tsx
│   ├── components/
│   │   ├── OrderHistory.tsx      # 订单历史
│   │   ├── ProductAnalysis.tsx   # 产品分析
│   │   ├── PurchaseTrend.tsx     # 采购趋势
│   │   └── Performance.tsx       # 绩效评估
├── SupplierCompare/    # 供应商对比 (NEW)
│   └── index.tsx
├── ProductList/        # 产品列表
└── PaymentDue/         # 账期跟踪
```

---

## 🚀 实施计划

### Phase 1: 数据模型和基础API（1-2天）
1. ✅ 创建Supplier和SupplierProduct模型
2. ✅ 创建供应商CRUD API
3. ✅ 实现从订单数据同步供应商
4. ✅ 创建供应商统计API

### Phase 2: 供应商列表页面（1天）
1. ✅ 创建供应商列表页面
2. ✅ 实现筛选、搜索、排序
3. ✅ 添加统计卡片
4. ✅ 实现供应商CRUD操作

### Phase 3: 供应商详情页面（1-2天）
1. ✅ 创建供应商详情页面
2. ✅ 实现订单历史Tab
3. ✅ 实现产品分析Tab
4. ✅ 实现采购趋势图表
5. ✅ 实现绩效评估

### Phase 4: UI整体改进（1天）
1. ✅ 添加侧边栏导航
2. ✅ 改进仪表盘布局
3. ✅ 优化订单列表（添加供应商筛选）
4. ✅ 统一样式和交互

### Phase 5: 高级功能（1天）
1. ✅ 供应商对比功能
2. ✅ 供应商绩效评分
3. ✅ 价格趋势分析
4. ✅ 导出功能优化

**总计：5-7天完成**

---

## 📊 预期效果

### 业务价值
1. **供应商洞察**: 清晰了解每个供应商的采购情况
2. **成本优化**: 通过对比分析找到价格更优的供应商
3. **风险管理**: 识别过度依赖单一供应商的风险
4. **决策支持**: 基于数据的供应商选择和谈判

### 用户体验
1. **信息集中**: 供应商信息统一管理
2. **操作便捷**: 快速查找、筛选、对比
3. **可视化**: 直观的图表展示采购趋势
4. **高效**: 减少手动统计和分析时间

---

## 🎯 下一步行动

请确认：
1. ✅ 是否采用侧边栏导航方案？（推荐）
2. ✅ 供应商信息字段是否需要调整？
3. ✅ 是否有其他特殊需求？

确认后我将立即开始实施！
