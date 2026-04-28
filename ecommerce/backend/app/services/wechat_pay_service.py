# 微信支付参数生成服务（正式版接入骨架）

from __future__ import annotations

import base64
import json
import secrets
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


@dataclass
class WxPayParams:
    appId: str
    timeStamp: str
    nonceStr: str
    package: str
    signType: str
    paySign: str


@dataclass
class WxPayOrderResult:
    prepay_id: str
    out_trade_no: str
    status: str
    raw_response: dict[str, Any]


def build_payment_flow_summary() -> dict:
    return {
        "step_1": "创建支付单",
        "step_2": "调用微信统一下单",
        "step_3": "拉起微信支付",
        "step_4": "支付回调更新订单",
        "step_5": "发送订阅消息",
    }


def build_signing_message(app_id: str, timestamp: str, nonce_str: str, package: str) -> str:
    """生成微信支付 V3 签名待签字符串"""
    return f"{app_id}\n{timestamp}\n{nonce_str}\n{package}\n"


def load_private_key_text() -> str:
    """读取商户私钥文本"""
    key_path = settings.WECHAT_PAY_PRIVATE_KEY_PATH
    if not key_path:
        return ""

    path = Path(key_path)
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def sign_with_private_key_stub(message: str) -> str:
    """RSA 签名占位：正式版请替换为商户私钥签名"""
    private_key_text = load_private_key_text()
    if not private_key_text:
        return ""

    # 正式版接入点：
    # 1. 使用 cryptography 读取 RSA 私钥
    # 2. 对 message 做 SHA256withRSA 签名
    # 3. 返回 base64 编码签名结果
    return base64.b64encode(message.encode("utf-8")).decode("utf-8")


def build_wechat_pay_params(prepay_id: str) -> WxPayParams:
    """构造微信支付参数骨架，真实签名后续补齐"""
    timestamp = str(int(datetime.now().timestamp()))
    nonce_str = secrets.token_hex(16)
    package = f"prepay_id={prepay_id}"
    sign_source = build_signing_message(settings.WECHAT_APPID, timestamp, nonce_str, package)
    pay_sign = sign_with_private_key_stub(sign_source)

    return WxPayParams(
        appId=settings.WECHAT_APPID,
        timeStamp=timestamp,
        nonceStr=nonce_str,
        package=package,
        signType="RSA",
        paySign=pay_sign,
    )


def build_unified_order_payload(order_number: str, amount: float, description: str) -> dict[str, Any]:
    """统一下单请求体骨架"""
    return {
        "appid": settings.WECHAT_APPID,
        "mchid": settings.WECHAT_MCH_ID,
        "description": description,
        "out_trade_no": order_number,
        "notify_url": settings.WECHAT_NOTIFY_URL,
        "amount": {
            "total": int(amount * 100),
            "currency": "CNY",
        },
    }


def create_unified_order_stub(order_number: str, amount: float, description: str) -> WxPayOrderResult:
    """微信统一下单占位：真实版接入时替换为 HTTP 调用微信支付 V3 接口"""
    payload = build_unified_order_payload(order_number, amount, description)
    prepay_id = f"wx{secrets.token_hex(16)}"
    return WxPayOrderResult(
        prepay_id=prepay_id,
        out_trade_no=order_number,
        status="SUCCESS",
        raw_response={
            "payload": payload,
            "prepay_id": prepay_id,
            "message": "unified order stub",
        },
    )


def verify_payment_callback_stub(raw_body: bytes, headers: dict[str, str] | None = None) -> bool:
    """支付回调验签占位：后续接入微信平台证书验证"""
    # 正式版接入点：
    # 1. 读取微信平台证书
    # 2. 验证签名
    # 3. 校验回调报文是否被篡改
    return bool(raw_body)


def decode_callback_payload(raw_body: bytes) -> dict[str, Any]:
    """尝试把回调原始报文解析为 JSON"""
    try:
        return json.loads(raw_body.decode("utf-8"))
    except Exception:
        return {}
