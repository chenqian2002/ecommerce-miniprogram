# API 文档

## 基础信息

- **基础 URL**：`http://127.0.0.1:8000/api`
- **响应格式**：JSON
- **认证方式**：JWT Bearer Token

## 请求头

```
Content-Type: application/json
Authorization: Bearer {token}
```

## 响应格式

### 成功响应 (200, 201)
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 错误响应 (400, 401, 500)
```json
{
  "code": 1,
  "message": "error description",
  "errors": []
}
```

---

## 认证相关 (Auth)

### 1. 用户登录

**请求**
```
POST /auth/login
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "123456"
}
```

**成功响应** (200)
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "phone": "13800138000",
    "name": "用户1",
    "avatar": "https://...",
    "created_at": "2026-04-16T10:00:00"
  }
}
```

**错误响应** (401)
```json
{
  "message": "账号或密码错误"
}
```

### 2. 获取用户信息

**请求**
```
GET /auth/info
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "id": 1,
  "phone": "13800138000",
  "name": "用户1",
  "avatar": "https://...",
  "created_at": "2026-04-16T10:00:00"
}
```

---

## 商品相关 (Products)

### 3. 获取商品列表

**请求**
```
GET /products?page=1&limit=10&category_id=1
```

**参数**
| 参数 | 类型 | 说明 |
|-----|------|------|
| page | int | 页码（默认 1） |
| limit | int | 每页数量（默认 10） |
| category_id | int | 分类 ID（可选） |
| search | string | 搜索关键词（可选） |

**成功响应** (200)
```json
{
  "data": [
    {
      "id": 1,
      "name": "汉堡包",
      "description": "美味的汉堡包",
      "price": 15.99,
      "image": "https://...",
      "category_id": 1,
      "stock": 100,
      "created_at": "2026-04-16"
    }
  ],
  "total": 12,
  "page": 1,
  "limit": 10
}
```

### 4. 获取商品详情

**请求**
```
GET /products/{id}
```

**URL 参数**
| 参数 | 类型 | 说明 |
|-----|------|------|
| id | int | 商品 ID |

**成功响应** (200)
```json
{
  "id": 1,
  "name": "汉堡包",
  "description": "美味的汉堡包，使用新鲜食材",
  "price": 15.99,
  "image": "https://...",
  "category_id": 1,
  "stock": 100,
  "rating": 4.5,
  "reviews_count": 156,
  "created_at": "2026-04-16"
}
```

### 5. 获取分类列表

**请求**
```
GET /categories
```

**成功响应** (200)
```json
{
  "data": [
    {
      "id": 1,
      "name": "汉堡",
      "description": "各式汉堡"
    },
    {
      "id": 2,
      "name": "炸鸡",
      "description": "炸鸡系列"
    }
  ]
}
```

---

## 购物车 (Cart)

### 6. 获取购物车

**请求**
```
GET /cart
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "name": "汉堡包",
      "price": 15.99,
      "quantity": 2,
      "subtotal": 31.98,
      "created_at": "2026-04-16"
    }
  ],
  "total": 31.98,
  "count": 2
}
```

### 7. 添加到购物车

**请求**
```
POST /cart
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 1
}
```

**成功响应** (201)
```json
{
  "message": "添加成功",
  "data": {
    "id": 1,
    "product_id": 1,
    "quantity": 1
  }
}
```

### 8. 更新购物车项

**请求**
```
PUT /cart/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 3
}
```

**成功响应** (200)
```json
{
  "message": "更新成功",
  "data": {
    "id": 1,
    "quantity": 3
  }
}
```

### 9. 删除购物车项

**请求**
```
DELETE /cart/{item_id}
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "message": "删除成功"
}
```

### 10. 清空购物车

**请求**
```
DELETE /cart
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "message": "购物车已清空"
}
```

---

## 订单 (Orders)

### 11. 获取订单列表

**请求**
```
GET /orders?status=all&page=1
Authorization: Bearer {token}
```

**参数**
| 参数 | 类型 | 说明 |
|-----|------|------|
| status | string | 状态：all/pending/paid/shipped/received |
| page | int | 页码（默认 1） |
| limit | int | 每页数量（默认 10） |

**成功响应** (200)
```json
{
  "data": [
    {
      "id": 1,
      "order_no": "ORD20260416001",
      "status": "pending",
      "status_text": "待付款",
      "total_amount": 31.98,
      "items_count": 2,
      "created_at": "2026-04-16"
    }
  ],
  "total": 5,
  "page": 1
}
```

### 12. 创建订单

**请求**
```
POST /orders
Authorization: Bearer {token}
Content-Type: application/json

