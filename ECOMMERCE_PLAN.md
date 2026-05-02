# 微信小程序电商系统 - 完整可行性方案

## 📊 项目可行性评估

| 维度 | 状态 | 说明 |
|-----|------|------|
| 技术难度 | ⭐⭐⭐ 中等 | 微信小程序开发相对成熟，API 完善 |
| 预计周期 | 4-8 周 | MVP 版本 2-3 周；完整版 6-8 周 |
| 成本评估 | 低 | 无需采购额外硬件；服务器可用已有配置 |
| 可维护性 | ⭐⭐⭐⭐ 高 | 组件化设计，模块解耦 |
| 扩展性 | ⭐⭐⭐⭐ 高 | 支持快速添加功能和新页面 |
| **综合评分** | **✅ 强烈可行** | **立即启动** |

---

## 🏗️ 完整系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                      用户端（微信小程序）                      │
│  ┌──────┬──────────┬──────────┬──────────┬──────────┐        │
│  │商品  │ 购物车   │ 订单管理 │ 个人中心 │ 搜索分类 │        │
│  └───┬──┴────┬─────┴────┬─────┴────┬─────┴────┬────┘        │
└──────┼───────┼──────────┼──────────┼──────────┼─────────────┘
       │ HTTP/HTTPS (RESTful API)                 │
┌──────┼───────┼──────────┼──────────┼──────────┼─────────────┐
│      │                                         │              │
│  ┌───▼──────────────────────────────────────────┐             │
│  │          FastAPI 后端服务                     │             │
│  │ ┌──────────────────────────────────────┐    │             │
│  │ │  API 接口层 (Router)                 │    │             │
│  │ ├─ products.py      (商品接口)        │    │             │
│  │ ├─ cart.py          (购物车接口)      │    │             │
│  │ ├─ orders.py        (订单接口)        │    │             │
│  │ ├─ users.py         (用户接口)        │    │             │
│  │ ├─ payments.py      (支付接口)        │    │             │
│  │ ├─ categories.py    (分类接口)        │    │             │
│  │ └─ search.py        (搜索接口)        │    │             │
│  │ ┌──────────────────────────────────────┐    │             │
│  │ │  业务逻辑层 (Services)                │    │             │
│  │ ├─ ProductService (商品服务)          │    │             │
│  │ ├─ OrderService   (订单服务)          │    │             │
│  │ ├─ PaymentService (支付服务)          │    │             │
│  │ ├─ UserService    (用户服务)          │    │             │
│  │ └─ InventoryService (库存服务)        │    │             │
│  │ ┌──────────────────────────────────────┐    │             │
│  │ │  数据层 (Models + Database)           │    │             │
│  │ ├─ SQLAlchemy ORM                      │    │             │
│  │ ├─ 用户表、商品表、订单表等            │    │             │
│  │ └─ 事务管理                            │    │             │
│  └──────────────────────────────────────────┘    │             │
│         │                            │            │             │
│    ┌────▼──────────┐         ┌──────▼─────┐     │             │
│    │  SQLite/MySQL │         │ 缓存(Redis) │     │             │
│    │   （本地DB）   │         │ 可选优化    │     │             │
│    └────────────────┘         └────────────┘     │             │
│                                                   │             │
│  ┌─────────────────────────────────────────┐    │             │
│  │ 第三方集成                              │    │             │
│  ├─ 微信支付 SDK                          │    │             │
│  ├─ 微信登录授权                          │    │             │
│  ├─ 物流查询 API (可选)                    │    │             │
│  └─ 短信服务 (可选)                       │    │             │
│                                                   │             │
└───────────────────────────────────────────────────────────────┘
```

---

## 📱 前端架构（微信小程序）

### 页面结构
```
pages/
├─ index/                          # 首页（可选商品推荐）
│  ├─ index.wxml
│  ├─ index.js
│  ├─ index.wxss
│  └─ index.json
│
├─ login/                          # 登录页
│  ├─ login.wxml                   # 微信授权 + 账密登录
│  ├─ login.js
│  ├─ login.wxss
│  └─ login.json
│
├─ products/                       # 商品列表页（TAB 页）
│  ├─ products.wxml                # 分类筛选 + 商品列表
│  ├─ products.js                  # 搜索、分电类、排序逻辑
│  ├─ products.wxss
│  └─ products.json
│
├─ product-detail/                 # 商品详情页
│  ├─ product-detail.wxml          # 轮播图 + 描述 + 规格选择
│  ├─ product-detail.js            # 加入购物车、立即购买
│  ├─ product-detail.wxss
│  └─ product-detail.json
│
├─ cart/                           # 购物车页（TAB 页）
│  ├─ cart.wxml                    # 购物车列表 + 结算
│  ├─ cart.js                      # 删除、修改数量、计算总价
│  ├─ cart.wxss
│  └─ cart.json
│
├─ checkout/                       # 结算页
│  ├─ checkout.wxml                # 收货地址选择 + 优惠券 + 支付
│  ├─ checkout.js                  # 调用支付接口
│  ├─ checkout.wxss
│  └─ checkout.json
│
├─ orders/                         # 订单列表页（TAB 页）
│  ├─ orders.wxml                  # 订单状态 TAB (待支付/待发货/待收货/已完成)
│  ├─ orders.js                    # 订单查询、过滤
│  ├─ orders.wxss
│  └─ orders.json
│
├─ order-detail/                   # 订单详情页
│  ├─ order-detail.wxml            # 订单信息、物流、操作按钮
│  ├─ order-detail.js              # 取消订单、确认收货、评价
│  ├─ order-detail.wxss
│  └─ order-detail.json
│
├─ address/                        # 收货地址管理
│  ├─ address-list.wxml            # 地址列表
│  ├─ address-list.js
│  ├─ address-add.wxml             # 新增/编辑地址
│  ├─ address-add.js
│  ├─ address-list.wxss
│  └─ address-list.json
│
└─ profile/                        # 个人中心（TAB 页）
   ├─ profile.wxml                 # 用户信息、订单统计、地址管理、设置
   ├─ profile.js
   ├─ profile.wxss
   └─ profile.json

