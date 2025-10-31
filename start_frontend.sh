#!/bin/bash

echo "🚀 启动采购管理系统前端..."

cd "$(dirname "$0")/frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动开发服务器
echo "✅ 启动前端开发服务器 (http://localhost:3000)"
npm run dev
