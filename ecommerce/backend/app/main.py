# FastAPI 主程序入口 (修正版)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os

from app.core.config import settings
from app.database.database import engine, Base
from app.api import auth, products, cart, orders, users, addresses, payments, announcement, merchant_settings, home

from app.api import upload

# --- 数据库初始化 ---

# 创建所有表
Base.metadata.create_all(bind=engine)

def ensure_sqlite_columns():
    """兼容开发阶段旧 SQLite 数据库，自动补充新增字段。"""
    if engine.dialect.name != 'sqlite':
        return

    # 修复了下方的缩进错误
    with engine.begin() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")).fetchall()
        if not tables:
            return

        # 获取 orders 表现有的列名
        existing_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(orders)")).fetchall()]
        
        # 自动补充物流相关字段 (修复了此处的缩进)
        if 'logistics_image_url' not in existing_columns:
            conn.execute(text("ALTER TABLE orders ADD COLUMN logistics_image_url VARCHAR(500)"))
        if 'logistics_company' not in existing_columns:
            conn.execute(text("ALTER TABLE orders ADD COLUMN logistics_company VARCHAR(100)"))
        if 'logistics_remark' not in existing_columns:
            conn.execute(text("ALTER TABLE orders ADD COLUMN logistics_remark VARCHAR(500)"))
        if 'merchant_hidden' not in existing_columns:
            conn.execute(text("ALTER TABLE orders ADD COLUMN merchant_hidden BOOLEAN DEFAULT 0"))

        # users 表新增 role 字段
        user_tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")).fetchall()
        if user_tables:
            user_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)")).fetchall()]
            if 'role' not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'customer'"))


# 执行 SQLite 补丁
ensure_sqlite_columns()

# 自动初始化数据（如果 users 表为空）
def auto_init_data():
    """启动时检查：如果数据库里没有用户数据，自动运行 init_data"""
    if engine.dialect.name != 'sqlite':
        return
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            if result == 0:
                print("📦 数据库为空，正在自动初始化测试数据...")
                from init_data import main as init_main
                init_main()
                print("✅ 自动初始化完成")
    except Exception as e:
        print(f"⚠️ 自动初始化跳过: {e}")

auto_init_data()

# 自动迁移：将旧商家手机号更新为新号码
def migrate_merchant_phone():
    if engine.dialect.name != 'sqlite':
        return
    try:
        from sqlalchemy import text
        with engine.begin() as conn:
            conn.execute(text(
                "UPDATE users SET phone='13859631156', role='merchant', "
                "nickname='张三（商家）' WHERE phone='13800138000'"
            ))
    except Exception:
        pass

migrate_merchant_phone()

# 自动创建测试买家账号（如果不存在）
def ensure_test_buyer_accounts():
    if engine.dialect.name != 'sqlite':
        return
    try:
        from app.core.security import hash_password as hp
        with engine.begin() as conn:
            existing = conn.execute(text("SELECT COUNT(*) FROM users WHERE phone='13800138001'")).scalar()
            if existing == 0:
                print("📦 创建测试买家账号...")
                conn.execute(text(
                    "INSERT INTO users (phone, nickname, role, password_hash) VALUES "
                    "('13800138001', '李四（买家测试）', 'customer', :pw1), "
                    "('13800138002', '王五（买家测试）', 'customer', :pw2)"
                ), {"pw1": hp("123456"), "pw2": hp("123456")})
                print("✅ 测试买家账号已创建")
    except Exception as e:
        print(f"⚠️ 创建测试买家跳过: {e}")

ensure_test_buyer_accounts()

# --- 初始化 FastAPI 应用 ---

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

# --- 静态文件处理 ---

# 确保上传目录存在，防止 StaticFiles 挂载失败
upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)

app.mount('/uploads', StaticFiles(directory=upload_dir), name='uploads')

# --- 路由注册 ---

# 健康检查
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api")
def api_root():
    return {"status": "ok", "message": f"{settings.APP_NAME} API 服务正在运行"}

@app.get("/api/health")
def api_health():
    return {"status": "ok"}


# 注册子模块路由

app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(products.router, prefix="/api", tags=["商品"])
app.include_router(cart.router, prefix="/api", tags=["购物车"])
app.include_router(orders.router, prefix="/api", tags=["订单"])
app.include_router(users.router, prefix="/api", tags=["用户"])
app.include_router(addresses.router, prefix="/api", tags=["地址"])
app.include_router(payments.router, prefix="/api", tags=["支付"])
app.include_router(upload.router, prefix="/api", tags=["上传"])
app.include_router(announcement.router, prefix="/api", tags=["公告"])
app.include_router(merchant_settings.router, prefix="/api", tags=["商家设置"])
app.include_router(home.router, prefix="/api", tags=["首页"])


# 根路由
@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API 服务正在运行"}

# --- 启动入口 ---

if __name__ == "__main__":
    import uvicorn
    # 使用 app 实例启动
    uvicorn.run(app, host="0.0.0.0", port=8000)