components/
├─ product-card/                   # 商品卡片组件
│  ├─ product-card.wxml
│  ├─ product-card.js
│  ├─ product-card.wxss
│  └─ product-card.json
│
├─ cart-item/                      # 购物车项组件
│  └─ ...
│
├─ spec-picker/                    # 规格选择器（弹窗）
│  └─ ...
│
├─ bottom-action/                  # 底部操作栏（加入购物车/立即购买）
│  └─ ...
│
└─ order-status-badge/             # 订单状态标签
   └─ ...

utils/
├─ request.js                      # HTTP 请求封装
├─ storage.js                      # 本地存储工具
├─ auth.js                         # 授权工具
├─ format.js                       # 格式化工具（日期、价格等）
└─ constants.js                    # 常量定义

styles/
├─ common.wxss                     # 全局样式
├─ colors.wxss                     # 颜色主题
└─ typography.wxss                # 排版基础

app.js                             # 全局配置
app.json                           # manifest 配置
app.wxss                           # 全局样式
project.config.json                # 项目配置
```

---

## 🛠️ 后端架构（FastAPI）

### 核心数据模型

```python
# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    openid = Column(String(100), unique=True)  # 微信 openid
    phone = Column(String(20))                 # 手机号
    nickname = Column(String(100))             # 昵称
    avatar = Column(String(500))               # 头像 URL
    password_hash = Column(String(255))        # 密码哈希
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# 商品表
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(2000))
    price = Column(Float)
    original_price = Column(Float)              # 原价（用于显示折扣）
    stock = Column(Integer)                     # 库存
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_url = Column(String(500))             # 主图
    images = Column(String(2000))               # 多张图片 (JSON 格式)
    specs = Column(String(1000))                # 规格信息 (JSON)
    sales = Column(Integer, default=0)          # 销量
    rating = Column(Float, default=5.0)         # 平均评分
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# 分类表
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    icon = Column(String(500))
    description = Column(String(500))


# 订单表
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True)  # 订单号
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(String(20))  # pending / paid / shipped / delivered / cancelled
    payment_method = Column(String(20))  # wechat_pay / alipay / balance
    address_id = Column(Integer, ForeignKey("addresses.id"))
    remark = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# 订单项表
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)  # 下单时的价格快照


