# 购物车 API 路由

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database.database import get_db
from app.database.models import CartItemModel, ProductModel, UserModel

router = APIRouter()

# 请求响应模型
class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    
    class Config:
        from_attributes = True

# 获取当前用户（简化版）
def get_current_user(db: Session = Depends(get_db)):
    # TODO: 从 token 解析用户 ID
    user_id = 1  # 示例
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    return user

@router.get("/cart")
def get_cart(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取购物车"""
    items = db.query(CartItemModel).filter(
        CartItemModel.user_id == user.id
    ).all()
    
    result = []
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url
        })
    
    return {"data": result}

@router.post("/cart/add")
def add_to_cart(
    request: CartItemRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加商品到购物车"""
    # 检查商品是否存在
    product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 查询购物车中是否已有该商品
    cart_item = db.query(CartItemModel).filter(
        CartItemModel.user_id == user.id,
        CartItemModel.product_id == request.product_id
    ).first()
    
    if cart_item:
        # 更新数量
        cart_item.quantity += request.quantity
    else:
        # 新增
        cart_item = CartItemModel(
            user_id=user.id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        db.add(cart_item)
    
    db.commit()
    return {"message": "添加成功"}

@router.put("/cart/{item_id}")
def update_cart_item(
    item_id: int,
    request: CartItemRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改购物车商品数量"""
    item = db.query(CartItemModel).filter(
        CartItemModel.id == item_id,
        CartItemModel.user_id == user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    
    item.quantity = request.quantity
    db.commit()
    
    return {"message": "修改成功"}

@router.delete("/cart/{item_id}")
def remove_from_cart(
    item_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除购物车项"""
    item = db.query(CartItemModel).filter(
        CartItemModel.id == item_id,
        CartItemModel.user_id == user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    
    db.delete(item)
    db.commit()
    
    return {"message": "删除成功"}

@router.delete("/cart/clear")
def clear_cart(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空购物车"""
    db.query(CartItemModel).filter(CartItemModel.user_id == user.id).delete()
    db.commit()
    
    return {"message": "清空成功"}
