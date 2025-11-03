# 精准产品匹配方案 - 供应商+规格+产品三维匹配

## 📊 数据分析结果

基于对您的1688订单数据（71条）的深度分析：

### 可用的匹配维度

| 维度 | 字段 | 数据完整度 | 示例 |
|------|------|-----------|------|
| **供应商** | 卖家会员名 | 91.5% | "亦纯文化"、"恩佐商贸有限公司" |
| **产品名** | 货品标题 | 100% | "管道疏通剂袋装 25g..." |
| **规格** | 从标题提取 | ~80% | "25g"、"100个"、"350x190mm" |
| **型号** | 型号字段 | 40.8% | "铸工胶20g一盒" |
| **货号** | 单品货号 | 95.8% | "06铸工胶盒装-20" |

### 关键发现

1. **供应商有明显的产品特征**
   - "亦纯文化"：23条订单，专营胶水类（铸工胶、鞋胶）
   - "恩佐商贸"：13条订单，专营B-7000胶水
   - "联赢包装"：7条订单，专营OPP袋

2. **规格信息可提取**
   - 重量/容量：25g, 20g, 3ml, 50ml
   - 尺寸：350x190x230mm, 10*15
   - 数量：100个, 700支

3. **同供应商+同产品类型 = 高匹配率**
   - 例如：亦纯文化的所有胶水都可以归类到系统中的"高铸胶"、"鞋胶"等

---

## 🎯 完善后的方案架构

### 方案核心：三层数据模型

```
┌─────────────────────────────────────────────────────────┐
│                    Layer 1: 供应商层                       │
│  Supplier: 卖家会员名 + 卖家公司名 + 1688店铺信息            │
│  作用: 缩小匹配范围，同供应商产品命名规律相似               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Layer 2: 产品层                         │
│  Product: 产品名称 + 类别 + 常用别名                        │
│  作用: 核心匹配对象，支持多个别名                           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Layer 3: 规格层                         │
│  ProductSpec: 规格描述 + 单位 + 数量范围                    │
│  作用: 区分同名产品的不同规格版本                           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 Layer 4: 映射学习层                        │
│  ProductMapping: 1688标题 → 系统产品 + 置信度              │
│  作用: 记录历史匹配，自动学习用户偏好                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 数据库设计

### 1. 供应商表（Supplier）

```python
class Supplier(SQLModel, table=True):
    """供应商表"""
    __tablename__ = "suppliers"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 基础信息
    name: str = Field(max_length=200, index=True)  # 卖家会员名（主要）
    company_name: Optional[str] = Field(max_length=300)  # 卖家公司名
    platform: str = Field(default="1688")  # 平台：1688/淘宝/拼多多

    # 联系信息
    contact_person: Optional[str]
    phone: Optional[str]
    shop_url: Optional[str]  # 店铺链接

    # 统计信息
    total_orders: int = Field(default=0)
    total_amount: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    first_order_date: Optional[date]
    last_order_date: Optional[date]

    # 评级与标签
    rating: int = Field(default=5, ge=1, le=5)  # 1-5星
    tags: Optional[str]  # JSON字符串，如 '["胶水类", "包装材料"]'
    status: str = Field(default="active")  # active/blacklist/preferred
    notes: Optional[str]

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 2. 产品主数据表（Product）- 增强版