# 收货地址表
class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    receiver_name = Column(String(100))
    phone = Column(String(20))
    province = Column(String(100))
    city = Column(String(100))
    district = Column(String(100))
    detail = Column(String(500))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# 购物车表（可选，也可用浏览器 localStorage）
class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### API 接口定义

```
前缀: /api/shop

【用户相关】
POST   /auth/login              登录（账密/手机号）
POST   /auth/wechat-login       微信授权登录
POST   /auth/logout             登出
GET    /users/profile           获取个人信息
POST   /users/profile           更新个人信息
POST   /users/change-password   修改密码

【商品相关】
GET    /products                获取商品列表 (带分页、搜索、分类过滤)
GET    /products/{id}           获取商品详情
GET    /categories              获取所有分类
GET    /products/search         全文搜索商品
GET    /products/recommend      推荐商品

【购物车】
GET    /cart                    获取购物车
POST   /cart/add                添加商品到购物车
PUT    /cart/{item_id}          修改购物车数量
DELETE /cart/{item_id}          删除购物车项
DELETE /cart/clear              清空购物车

【订单】
POST   /orders                  创建订单
GET    /orders                  获取订单列表 (带分页、状态过滤)
GET    /orders/{order_id}       获取订单详情
PUT    /orders/{order_id}/cancel   取消订单
PUT    /orders/{order_id}/confirm  确认收货
POST   /orders/{order_id}/review   提交评价

【支付】
POST   /payments/create         创建支付预付单（获取支付参数）
POST   /payments/notify         支付回调（微信服务器调用）
GET    /payments/{order_id}/status  查询支付状态

【地址】
GET    /addresses               获取收货地址列表
POST   /addresses               新增地址
PUT    /addresses/{id}          编辑地址
DELETE /addresses/{id}          删除地址
POST   /addresses/{id}/default  设为默认地址
```

---

## 💾 数据库设计

### SQLite/MySQL 建表语句

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    openid VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    nickname VARCHAR(100),
    avatar VARCHAR(500),
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_openid (openid)
);

-- 分类表
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(500),
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    stock INTEGER DEFAULT 0,
    category_id INTEGER,
    image_url VARCHAR(500),
    images JSON,
    specs JSON,
    sales INTEGER DEFAULT 0,
    rating DECIMAL(3, 1) DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_category (category_id),
    INDEX idx_name (name)
);

-- 用户收货地址表
CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    receiver_name VARCHAR(100),
    phone VARCHAR(20),
    province VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    detail VARCHAR(500),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    total_price DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20),
    address_id INTEGER,
    remark VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES addresses(id),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_order_number (order_number)
);

-- 订单项表
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order (order_id)
);

-- 购物车表
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- 支付记录表
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    order_id INTEGER NOT NULL,
    amount DECIMAL(10, 2),
    transaction_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order (order_id)
);
```

---

## 🔐 核心业务流程

### 1️⃣ 用户登录流程
```
小程序端                     后端服务
   │                         │
   ├─ 点击"微信授权"
   ├─ wx.login()  ────────────>  POST /auth/wechat-login
   │  (获取 code)
   │                         │
   │                    利用 code 向微信服务器
   │                    获取 openid, session_key
   │                         │
   │<──────── token,user ────│ 返回 JWT token
   │  保存到本地              │
   │  storage
   │
```

### 2️⃣ 商品浏览 → 购物车 → 支付流程
```
步骤1: 浏览商品
  GET /api/shop/products?category=1&page=1
  返回: [商品列表]

步骤2: 查看详情
  GET /api/shop/products/123
  返回: 商品详细信息、规格、库存

步骤3: 加入购物车
  POST /api/shop/cart/add
  {product_id: 123, quantity: 2}

步骤4: 进入购物车确认
  GET /api/shop/cart
  返回: 购物车列表、小计、总价

步骤5: 结算
  POST /api/shop/orders
  {
    items: [{product_id: 123, quantity: 2}],
    address_id: 5,
    remark: "请尽快发货"
  }
  返回: {order_id: 666, order_number: "20250416001"}

