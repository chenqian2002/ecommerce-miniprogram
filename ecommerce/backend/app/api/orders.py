# 订单 API 路由（修正版）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

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
from app.services.wechat_official_service import send_order_notice_to_merchant

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

class ShipOrderRequest(BaseModel):
    logistics_company: str | None = None

# --- Helpers (辅助函数) ---

def build_order_number() -> str:
    """生成唯一订单号"""
    return f"ORD{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{uuid.uuid4().hex[:4].upper()}"

def is_merchant_user(user: UserModel) -> bool:
    """判断当前用户是否为商家"""
    return bool(
        getattr(user, 'isMerchant', False)
        or getattr(user, 'role', None) == 'merchant'
        or getattr(user, 'phone', None) == '13859631156'
    )

def build_order_items_summary(db: Session, order_id: int) -> tuple[list[dict], str]:
    """生成订单商品明细和摘要"""
    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
    detail_items = []
    summary_parts = []
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        name = product.name if product else "未知商品"
        detail_items.append({
            "product_id": item.product_id,
            "name": name,
            "image_url": product.image_url if product else "",
            "quantity": item.quantity,
            "price": item.price,
        })
        summary_parts.append(f"{name}×{item.quantity}")
    return detail_items, "，".join(summary_parts)

def build_order_address(db: Session, address_id: int | None):
    """生成订单地址信息"""
    if not address_id:
        return None
    address = db.query(AddressModel).filter(AddressModel.id == address_id).first()
    if not address:
        return None
    return {
        "receiver_name": address.receiver_name,
        "phone": address.phone,
        "province": address.province,
        "city": address.city,
        "district": address.district,
        "detail": address.detail,
        "full_address": f"{address.province}{address.city}{address.district}{address.detail}"
    }

def notify_merchant_new_order(order: OrderModel, address: dict | None, items_summary: str):
    """控制台消息通知"""
    print("\n========== 商家新订单通知 ==========")
    print(f"订单号：{order.order_number}")
    print(f"商品：{items_summary}")
    print(f"金额：¥{order.total_price}")
    print(f"地址：{address.get('full_address') if address else '无'}")
    print("===================================\n")


def ensure_order_columns(db: Session):
    """兼容旧 SQLite 数据库，接口调用时兜底补充新增字段"""
    if db.get_bind().dialect.name != "sqlite":
        return

    columns = [row[1] for row in db.execute(text("PRAGMA table_info(orders)")).fetchall()]
    if "merchant_hidden" not in columns:
        db.execute(text("ALTER TABLE orders ADD COLUMN merchant_hidden BOOLEAN DEFAULT 0"))
    if "logistics_company" not in columns:
        db.execute(text("ALTER TABLE orders ADD COLUMN logistics_company VARCHAR(100)"))
    if "logistics_image_url" not in columns:
        db.execute(text("ALTER TABLE orders ADD COLUMN logistics_image_url VARCHAR(500)"))
    if "logistics_remark" not in columns:
        db.execute(text("ALTER TABLE orders ADD COLUMN logistics_remark VARCHAR(500)"))
    db.commit()


# --- Merchant Routes (商家接口) ---


@router.get("/merchant/orders")
def merchant_orders(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """商家查看全站订单列表"""
    ensure_order_columns(db)
    if not is_merchant_user(user):
        raise HTTPException(status_code=403, detail="无商家权限")

    orders = db.query(OrderModel).filter(
        (OrderModel.merchant_hidden == False) | (OrderModel.merchant_hidden.is_(None))
    ).order_by(OrderModel.created_at.desc()).all()

    result = []

    for o in orders:
        detail_items, items_summary = build_order_items_summary(db, o.id)
        address = build_order_address(db, o.address_id)
        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at,
            "item_count": sum(item.get("quantity", 0) for item in detail_items),
            "items": detail_items,
            "items_summary": items_summary,
            "address": address,
            "logistics_company": getattr(o, "logistics_company", None),
        })
    return {"data": result}

@router.delete("/merchant/orders")
def clear_merchant_orders(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """商家清除后台订单：只对商家后台隐藏，不删除买家的订单"""
    ensure_order_columns(db)
    if not is_merchant_user(user):

        raise HTTPException(status_code=403, detail="无商家权限")
    try:
        orders = db.query(OrderModel).filter(
            (OrderModel.merchant_hidden == False) | (OrderModel.merchant_hidden.is_(None))
        ).all()
        for order in orders:
            order.merchant_hidden = True
        db.commit()
        return {"message": "商家后台订单已清除", "deleted_count": len(orders)}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="清空失败")