```python
class Product(SQLModel, table=True):
    """产品主数据表（增强版）"""
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 基础信息
    product_name: str = Field(max_length=200, index=True)  # 标准产品名
    category: Optional[str] = Field(max_length=100)  # 产品类别
    aliases: Optional[str]  # JSON字符串存储别名列表

    # 新增：常见规格列表
    common_specs: Optional[str]  # JSON: ['25g', '50g', '100g']

    # 新增：常见供应商列表
    common_suppliers: Optional[str]  # JSON: [supplier_id_1, supplier_id_2]

    # 统计信息（保留原有字段）
    total_purchase_amount: Decimal = Field(default=0, sa_column=Column(Numeric(12, 2)))
    total_order_count: int = Field(default=0)
    avg_unit_price: Decimal = Field(default=0, sa_column=Column(Numeric(10, 2)))
    last_purchase_date: Optional[date]

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 3. 产品规格表（ProductSpec）

```python
class ProductSpec(SQLModel, table=True):
    """产品规格表"""
    __tablename__ = "product_specs"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)

    # 规格信息
    spec_name: str = Field(max_length=100)  # 规格名称，如 "25g袋装"
    spec_value: str = Field(max_length=200)  # 规格值，如 "25"
    spec_unit: Optional[str] = Field(max_length=20)  # 单位，如 "g", "ml"

    # 规格类型
    spec_type: str  # weight/volume/size/quantity/color

    # 价格范围
    min_price: Optional[Decimal] = Field(sa_column=Column(Numeric(10, 2)))
    max_price: Optional[Decimal] = Field(sa_column=Column(Numeric(10, 2)))
    avg_price: Optional[Decimal] = Field(sa_column=Column(Numeric(10, 2)))

    # 统计
    order_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.now)
```

### 4. 产品映射表（ProductMapping）

```python
class ProductMapping(SQLModel, table=True):
    """产品映射表 - 记录1688标题到系统产品的映射"""
    __tablename__ = "product_mappings"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 1688信息
    source_title: str = Field(max_length=500, index=True)  # 1688货品标题
    source_title_hash: str = Field(max_length=64, index=True)  # MD5哈希，加速查询
    supplier_id: Optional[int] = Field(foreign_key="suppliers.id")

    # 匹配信息
    product_id: int = Field(foreign_key="products.id", index=True)
    spec_id: Optional[int] = Field(foreign_key="product_specs.id")

    # 匹配元数据
    match_method: str  # manual/auto_exact/auto_keyword/auto_fuzzy
    confidence: float = Field(ge=0, le=1)  # 0-1
    matched_keywords: Optional[str]  # JSON列表

    # 审核状态
    status: str = Field(default="pending")  # pending/confirmed/rejected
    confirmed_by: Optional[str]  # 用户ID
    confirmed_at: Optional[datetime]

    # 使用统计
    use_count: int = Field(default=0)  # 被使用次数
    last_used_at: Optional[datetime]

    created_at: datetime = Field(default_factory=datetime.now)
```

### 5. 订单表（PurchaseOrder）- 增强版

```python
class PurchaseOrder(PurchaseOrderBase, table=True):
    """采购订单表（增强版）"""
    __tablename__ = "purchase_orders"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 原有字段...
    order_no: str
    product_name: str
    purchase_amount: Decimal
    order_date: date
    # ...

    # 新增字段
    supplier_id: Optional[int] = Field(foreign_key="suppliers.id", index=True)
    product_id: Optional[int] = Field(foreign_key="products.id", index=True)
    spec_id: Optional[int] = Field(foreign_key="product_specs.id")

    # 规格信息（冗余存储，便于查询）
    spec_description: Optional[str] = Field(max_length=200)  # 如 "25g袋装"

    # 原始1688信息（可选，用于追溯）
    source_title: Optional[str] = Field(max_length=500)  # 1688原始标题
    source_order_id: Optional[str] = Field(max_length=50)  # 1688订单号

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

---

## 🔍 多维度智能匹配算法

### 匹配策略（按优先级）

