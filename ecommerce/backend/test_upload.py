import requests
import os

BASE = "http://127.0.0.1:8000/api"

# 先登录获取 token
print("=== 登录 ===")
r = requests.post(f"{BASE}/auth/login", json={"phone": "13859631156", "password": "123456"}, timeout=10)
token = r.json().get("token")
print(f"Status: {r.status_code}, Token: {token[:30]}...")

if not token:
    print("登录失败，无法测试上传")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 创建一个测试图片 (1x1 红色 PNG)
import struct, zlib

def create_test_png():
    # 最小 PNG: 1x1 红色像素
    sig = b'\x89PNG\r\n\x1a\n'
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    
    ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw = zlib.compress(b'\x00\xff\x00\x00')
    
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', raw) + chunk(b'IEND', b'')

png_data = create_test_png()
test_file = os.path.join(os.path.dirname(__file__), 'test_image.png')
with open(test_file, 'wb') as f:
    f.write(png_data)

print("\n=== 测试上传图片 ===")
with open(test_file, 'rb') as f:
    r2 = requests.post(
        f"{BASE}/upload/image",
        headers=headers,
        files={"file": ("test.png", f, "image/png")},
        timeout=15
    )
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:500]}")

if r2.status_code == 200:
    data = r2.json()
    img_url = data.get("url", "")
    full_url = f"http://127.0.0.1:8000{img_url}"
    print(f"\n图片URL: {full_url}")

    # 验证图片可访问
    r3 = requests.get(full_url, timeout=10)
    print(f"图片访问: Status={r3.status_code}, Content-Type={r3.headers.get('content-type', 'N/A')}")

    # 测试用上传的图片更新商品
    print("\n=== 更新商品图片 ===")
    rp = requests.get(f"{BASE}/products", timeout=10)
    products = rp.json()
    if products:
        pid = products[0]["id"]
        r4 = requests.put(
            f"{BASE}/products/{pid}",
            headers={**headers, "Content-Type": "application/json"},
            json={"image_url": full_url},
            timeout=10
        )
        print(f"更新商品 {pid}: Status={r4.status_code}")
        print(f"Response: {r3.text[:300]}")

# 清理测试文件
os.remove(test_file)
print("\n=== 测试完成 ===")