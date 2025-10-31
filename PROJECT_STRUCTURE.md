# 项目结构说明

## 📁 目录结构

```
Procurement-Management-System/
│
├── backend/                          # 后端目录
│   ├── __init__.py
│   ├── main.py                       # FastAPI应用入口
│   ├── database.py                   # 数据库配置
│   ├── requirements.txt              # Python依赖
│   ├── procurement.db                # SQLite数据库文件（运行时生成）
│   │
│   ├── models/                       # 数据模型
│   │   ├── __init__.py
│   │   ├── purchase_order.py         # 订单模型（SQLAlchemy）
│   │   └── schemas.py                # Pydantic模式（API验证）
│   │
│   ├── api/                          # API路由
│   │   ├── __init__.py
│   │   ├── orders.py                 # 订单相关API
│   │   └── import_export.py          # 导入导出API
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py
│   │   └── order_service.py          # 订单服务
│   │
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       └── import_data.py            # Excel数据导入工具
│
├── frontend/                         # 前端目录
│   ├── package.json                  # Node依赖配置
│   ├── tsconfig.json                 # TypeScript配置
│   ├── vite.config.ts                # Vite构建配置
│   ├── index.html                    # HTML入口
│   │
│   └── src/                          # 源代码
│       ├── main.tsx                  # React应用入口
│       ├── App.tsx                   # 主应用组件
│       ├── App.css                   # 应用样式
│       ├── index.css                 # 全局样式
│       │
│       ├── types/                    # TypeScript类型定义
│       │   └── index.ts
│       │
│       ├── services/                 # API服务
│       │   └── api.ts                # API客户端
│       │
│       ├── pages/                    # 页面组件
│       │   ├── Dashboard.tsx         # 数据概览页
│       │   ├── OrderList.tsx         # 订单列表页
│       │   ├── ProductAnalysis.tsx   # 产品分析页
│       │   └── ImportExport.tsx      # 导入导出页
│       │
│       └── components/               # 通用组件（暂未使用）
│
├── 采购表-2（最新版.xlsx              # 原始Excel数据
│
├── .gitignore                        # Git忽略配置
├── README.md                         # 项目说明文档
├── USAGE.md                          # 使用指南
├── PROJECT_STRUCTURE.md              # 项目结构说明（本文件）
│
├── start_backend.sh                  # 后端启动脚本
└── start_frontend.sh                 # 前端启动脚本
```

## 🔧 核心文件说明

### 后端核心文件

#### `backend/main.py`
- FastAPI应用主入口
- 配置CORS中间件
- 注册API路由
- 全局异常处理

#### `backend/database.py`
- SQLAlchemy数据库配置
- 数据库会话管理
- 数据库初始化

#### `backend/models/purchase_order.py`
- 订单数据模型（ORM）
- 数据库表结构定义
- 索引配置

#### `backend/models/schemas.py`
- Pydantic数据模式
- API请求/响应验证
- 数据序列化

#### `backend/services/order_service.py`
- 订单业务逻辑
- CRUD操作
- 统计分析功能

#### `backend/api/orders.py`
- 订单管理API端点
- GET/POST/PUT/DELETE路由
- 统计API

#### `backend/api/import_export.py`
- Excel导入导出API
- 文件上传处理
- 数据转换

### 前端核心文件

#### `frontend/src/main.tsx`
- React应用入口
- 全局配置（Ant Design中文化）

#### `frontend/src/App.tsx`
- 主应用组件
- 路由配置
- 布局结构

#### `frontend/src/services/api.ts`
- Axios HTTP客户端
- API封装
- 请求/响应拦截器

#### `frontend/src/pages/Dashboard.tsx`
- 数据概览页面
- 统计卡片
- 图表展示

#### `frontend/src/pages/OrderList.tsx`
- 订单列表页面
- 表格展示
- CRUD操作

#### `frontend/src/pages/ProductAnalysis.tsx`
- 产品分析页面
- 产品统计
- 排行榜

#### `frontend/src/pages/ImportExport.tsx`
- 数据导入导出页面
- 文件上传
- 数据下载