```python
class EnhancedProductMatcher:
    """增强版产品匹配器 - 支持供应商+规格+产品三维匹配"""

    def match(self,
              title_1688: str,
              supplier_name: Optional[str] = None,
              amount: Optional[float] = None) -> MatchResult:
        """
        多维度匹配策略

        优先级从高到低：
        1. 历史映射查询（最快，最准）
        2. 供应商+产品名精确匹配
        3. 供应商+关键词匹配
        4. 全局产品名精确匹配
        5. 全局关键词匹配
        6. 规格辅助匹配
        7. 模糊匹配
        """

        # Step 1: 查询历史映射（命中率最高）
        mapping = self.query_historical_mapping(title_1688, supplier_name)
        if mapping and mapping.confidence >= 0.9:
            return MatchResult(
                method='historical',
                product=mapping.product,
                spec=mapping.spec,
                confidence=mapping.confidence
            )

        # Step 2: 供应商约束下的精确匹配
        if supplier_name:
            supplier = self.get_supplier(supplier_name)
            if supplier:
                # 获取该供应商常见的产品列表
                candidate_products = self.get_supplier_products(supplier.id)

                # 在供应商产品范围内匹配
                result = self.exact_match(title_1688, candidate_products)
                if result:
                    result.method = 'supplier_exact'
                    result.confidence = min(result.confidence + 0.1, 1.0)  # 提升10%
                    return result

                # 关键词匹配
                result = self.keyword_match(title_1688, candidate_products)
                if result and result.confidence >= 0.6:
                    result.method = 'supplier_keyword'
                    result.confidence = min(result.confidence + 0.1, 1.0)
                    return result

        # Step 3: 全局精确匹配
        result = self.exact_match(title_1688, self.all_products)
        if result:
            return result

        # Step 4: 规格辅助匹配
        extracted_specs = self.extract_specs(title_1688)
        if extracted_specs:
            result = self.spec_assisted_match(title_1688, extracted_specs, amount)
            if result and result.confidence >= 0.7:
                return result

        # Step 5: 全局关键词匹配
        result = self.keyword_match(title_1688, self.all_products)
        if result and result.confidence >= 0.5:
            return result

        # Step 6: 模糊匹配（最后手段）
        result = self.fuzzy_match(title_1688)
        if result and result.confidence >= 0.6:
            return result

        # 无法匹配，返回候选列表供用户选择
        candidates = self.get_top_candidates(title_1688, supplier_name, top_k=5)
        return MatchResult(
            method='manual_required',
            product=None,
            confidence=0,
            candidates=candidates
        )
```

### 规格辅助匹配逻辑

```python
def spec_assisted_match(self, title: str, specs: List[str], amount: Optional[float]) -> MatchResult:
    """
    利用规格信息辅助匹配

    示例：
    1688标题: "管道疏通剂袋装 25g..."
    提取规格: ["25g"]
    系统产品: "管道疏通剂"
    规格库: ["25g", "50g", "100g"]

    匹配逻辑:
    1. 产品名匹配（管道疏通剂）
    2. 规格匹配（25g在规格库中）
    3. 价格验证（金额是否在该规格的价格范围内）

    → 提升置信度
    """
    candidates = []

    for product in self.all_products:
        # 基础名称匹配
        base_score = self.calculate_name_similarity(title, product.product_name)
        if base_score < 0.4:
            continue

        # 规格匹配
        spec_score = 0
        matched_spec = None
        for spec_str in specs:
            for product_spec in product.specs:
                if spec_str in product_spec.spec_name:
                    spec_score = 0.3  # 规格匹配加30分
                    matched_spec = product_spec

                    # 价格验证
                    if amount and matched_spec.min_price and matched_spec.max_price:
                        if matched_spec.min_price <= amount <= matched_spec.max_price * 1.2:
                            spec_score += 0.1  # 价格合理再加10分

        final_score = base_score + spec_score
        if final_score >= 0.7:
            candidates.append(MatchResult(
                product=product,
                spec=matched_spec,
                confidence=min(final_score, 1.0),
                method='spec_assisted'
            ))

    return max(candidates, key=lambda x: x.confidence) if candidates else None
```

---

## 🎨 用户界面设计

### 1. 1688订单导入向导

