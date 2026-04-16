# 商品 API 路由

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import ProductModel, CategoryModel

router = APIRouter()

# 响应模型
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    original_price: float | None
    stock: int
    category_id: int
    image_url: str
    sales: int
    rating: float

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    description: str

    class Config:
        from_attributes = True

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """获取所有商品分类"""
    categories = db.query(CategoryModel).all()
    return categories

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    sort_by: str = Query("default"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取商品列表（支持分类、搜索、排序、分页）
    """
    query = db.query(ProductModel)
    
    # 分类过滤
    if category_id:
        query = query.filter(ProductModel.category_id == category_id)
    
    # 关键词搜索
    if keyword:
        query = query.filter(ProductModel.name.ilike(f"%{keyword}%"))
    
    # 排序
    if sort_by == "price-asc":
        query = query.order_by(ProductModel.price.asc())
    elif sort_by == "price-desc":
        query = query.order_by(ProductModel.price.desc())
    elif sort_by == "sales":
        query = query.order_by(ProductModel.sales.desc())
    else:
        query = query.order_by(ProductModel.created_at.desc())
    
    # 分页
    skip = (page - 1) * page_size
    products = query.offset(skip).limit(page_size).all()
    
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    return product

@router.get("/products/search", response_model=List[ProductResponse])
def search_products(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """全文搜索商品"""
    products = db.query(ProductModel).filter(
        ProductModel.name.ilike(f"%{q}%") |
        ProductModel.description.ilike(f"%{q}%")
    ).limit(20).all()
    
    return products

@router.get("/products/recommend", response_model=List[ProductResponse])
def recommend_products(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """获取推荐商品（根据销量和评分）"""
    products = db.query(ProductModel).order_by(
        ProductModel.sales.desc(),
        ProductModel.rating.desc()
    ).limit(limit).all()
    
    return products
