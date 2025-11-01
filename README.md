# 采购管理系统 (Procurement Management System)

**版本**: v1.0
**项目说明**: 1688采购管理系统 - 专为TikTok Shop东南亚市场采购管理设计

---

## 项目概述

这是一个基于FastAPI + SQLAlchemy构建的采购管理系统，旨在替代传统的Excel表格管理方式，提供更高效、可靠的采购数据管理解决方案。

### 核心功能

✅ **订单管理**
- 订单CRUD操作
- 多维度筛选和搜索
- 订单详情查看
- 分页列表展示

✅ **产品管理**
- 产品统计数据自动计算
- 产品采购历史追踪
- 月度采购趋势分析
- TOP产品排行

✅ **统计分析**
- Dashboard综合统计
- 月度采购趋势图表
- 支付方式分布分析
- 日期范围统计

✅ **先采后付管理**
- 自动计算到期日期
- 到期订单提醒
- 逾期订单标记
- 账期管理

✅ **数据导入导出**
- Excel批量导入
- 数据验证和去重
- Excel数据导出
- 自定义导出字段

---

## 技术栈

### 后端
- **Python 3.11+**
- **FastAPI 0.104+** - 高性能Web框架
- **SQLAlchemy 2.0+** - ORM
- **Pydantic 2.0+** - 数据验证
- **Pandas** - Excel数据处理
- **SQLite/PostgreSQL** - 数据库

### 前端
- **React 18** - UI框架
- **TypeScript 5** - 类型安全
- **Vite 5** - 构建工具
- **Ant Design 5** - UI组件库
- **Ant Design Charts** - 数据可视化
- **Axios** - HTTP客户端

### 数据库设计
- `purchase_orders` - 采购订单表
- `products` - 产品主数据表
- `users` - 用户表（预留）

---

## 快速开始

### 后端启动

#### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制`.env.example`为`.env`并修改配置：

```bash
cp .env.example .env
```

主要配置项：
```ini
# 数据库URL（开发环境使用SQLite）
DATABASE_URL=sqlite:///./procurement.db

# 生产环境使用PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/procurement_system

# 安全密钥（生产环境必须修改）
SECRET_KEY=your-secret-key-change-in-production
```

#### 3. 导入Excel数据

将现有的Excel采购数据导入数据库：

```bash
python migrate_excel.py
```

**注意**: 修改`migrate_excel.py`中的Excel文件路径为你的实际文件路径。

#### 4. 启动后端服务器

```bash
python main.py
```

后端服务器将在 `http://localhost:8000` 启动。

#### 5. 访问API文档

FastAPI自动生成的交互式API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### 前端启动

#### 1. 安装依赖

```bash
cd frontend
npm install
```

或使用yarn:
```bash
yarn install
```

#### 2. 启动开发服务器

```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动。

#### 3. 访问应用

打开浏览器访问: http://localhost:3000

**默认页面**:
- 数据概览: http://localhost:3000/dashboard
- 订单管理: http://localhost:3000/orders
- 产品管理: http://localhost:3000/products
- 先采后付: http://localhost:3000/payment-due

---

## API文档

### 订单管理 API

#### 1. 创建订单
```http
POST /api/orders
Content-Type: application/json

{
    "order_no": "3655240347686198464",
    "product_name": "高铸胶",
    "purchase_amount": 2880.00,
    "order_date": "2025-10-28",
    "order_status": "已付款",
    "payment_method": "已付款"
}
```

#### 2. 获取订单列表
```http
GET /api/orders?page=1&size=20&product_name=高铸胶&start_date=2025-01-01
```

**查询参数**:
- `page`: 页码（默认1）
- `size`: 每页数量（默认20）
- `product_name`: 产品名称筛选
- `order_status`: 订单状态筛选
- `payment_method`: 支付方式筛选
- `start_date`: 开始日期
- `end_date`: 结束日期
- `search`: 搜索关键词
- `sort_by`: 排序字段
- `sort_order`: 排序顺序（asc/desc）

#### 3. 获取订单详情
```http
GET /api/orders/{order_id}
```

#### 4. 更新订单
```http
PUT /api/orders/{order_id}
Content-Type: application/json

