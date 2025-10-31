#!/bin/bash

echo "🚀 启动采购管理系统后端..."

cd "$(dirname "$0")"

# 检查Python依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 安装Python依赖..."
    pip3 install -r backend/requirements.txt
fi

# 启动FastAPI服务器
echo "✅ 启动API服务器 (http://localhost:8000)"
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
