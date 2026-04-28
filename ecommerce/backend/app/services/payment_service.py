# 支付相关服务（正式版接入骨架）

from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import OrderModel, PaymentModel, OrderItemModel, ProductModel, UserModel


def create_payment_record(db: Session, order: OrderModel, payment_method: str, transaction_id: str) -> PaymentModel:
    """创建支付记录"""
    payment = PaymentModel(
        order_id=order.id,
        amount=order.total_price,
        transaction_id=transaction_id,
        status="pending",
        payment_method=payment_method,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def mark_payment_completed(db: Session, order_id: int, transaction_id: str | None = None) -> PaymentModel | None:
    """标记支付记录为已完成"""
    payment = (
        db.query(PaymentModel)
        .filter(PaymentModel.order_id == order_id)
        .order_by(PaymentModel.created_at.desc())
        .first()
    )
    if payment:
        payment.status = "completed"
        if transaction_id:
            payment.transaction_id = transaction_id
        db.commit()
        db.refresh(payment)
    return payment


def update_payment_success(db: Session, order_id: int, transaction_id: str | None = None):
    """支付成功后的统一处理：更新支付记录、订单状态、消息通知占位"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise ValueError("订单不存在")

    mark_payment_completed(db, order_id, transaction_id=transaction_id)

    order.status = "paid"
    db.commit()
    db.refresh(order)
    return order


def build_order_message(db: Session, order_id: int) -> dict:
    """构造支付成功通知内容（后续可接微信订阅消息）"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise ValueError("订单不存在")

    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
    detail_lines = []
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        name = product.name if product else "未知商品"
        detail_lines.append(f"{name} x{item.quantity}")

    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "total_price": order.total_price,
        "status": order.status,
        "items": detail_lines,
        "title": "支付成功通知",
        "content": f"你已购买：{'，'.join(detail_lines)}；合计：¥{order.total_price}",
    }


def send_subscribe_message_placeholder(user: UserModel, message: dict):
    """订阅消息发送占位：后续接微信订阅消息接口"""
    # 正式版这里应该调用微信订阅消息 API
    # 目前仅做占位，不阻塞支付流程
    return {
        "sent": False,
        "user_id": user.id,
        "message": message,
        "reason": "subscribe message api not implemented yet",
    }