{
    "purchase_amount": 2900.00,
    "order_status": "已付款"
}
```

#### 5. 删除订单
```http
DELETE /api/orders/{order_id}
```

---

### 产品管理 API

#### 1. 获取产品列表
```http
GET /api/products?sort_by=total_purchase_amount&sort_order=desc
```

**响应示例**:
```json
{
    "total": 101,
    "total_amount": 748511.46,
    "items": [
        {
            "id": 97,
            "product_name": "高铸胶",
            "total_purchase_amount": 279652.11,
            "total_order_count": 116,
            "avg_unit_price": 2410.79,
            "last_purchase_date": "2025-10-26",
            "percentage": 37.36
        }
    ]
}
```

#### 2. 获取产品详情
```http
GET /api/products/{product_id}
```

**响应包含**:
- 产品基本信息
- 最近20单订单历史
- 最近6个月采购趋势

---

### 统计分析 API

#### 1. Dashboard统计
```http
GET /api/statistics/dashboard
```

**响应示例**:
```json
{
    "total_amount": 748511.46,
    "total_orders": 792,
    "total_products": 101,
    "this_month_amount": 44475.71,
    "this_month_growth": 144.24,
    "payment_distribution": {
        "先采后付": {"count": 40, "amount": 31923.44},
        "已付款": {"count": 752, "amount": 716588.02}
    },
    "monthly_trend": [...],
    "top_products": [...]
}
```

#### 2. 先采后付到期订单
```http
GET /api/statistics/payment-due?days_threshold=7
```

**响应示例**:
```json
[
    {
        "order_id": 537,
        "order_no": "4320321231999870000",
        "product_name": "100g黄色胶水",
        "purchase_amount": 960.0,
        "order_date": "2025-04-30",
        "due_date": "2025-05-30",
        "days_remaining": -154,
        "status": "overdue"
    }
]
```

**状态说明**:
- `overdue`: 已逾期
- `warning`: 7天内到期
- `normal`: 正常

#### 3. 日期范围统计
```http
GET /api/statistics/date-range?start_date=2025-01-01&end_date=2025-10-31
```

---

### 导入导出 API

#### 1. Excel导入
```http
POST /api/import/excel
Content-Type: multipart/form-data

file: <Excel文件>
```

**Excel格式要求**:
- 工作表名称: `CAISHENDAO`
- 列名（第7行开始）: 日期, 初始状态, 订单编号, 产品名称, 采购金额, 时间, 先采后付

**响应示例**:
```json
{
    "total_rows": 500,
    "success_count": 498,
    "error_count": 2,
    "errors": [
        {"row": 3, "error": "订单编号缺失"},
        {"row": 156, "error": "金额格式错误"}
    ]
}
```

#### 2. Excel导出
```http
GET /api/export/excel?start_date=2025-01-01&end_date=2025-10-31
```

支持筛选参数：
- `product_name`: 产品名称
- `order_status`: 订单状态
- `payment_method`: 支付方式
- `start_date`: 开始日期
- `end_date`: 结束日期

---

## 数据库结构

### 1. purchase_orders (采购订单表)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(50) | 订单编号（唯一） |
| product_name | VARCHAR(200) | 产品名称 |
| purchase_amount | DECIMAL(10,2) | 采购金额 |
| order_date | DATE | 订单日期 |
| order_status | VARCHAR(20) | 订单状态 |
| payment_method | VARCHAR(20) | 支付方式 |
| record_time | DATETIME | 记录时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| created_by | INTEGER | 创建人ID |

**索引**:
- `order_no` (UNIQUE)
- `order_date`
- `product_name`
- `order_status`
- `payment_method`

### 2. products (产品主数据表)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| product_name | VARCHAR(200) | 产品名称（唯一） |
| total_purchase_amount | DECIMAL(12,2) | 累计采购金额 |
| total_order_count | INTEGER | 累计订单数 |
| avg_unit_price | DECIMAL(10,2) | 平均单价 |
| last_purchase_date | DATE | 最近采购日期 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**自动更新**: 产品统计数据在订单创建/更新/删除时自动更新。

### 3. users (用户表)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| real_name | VARCHAR(100) | 真实姓名 |
| role | VARCHAR(20) | 角色 |
| is_active | BOOLEAN | 是否激活 |
| created_at | DATETIME | 创建时间 |
| last_login_at | DATETIME | 最后登录时间 |

---

## 项目结构

```
Procurement-Management-System/
├── backend/
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接
│   ├── migrate_excel.py        # Excel数据迁移脚本
│   ├── requirements.txt        # Python依赖
│   ├── .env.example            # 环境变量示例
│   ├── .gitignore              # Git忽略文件
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── order.py           # 订单模型
│   │   ├── product.py         # 产品模型
│   │   └── user.py            # 用户模型
│   │
│   ├── schemas/                # Pydantic模型
│   │   ├── __init__.py
│   │   ├── order.py
│   │   ├── product.py
│   │   └── statistics.py
│   │
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── orders.py          # 订单API
│   │   ├── products.py        # 产品API
│   │   ├── statistics.py      # 统计API
│   │   └── import_export.py   # 导入导出API
│   │
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── order_service.py
│   │   ├── product_service.py
│   │   └── statistics_service.py
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── excel.py           # Excel处理
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── components/         # 公共组件
│   │   │   └── Layout/        # 布局组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── Dashboard/     # 数据概览
│   │   │   ├── OrderList/     # 订单管理
│   │   │   ├── ProductList/   # 产品管理
│   │   │   └── PaymentDue/    # 先采后付
│   │   ├── services/          # API服务
│   │   │   ├── api.ts         # Axios配置
│   │   │   ├── order.ts       # 订单API
│   │   │   ├── product.ts     # 产品API
│   │   │   ├── statistics.ts  # 统计API
│   │   │   └── import-export.ts # 导入导出
│   │   ├── App.tsx            # 主应用
│   │   ├── main.tsx           # 入口文件
│   │   └── index.css          # 全局样式
│   ├── package.json           # NPM依赖
│   ├── vite.config.ts         # Vite配置
│   ├── tsconfig.json          # TypeScript配置
│   └── README.md              # 前端文档
│
├── docs/                       # 文档
├── tests/                      # 测试
└── README.md                   # 项目说明
```

---

## 业务逻辑说明

### 1. 订单创建流程

```
用户创建订单
    ↓
