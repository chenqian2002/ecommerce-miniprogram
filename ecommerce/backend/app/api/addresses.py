# 地址 API 路由（可用版本）

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import AddressModel, UserModel
from app.core.security import get_current_user

router = APIRouter()

class AddressRequest(BaseModel):
    receiver_name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False

class AddressResponse(BaseModel):
    id: int
    receiver_name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool

    class Config:
        from_attributes = True

@router.get("/addresses")
def get_addresses(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取收货地址列表"""
    addresses = db.query(AddressModel).filter(
        AddressModel.user_id == user.id
    ).order_by(AddressModel.is_default.desc(), AddressModel.created_at.desc()).all()

    return {"data": addresses}

@router.post("/addresses")
def add_address(
    request: AddressRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """新增地址"""
    if request.is_default:
        db.query(AddressModel).filter(AddressModel.user_id == user.id).update({"is_default": False})

    address = AddressModel(
        user_id=user.id,
        receiver_name=request.receiver_name,
        phone=request.phone,
        province=request.province,
        city=request.city,
        district=request.district,
        detail=request.detail,
        is_default=request.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)

    return {"message": "新增成功", "data": address}

@router.put("/addresses/{address_id}")
def update_address(
    address_id: int,
    request: AddressRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """编辑地址"""
    address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.user_id == user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    if request.is_default:
        db.query(AddressModel).filter(AddressModel.user_id == user.id).update({"is_default": False})

    address.receiver_name = request.receiver_name
    address.phone = request.phone
    address.province = request.province
    address.city = request.city
    address.district = request.district
    address.detail = request.detail
    address.is_default = request.is_default

    db.commit()
    db.refresh(address)
    return {"message": "编辑成功", "data": address}

@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除地址"""
    address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.user_id == user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    db.delete(address)
    db.commit()
    return {"message": "删除成功"}

@router.post("/addresses/{address_id}/default")
def set_default_address(
    address_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设为默认地址"""
    address = db.query(AddressModel).filter(
        AddressModel.id == address_id,
        AddressModel.user_id == user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")

    db.query(AddressModel).filter(AddressModel.user_id == user.id).update({"is_default": False})
    address.is_default = True
    db.commit()
    return {"message": "已设为默认地址"}
