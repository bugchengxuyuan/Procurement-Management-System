#!/bin/bash

echo "=========================================="
echo "  采购管理系统 v2.0 - 启动脚本"
echo "=========================================="

# 检查是否在项目根目录
if [ ! -d "api" ] || [ ! -d "web" ]; then
    echo "错误: 请在项目根目录下运行此脚本"
    exit 1
fi

# 创建数据目录
mkdir -p data

echo ""
echo "1. 安装后端依赖..."
cd api
pip install -q -r requirements.txt
cd ..

echo "2. 启动后端服务..."
cd api
python run.py > ../data/api.log 2>&1 &
API_PID=$!
echo "   后端 PID: $API_PID"
cd ..

echo "3. 等待后端启动..."
sleep 3

echo "4. 安装前端依赖..."
cd web
npm install --silent
cd ..

echo "5. 启动前端服务..."
cd web
npm run dev > ../data/web.log 2>&1 &
WEB_PID=$!
echo "   前端 PID: $WEB_PID"
cd ..

echo ""
echo "=========================================="
echo "  启动完成！"
echo "=========================================="
echo "后端服务: http://localhost:8000"
echo "API文档:  http://localhost:8000/docs"
echo "前端应用: http://localhost:3000"
echo ""
echo "日志文件:"
echo "  后端: data/api.log"
echo "  前端: data/web.log"
echo ""
echo "停止服务: kill $API_PID $WEB_PID"
echo "=========================================="