验证订单编号唯一性
    ↓
保存订单到数据库
    ↓
自动更新产品统计数据
    ↓
返回创建成功响应
```

### 2. 产品统计自动更新

当订单创建、更新或删除时，系统会自动更新相关产品的统计数据：
- `total_purchase_amount`: 累计采购金额
- `total_order_count`: 累计订单数
- `avg_unit_price`: 平均单价
- `last_purchase_date`: 最近采购日期

### 3. 先采后付订单管理

- **默认账期**: 30天（可在配置中修改）
- **到期日计算**: 订单日期 + 30天
- **状态判断**:
  - 逾期：到期日 < 今天
  - 预警：7天内到期
  - 正常：超过7天

---

## 使用示例

### 示例1: 创建订单

```bash
curl -X POST "http://localhost:8000/api/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "order_no": "3655240347686198464",
    "product_name": "高铸胶",
    "purchase_amount": 2880.00,
    "order_date": "2025-10-28",
    "order_status": "已付款",
    "payment_method": "已付款"
  }'
```

### 示例2: 查询产品统计

```bash
curl "http://localhost:8000/api/products?sort_by=total_purchase_amount&sort_order=desc"
```

### 示例3: 获取Dashboard数据

```bash
curl "http://localhost:8000/api/statistics/dashboard"
```

### 示例4: 查询即将到期的订单

```bash
curl "http://localhost:8000/api/statistics/payment-due?days_threshold=7"
```

---

## 开发指南

### 添加新的API端点

1. 在`services/`中创建业务逻辑函数
2. 在`api/`中创建路由
3. 在`main.py`中注册路由

### 数据库迁移

如果需要修改数据库结构，建议使用Alembic进行版本管理：

```bash
# 初始化Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Add new column"

# 执行迁移
alembic upgrade head
```

### 运行测试

```bash
pytest tests/
```

---

## 部署指南

### 开发环境

```bash
python main.py
```

### 生产环境

使用Gunicorn + Uvicorn workers：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 性能优化

### 1. 数据库索引

已为以下字段创建索引以提升查询性能：
- `order_no` (唯一索引)
- `order_date`
- `product_name`
- `order_status`
- `payment_method`

### 2. 分页查询

所有列表接口都支持分页，默认每页20条记录。

### 3. 数据库连接池

SQLAlchemy自动管理连接池，生产环境建议配置：

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 常见问题 (FAQ)

### Q1: 如何修改先采后付的默认账期？

在`.env`文件中修改：
```ini
DEFAULT_PAYMENT_TERM_DAYS=30
```

### Q2: 如何备份数据库？

**SQLite**:
```bash
cp procurement.db procurement_backup.db
```

**PostgreSQL**:
```bash
pg_dump procurement_system > backup.sql
```

### Q3: 订单编号重复怎么办？

系统会自动检测重复的订单编号并返回错误。如果需要更新已有订单，请使用PUT接口。

### Q4: 如何批量导入大量数据？

使用`migrate_excel.py`脚本，系统会自动处理重复数据和错误数据。

---

## 更新日志

### v1.0.0 (2025-10-31)

**功能实现**:
- ✅ 订单管理完整CRUD
- ✅ 产品管理和统计
- ✅ Dashboard统计分析
- ✅ 先采后付订单管理
- ✅ Excel导入导出
- ✅ 数据迁移脚本

**已完成数据迁移**:
- 792个订单
- 101个产品
- 总采购金额: ¥748,511.46

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 许可证

MIT License

---

## 联系方式

项目负责人: Claude
项目地址: [GitHub Repository](https://github.com/bugchengxuyuan/Procurement-Management-System)

---

## 致谢

- FastAPI - 现代化的Python Web框架
- SQLAlchemy - 强大的Python ORM
- Pandas - 数据处理利器
- Pydantic - 数据验证工具

---

**Last Updated**: 2025-10-31
