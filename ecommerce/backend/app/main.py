# FastAPI 主程序入口

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from app.core.config import settings
from app.database.database import engine, Base
from app.api import auth, products, cart, orders, users, addresses, payments

# 创建所有表
Base.metadata.create_all(bind=engine)

# 初始化 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
def health():
    return {"status": "ok"}

# 注册路由
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(products.router, prefix="/api", tags=["商品"])
app.include_router(cart.router, prefix="/api", tags=["购物车"])
app.include_router(orders.router, prefix="/api", tags=["订单"])
app.include_router(users.router, prefix="/api", tags=["用户"])
app.include_router(addresses.router, prefix="/api", tags=["地址"])
app.include_router(payments.router, prefix="/api", tags=["支付"])

# 根路由
@app.get("/")
def root():
    return {"message": "电商平台 API 服务正在运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
