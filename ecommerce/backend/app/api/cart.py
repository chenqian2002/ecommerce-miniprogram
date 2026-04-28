# 购物车 API 路由

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import CartItemModel, ProductModel, UserModel
from app.core.security import get_current_user

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

@router.get("/cart")
def get_cart(user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取购物车"""
    items = db.query(CartItemModel).filter(CartItemModel.user_id == user.id).all()
    result = []
    for item in items:
        product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
        if not product:
            continue
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "stock": product.stock,
        })
    return {"data": result}

@router.post("/cart/add")
def add_to_cart(
    request: CartItemRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加商品到购物车"""
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="数量必须大于0")

    product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    cart_item = db.query(CartItemModel).filter(
        CartItemModel.user_id == user.id,
        CartItemModel.product_id == request.product_id
    ).first()

    next_quantity = request.quantity + (cart_item.quantity if cart_item else 0)
    if product.stock is not None and next_quantity > product.stock:
        raise HTTPException(status_code=400, detail=f"库存不足，仅剩 {product.stock} 件")

    if cart_item:
        cart_item.quantity = next_quantity
    else:
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

    if request.quantity <= 0:
        db.delete(item)
        db.commit()
        return {"message": "已删除"}

    product = db.query(ProductModel).filter(ProductModel.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if product.stock is not None and request.quantity > product.stock:
        raise HTTPException(status_code=400, detail=f"库存不足，仅剩 {product.stock} 件")

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

