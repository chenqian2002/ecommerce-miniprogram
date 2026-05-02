# 初始化文件

from .auth import router as auth_router
from .products import router as products_router
from .cart import router as cart_router
from .orders import router as orders_router
from .users import router as users_router
from .addresses import router as addresses_router
from .payments import router as payments_router
from .announcement import router as announcement_router


__all__ = [
    "auth_router",
    "products_router",
    "cart_router", 
    "orders_router",
    "users_router",
    "addresses_router",
        "payments_router",
    "announcement_router"
]

