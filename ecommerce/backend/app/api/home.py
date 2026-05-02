# 首页聚合 API

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import ProductModel, AnnouncementModel, CategoryModel

router = APIRouter()


@router.get("/home")
def get_home_data(db: Session = Depends(get_db)):
    """首页聚合数据：公告、分类、推荐商品"""
    # 公告
    announcements = (
        db.query(AnnouncementModel)
        .filter(AnnouncementModel.is_active == True)
        .order_by(AnnouncementModel.updated_at.desc())
        .limit(5)
        .all()
    )
    announcement_list = [
        {"id": a.id, "title": a.title, "content": a.content}
        for a in announcements
    ]

    # 分类
    categories = db.query(CategoryModel).order_by(CategoryModel.id).limit(20).all()
    category_list = [
        {"id": c.id, "name": c.name, "icon": c.icon or ""}
        for c in categories
    ]

    # 推荐商品（按销量排序前10）
    recommended = (
        db.query(ProductModel)
        .filter(ProductModel.stock > 0)
        .order_by(ProductModel.sales.desc())
        .limit(10)
        .all()
    )
    recommended_list = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "original_price": p.original_price,
            "image_url": p.image_url,
            "sales": p.sales,
            "rating": p.rating,
        }
        for p in recommended
    ]

    # 新品（按创建时间倒序前10）
    new_products = (
        db.query(ProductModel)
        .filter(ProductModel.stock > 0)
        .order_by(ProductModel.created_at.desc())
        .limit(10)
        .all()
    )
    new_list = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "original_price": p.original_price,
            "image_url": p.image_url,
            "sales": p.sales,
        }
        for p in new_products
    ]

    return {
        "announcements": announcement_list,
        "categories": category_list,
        "recommended": recommended_list,
        "new_products": new_list,
    }