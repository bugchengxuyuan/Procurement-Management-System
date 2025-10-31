"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .database import init_db
from .api import orders_router, import_export_router

# 创建FastAPI应用
app = FastAPI(
    title="采购管理系统 API",
    description="完整的采购订单管理系统后端API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(orders_router)
app.include_router(import_export_router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("🚀 启动采购管理系统...")
    init_db()
    print("✅ 数据库已初始化")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "采购管理系统 API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"message": f"服务器错误: {str(exc)}"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