## 🏗️ 架构设计

### 后端架构（三层架构）

```
API层 (api/)
    ↓
服务层 (services/)
    ↓
数据层 (models/)
    ↓
数据库 (SQLite)
```

**API层**:
- 处理HTTP请求
- 参数验证
- 路由定义

**服务层**:
- 业务逻辑处理
- 数据查询和操作
- 统计计算

**数据层**:
- ORM模型定义
- 数据库操作
- 数据验证

### 前端架构（组件化）

```
App (路由容器)
  ├── Dashboard (数据概览)
  ├── OrderList (订单管理)
  ├── ProductAnalysis (产品分析)
  └── ImportExport (导入导出)
```

**数据流**:
```
UI组件 → API服务 → 后端API → 数据库
       ← 响应数据 ←          ←
```

## 📊 数据库设计

### purchase_orders 表

| 列名 | 类型 | 说明 | 索引 |
|------|------|------|------|
| id | Integer | 主键 | ✓ |
| order_no | String(50) | 订单编号 | ✓ 唯一 |
| product_name | String(200) | 产品名称 | ✓ |
| purchase_amount | Float | 采购金额 | |
| order_date | DateTime | 订单日期 | ✓ |
| order_time | DateTime | 订单时间 | |
| initial_status | String(50) | 初始状态 | |
| payment_status | String(50) | 支付状态 | ✓ |
| shop_name | String(100) | 店铺名称 | ✓ |
| created_at | DateTime | 创建时间 | |
| updated_at | DateTime | 更新时间 | |

**复合索引**:
- (order_date, shop_name)
- (product_name, shop_name)
- (payment_status, shop_name)

## 🔌 API设计

### RESTful API端点

```
订单管理:
GET    /api/orders/              # 获取订单列表（分页、筛选）
POST   /api/orders/              # 创建订单
GET    /api/orders/{id}          # 获取订单详情
PUT    /api/orders/{id}          # 更新订单
DELETE /api/orders/{id}          # 删除订单

统计分析:
GET /api/orders/statistics/summary    # 汇总统计
GET /api/orders/statistics/products   # 产品统计
GET /api/orders/payment/pending       # 待支付订单

导入导出:
POST /api/import-export/import        # 导入Excel
GET  /api/import-export/export        # 导出Excel
```

## 🎨 UI组件库

### Ant Design组件使用

- **Layout**: 页面布局
- **Menu**: 侧边栏导航
- **Table**: 数据表格
- **Form**: 表单输入
- **Card**: 卡片容器
- **Statistic**: 统计数值
- **DatePicker**: 日期选择
- **Select**: 下拉选择
- **Upload**: 文件上传
- **Modal**: 对话框
- **Button**: 按钮

### Recharts图表

- **BarChart**: 柱状图（店铺对比、产品排行）
- **PieChart**: 饼图（支付状态分布）

## 🔒 数据流转

### 创建订单流程

```
前端表单 → 验证 → POST请求
                      ↓
            API层接收请求
                      ↓
              Pydantic验证
                      ↓
           服务层业务逻辑
                      ↓
            SQLAlchemy保存
                      ↓
              返回订单对象
                      ↓
            前端更新列表
```

### 数据导入流程

```
用户上传Excel → FormData
                    ↓
         后端接收文件
                    ↓
        Pandas读取Excel
                    ↓
         数据清洗和验证
                    ↓
        批量插入数据库
                    ↓
         返回导入统计
```

## 🚀 性能优化

### 后端优化
- 数据库索引优化
- 批量操作（100条/次提交）
- 分页查询
- API响应缓存

### 前端优化
- 组件懒加载
- 图表数据限制
- 表格虚拟滚动
- API请求去重

## 🔐 安全考虑

### 当前实现
- 数据验证（Pydantic）
- SQL注入防护（SQLAlchemy）
- 文件类型验证
- 文件大小限制

### 生产环境建议
- 添加用户认证
- API速率限制
- HTTPS支持
- 数据库备份
- 日志审计

---

本文档最后更新：2024-10-31
