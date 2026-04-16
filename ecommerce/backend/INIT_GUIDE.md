# 🎓 数据库初始化脚本详解 - 为什么这样做？

## 📚 核心概念

### 问题 1: 数据库是空的

当你新建项目时：

```
你的项目
  ├─ 代码 ✅ (已经完成)
  ├─ 数据库表结构 ✅ (models.py 定义好了)
  └─ 数据库中的数据 ❌ (什么都没有！)
```

**结果**：
- API 能调用，但查不到任何东西
- 登录失败（没有用户）
- 商品列表为空
- 无法测试任何功能

---

### 解决方案：创建初始化脚本

```
脚本运行流程：

1️⃣  创建数据库表  (Base.metadata.create_all)
    ↓
2️⃣  插入分类数据    (categories = [...])
    ↓
3️⃣  插入商品数据    (products = [...])
    ↓
4️⃣  插入用户数据    (users = [...])
    ↓
5️⃣  插入地址数据    (addresses = [...])
    ↓
✅ 数据库已准备就绪！
```

---

## 🔍 代码讲解

### Part 1: 创建表

```python
def init_database():
    """初始化数据库 - 创建表"""
    Base.metadata.create_all(bind=engine)
```

**为什么？**

你在 `models.py` 中定义了数据库表的**"蓝图"**：

```python
class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    price = Column(Float)
    ...
```

但这只是**定义**，你还需要**真的去创建**这些表。

```
类比：
┌─────────────────────┐
│ 建筑师设计图 (模型)  │
│                     │
│ import Base...      │
│ class ProductModel..│
├─────────────────────┤
    ↓ Base.metadata.create_all()
┌─────────────────────┐
│ 真的建造出房子 (表)  │
│                     │
│ CREATE TABLE...     │
└─────────────────────┘
```

---

### Part 2: 插入测试数据

#### 为什么需要测试数据？

```python
products = [
    ProductModel(
        name="iPhone 15 Pro",      # 数据
        price=8999.00,
        stock=50,
        ...
    ),
    ProductModel(...),
    ProductModel(...),
]

for product in products:
    db.add(product)
db.commit()
```

**场景 1：没有测试数据**

```
你调用 API:
  GET /api/shop/products
  
返回结果：
  {
    "data": []  # 空的！
  }

你无法测试：
❌ 商品列表显示是否正确
❌ 商品搜索、排序是否工作
❌ 前端页面布局是否正常
```

**场景 2：有测试数据**

```
你调用 API:
  GET /api/shop/products
  
返回结果：
  {
    "data": [
      {"id": 1, "name": "iPhone 15 Pro", "price": 8999.00},
      {"id": 2, "name": "MacBook Pro", "price": 18999.00},
      ...
    ]
  }

你能测试：
✅ 商品是否正常显示
✅ 搜索功能是否工作
✅ 前端界面是否美观
```

---

### Part 3: 测试账号

```python
UserModel(
    phone="13800138000",
    nickname="张三",
    password_hash=hash_password("123456")  # 密码加密
)
```

**为什么需要？**

```
场景：你要测试登录功能

没有测试账号：
❌ 无法测试登录是否工作
❌ 无法获取 token
❌ 无法调用其他受保护的 API

有测试账号 (13800138000 / 123456)：
✅ 能登录
✅ 能获取 token
✅ 能测试所有需要认证的功能
```

---

## 🎯 初始化脚本的工作流

```
用户运行: python init_data.py
            ↓
        1. 创建表
            ↓
           执行 SQL:
           CREATE TABLE users (...)
           CREATE TABLE products (...)
           CREATE TABLE orders (...)
            ↓
        2. 插入分类
            ↓
           执行 SQL:
           INSERT INTO categories ...
            ↓
        3. 插入商品
            ↓
           执行 SQL:
           INSERT INTO products ...
           (12 条商品数据)
            ↓
        4. 插入用户
            ↓
           执行 SQL:
           INSERT INTO users ...
           (验证账号密码正确)
            ↓
        5. 插入地址
            ↓
           执行 SQL:
           INSERT INTO addresses ...
            ↓
        ✅ 完成！
            ↓
        数据库现状：
        ├─ users 表 (3条测试用户)
        ├─ categories 表 (5个分类)
        ├─ products 表 (12件商品)
        └─ addresses 表 (2个测试地址)
```

