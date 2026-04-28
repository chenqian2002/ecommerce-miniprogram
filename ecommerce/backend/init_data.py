"""
数据库初始化脚本

这个脚本的作用：
1. 创建所有数据库表
2. 插入初始测试数据
3. 让你能够本地调试 API

使用方法：
    python init_data.py

这样数据库就会被初始化，你可以开始测试了！
"""

from app.database.database import SessionLocal, engine, Base
from app.database.models import (
    UserModel, CategoryModel, ProductModel, 
    AddressModel, OrderModel, OrderItemModel
)
from app.core.security import hash_password
from datetime import datetime, timedelta
import json

def init_database():
    """初始化数据库 - 创建表"""
    print("📦 正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成！")

def add_categories(db):
    """添加商品分类"""
    print("\n📦 正在添加商品分类...")
    
    categories = [
        CategoryModel(
            name="电子产品",
            icon="📱",
            description="手机、电脑、平板等高科技产品"
        ),
        CategoryModel(
            name="服装鞋帽",
            icon="👕",
            description="衣服、鞋子、帽子、包包"
        ),
        CategoryModel(
            name="图书音像",
            icon="📚",
            description="书籍、杂志、音乐、电影"
        ),
        CategoryModel(
            name="食品酒水",
            icon="🍔",
            description="零食、饮料、酒类"
        ),
        CategoryModel(
            name="家居用品",
            icon="🏠",
            description="家具、装饰、日用品"
        ),
    ]
    
    for category in categories:
        # 避免重复插入
        existing = db.query(CategoryModel).filter(
            CategoryModel.name == category.name
        ).first()
        if not existing:
            db.add(category)
    
    db.commit()
    print(f"✅ 添加了 {len(categories)} 个分类")

def add_products(db):
    """添加商品"""
    print("\n📦 正在添加商品...")
    
    # 先获取分类
    categories = db.query(CategoryModel).all()
    if not categories:
        print("❌ 请先添加分类！")
        return
    
    products = [
        # 电子产品
        ProductModel(
            name="iPhone 15 Pro",
            description="最新款苹果手机，搭载 A17 Pro 芯片",
            price=8999.00,
            original_price=9999.00,
            stock=50,
            category_id=categories[0].id,
            image_url="https://via.placeholder.com/300x300?text=iPhone+15+Pro",
            images=json.dumps([
                "https://via.placeholder.com/300x300?text=iPhone+15+Pro+1",
                "https://via.placeholder.com/300x300?text=iPhone+15+Pro+2",
                "https://via.placeholder.com/300x300?text=iPhone+15+Pro+3",
            ]),
            specs=json.dumps({
                "颜色": ["深空黑", "银色", "金色"],
                "容量": ["128GB", "256GB", "512GB"],
                "屏幕": "6.1英寸"
            }),
            sales=3500,
            rating=4.8
        ),
        ProductModel(
            name="MacBook Pro 16",
            description="专业级笔记本电脑，M3 Pro 芯片",
            price=18999.00,
            original_price=19999.00,
            stock=30,
            category_id=categories[0].id,
            image_url="https://via.placeholder.com/300x300?text=MacBook+Pro",
            images=json.dumps([]),
            specs=json.dumps({"屏幕": "16英寸", "内存": "16GB"}),
            sales=1200,
            rating=4.9
        ),
        ProductModel(
            name="iPad Air",
            description="轻薄高效的平板电脑",
            price=5499.00,
            original_price=6499.00,
            stock=100,
            category_id=categories[0].id,
            image_url="https://via.placeholder.com/300x300?text=iPad+Air",
            images=json.dumps([]),
            specs=json.dumps({"屏幕": "11英寸"}),
            sales=2000,
            rating=4.7
        ),
        
        # 服装鞋帽
        ProductModel(
            name="运动T恤",
            description="透气舒适的运动T恤",
            price=99.00,
            original_price=199.00,
            stock=500,
            category_id=categories[1].id,
            image_url="https://via.placeholder.com/300x300?text=T-Shirt",
            images=json.dumps([]),
            specs=json.dumps({"尺码": ["S", "M", "L", "XL"], "颜色": ["黑", "白", "蓝"]}),
            sales=5000,
            rating=4.5
        ),
        ProductModel(
            name="休闲裤",
            description="舒适百搭的休闲裤",
            price=159.00,
            original_price=299.00,
            stock=300,
            category_id=categories[1].id,
            image_url="https://via.placeholder.com/300x300?text=Jeans",
            images=json.dumps([]),
            specs=json.dumps({"尺码": ["28", "30", "32", "34"]}),
            sales=3500,
            rating=4.6
        ),
        ProductModel(
            name="运动鞋",
            description="专业运动鞋，减震舒适",
            price=599.00,
            original_price=999.00,
            stock=200,
            category_id=categories[1].id,
            image_url="https://via.placeholder.com/300x300?text=Sneaker",
            images=json.dumps([]),
            specs=json.dumps({"尺码": ["35", "36", "37", "38", "39", "40", "41", "42", "43"]}),
            sales=4200,
            rating=4.7
        ),
        
        # 图书音像
        ProductModel(
            name="Python 从入门到精通",
            description="零基础学 Python 编程的最佳读物",
            price=89.00,
            original_price=129.00,
            stock=150,
            category_id=categories[2].id,
            image_url="https://via.placeholder.com/300x300?text=Python+Book",
            images=json.dumps([]),
            specs=json.dumps({"作者": "张三", "页数": "500"}),
            sales=2000,
            rating=4.8
        ),
        ProductModel(
            name="深入浅出数据结构",
            description="专业讲解各种数据结构和算法",
            price=79.00,
            original_price=119.00,
            stock=200,
            category_id=categories[2].id,
            image_url="https://via.placeholder.com/300x300?text=Data+Structure",
            images=json.dumps([]),
            specs=json.dumps({"作者": "李四", "页数": "600"}),
            sales=1800,
            rating=4.9
        ),
        
        # 食品酒水
        ProductModel(
            name="精选咖啡豆 500g",
            description="进口精选咖啡豆，香味浓郁",
            price=89.00,
            original_price=129.00,
            stock=300,
            category_id=categories[3].id,
            image_url="https://via.placeholder.com/300x300?text=Coffee",
            images=json.dumps([]),
            specs=json.dumps({"产地": "埃塞俄比亚", "烘焙": "中度"}),
            sales=2500,
            rating=4.6
        ),
        ProductModel(
            name="进口葡萄酒",
            description="法国红酒，口感醇厚",
            price=199.00,
            original_price=299.00,
            stock=100,
            category_id=categories[3].id,
            image_url="https://via.placeholder.com/300x300?text=Wine",
            images=json.dumps([]),
            specs=json.dumps({"产地": "法国", "年份": "2020"}),
            sales=800,
            rating=4.7
        ),
        
        # 家居用品
        ProductModel(
            name="LED 台灯",
            description="护眼台灯，三档亮度",
            price=129.00,
            original_price=199.00,
            stock=250,
            category_id=categories[4].id,
            image_url="https://via.placeholder.com/300x300?text=Lamp",
            images=json.dumps([]),
            specs=json.dumps({"功率": "12W", "亮度": "3档"}),
            sales=3000,
            rating=4.5
        ),
        ProductModel(
            name="双人床垫",
            description="高弹性床垫，舒适透气",
            price=999.00,
            original_price=1499.00,
            stock=50,
            category_id=categories[4].id,
            image_url="https://via.placeholder.com/300x300?text=Mattress",
            images=json.dumps([]),
            specs=json.dumps({"尺寸": "1.8m", "厚度": "25cm"}),
            sales=500,
            rating=4.8
        ),
    ]
    
    for product in products:
        existing = db.query(ProductModel).filter(
            ProductModel.name == product.name
        ).first()
        if not existing:
            db.add(product)
    
    db.commit()
    print(f"✅ 添加了 {len(products)} 个商品")

