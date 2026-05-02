# 微信公众号/订阅号通知服务

import httpx
from app.core.config import settings


def _is_enabled() -> bool:
    """检查是否已配置公众号通知参数"""
    return bool(
        settings.WECHAT_OFFICIAL_APPID
        and settings.WECHAT_OFFICIAL_SECRET
        and settings.WECHAT_ORDER_TEMPLATE_ID
        and settings.WECHAT_MERCHANT_OPENID
    )


async def get_official_access_token() -> str | None:
    """获取公众号 access_token"""
    if not settings.WECHAT_OFFICIAL_APPID or not settings.WECHAT_OFFICIAL_SECRET:
        return None

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_OFFICIAL_APPID,
        "secret": settings.WECHAT_OFFICIAL_SECRET,
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    token = data.get("access_token")
    if not token:
        print(f"[订阅号通知] 获取 access_token 失败：{data}")
        return None
    return token


async def send_order_notice_to_merchant(order, address: dict | None, items_summary: str):
    """发送新订单通知给卖家微信。

    需要在 .env 中配置：
    WECHAT_OFFICIAL_APPID=公众号appid
    WECHAT_OFFICIAL_SECRET=公众号secret
    WECHAT_ORDER_TEMPLATE_ID=模板消息id
    WECHAT_MERCHANT_OPENID=接收通知的卖家openid
    """
    fallback_text = (
        "\n========== 新订单通知 =========="
        f"\n订单号：{order.order_number}"
        f"\n商品：{items_summary}"
        f"\n金额：¥{order.total_price}"
        f"\n收货人：{address.get('receiver_name') if address else '无'}"
        f"\n电话：{address.get('phone') if address else '无'}"
        f"\n地址：{address.get('full_address') if address else '无'}"
        "\n================================\n"
    )

    if not _is_enabled():
        print("[订阅号通知] 未配置公众号参数，已跳过真实推送。")
        print(fallback_text)
        return False

    access_token = await get_official_access_token()
    if not access_token:
        print(fallback_text)
        return False

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    payload = {
        "touser": settings.WECHAT_MERCHANT_OPENID,
        "template_id": settings.WECHAT_ORDER_TEMPLATE_ID,
        "data": {
            "first": {"value": "你有一笔新的商城订单", "color": "#173177"},
            "keyword1": {"value": str(order.order_number)},
            "keyword2": {"value": items_summary[:200]},
            "keyword3": {"value": f"¥{float(order.total_price or 0):.2f}"},
            "keyword4": {"value": address.get("full_address") if address else "无地址"},
            "keyword5": {"value": address.get("phone") if address else "无电话"},
            "remark": {"value": "请及时进入卖家后台处理订单。", "color": "#173177"},
        },
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.post(url, json=payload)
        data = resp.json()

    if data.get("errcode") != 0:
        print(f"[订阅号通知] 发送失败：{data}")
        print(fallback_text)
        return False

    print(f"[订阅号通知] 新订单通知已发送：{order.order_number}")
    return True
