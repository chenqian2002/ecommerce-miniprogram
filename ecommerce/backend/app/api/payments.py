# 支付 API 路由（正式版接入骨架）

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import OrderModel, PaymentModel, UserModel
from app.services.payment_service import (
    build_order_message,
    create_payment_record,
    send_subscribe_message_placeholder,
    update_payment_success,
)
from app.services.wechat_pay_service import (
    build_payment_flow_summary,
    build_wechat_pay_params,
    create_unified_order_stub,
    decode_callback_payload,
    verify_payment_callback_stub,
)

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    order_id: int
    payment_method: str = "wechat"


@router.post("/payments/create")
def create_payment(
    request: CreatePaymentRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建支付单：正式版用于向微信支付下单，当前返回支付骨架数据"""
    order = (
        db.query(OrderModel)
        .filter(OrderModel.id == request.order_id, OrderModel.user_id == user.id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="当前订单状态不允许支付")

    transaction_id = f"TXN{uuid.uuid4().hex[:24].upper()}"
    payment = create_payment_record(db, order, request.payment_method, transaction_id)
    unified_order = create_unified_order_stub(
        order.order_number,
        order.total_price,
        f"订单支付-{order.order_number}",
    )
    pay_params = build_wechat_pay_params(unified_order.prepay_id)

    return {
        "message": "支付预下单成功",
        "data": {
            "order_id": order.id,
            "order_number": order.order_number,
            "amount": order.total_price,
            "payment_method": request.payment_method,
            "transaction_id": transaction_id,
            "prepay_id": unified_order.prepay_id,
            "payment_status": payment.status,
            "subscribe_template_id": settings.WECHAT_SUBSCRIBE_TEMPLATE_ID,
            "payment_flow": build_payment_flow_summary(),
            "wxpay": {
                "appId": pay_params.appId,
                "timeStamp": pay_params.timeStamp,
                "nonceStr": pay_params.nonceStr,
                "package": pay_params.package,
                "signType": pay_params.signType,
                "paySign": pay_params.paySign,
            },
            "unified_order": unified_order.raw_response,
            "mock": False,
        },
    }


@router.post("/payments/notify")
async def payment_notify(request: Request, db: Session = Depends(get_db)):
    """支付回调：正式版微信支付成功后由微信服务器回调到这里"""
    raw_body = await request.body()

    if not verify_payment_callback_stub(raw_body, dict(request.headers)):
        raise HTTPException(status_code=400, detail="支付回调验签失败")

    try:
        payload = await request.json()
    except Exception:
        payload = decode_callback_payload(raw_body)

    order_id = payload.get("order_id") or payload.get("out_trade_no")
    transaction_id = payload.get("transaction_id") or payload.get("trade_no")

    if order_id:
        try:
            order = update_payment_success(db, int(order_id), transaction_id=transaction_id)
            message = build_order_message(db, int(order_id))

            user = db.query(UserModel).filter(UserModel.id == order.user_id).first()
            notify_result = None
            if user:
                notify_result = send_subscribe_message_placeholder(user, message)

            return {
                "code": "SUCCESS",
                "message": "回调已处理",
                "order_id": order.id,
                "order_status": order.status,
                "payment_status": "completed",
                "notify": notify_result,
                "order_message": message,
                "body_length": len(raw_body),
            }
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"回调处理失败: {str(exc)}")

    return {
        "code": "SUCCESS",
        "message": "回调已接收",
        "body_length": len(raw_body),
    }


@router.get("/payments/{order_id}/status")
def get_payment_status(order_id: int, db: Session = Depends(get_db)):
    """查询支付状态"""
    payment = (
        db.query(PaymentModel)
        .filter(PaymentModel.order_id == order_id)
        .order_by(PaymentModel.created_at.desc())
        .first()
    )
    if not payment:
        return {"message": "暂无支付记录", "order_id": order_id, "status": "none"}

    return {
        "message": "查询支付状态成功",
        "order_id": order_id,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "transaction_id": payment.transaction_id,
        "amount": payment.amount,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at,
    }