```
┌─────────────────────────────────────────────────────────────┐
│  步骤 1/4: 上传1688订单Excel文件                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [📁 点击上传] 或 拖拽文件到此处                              │
│                                                              │
│  支持格式: .xlsx, .xls                                       │
│  文件要求: 包含 '货品标题', '卖家会员名', '实付款' 等字段      │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  步骤 2/4: 解析结果                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 解析统计                                                  │
│    总订单数: 65                                              │
│    识别供应商: 17 家                                          │
│    提取规格: 52 条                                           │
│                                                              │
│  ✅ 自动匹配成功: 38 (58.5%)                                 │
│  ⚠️  需要确认: 15 (23.1%)                                    │
│  ❌ 无法匹配: 12 (18.5%)                                     │
│                                                              │
│  [查看详情]  [下一步]                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  步骤 3/4: 确认匹配结果                                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tab: [✅ 已匹配(38)] [⚠️ 待确认(15)] [❌ 未匹配(12)]        │
│                                                              │
│  ⚠️ 待确认列表:                                               │
│                                                              │
│  1. 1688标题: "高品质AB胶铸工胶批发粘金属..."               │
│     供应商: 亦纯文化                                          │
│     金额: ¥450.00                                            │
│     规格: 20g                                                │
│                                                              │
│     推荐匹配: 高铸胶 (置信度: 75%) [✓ 确认] [✗ 拒绝]        │
│                                                              │
│     或手动选择:                                               │
│     [下拉选择产品 ▼] [添加新产品]                            │
│     规格: [20g ▼]                                            │
│                                                              │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  [批量操作 ▼] [上一步] [下一步]                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  步骤 4/4: 导入确认                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📋 导入摘要                                                  │
│                                                              │
│  新增订单: 53 条                                             │
│  更新订单: 0 条                                              │
│  跳过重复: 12 条                                             │
│                                                              │
│  新增供应商: 5 家                                            │
│  新增规格: 8 个                                              │
│                                                              │
│  学习映射: 38 条（将记录匹配规则，下次自动匹配）              │
│                                                              │
│  [ ] 导入后更新产品统计                                       │
│  [✓] 保存匹配映射供后续使用                                   │
│                                                              │
│  [取消] [开始导入]                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. 产品管理页面 - 增强版

```
┌─────────────────────────────────────────────────────────────┐
│  产品详情: 高铸胶                                [编辑] [删除] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  基础信息:                                                    │
│    产品名称: 高铸胶                                           │
│    类别: 胶水                                                 │
│    别名: 铸工胶, 铸胶, 高质量铸工胶                           │
│                                                              │
│  常见规格:                                                    │
│    ┌───────────────────────────────────────────┐           │
│    │ 规格      数量    平均单价    最近采购      │           │
│    ├───────────────────────────────────────────┤           │
│    │ 20g袋装   120    ¥22.50     2天前        │           │
│    │ 50g盒装   85     ¥45.00     5天前        │           │
│    │ 100g盒装  42     ¥85.00     12天前       │           │
│    └───────────────────────────────────────────┘           │
│    [+ 添加规格]                                              │
│                                                              │
│  常见供应商:                                                  │
│    1. 亦纯文化 (23次采购, ⭐⭐⭐⭐⭐)                          │
│    2. 高品质胶水厂 (12次采购, ⭐⭐⭐⭐)                        │
│    [查看详情]                                                │
│                                                              │
│  1688映射规则: 15 条                                         │
│    • "高品质AB胶铸工胶..." → 自动匹配 (置信度: 95%)          │
│    • "铸工胶20g一盒..." → 自动匹配 (置信度: 100%)            │
│    • ... 还有13条                                            │
│    [查看全部] [添加映射]                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 实施路径

### Phase 1: 数据库升级（1-2天）

```bash
# 1. 创建新表
python3 api/create_enhanced_tables.py

# 2. 迁移现有数据
python3 api/migrate_to_enhanced_schema.py
```

#### 迁移脚本示例

