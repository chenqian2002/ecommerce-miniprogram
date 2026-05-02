# 数据库模型定义 (修正版)

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, func
from sqlalchemy.orm import relationship
from app.database.database import Base


# 用户表
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    openid = Column(String(100), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    role = Column(String(20), default="customer")  # customer / merchant
    nickname = Column(String(100))
    avatar = Column(String(500))
    password_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    addresses = relationship("AddressModel", back_populates="user")
    orders = relationship("OrderModel", back_populates="user")
    cart_items = relationship("CartItemModel", back_populates="user")


# 分类表
class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    icon = Column(String(500))
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    products = relationship("ProductModel", back_populates="category")


# 商品表
class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), index=True)
    description = Column(String(2000))
    price = Column(Float)
    original_price = Column(Float)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_url = Column(String(500))
    images = Column(JSON)  # 多张图片
    specs = Column(JSON)   # 规格信息
    sales = Column(Integer, default=0)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    category = relationship("CategoryModel", back_populates="products")
    order_items = relationship("OrderItemModel", back_populates="product")
    cart_items = relationship("CartItemModel", back_populates="product")


# 收货地址表
class AddressModel(Base):
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
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("UserModel", back_populates="addresses")


# 订单表
class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(String(20), default="pending")  # pending/paid/shipped/completed/cancelled
    payment_method = Column(String(20))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    remark = Column(String(500))
    
    # 修正了下方的缩进
    logistics_image_url = Column(String(500), nullable=True)
    logistics_company = Column(String(100), nullable=True)
    logistics_remark = Column(String(500), nullable=True)
    merchant_hidden = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("UserModel", back_populates="orders")
    items = relationship("OrderItemModel", back_populates="order")


# 订单项表
class OrderItemModel(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)  # 下单时的快照价格

    # 关系
    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel", back_populates="order_items")


# 购物车表
class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("UserModel", back_populates="cart_items")
    product = relationship("ProductModel", back_populates="cart_items")


# 公告表
class AnnouncementModel(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), default="平台公告")
    content = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)


# 商家设置表
class MerchantSettingsModel(Base):
    __tablename__ = "merchant_settings"

    id = Column(Integer, primary_key=True)
    merchant_id = Column(String(100), default="")
    official_appid = Column(String(100), default="")
    official_secret = Column(String(200), default="")
    customer_service_wechat = Column(String(100), default="kefu888888")
    customer_service_qr_code = Column(String(500), default="/images/kefu-qrcode.png")
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# 支付记录表

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float)
    transaction_id = Column(String(100), unique=True)
    status = Column(String(20), default="pending")  # pending/completed/failed
    payment_method = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())