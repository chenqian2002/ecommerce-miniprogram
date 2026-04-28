# 电商平台小程序

完整的 WeChat 小程序电商解决方案，包含 FastAPI 后端和全功能前端。

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js 12+（可选）
- 微信开发者工具
- 微信小程序账号

### 后端启动

```bash
# 1. 进入后端目录
cd ecommerce/backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库（首次运行）
python init_data.py

# 4. 启动服务
python run.py

# 访问 http://127.0.0.1:8000/docs 查看 API 文档
```

### 小程序启动

1. 打开微信开发者工具
2. 选择"本地项目"
3. 项目路径：`ecommerce/minprogram`
4. AppID：`wxf20133399e7c179c`（测试用）
5. 勾选"使用 npm 模块"（可选）

**重要**：需要关闭域名检查
- 点击右下角 ⚙️ 齿轮
- 选择 "详情" → "本地设置"
- 取消勾选 "域名检查"

## 📱 项目结构

```
ecommerce/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py       # 认证接口
│   │   │   ├── products.py   # 商品接口
│   │   │   ├── cart.py       # 购物车接口
│   │   │   ├── orders.py     # 订单接口
│   │   │   ├── addresses.py  # 地址接口
│   │   │   ├── users.py      # 用户接口
│   │   │   └── payments.py   # 支付接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py     # 应用配置
│   │   │   └── security.py   # 加密安全
│   │   ├── database/          # 数据库
│   │   │   ├── database.py   # 连接配置
│   │   │   └── models.py     # ORM 模型
│   │   └── main.py           # 应用入口
│   ├── init_data.py          # 初始化脚本
│   ├── run.py                # 启动脚本
│   ├── ecommerce.db          # SQLite 数据库
│   └── requirements.txt       # 依赖列表
│
├── minprogram/               # WeChat 小程序
│   ├── pages/
│   │   ├── login/            # 登录页
│   │   ├── products/         # 商品列表
│   │   ├── product-detail/   # 商品详情（未创建）
│   │   ├── cart/             # 购物车
│   │   ├── orders/           # 订单列表
│   │   ├── order-detail/     # 订单详情（未创建）
│   │   ├── mine/             # 个人页面
│   │   ├── address-list/     # 地址列表（未创建）
│   │   └── address-add/      # 添加地址（未创建）
│   ├── utils/
│   │   ├── request.js        # HTTP 请求封装
│   │   ├── storage.js        # 本地存储封装
│   │   └── format.js         # 格式化工具
│   ├── app.js                # 全局应用
│   ├── app.json              # 配置文件
│   ├── app.wxss              # 全局样式
│   └── project.config.json   # 项目配置
│
├── README.md                 # 本文件
├── API.md                    # API 文档
├── DEPLOY.md                 # 部署指南
└── .env.example              # 环境变量示例
```

## 🔑 测试账号

| 账号 | 密码 | 说明 |
|-----|------|------|
| 13800138000 | 123456 | 测试账号 1 |
| 13800138001 | 123456 | 测试账号 2 |
| 13800138002 | 123456 | 测试账号 3 |

## 🎨 功能特性

### 已完成 ✅
- ✅ 用户认证系统（JWT + SHA256）
- ✅ 商品列表（左侧分类，右侧商品网格）
- ✅ 购物车管理
- ✅ 订单管理
- ✅ 个人信息页面
- ✅ 登出功能

### 进行中 🔄
- 🔄 商品详情页
- 🔄 收货地址管理
- 🔄 订单详情页

### 待开发 📋
- 📋 支付集成
- 📋 搜索功能
- 📋 商品收藏
- 📋 用户评价
- 📋 优惠券系统

## 📡 API 接口

所有接口基础 URL：`http://127.0.0.1:8000/api`

### 认证相关
- **POST** `/auth/login` - 用户登录
- **GET** `/auth/info` - 获取用户信息

### 商品相关
- **GET** `/products` - 获取商品列表
- **GET** `/products/{id}` - 获取商品详情
- **GET** `/categories` - 获取商品分类

### 购物车
- **GET** `/cart` - 获取购物车
- **POST** `/cart` - 添加到购物车
- **PUT** `/cart/{item_id}` - 更新购物车项
- **DELETE** `/cart/{item_id}` - 删除购物车项

