# 订单 API 路由（框架代码）

from fastapi import APIRouter

router = APIRouter()

@router.post("/orders")
def create_order():
    """创建订单"""
    return {"message": "订单创建接口"}

@router.get("/orders")
def get_orders():
    """获取订单列表"""
    return {"message": "订单列表接口"}

@router.get("/orders/{order_id}")
def get_order_detail(order_id: int):
    """获取订单详情"""
    return {"message": "订单详情接口"}

@router.put("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    """取消订单"""
    return {"message": "取消订单接口"}

@router.put("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    """确认收货"""
    return {"message": "确认收货接口"}

@router.post("/orders/{order_id}/review")
def review_order(order_id: int):
    """提交评价"""
    return {"message": "评价接口"}
