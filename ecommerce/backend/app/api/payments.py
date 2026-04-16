# 支付 API 路由（框架代码）

from fastapi import APIRouter

router = APIRouter()

@router.post("/payments/create")
def create_payment():
    """创建支付预付单"""
    return {"message": "创建支付接口"}

@router.post("/payments/notify")
def payment_notify():
    """支付回调"""
    return {"message": "支付回调接口"}

@router.get("/payments/{order_id}/status")
def get_payment_status(order_id: int):
    """查询支付状态"""
    return {"message": "查询支付状态接口"}
