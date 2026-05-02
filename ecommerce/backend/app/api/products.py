# 商品 API 路由 (修正版)

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.database.database import get_db
from app.database.models import ProductModel, CategoryModel, UserModel
from app.core.security import get_current_user

router = APIRouter()

# --- 响应模型 (Schemas) ---

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    original_price: float | None = None
    stock: int
    category_id: int | None = None
    image_url: str
    sales: int
    rating: float

    # Pydantic v2 推荐写法
    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    icon: str = ''
    description: str = ''

class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ''
    price: float = Field(..., ge=0)
    original_price: float | None = None
    stock: int = Field(0, ge=0)
    category_id: int | None = None
    image_url: str = ''
    sales: int = Field(0, ge=0)
    rating: float = Field(5.0, ge=0, le=5)
    images: list[str] | None = None
    specs: dict | None = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    original_price: Optional[float] = None
    stock: Optional[int] = Field(default=None, ge=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    sales: Optional[int] = Field(default=None, ge=0)
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    images: Optional[list[str]] = None
    specs: Optional[dict] = None

# --- 权限校验 ---

def require_merchant(user: UserModel):
    """商家校验：默认测试账号 13800138000 为商家"""
    if user.phone != '13859631156':
        raise HTTPException(status_code=403, detail='仅商家账号可操作商品管理')

# --- 路由接口 ---

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """获取所有商品分类"""
    return db.query(CategoryModel).all()

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    request: CategoryCreateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家新增商品分类"""
    require_merchant(user)
    name = request.name.strip()
    
    existing = db.query(CategoryModel).filter(CategoryModel.name == name).first()
    if existing:
        return existing

    category = CategoryModel(
        name=name,
        icon=request.icon or '',
        description=request.description or ''
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家删除商品分类：不删除商品，只把商品改为未分类"""
    require_merchant(user)

    category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    db.query(ProductModel).filter(ProductModel.category_id == category_id).update({
        ProductModel.category_id: None
    })
    db.delete(category)
    db.commit()
    return {"message": "分类已删除"}

@router.get("/products", response_model=List[ProductResponse])

def get_products(
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    sort_by: str = Query("default"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取商品列表（支持过滤、排序、分页）"""
    query = db.query(ProductModel)
    
    if category_id:
        query = query.filter(ProductModel.category_id == category_id)
    
    if keyword:
        query = query.filter(ProductModel.name.ilike(f"%{keyword}%"))
    
    if sort_by == "price-asc":
        query = query.order_by(ProductModel.price.asc())
    elif sort_by == "price-desc":
        query = query.order_by(ProductModel.price.desc())
    elif sort_by == "sales":
        query = query.order_by(ProductModel.sales.desc())
    else:
        query = query.order_by(ProductModel.created_at.desc())
    
    skip = (page - 1) * page_size
    return query.offset(skip).limit(page_size).all()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取单个商品详情"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

@router.post("/products", response_model=ProductResponse)
def create_product(
    request: ProductCreateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家新增商品"""
    require_merchant(user)

    # 校验分类是否存在
    if request.category_id is not None:
        category = db.query(CategoryModel).filter(CategoryModel.id == request.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="商品分类不存在")

    product = ProductModel(
        name=request.name,
        description=request.description or '',
        price=request.price,
        original_price=request.original_price,
        stock=request.stock,
        category_id=request.category_id,
        image_url=request.image_url or '',
        images=request.images or [],
        specs=request.specs or {},
        sales=request.sales,
        rating=request.rating,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家编辑商品"""
    require_merchant(user)

    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    if request.category_id is not None:
        category = db.query(CategoryModel).filter(CategoryModel.id == request.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="商品分类不存在")
        product.category_id = request.category_id

    # 批量更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'category_id':
            continue
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """商家删除商品"""
    require_merchant(user)

    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    db.delete(product)
    db.commit()
    return {"message": "商品已删除"}