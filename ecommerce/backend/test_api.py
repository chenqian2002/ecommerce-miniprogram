import requests
import json

BASE = "http://127.0.0.1:8000/api"

def test(name, method, url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{url}", headers=headers, timeout=10)
        elif method == "PUT":
            r = requests.put(f"{BASE}{url}", headers=headers, json=data, timeout=10)
        else:
            r = requests.post(f"{BASE}{url}", headers=headers, json=data, timeout=10)
        print(f"[{r.status_code}] {name}")
        try:
            body = r.json()
            # truncate long output
            s = json.dumps(body, ensure_ascii=False)
            if len(s) > 300:
                s = s[:300] + "..."
            print(f"  {s}")
        except:
            print(f"  {r.text[:200]}")
        return r
    except Exception as e:
        print(f"[ERR] {name}: {e}")
        return None

print("=== 1. 健康检查 ===")
test("health", "GET", "")

print("\n=== 2. 买家登录 13800138001 ===")
r1 = test("buyer_login", "POST", "/auth/login", {"phone": "13800138001", "password": "123456"})
buyer_token = r1.json().get("token") if r1 and r1.status_code == 200 else None

print("\n=== 3. 商家登录 13859631156 ===")
r2 = test("merchant_login", "POST", "/auth/login", {"phone": "13859631156", "password": "123456"})
merchant_token = r2.json().get("token") if r2 and r2.status_code == 200 else None

print("\n=== 4. 商品列表 ===")
test("products", "GET", "/products")

print("\n=== 5. 分类列表 ===")
test("categories", "GET", "/categories")

if buyer_token:
    print("\n=== 6. 买家添加地址 ===")
    test("add_address", "POST", "/addresses", {
        "receiver_name": "测试收货人",
        "phone": "13800138001",
        "province": "福建省",
        "city": "漳州市",
        "district": "龙文区",
        "detail": "测试地址123号"
    }, buyer_token)

    print("\n=== 7. 买家获取地址列表 ===")
    test("addresses", "GET", "/addresses", token=buyer_token)

    print("\n=== 8. 买家添加购物车 ===")
    # Get product list first to get a valid product_id
    rp = requests.get(f"{BASE}/products", timeout=10)
    products = rp.json()
    if products and len(products) > 0:
        pid = products[0]["id"]
        test("add_cart", "POST", "/cart/add", {"product_id": pid, "quantity": 2}, buyer_token)
        print("\n=== 9. 买家购物车 ===")
        test("cart", "GET", "/cart", token=buyer_token)

        print("\n=== 10. 获取地址（下单用）===")
        ra = requests.get(f"{BASE}/addresses", headers={"Authorization": f"Bearer {buyer_token}"}, timeout=10)
        addrs = ra.json()
        addr_list = addrs.get("data", addrs) if isinstance(addrs, dict) else addrs
        if addr_list and len(addr_list) > 0:
            addr_id = addr_list[0]["id"]
            print(f"  Using address_id={addr_id}")

            print("\n=== 11. 买家下单 ===")
            r_order = test("create_order", "POST", "/orders", {
                "address_id": addr_id,
                "payment_method": "mock",
                "cart_items": [{"product_id": pid, "quantity": 1}]
            }, buyer_token)

            if r_order and r_order.status_code == 200:
                order_id = r_order.json().get("order_id")
                print(f"  Order ID: {order_id}")

                print("\n=== 12. 模拟支付 ===")
                r_pay = requests.put(f"{BASE}/orders/{order_id}/pay", headers={"Authorization": f"Bearer {buyer_token}", "Content-Type": "application/json"}, timeout=10)
                print(f"[{r_pay.status_code}] pay_order")
                print(f"  {r_pay.text[:300]}")

                print("\n=== 13. 订单详情 ===")
                test("order_detail", "GET", f"/orders/{order_id}", token=buyer_token)

                print("\n=== 14. 订单列表 ===")
                test("orders", "GET", "/orders", token=buyer_token)

if merchant_token:
    print("\n=== 15. 商家订单列表 ===")
    test("merchant_orders", "GET", "/merchant/orders", token=merchant_token)

print("\n=== ALL TESTS DONE ===")