def add_users(db):
    """添加测试用户"""
    print("\n📦 正在添加测试用户...")
    
    users = [
        UserModel(
            phone="13800138000",
            nickname="张三",
            avatar="https://via.placeholder.com/100x100?text=User1",
            password_hash=hash_password("123456")  # 密码: 123456
        ),
        UserModel(
            phone="13800138001",
            nickname="李四",
            avatar="https://via.placeholder.com/100x100?text=User2",
            password_hash=hash_password("123456")  # 密码: 123456
        ),
        UserModel(
            openid="test_openid_001",
            nickname="微信用户",
            avatar="https://via.placeholder.com/100x100?text=WeChat",
            password_hash=hash_password("123456")
        ),
    ]
    
    for user in users:
        existing = db.query(UserModel).filter(
            (UserModel.phone == user.phone) if user.phone else (UserModel.openid == user.openid)
        ).first()
        if not existing:
            db.add(user)
    
    db.commit()
    print(f"✅ 添加了 {len(users)} 个测试用户")
    print("\n📝 测试账号信息：")
    print("   账号: 13800138000  密码: 123456")
    print("   账号: 13800138001  密码: 123456")

def add_addresses(db):
    """添加收货地址"""
    print("\n📦 正在添加收货地址...")
    
    users = db.query(UserModel).filter(UserModel.phone != None).all()
    
    if not users:
        print("❌ 请先添加用户！")
        return
    
    for user in users:
        address = AddressModel(
            user_id=user.id,
            receiver_name=user.nickname,
            phone=user.phone or "13800138000",
            province="北京市",
            city="朝阳区",
            district="三里屯",
                                    detail="",
            is_default=True
        )
        db.add(address)
    
    db.commit()
    print(f"✅ 为 {len(users)} 个用户添加了收货地址")

def main():
    """主函数 - 执行所有初始化"""
    print("=" * 60)
    print("🚀 电商平台 - 数据库初始化脚本")
    print("=" * 60)
    
    # 创建数据库表
    init_database()
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 添加数据
        add_categories(db)
        add_products(db)
        add_users(db)
        add_addresses(db)
        
        print("\n" + "=" * 60)
        print("✅ 所有初始化完成！")
        print("=" * 60)
        print("\n📚 你现在可以：")
        print("   1. 运行后端: python run.py")
        print("   2. 访问 http://127.0.0.1:8000/docs 查看 API")
        print("   3. 用测试账号登录小程序")
        print("   4. 浏览商品、加入购物车等功能")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
