# 采购管理系统 v2.0

现代化的采购管理系统，用于TikTok Shop东南亚市场的采购数据管理。

## 技术栈

### 后端
- **FastAPI** 0.109+ - 高性能异步Web框架
- **SQLModel** - 类型安全的ORM
- **Pydantic** V2 - 数据验证
- **SQLite/PostgreSQL** - 数据库
- **Pandas & openpyxl** - Excel处理

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite 5** - 构建工具
- **Ant Design 5** - UI组件库
- **TanStack Query** - 服务端状态管理
- **Zustand** - 客户端状态管理
- **ECharts** - 数据可视化
- **React Hook Form + Zod** - 表单处理

## 快速开始

### 方式一：Docker部署（推荐）

```bash
# 启动服务
docker-compose up -d

# 访问应用
http://localhost
```

### 方式二：本地开发

#### 1. 后端启动

```bash
cd api

# 安装依赖
pip install -r requirements.txt

# 数据迁移（可选）
python migrate_data.py

# 启动服务
python run.py
```

后端运行在: http://localhost:8000  
API文档: http://localhost:8000/docs

#### 2. 前端启动

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在: http://localhost:3000

## 主要功能

### 1. 数据总览
- 采购总额、订单数、产品数统计
- 本月采购额及环比增长
- 支付方式分布
- TOP 5 热门产品
- 月度采购趋势图表

### 2. 订单管理
- 订单列表查看（分页）
- 新增/编辑/删除订单
- 多维度筛选（产品、状态、支付方式、日期范围）
- 订单搜索
- Excel导入导出

### 3. 产品分析
- 产品排行榜
- 采购总额、订单数量统计
- 产品占比可视化
- 产品详情查看
- 月度采购趋势
- 订单历史记录

### 4. 账期跟踪
- 先采后付订单管理
- 到期日期计算
- 状态分类（已逾期/即将到期/正常）
- 剩余天数提醒
- 统计卡片展示

## 数据迁移

从旧系统迁移数据:

```bash
cd api
python migrate_data.py
```

## API文档

启动后端后访问: http://localhost:8000/docs

## License

MIT
