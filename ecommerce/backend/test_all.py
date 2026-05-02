# -*- coding: utf-8 -*-
"""电商小程序全部功能测试"""
import requests
import json

BASE = "http://127.0.0.1:8000/api"
RESULTS = []

def test(name, method, url, data=None, token=None, expect_status=200):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{url}", headers=headers, timeout=10)
        elif method == "PUT":
            r = requests.put(f"{BASE}{url}", headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            r = requests.delete(f"{BASE}{url}", headers=headers, timeout=10)
        else:
            r = requests.post(f"{BASE}{url}", headers=headers, json=data, timeout=10)
        
        status = "✅" if r.status_code == expect_status else "❌"
        if r.status_code != expect_status:
            status = f"❌ (期望{expect_status}，实际{r.status_code})"
        
        body = {}
        try:
            body = r.json()
        except:
            body = r.text[:200]
        
        RESULTS.append({"name": name, "status": r.status_code, "ok": r.status_code == expect_status})
        print(f"  {status} {name} [{r.status_code}]")
        
        # 截断输出
        s = json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else str(body)
        if len(s) > 200:
            s = s[:200] + "..."
        print(f"      {s}")
        return r
    except Exception as e:
        RESULTS.append({"name": name, "status": "ERR", "ok": False})
        print(f"  ❌ {name} [ERR] {e}")
        return None

print("=" * 60)
print("电商小程序全功能测试")
print("=" * 60)

# ===== 1. 健康检查 =====
print("\n【1. 系统检查】")
test("健康检查", "GET", "/../health", expect_status=200)

# ===== 2. 认证 =====
print("\n【2. 认证功能】")
r_buyer = test("买家登录(13800138001)", "POST", "/auth/login", {"phone": "13800138001", "password": "123456"})
buyer_token = r_buyer.json().get("token") if r_buyer and r_buyer.status_code == 200 else None

r_merchant = test("商家登录(13859631156)", "POST", "/auth/login", {"phone": "13859631156", "password": "123456"})
merchant_token = r_merchant.json().get("token") if r_merchant and r_merchant.status_code == 200 else None

test("微信登录(test_code)", "POST", "/auth/wechat-login", {"code": "test_code", "userInfo": {"nickName": "测试用户"}})

test("错误密码登录", "POST", "/auth/login", {"phone": "13800138001", "password": "wrong"}, expect_status=401)

# ===== 3. 首页 =====
print("\n【3. 首页】")
test("首页数据", "GET", "/home")
test("公告列表", "GET", "/announcement")
test("公共设置", "GET", "/settings/public")

# ===== 4. 商品 =====
print("\n【4. 商品功能】")
r_products = test("商品列表", "GET", "/products")
test("分类列表", "GET", "/categories")
test("商品搜索", "GET", "/products?keyword=咖啡")
test("分类筛选", "GET", "/products?category_id=1")
test("销量排序", "GET", "/products?sort_by=sales")

# ===== 5. 用户信息 =====
print("\n【5. 用户信息】")
if buyer_token:
    test("获取个人信息", "GET", "/users/profile", token=buyer_token)
    test("更新昵称", "POST", "/users/profile", {"nickname": "测试买家昵称"}, buyer_token)

# ===== 6. 地址管理 =====
print("\n【6. 地址管理】")
if buyer_token:
    test("地址列表", "GET", "/addresses", token=buyer_token)
    r_addr = test("新增地址", "POST", "/addresses", {
        "receiver_name": "测试收货人", "phone": "13900001111",
        "province": "福建省", "city": "厦门市", "district": "思明区",
        "detail": "测试路100号"
    }, buyer_token)
    addr_id = r_addr.json().get("data", {}).get("id") if r_addr and r_addr.status_code == 200 else None
    if addr_id:
        test("修改地址", "PUT", f"/addresses/{addr_id}", {
            "receiver_name": "修改后收货人", "phone": "13900002222",
            "province": "福建省", "city": "福州市", "district": "鼓楼区",
            "detail": "修改后地址"
        }, buyer_token)
        test("设为默认", "POST", f"/addresses/{addr_id}/default", None, buyer_token)

# ===== 7. 购物车 =====
print("\n【7. 购物车功能】")
if buyer_token and r_products:
    products = r_products.json()
    pid1 = products[0]["id"] if products else None
    pid2 = products[1]["id"] if len(products) > 1 else None

    if pid1:
        test("添加购物车", "POST", "/cart/add", {"product_id": pid1, "quantity": 1}, buyer_token)
    if pid2:
        test("添加购物车(另一商品)", "POST", "/cart/add", {"product_id": pid2, "quantity": 2}, buyer_token)
    test("查询购物车", "GET", "/cart", token=buyer_token)

# ===== 8. 下单 =====
print("\n【8. 下单功能】")
if buyer_token and addr_id and pid1:
    r_order = test("创建订单", "POST", "/orders", {
        "address_id": addr_id, "payment_method": "mock",
        "cart_items": [{"product_id": pid1, "quantity": 1}]
    }, buyer_token)
    order_id = r_order.json().get("order_id") if r_order and r_order.status_code == 200 else None
    
    if order_id:
        test("订单详情", "GET", f"/orders/{order_id}", token=buyer_token)
        test("支付订单", "PUT", f"/orders/{order_id}/pay", token=buyer_token)
        test("确认支付后状态", "GET", f"/orders/{order_id}", token=buyer_token)
        
        # 模拟发货
        if merchant_token:
            test("商家发货", "PUT", f"/merchant/orders/{order_id}/ship", None, merchant_token)
        
        test("确认收货", "PUT", f"/orders/{order_id}/confirm", token=buyer_token)
        
        test("取消订单(新订单)", "POST", "/orders", {
            "address_id": addr_id, "payment_method": "mock",
            "cart_items": [{"product_id": pid1, "quantity": 1}]
        }, buyer_token)

test("订单列表", "GET", "/orders", token=buyer_token)

# ===== 9. 商家功能 =====
print("\n【9. 商家功能】")
if merchant_token:
    test("商家订单列表", "GET", "/merchant/orders", token=merchant_token)
    test("商家设置", "GET", "/merchant/settings", token=merchant_token)
    test("公告管理", "POST", "/announcement", {
        "title": "测试公告", "content": "这是一条测试公告内容", "is_active": True
    }, merchant_token)

# ===== 10. 图片上传 =====
print("\n【10. 图片上传】")
if merchant_token:
    import struct, zlib
    sig = b'\x89PNG\r\n\x1a\n'
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw = zlib.compress(b'\x00\xff\x00\x00')
    png_data = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', raw) + chunk(b'IEND', b'')
    
    r_upload = requests.post(f"{BASE}/upload/image",
        headers={"Authorization": f"Bearer {merchant_token}"},
        files={"file": ("test.png", png_data, "image/png")},
        timeout=15
    )
    upload_ok = "✅" if r_upload.status_code == 200 else "❌"
    print(f"  {upload_ok} 上传图片 [{r_upload.status_code}]")
    RESULTS.append({"name": "上传图片", "status": r_upload.status_code, "ok": r_upload.status_code == 200})
    if r_upload.status_code == 200:
        img_url = f"http://127.0.0.1:8000{r_upload.json().get('url', '')}"
        r_verify = requests.get(img_url, timeout=10)
        v_ok = "✅" if r_verify.status_code == 200 else "❌"
        print(f"  {v_ok} 访问上传图片 [{r_verify.status_code}]")
        RESULTS.append({"name": "访问上传图片", "status": r_verify.status_code, "ok": r_verify.status_code == 200})

# ===== 结果汇总 =====
print("\n" + "=" * 60)
total = len(RESULTS)
passed = sum(1 for r in RESULTS if r["ok"])
failed = total - passed
print(f"测试结果: {passed}/{total} 通过, {failed} 失败")
if failed == 0:
    print("🎉 全部测试通过！")
else:
    print("⚠️ 失败项：")
    for r in RESULTS:
        if not r["ok"]:
            print(f"  - {r['name']} (状态码: {r['status']})")
print("=" * 60)