{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "address_id": 1,
  "remarks": "请尽快发货"
}
```

**成功响应** (201)
```json
{
  "message": "订单创建成功",
  "data": {
    "id": 1,
    "order_no": "ORD20260416001",
    "status": "pending",
    "total_amount": 31.98
  }
}
```

### 13. 获取订单详情

**请求**
```
GET /orders/{id}
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "id": 1,
  "order_no": "ORD20260416001",
  "status": "pending",
  "total_amount": 31.98,
  "items": [
    {
      "product_id": 1,
      "name": "汉堡包",
      "price": 15.99,
      "quantity": 2
    }
  ],
  "address": {
    "id": 1,
    "city": "北京",
    "detail": "朝阳区"
  },
  "created_at": "2026-04-16",
  "updated_at": "2026-04-16"
}
```

### 14. 取消订单

**请求**
```
PUT /orders/{id}/cancel
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "message": "订单已取消"
}
```

---

## 地址 (Addresses)

### 15. 获取地址列表

**请求**
```
GET /addresses
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "data": [
    {
      "id": 1,
      "name": "李四",
      "phone": "13900000000",
      "province": "北京",
      "city": "北京",
      "district": "朝阳区",
                  "detail": "",
      "is_default": true
    }
  ]
}
```

### 16. 创建地址

**请求**
```
POST /addresses
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "李四",
  "phone": "13900000000",
  "province": "北京",
  "city": "北京",
  "district": "朝阳区",
  "detail": "",
  "is_default": false
}
```

**成功响应** (201)
```json
{
  "message": "地址添加成功",
  "data": {
    "id": 1,
    "name": "李四"
  }
}
```

### 17. 更新地址

**请求**
```
PUT /addresses/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "李四",
  "phone": "13900000000",
  "detail": "新地址"
}
```

**成功响应** (200)
```json
{
  "message": "地址更新成功"
}
```

### 18. 删除地址

**请求**
```
DELETE /addresses/{id}
Authorization: Bearer {token}
```

**成功响应** (200)
```json
{
  "message": "地址已删除"
}
```

---

## 错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| 1001 | 400 | 参数验证失败 |
| 1002 | 401 | 未授权 / Token 无效 |
| 1003 | 401 | Token 已过期 |
| 1004 | 403 | 权限不足 |
| 1005 | 404 | 资源不存在 |
| 1006 | 409 | 冲突（如重复添加） |
| 1007 | 500 | 服务器错误 |
| 2001 | 400 | 账号或密码错误 |
| 2002 | 400 | 账号已存在 |
| 3001 | 400 | 商品库存不足 |
| 3002 | 400 | 购物车为空 |
| 4001 | 400 | 订单不存在 |
| 4002 | 400 | 订单状态异常 |

---

## 测试工具

### 使用 curl 测试
```bash
# 登录
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"123456"}'

# 获取商品列表
curl -X GET http://127.0.0.1:8000/api/products
```

### 使用 Postman
1. 导入 API 文档
2. 设置环境变量：`base_url=http://127.0.0.1:8000/api`
3. 根据需要调用各个接口

### 查看 Swagger UI
访问：`http://127.0.0.1:8000/docs`

---

**最后更新**：2026年4月16日
