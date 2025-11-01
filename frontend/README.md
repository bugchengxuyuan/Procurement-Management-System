# 采购管理系统 - 前端

这是采购管理系统的前端应用,基于React + TypeScript + Vite + Ant Design构建。

## 技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design 5** - UI组件库
- **Ant Design Charts** - 数据可视化
- **React Router DOM** - 路由管理
- **Axios** - HTTP客户端
- **Day.js** - 日期处理

## 快速开始

### 1. 安装依赖

```bash
npm install
```

或使用yarn:

```bash
yarn install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动。

### 3. 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # 公共组件
│   │   └── Layout/        # 布局组件
│   ├── pages/             # 页面组件
│   │   ├── Dashboard/     # 数据概览
│   │   ├── OrderList/     # 订单管理
│   │   ├── ProductList/   # 产品管理
│   │   └── PaymentDue/    # 先采后付
│   ├── services/          # API服务
│   │   ├── api.ts         # Axios配置
│   │   ├── order.ts       # 订单API
│   │   ├── product.ts     # 产品API
│   │   ├── statistics.ts  # 统计API
│   │   └── import-export.ts # 导入导出API
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 应用入口
│   └── index.css          # 全局样式
├── index.html             # HTML模板
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript配置
├── vite.config.ts         # Vite配置
└── README.md             # 项目说明
```

## 功能模块

### 1. 数据概览 (Dashboard)

- 核心指标卡片
  - 采购总额
  - 订单总数
  - 产品种类
  - 本月采购额及环比
- 支付方式分布图
- TOP 5产品排行
- 月度采购趋势图

### 2. 订单管理 (Order Management)

**订单列表**:
- 分页展示
- 多维度筛选（产品、状态、日期范围）
- 快速搜索
- 排序功能

**订单操作**:
- 新建订单
- 编辑订单
- 删除订单
- Excel批量导入
- Excel批量导出

### 3. 产品管理 (Product Management)

**产品列表**:
- 产品排行榜
- 采购金额占比可视化
- 产品搜索

**产品详情**:
- 基本统计信息
- 月度采购趋势图
- 订单历史记录

### 4. 先采后付管理 (Payment Due)

**功能特性**:
- 到期订单提醒
- 状态分类（已逾期、即将到期、正常）
- 剩余天数显示
- 一键标记付款
- 统计数据展示

## API接口

所有API请求通过`/api`代理到后端服务（`http://localhost:8000`）。

### 主要接口

- `GET /api/orders` - 获取订单列表
- `POST /api/orders` - 创建订单
- `PUT /api/orders/:id` - 更新订单
- `DELETE /api/orders/:id` - 删除订单
- `GET /api/products` - 获取产品列表
- `GET /api/statistics/dashboard` - 获取Dashboard统计
- `GET /api/statistics/payment-due` - 获取先采后付订单
- `POST /api/import/excel` - 导入Excel
- `GET /api/export/excel` - 导出Excel

## 开发指南

### 添加新页面

1. 在`src/pages`下创建新的页面组件
2. 在`App.tsx`中添加路由
3. 在`Layout`组件中添加菜单项

### 添加新的API服务

1. 在`src/services`下创建新的服务文件
2. 定义TypeScript接口
3. 实现API调用函数

### 使用Ant Design组件

```tsx
import { Button, Table, Form } from 'antd';

// 使用组件
<Button type="primary">主按钮</Button>
```

### 使用图表

```tsx
import { Column, Line, Pie } from '@ant-design/charts';

// 配置图表
const config = {
  data: chartData,
  xField: 'x',
  yField: 'y',
};

<Column {...config} />
```

## 环境变量

创建`.env.local`文件配置环境变量:

```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000
```

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 开发提示

### 热重载

Vite提供了快速的热模块替换(HMR),修改代码后浏览器会自动刷新。

### TypeScript类型检查

```bash
npm run lint
```

### 生产优化

- 代码分割
- Tree Shaking
- 资源压缩
- 懒加载

## 常见问题

### Q1: 如何修改API地址?

在`vite.config.ts`中修改proxy配置:

```ts
server: {
  proxy: {
    '/api': {
      target: 'http://your-api-server:8000',
      changeOrigin: true,
    },
  },
}
```

### Q2: 如何添加全局样式?

在`src/index.css`中添加全局样式。

### Q3: 如何处理API错误?

在`src/services/api.ts`的响应拦截器中统一处理。

## 更新日志

### v1.0.0 (2025-11-01)

**功能**:
- ✅ 数据概览Dashboard
- ✅ 订单管理（CRUD + 导入导出）
- ✅ 产品管理（列表 + 详情）
- ✅ 先采后付订单管理
- ✅ 数据可视化图表
- ✅ 响应式布局

**技术**:
- React 18 + TypeScript
- Ant Design 5
- Vite 5
- Axios

---

**最后更新**: 2025-11-01
