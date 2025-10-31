# 采购管理系统

一个完整的采购订单管理系统，用于管理和分析采购数据。

## 📋 功能特性

### 核心功能

- ✅ **订单管理** - 完整的 CRUD 操作
  - 订单创建、编辑、删除
  - 多维度筛选和搜索
  - 批量导入导出

- ✅ **数据分析** - 强大的统计分析功能
  - 实时 Dashboard 统计
  - 产品采购分析
  - 店铺对比分析
  - 支付状态追踪

- ✅ **可视化图表** - 直观的数据展示
  - 柱状图、饼图、折线图
  - 产品排行榜
  - 趋势分析

- ✅ **数据导入导出**
  - Excel 批量导入
  - 自定义筛选导出
  - 数据备份和迁移

### 数据统计

- **订单总数**: 1107+
- **采购总额**: ¥848,058.97+
- **产品种类**: 173+
- **店铺数量**: 2 (CAISHENDAO, Kitchen maestro)

## 🏗️ 技术架构

### 后端技术栈

- **框架**: FastAPI 0.109
- **数据库**: SQLite / SQLAlchemy
- **数据处理**: Pandas
- **Excel 处理**: OpenPyXL, XlsxWriter
- **API 文档**: Swagger / ReDoc

### 前端技术栈

- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **路由**: React Router 6
- **图表**: Recharts
- **构建工具**: Vite 5
- **日期处理**: Day.js
- **HTTP 客户端**: Axios

## 📦 安装和运行

### 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 快速开始

#### 1. 克隆项目

```bash
git clone <repository-url>
cd Procurement-Management-System
```

#### 2. 后端设置

```bash
# 安装Python依赖
pip3 install -r backend/requirements.txt

# 导入初始数据（可选）
python3 backend/utils/import_data.py

# 启动后端服务器
./start_backend.sh
# 或者
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

后端将运行在: http://localhost:8000
API 文档: http://localhost:8000/api/docs

#### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在: http://localhost:3000

## 📚 API 文档

### 订单管理 API

```
GET    /api/orders/                  # 获取订单列表
POST   /api/orders/                  # 创建订单
GET    /api/orders/{id}              # 获取订单详情
PUT    /api/orders/{id}              # 更新订单
DELETE /api/orders/{id}              # 删除订单
```

### 统计分析 API

```
GET /api/orders/statistics/summary    # 获取统计摘要
GET /api/orders/statistics/products   # 获取产品统计
GET /api/orders/payment/pending       # 获取待支付订单
```

### 导入导出 API

```
POST /api/import-export/import        # 导入Excel
GET  /api/import-export/export        # 导出Excel
```

完整的 API 文档请访问: http://localhost:8000/api/docs

## 📊 数据库模型

### 订单表 (purchase_orders)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| order_no | String | 订单编号（唯一） |
| product_name | String | 产品名称 |
| purchase_amount | Float | 采购金额 |
| order_date | DateTime | 订单日期 |
| order_time | DateTime | 订单时间 |
| initial_status | String | 初始状态 |
| payment_status | String | 支付状态 |
| shop_name | String | 店铺名称 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 🎯 使用指南

### 1. 数据导入

1. 进入 "数据导入导出" 页面
2. 点击上传区域或拖拽 Excel 文件
3. 系统自动解析并导入数据
4. 查看导入结果统计

### 2. 订单管理

1. 进入 "订单管理" 页面
2. 使用筛选器查找订单
3. 点击 "新建订单" 创建订单
4. 点击 "编辑" 修改订单
5. 点击 "删除" 删除订单

### 3. 数据分析

1. 进入 "数据概览" 查看总体统计
2. 进入 "产品分析" 查看产品详细数据
3. 使用日期范围和店铺筛选
4. 导出分析报表

### 4. 数据导出

1. 进入 "数据导入导出" 页面
2. 选择筛选条件
3. 点击 "导出 Excel 数据"
4. 下载 Excel 文件

## 🔧 配置说明

### 后端配置

数据库配置在 `backend/database.py`:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./procurement.db"
```

### 前端配置

API 代理配置在 `frontend/vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 🚀 部署

### 后端部署

```bash
# 生产环境运行
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

```bash
# 构建生产版本
cd frontend
npm run build

# 构建产物在 frontend/dist 目录
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

### v1.0.0 (2024-10-31)

- ✅ 完整的采购订单管理系统
- ✅ 数据分析和可视化
- ✅ Excel 导入导出
- ✅ 响应式 Web 界面
- ✅ RESTful API
- ✅ 完整的文档

## 📄 许可证

MIT License

## 👥 联系方式

如有问题或建议，请提交 Issue。

---

**采购管理系统** - 让采购数据管理更简单、更高效！
