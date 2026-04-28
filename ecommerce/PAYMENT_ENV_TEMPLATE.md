# 正式支付配置模板

> 说明：这是微信支付正式接入时需要准备的环境变量模板。你现在可以先保存，等申请到商户号后再填写。

## 基础配置

```env
APP_NAME=电商平台 API
APP_VERSION=1.0.0
DEBUG=true
DATABASE_URL=sqlite:///./ecommerce.db
JWT_SECRET_KEY=please-change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 微信小程序配置

```env
WECHAT_APPID=你的微信小程序AppID
WECHAT_APPSECRET=你的微信小程序AppSecret
```

## 微信支付配置

```env
WECHAT_MCH_ID=你的微信支付商户号
WECHAT_API_KEY=你的商户API密钥
WECHAT_NOTIFY_URL=https://你的域名/api/payments/notify
WECHAT_CERT_PATH=./certs/apiclient_cert.pem
WECHAT_KEY_PATH=./certs/apiclient_key.pem
```

## 订阅消息配置

```env
WECHAT_SUBSCRIBE_TEMPLATE_ID=你的订阅消息模板ID
```

## 生产环境建议

```env
DEBUG=false
CORS_ORIGINS=["https://你的前端域名"]
```

---

# 字段说明

- `WECHAT_APPID`：小程序 AppID
- `WECHAT_APPSECRET`：小程序 AppSecret
- `WECHAT_MCH_ID`：微信支付商户号
- `WECHAT_API_KEY`：商户 API 密钥
- `WECHAT_NOTIFY_URL`：微信支付成功回调地址
- `WECHAT_CERT_PATH`：商户证书路径
- `WECHAT_KEY_PATH`：商户私钥路径
- `WECHAT_SUBSCRIBE_TEMPLATE_ID`：支付成功订阅消息模板 ID

---

# 你当前还缺的东西

- 微信支付商户号
- 商户 API 密钥 / 证书
- 订阅消息模板 ID
- 公网可访问的回调地址

---

# 后续接入顺序

1. 填写 `.env`
2. 实现微信统一下单
3. 实现支付回调验签
4. 支付成功后发订阅消息
5. 真机测试支付流程