步骤6: 调起微信支付
  POST /api/shop/payments/create
  {order_id: 666}
  返回: {
    timeStamp: "1234567890",
    nonceStr: "abc123",
    package: "prepay_id=wx...",
    signType: "RSA",
    paySign: "signature..."
  }

步骤7: 小程序端发起支付
  wx.requestPayment({...支付参数...})

步骤8: 支付完成
  后端接收微信支付回调
  验证签名 ✓ 更新订单状态为 "paid"

步骤9: 用户查看订单
  GET /api/shop/orders/666
  返回: 订单详情、支付状态、物流信息
```

### 3️⃣ 订单状态流转
```
pending (待支付)
    ↓
    ├─ [用户支付] → paid (已支付/待发货)
    └─ [取消分] → cancelled (已取消)
              ↓
         shipped (已发货/待收货)
              ↓
         delivered (已收货)
              ↓
         completed (已完成/可评价)
```

---

## 📦 第三方集成

### 微信支付集成
```python
# app/services/payment_service.py

from wechatpay import WeChatPayV3

class PaymentService:
    def __init__(self):
        self.client = WeChatPayV3(
            mchid='你的商户号',
            private_key=open('private_key.pem').read(),
            cert_serial_no='证书序列号',
            appid='你的APPID'
        )
    
    def create_payment(self, order_id, amount):
        """创建支付预付单"""
        # 调用微信支付 API
        # 返回支付参数给前端
        pass
    
    def verify_callback(self, callback_data):
        """验证微信支付回调签名并处理"""
        pass
```

### 微信登录授权
```javascript
// utils/auth.js (小程序端)

export async function wechatLogin() {
  // 1. 获取 code
  const loginRes = await wx.login();
  const code = loginRes.code;
  
  // 2. 获取用户信息（需用户授权）
  const userInfo = await wx.getUserProfile();
  
  // 3. 后端验证 code 并返回 token
  const response = await request({
    url: '/api/shop/auth/wechat-login',
    method: 'POST',
    data: { code, userInfo }
  });
  
  // 4. 保存 token
  wx.setStorageSync('token', response.token);
  
  return response.user;
}
```

---

## 📅 开发时间规划

| 阶段 | 工作内容 | 预计时间 |
|------|---------|---------|
| **第1周** | 环境搭建、数据库设计、后端骨架 | 3-4 天 |
| **第2周** | 用户认证、商品 CRUD、购物车逻辑 | 4-5 天 |
| **第3周** | 订单系统、支付集成、前端联调 | 5-7 天 |
| **第4周** | 优化、测试、bug 修复、部署 | 3-5 天 |
| **MVP 版本** | **可上线运行** | **2-3 周** |
| **第5-8周** | 评价系统、推荐算法、后台管理(可选) | 可选 |

---

## 🔍 可行性总结

### ✅ 优势
1. **技术成熟** - 微信小程序 API 完善，FastAPI 开发效率高
2. **前期投入小** - 可用已有服务器/数据库，无需企业认证即可测试
3. **快速迭代** - 组件化设计，易于添加新功能
4. **用户基数大** - 微信生态拥有 10+ 亿用户
5. **支付便捷** - 微信支付一键接入，用户体验好

### ⚠️ 风险和约束
1. **微信审核** - 商业类小程序需要企业认证，个人开发者有限制
2. **支付权限** - 需企业资质才能开通微信支付
3. **并发处理** - 高峰期需要考虑数据库和服务器性能优化
4. **库存管理** - 秒杀场景需要分布式锁防止超卖
5. **隐私合规** - 需符合《个人信息保护法》相关规定

### 💡 建议
- **第1步** 用个人开发者账号搭建完整技术栈
- **第2步** 准备好企业资质后，申请商业权限和微信支付
- **第3步** 从 MVP 版本（商品展示 + 订单）开始上线
- **第4步** 逐步加入支付、发货等高级功能

---

## 🚀 立即启动建议

希望你现在启动以下工作：

1. **后端框架** - 基于已有 `claude_web_agent_py` 扩展
2. **数据库** - 建表并初始化测试数据
3. **前端骨架** - 创建各页面的 wxml/js 框架
4. **API 联调** - 实现用户登录 + 商品查询的完整链路

需要我帮你生成代码框架吗？