### 订单
- **GET** `/orders` - 获取订单列表
- **POST** `/orders` - 创建订单
- **GET** `/orders/{id}` - 获取订单详情
- **PUT** `/orders/{id}` - 更新订单

详细 API 文档见 [API.md](./API.md)

## 🛠 技术栈

### 后端
- **框架**：FastAPI
- **Web 服务器**：Uvicorn
- **ORM**：SQLAlchemy
- **数据库**：SQLite
- **认证**：JWT
- **加密**：SHA256

### 前端
- **框架**：WeChat MiniProgram
- **标记语言**：WXML
- **样式**：WXSS
- **脚本**：JavaScript (ES6)
- **状态管理**：数据绑定

## 📊 数据库模型

### 用户表 (User)
```
id: 主键
phone: 手机号（唯一）
password: 密码（SHA256）
name: 用户名
avatar: 头像
created_at: 创建时间
updated_at: 更新时间
```

### 商品表 (Product)
```
id: 主键
name: 商品名称
description: 描述
price: 价格
image: 图片
category_id: 分类 ID
stock: 库存
created_at: 创建时间
```

### 订单表 (Order)
```
id: 主键
order_no: 订单号（唯一）
user_id: 用户 ID
status: 状态（pending/paid/shipped/received）
total_amount: 总金额
created_at: 创建时间
```

## 🔐 安全性

### 已实现
- ✅ JWT 令牌认证
- ✅ 密码 SHA256 加密
- ✅ CORS 跨域配置
- ✅ 请求超时保护

### 建议加强
- [ ] 使用 HTTPS
- [ ] 添加速率限制
- [ ] 实现 OTP 二次验证
- [ ] SQL 注入防护
- [ ] 敏感数据加密

## 📝 配置说明

### 环境变量 (.env)
```
# 数据库
DATABASE_URL=sqlite:///./ecommerce.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_TITLE=电商平台 API
API_VERSION=1.0.0

# 微信
WECHAT_APPID=your-appid
WECHAT_SECRET=your-secret
```

详见 [部署指南](./DEPLOY.md)

## 🐛 常见问题

### 1. 小程序无法连接后端
**解决方案**：
- 确保后端已启动：`python run.py`
- 检查后端地址：`http://127.0.0.1:8000`
- 关闭微信开发工具的域名检查

### 2. 登录失败
**解决方案**：
- 使用测试账号：`13800138000/123456`
- 检查后端日志

### 3. 页面加载超时
**解决方案**：
- 刷新页面（F5）
- 清空缓存
- 检查网络连接

### 4. 数据库错误
**解决方案**：
```bash
# 重新初始化数据库
rm ecommerce.db
python init_data.py
```

## 📚 文档链接

- [API 接口文档](./API.md)
- [部署指南](./DEPLOY.md)
- [项目总结](./PROJECT_SUMMARY.md)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

- GitHub：https://github.com/chenqian2002/ecommerce-miniprogram
- 邮箱：dev@example.com

## 📦 最终交付清单

### 已整理文档
- `README.md`：项目简介、快速启动、功能概览、接口说明
- `PROJECT_SUMMARY.md`：项目实现时间线与最终状态
- `PROJECT_LOG.md`：按天开发日志与阶段总结
- `DEPLOY.md`：本地开发、生产部署与常见问题
- `API.md`：接口说明与调试参考

### 当前项目状态
- 核心功能已完成并可演示
- 订单、地址、支付、个人中心链路已打通
- 页面文案与空态提示已统一
- 可继续扩展收藏、优惠券、评价等功能

### 建议的交付方式
1. 先启动后端并确认健康检查通过
2. 再用微信开发者工具打开小程序项目
3. 使用测试账号完成一次完整下单流程
4. 将项目日志和部署说明一并交付

### 后续维护建议
- 优先保持接口与前端字段一致
- 新增页面时同步更新 `app.json`
- 重要功能完成后及时补日志
- 发布前建议再跑一轮完整联调

---

**最后更新**：2026年4月16日

**项目状态**：🟢 可用