@router.put("/merchant/orders/{order_id}/ship")
def ship_order(
    order_id: int,
    request: ShipOrderRequest | None = None,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家发货"""
    ensure_order_columns(db)
    if not is_merchant_user(user):
        raise HTTPException(status_code=403, detail="无商家权限")

    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order or order.status != "paid":
        raise HTTPException(status_code=400, detail="订单状态不可发货")
    order.status = "shipped"
    if request and request.logistics_company:
        order.logistics_company = request.logistics_company
    db.commit()
    return {"message": "发货成功"}

# --- User Routes (用户接口) ---

@router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户下单：扣库存、创建订单、通知商家"""
    address_data = db.query(AddressModel).filter(
        AddressModel.id == request.address_id,
        AddressModel.user_id == user.id
    ).first()
    if not address_data:
        raise HTTPException(status_code=404, detail="收货地址不存在")

    if request.cart_items:
        source_items = [
            {"product_id": i.product_id, "quantity": i.quantity}
            for i in request.cart_items
            if i.quantity > 0
        ]
    else:
        db_cart = db.query(CartItemModel).filter(CartItemModel.user_id == user.id).all()
        source_items = [
            {"product_id": i.product_id, "quantity": i.quantity}
            for i in db_cart
            if i.product_id and (i.quantity or 0) > 0
        ]

    if not source_items:
        raise HTTPException(status_code=400, detail="未选择商品")

    try:
        total_price = 0.0
        prepared_items = []

        for item in source_items:
            product = db.query(ProductModel).filter(ProductModel.id == item["product_id"]).with_for_update().first()
            if not product:
                raise HTTPException(status_code=404, detail=f"商品 {item['product_id']} 不存在")
            if product.stock < item["quantity"]:
                raise HTTPException(status_code=400, detail=f"商品 {product.name} 库存不足")

            price = float(product.price or 0)
            total_price += price * item["quantity"]
            product.stock -= item["quantity"]
            product.sales = (product.sales or 0) + item["quantity"]
            prepared_items.append({
                "product_id": product.id,
                "quantity": item["quantity"],
                "price": price,
            })

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

        for pi in prepared_items:
            db.add(OrderItemModel(
                order_id=new_order.id,
                product_id=pi["product_id"],
                quantity=pi["quantity"],
                price=pi["price"],
            ))

        if not request.cart_items:
            db.query(CartItemModel).filter(CartItemModel.user_id == user.id).delete()

        db.commit()
        db.refresh(new_order)

        _, summary = build_order_items_summary(db, new_order.id)
        order_address = build_order_address(db, new_order.address_id)
        notify_merchant_new_order(new_order, order_address, summary)
        await send_order_notice_to_merchant(new_order, order_address, summary)

        return {
            "message": "下单成功",
            "order_id": new_order.id,
            "order_number": new_order.order_number,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="系统下单异常")



@router.get("/orders")
def get_orders(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """我的订单列表"""
    orders = db.query(OrderModel).filter(OrderModel.user_id == user.id).order_by(OrderModel.created_at.desc()).all()
    result = []
    for o in orders:
        detail_items, _ = build_order_items_summary(db, o.id)
        result.append({
            "id": o.id,
            "order_number": o.order_number,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at,
            "item_count": sum(item.get("quantity", 0) for item in detail_items),
            "logistics_company": getattr(o, "logistics_company", None),
        })
    return {"data": result}

@router.get("/orders/{order_id}")
def get_order_detail(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """订单详情"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    detail_items, _ = build_order_items_summary(db, order.id)
    address = build_order_address(db, order.address_id)
    return {
        "id": order.id,
        "order_number": order.order_number,
        "total_price": order.total_price,
        "status": order.status,
        "payment_method": order.payment_method,
        "remark": order.remark,
        "logistics_company": getattr(order, "logistics_company", None),
        "created_at": order.created_at,
        "items": detail_items,
        "address": address,
    }

@router.put("/orders/{order_id}/pay")
def pay_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """支付订单"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status != "pending":
        raise HTTPException(status_code=400, detail="不可支付")
    update_payment_success(db, order.id)
    return {"message": "支付成功"}

@router.put("/orders/{order_id}/cancel")
def cancel_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """用户取消订单 (回滚库存)"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status != "pending":
        raise HTTPException(status_code=400, detail="无法取消")
    try:
        items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
        for item in items:
            product = db.query(ProductModel).filter(ProductModel.id == item.product_id).with_for_update().first()
            if product:
                product.stock += item.quantity
                product.sales = max(0, (product.sales or 0) - item.quantity)
        order.status = "cancelled"
        db.commit()
        return {"message": "订单已取消"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="取消失败")

@router.put("/orders/{order_id}/confirm")
def confirm_order(order_id: int, user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """确认收货"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == user.id).first()
    if not order or order.status not in ["paid", "shipped"]:
        raise HTTPException(status_code=400, detail="无法确认收货")
    order.status = "completed"
    db.commit()
    return {"message": "已完成收货"}