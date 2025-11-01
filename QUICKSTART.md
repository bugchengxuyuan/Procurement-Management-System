# 采购管理系统 - 快速启动指南

本指南将帮助你快速启动采购管理系统的前端和后端服务。

## 前置要求

- Python 3.11+
- Node.js 16+ 和 npm
- Git

## 一键启动脚本

### Linux/Mac

创建 `start.sh` 文件：

```bash
#!/bin/bash

echo "========================================="
echo "  启动采购管理系统"
echo "========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.11+"
    exit 1
fi

# 检查Node.js
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm 未安装，请先安装 Node.js 16+"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 启动后端
echo "📦 启动后端服务..."
cd backend
if [ ! -f "procurement.db" ]; then
    echo "⚠️  数据库不存在，请先运行数据迁移脚本"
    echo "   python migrate_excel.py"
    exit 1
fi

python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "   访问: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd frontend

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装前端依赖..."
    npm install
fi

npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "   访问: http://localhost:3000"
cd ..

echo ""
echo "========================================="
echo "  🎉 系统启动成功！"
echo "========================================="
echo ""
echo "📌 访问地址:"
echo "   前端应用: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "📝 查看日志:"
echo "   后端日志: tail -f /tmp/backend.log"
echo "   前端日志: tail -f /tmp/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
```

使用方法：

```bash
chmod +x start.sh
./start.sh
```

### Windows

创建 `start.bat` 文件：

```batch
@echo off
echo =========================================
echo   启动采购管理系统
echo =========================================
echo.

REM 启动后端
echo 📦 启动后端服务...
cd backend
if not exist "procurement.db" (
    echo ❌ 数据库不存在，请先运行数据迁移脚本
    echo    python migrate_excel.py
    exit /b 1
)
start /B python main.py
echo ✅ 后端服务已启动
echo    访问: http://localhost:8000
echo    API文档: http://localhost:8000/docs
cd ..

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo.
echo 🎨 启动前端服务...
cd frontend
if not exist "node_modules" (
    echo 📦 正在安装前端依赖...
    call npm install
)
start /B npm run dev
echo ✅ 前端服务已启动
echo    访问: http://localhost:3000
cd ..

echo.
echo =========================================
echo   🎉 系统启动成功！
echo =========================================
echo.
echo 📌 访问地址:
echo    前端应用: http://localhost:3000
echo    后端API: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
pause
```

## 手动启动

### 1. 启动后端

```bash
# 进入后端目录
cd backend

# 首次运行需要安装依赖
pip install -r requirements.txt

# 如果数据库不存在，运行迁移脚本
python migrate_excel.py

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

### 2. 启动前端

打开新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 首次运行需要安装依赖
npm install

# 启动前端开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动。

## 访问系统

### 前端应用
打开浏览器访问: **http://localhost:3000**

主要页面：
- 数据概览: http://localhost:3000/dashboard
- 订单管理: http://localhost:3000/orders
- 产品管理: http://localhost:3000/products
- 先采后付: http://localhost:3000/payment-due

### 后端API
- API根地址: http://localhost:8000
- Swagger UI文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 停止服务

### 方法1: 使用进程管理器

```bash
# 查找进程
ps aux | grep "python main.py"
ps aux | grep "npm run dev"

# 终止进程
kill <PID>
```

### 方法2: 在启动的终端中按 Ctrl+C

## 常见问题

### Q1: 端口被占用

如果8000或3000端口被占用：

**后端**: 修改 `backend/config.py` 中的端口配置

**前端**: 修改 `frontend/vite.config.ts` 中的端口配置：
```typescript
server: {
  port: 3001,  // 改成其他端口
}
```

### Q2: 数据库不存在

运行数据迁移脚本：

```bash
cd backend
python migrate_excel.py
```

### Q3: 前端无法连接后端

确保：
1. 后端服务正在运行 (访问 http://localhost:8000/health 测试)
2. 前端proxy配置正确 (检查 `frontend/vite.config.ts`)

### Q4: Excel导入失败

现在系统会自动生成缺失的订单编号，不会因为订单编号缺失而失败。

如果还是失败，检查：
- Excel文件格式是否正确 (.xlsx 或 .xls)
- 是否有必需字段（产品名称、采购金额、订单日期）

### Q5: 页面显示空白

打开浏览器开发者工具 (F12) 查看：
1. Console是否有错误
2. Network标签页查看API请求是否正常

## 开发提示

### 热重载

- **前端**: Vite提供快速热重载，修改代码后自动刷新
- **后端**: FastAPI支持热重载，修改代码后自动重启

### 调试

**后端调试**:
```bash
# 查看后端日志
tail -f /tmp/backend.log

# 或直接在前台运行
cd backend
python main.py
```

**前端调试**:
- 使用浏览器开发者工具 (F12)
- 查看Console和Network标签页
- React DevTools扩展

### 测试API

使用Swagger UI进行API测试:
http://localhost:8000/docs

或使用curl:
```bash
# 健康检查
curl http://localhost:8000/health

# 获取Dashboard数据
curl http://localhost:8000/api/statistics/dashboard

# 获取订单列表
curl "http://localhost:8000/api/orders?page=1&size=10"
```

## 生产部署

### 后端

```bash
# 使用gunicorn + uvicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端

```bash
# 构建生产版本
npm run build

# dist目录包含静态文件，可以部署到任何静态服务器
# 例如：nginx, Apache, GitHub Pages等
```

## 数据备份

定期备份数据库文件：

```bash
cp backend/procurement.db backend/procurement_backup_$(date +%Y%m%d).db
```

## 更新日志

### v1.0.0 (2025-11-01)

**新功能**:
- ✅ 自动生成缺失的订单编号
- ✅ Excel导入更加智能，不会因为订单编号缺失而失败
- ✅ 完整的前后端系统
- ✅ 一键启动脚本

---

**最后更新**: 2025-11-01

如有问题，请查看完整文档: [README.md](../README.md)
