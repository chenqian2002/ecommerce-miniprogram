# 订单 API 路由（修正版）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid
import traceback

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import (
    AddressModel,
    CartItemModel,
    OrderItemModel,
    OrderModel,
    ProductModel,
    UserModel,
)
from app.services.payment_service import update_payment_success

router = APIRouter()

# --- Schemas (数据模型) ---

class CreateOrderItem(BaseModel):
    product_id: int
    quantity: int

class CreateOrderRequest(BaseModel):
    address_id: int
    payment_method: str = "mock"
    remark: str | None = None
    cart_items: list[CreateOrderItem] | None = None

# --- Helpers (辅助函数) ---

def build_order_number() -> str:
    """生成唯一订单号"""
    return f"ORD{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{uuid.uuid4().hex[:4].upper()}"

# --- Routes (接口路由) ---

@router.post("/orders")
def create_order(
    request: CreateOrderRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建订单：支持立即购买（传 cart_items）或从购物车结算"""
    
    # 1. 验证收货地址
    address = db.query(AddressModel).filter(
        AddressModel.id == request.address_id, 
        AddressModel.user_id == user.id
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="收货地址不存在")

    source_items = []
    # 2. 确定商品来源
    if request.cart_items and len(request.cart_items) > 0:
        source_items = [{"product_id": i.product_id, "quantity": i.quantity} for i in request.cart_items if i.quantity > 0]
    else:
        cart_db_items = db.query(CartItemModel).filter(CartItemModel.user_id == user.id).all()
        source_items = [{"product_id": i.product_id, "quantity": i.quantity} for i in cart_db_items if i.product_id and (i.quantity or 0) > 0]

    if not source_items:
        raise HTTPException(status_code=400, detail="未选中任何有效商品")

    total_price = 0.0
    prepared_items = []

    try:
        # 3. 校验库存并计算总价
        for item in source_items:
            # 使用 with_for_update 防止并发超卖
            product = db.query(ProductModel).filter(ProductModel.id == item["product_id"]).with_for_update().first()
            if not product:
                raise HTTPException(status_code=404, detail=f"商品 ID {item['product_id']} 不存在")
            if product.stock < item["quantity"]:
                raise HTTPException(status_code=400, detail=f"商品 {product.name} 库存不足")

            price = float(product.price or 0)
            total_price += price * item["quantity"]
            
            # 扣减库存
            product.stock -= item["quantity"]
            product.sales = (product.sales or 0) + item["quantity"]

            prepared_items.append({
                "product_id": product.id,
                "quantity": item["quantity"],
                "price": price
            })

        # 4. 创建订单记录
        new_order = OrderModel(
            order_number=build_order_number(),
            user_id=user.id,
            total_price=total_price,
            status="pending",
            payment_method=request.payment_method,
            address_id=request.address_id,
            remark=request.remark or "",
        )
        db.add(new_order)
        db.flush()

        # 5. 创建订单详情
        for pi in prepared_items:
            db.add(OrderItemModel(
                order_id=new_order.id,
                product_id=pi["product_id"],
                quantity=pi["quantity"],
                price=pi["price"]
            ))

        # 6. 如果是从购物车结算，则清理购物车
        if not request.cart_items:
            db.query(CartItemModel).filter(CartItemModel.user_id == user.id).delete()

        db.commit()
        db.refresh(new_order)
        return {"message": "订单创建成功", "order_id": new_order.id, "order_number": new_order.order_number}

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="订单系统异常")


@router.get("/orders")
def get_orders(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取用户订单列表"""
    orders = db.query(OrderModel).filter(OrderModel.user_id == user.id).order_by(OrderModel.created_at.desc()).all()
    result = []
    for o in orders:
        count = db.query(OrderItemModel).filter(OrderItemModel.order_id == o.id).count()
        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at,
            "item_count": count
        })
    return {"data": result}


@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取订单详情"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
    address = db.query(AddressModel).filter(AddressModel.id == order.address_id).first()

    detail_items = []
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        detail_items.append({
            "product_id": item.product_id,
            "name": product.name if product else "未知商品",
            "image_url": product.image_url if product else "",
            "quantity": item.quantity,
            "price": item.price,
        })

    return {
        "id": order.id,
        "order_number": order.order_number,
        "total_price": order.total_price,
        "status": order.status,
        "payment_method": order.payment_method,
        "remark": order.remark,
        "created_at": order.created_at,
        "address": {
            "receiver_name": address.receiver_name,
            "phone": address.phone,
            "full_address": f"{address.province}{address.city}{address.district}{address.detail}"
        } if address else None,
        "items": detail_items,
    }


@router.put("/orders/{order_id}/pay")
def pay_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """模拟支付"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")

    # 调用服务层更新支付成功状态
    update_payment_success(db, order.id)
    return {"message": "支付成功"}


@router.put("/orders/{order_id}/cancel")
def cancel_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """取消订单并归还库存"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status != "pending":
        raise HTTPException(status_code=400, detail="当前订单状态不可取消")

    try:
        # 回滚商品库存和销量
        items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
        for item in items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).with_for_update().first()
            if product:
                product.stock += item.quantity
                product.sales = max(0, (product.sales or 0) - item.quantity)

        order.status = "cancelled"
        db.commit()
        return {"message": "订单已取消，库存已返还"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="取消订单失败")


@router.put("/orders/{order_id}/confirm")
def confirm_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """确认收货"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status not in ["paid", "shipped"]:
        raise HTTPException(status_code=400, detail="当前订单状态无法确认收货")

    order.status = "completed"
    db.commit()
    return {"message": "订单已完成"}