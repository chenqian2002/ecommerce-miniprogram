# 电商平台后端 API

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 入口文件
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证接口
│   │   ├── products.py      # 商品接口
│   │   ├── cart.py          # 购物车接口
│   │   ├── orders.py        # 订单接口
│   │   ├── payments.py      # 支付接口
│   │   ├── users.py         # 用户接口
│   │   └── addresses.py     # 地址接口
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 配置文件
│   │   ├── security.py      # 安全相关
│   │   └── constants.py     # 常量定义
│   ├── database/            # 数据库相关
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy 模型
│   │   ├── database.py      # 数据库连接
│   │   └── crud.py          # 数据库操作
│   └── services/            # 业务逻辑
│       ├── __init__.py
│       ├── auth_service.py
│       ├── product_service.py
│       ├── order_service.py
│       └── payment_service.py
├── requirements.txt
├── .env.example
├── README.md
└── run.py
```

## 快速启动

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境
```bash
cp .env.example .env
# 编辑 .env，填入你的配置
```

3. 运行项目
```bash
python run.py
```

4. 访问接口文档
```
http://localhost:8000/docs
```

## 环境变量

在 `.env` 中配置：
- `DATABASE_URL`: 数据库连接字符串
- `JWT_SECRET_KEY`: JWT 密钥
- `WECHAT_APPID`: 微信小程序 APPID
- `WECHAT_APPSECRET`: 微信小程序秘钥
- `WECHAT_MCH_ID`: 微信商户号
- `WECHAT_API_KEY`: 微信支付密钥

## API 文档

详见 [API 接口文档](./docs/API.md)