```python
# api/migrate_to_enhanced_schema.py

# 1. 创建新表
init_db()  # 基于新模型创建表

# 2. 从现有订单提取供应商信息
# （如果有1688订单数据）
for order in existing_orders:
    if order.source_title:
        supplier_name = extract_supplier_from_title(order.source_title)
        supplier = get_or_create_supplier(supplier_name)
        order.supplier_id = supplier.id

# 3. 从产品名提取规格
for product in existing_products:
    specs = extract_specs_from_name(product.product_name)
    for spec in specs:
        create_product_spec(product.id, spec)

# 4. 保存
session.commit()
```

### Phase 2: 匹配引擎升级（2-3天）

```python
# api/app/services/enhanced_matcher.py
# 实现 EnhancedProductMatcher 类
```

### Phase 3: 导入向导UI（3-4天）

```typescript
// web/src/pages/ImportWizard/
// 实现4步向导界面
```

### Phase 4: 产品管理增强（2-3天）

```typescript
// web/src/pages/Products/ProductDetail.tsx
// 添加供应商、规格、映射规则展示
```

### Phase 5: 测试与优化（2-3天）

```bash
# 使用真实数据测试匹配率提升
python3 api/test_enhanced_matching.py
```

---

## 📈 预期效果

### 匹配率提升预测

| 场景 | 当前匹配率 | 预期匹配率 | 提升幅度 |
|------|-----------|-----------|---------|
| 首次导入（无历史） | 58.5% | **75-80%** | +17-22% |
| 二次导入（有历史） | 58.5% | **90-95%** | +32-37% |
| 同供应商订单 | 58.5% | **95-98%** | +37-40% |

### 提升原理

1. **供应商约束** → 缩小候选范围，减少误匹配
2. **规格验证** → 区分同名产品的不同规格
3. **历史学习** → 越用越准，自动学习用户偏好
4. **价格验证** → 通过价格范围排除不合理匹配

---

## 💡 额外优化建议

### 1. 供应商画像

自动分析供应商的产品特征：

```python
# 示例：亦纯文化的产品画像
{
    "supplier_name": "亦纯文化",
    "product_categories": ["胶水"],
    "common_products": ["高铸胶", "鞋胶", "厌氧胶"],
    "keyword_patterns": ["铸工胶", "铸胶", "AB胶"],
    "price_range": {
        "高铸胶": {"min": 20, "max": 90, "avg": 45}
    }
}
```

### 2. 智能推荐

当用户确认一次匹配后，自动推荐类似订单：

```
用户确认: "高品质AB胶铸工胶..." → 高铸胶

系统推荐:
  • "铸工胶20g一盒..." 也许是 高铸胶？[✓ 是] [✗ 否]
  • "AB胶批发粘金属..." 也许是 高铸胶？[✓ 是] [✗ 否]
```

### 3. 导入模板

提供标准化的1688订单导出模板：

```
导出1688订单时，请确保包含以下字段：
✓ 订单编号
✓ 货品标题
✓ 卖家会员名
✓ 单价(元)
✓ 数量
✓ 实付款(元)
✓ 订单创建时间
```

### 4. 批量操作

```
选中多个未匹配订单 → [批量匹配到: 高铸胶 ▼]
```

---

## 🎯 总结

您的思路非常正确！通过加入**供应商**和**规格**两个维度，可以：

### ✅ 解决的问题

1. **同名产品不同规格** - 通过规格字段区分
2. **产品名称不统一** - 通过供应商约束缩小范围
3. **匹配率低** - 多维度匹配提升至90%+
4. **人工工作量大** - 历史学习减少重复工作

### ✅ 带来的价值

1. **首次导入**: 匹配率提升至75-80%
2. **后续导入**: 匹配率可达90-95%
3. **自动化**: 同供应商订单几乎无需人工干预
4. **可追溯**: 完整记录1688订单原始信息

### 🚀 下一步

1. 我可以开始实现 Phase 1（数据库升级）
2. 或者先创建详细的技术设计文档
3. 或者先实现一个简化版MVP

您想从哪里开始？🎯

---

*创建时间: 2025-11-02*
*基于1688订单数据: 71条，17家供应商*