---

## 🔐 密码为什么要加密？

### 坏做法：存明文密码
```python
user.password = "123456"  # ❌ 直接存

# 如果数据库被黑：
# 黑客直接看到所有用户的明文密码
# 用户账号完全暴露！
```

### 好做法：存加密密码
```python
user.password_hash = hash_password("123456")
# password_hash = "8d969eef6ecad3c29a3a873fba8cac1fc8..."

# 如果数据库被黑：
# 黑客只看到 hash 值
# 无法直接反推出原密码
# 需要用暴力破解（很困难）
```

### 登录验证流程
```
用户输入: "123456"
            ↓
        对其进行 hash 加密
            ↓
        hash("123456") = "8d969eef..."
            ↓
        对比数据库中的值
            ↓
        是否相等？
        ├─ 是 → ✅ 登录成功
        └─ 否 → ❌ 密码错误
```

---

## 📊 数据库初始化后的状态

### 表结构

```sql
-- 创建的表
1. users (用户表)
   ├─ id: 1, 2, 3
   ├─ phone: 13800138000, 13800138001
   ├─ nickname: 张三, 李四
   └─ password_hash: 加密的密码

2. categories (分类表)
   ├─ id: 1, 2, 3, 4, 5
   ├─ name: 电子产品, 服装鞋帽, 图书音像...
   └─ ...

3. products (商品表)
   ├─ id: 1-12
   ├─ name: iPhone 15 Pro, MacBook Pro...
   ├─ price: 8999.00, 18999.00...
   ├─ stock: 50, 30, 100...
   └─ category_id: 1, 1, 2...

4. addresses (地址表)
   ├─ id: 1, 2
   ├─ user_id: 1, 2
   ├─ receiver_name: 张三, 李四
   └─ ...
```

---

## ✅ 现在你可以做什么

### 1️⃣ 运行后端服务

```bash
python run.py
```

访问：http://127.0.0.1:8000/docs

### 2️⃣ 测试登录 API

```
POST /api/shop/auth/login

请求：
{
  "phone": "13800138000",
  "password": "123456"
}

返回：
{
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "phone": "13800138000",
    "nickname": "张三"
  }
}
```

### 3️⃣ 测试商品列表 API

```
GET /api/shop/products?page=1&page_size=10

返回：
[
  {
    "id": 1,
    "name": "iPhone 15 Pro",
    "price": 8999.00,
    "stock": 50,
    "sales": 3500
  },
  ...
]
```

### 4️⃣ 在小程序中测试

用账号 **13800138000** 和密码 **123456** 登录小程序

---

## 🚀 完整流程

```
你现在的状态：

项目创建 ✅
  ├─ 代码已写好
  ├─ 表结构已定义
  ├─ API 接口已编写
  └─ 都已就绪

    ↓ 初始化脚本 (python init_data.py)

    ✅ 数据库创建
    ✅ 测试数据导入
    ✅ 可以开始测试了！

    ↓ 启动后端 (python run.py)

    ✅ API 服务运行
    ✅ 可以调用接口
    ✅ 可以联调前端

    ↓ 打开小程序

    ✅ 可以登录
    ✅ 可以浏览商品
    ✅ 可以加入购物车
    ✅ 完整的电商流程！
```

---

## 📝 总结

| 问题 | 解决方案 | 为什么 |
|------|---------|-------|
| 数据库表为空 | 运行 `Base.metadata.create_all()` | 需要"建造"表 |
| 没有测试数据 | 插入初始商品、用户、分类 | 否则 API 返回空列表 |
| 无法测试登录 | 创建测试账号 | 需要真实用户来验证登录功能 |
| 无法测试订单 | 创建测试地址数据 | 下单需要收货地址 |
| 密码泄露风险 | 使用 hash_password 加密 | 安全编程最佳实践 |

**核心：初始化脚本是开发调试的必要步骤！** 🎯
