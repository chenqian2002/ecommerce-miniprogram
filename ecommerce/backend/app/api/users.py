0000000000000000000000000000000000000000000000000000# 用户 API 路由

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.hash import bcrypt

from app.database.database import get_db
from app.database.models import UserModel
from app.core.security import get_current_user

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangePhoneRequest(BaseModel):
    phone: str


@router.get("/users/profile")
def get_profile(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户个人信息"""
    return {
        "id": user.id,
        "nickname": user.nickname or "微信用户",
        "avatar": user.avatar or "",
        "phone": user.phone or "",
        "created_at": str(user.created_at) if user.created_at else None,
    }


@router.post("/users/profile")
def update_profile(
    request: UpdateProfileRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新昵称/头像"""
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.avatar is not None:
        user.avatar = request.avatar
    db.commit()
    db.refresh(user)
    return {
        "message": "更新成功",
        "data": {
            "nickname": user.nickname,
            "avatar": user.avatar,
        },
    }


@router.post("/users/change-password")
def change_password(
    request: ChangePasswordRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    if not user.password_hash:
        raise HTTPException(status_code=400, detail="当前账号未设置密码，无法修改")
    if not bcrypt.verify(request.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码不能少于6位")
    user.password_hash = bcrypt.hash(request.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.post("/users/bindphone")
def bind_phone(
    request: ChangePhoneRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """绑定/修改手机号"""
    existing = db.query(UserModel).filter(
        UserModel.phone == request.phone,
        UserModel.id != user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已被其他账号绑定")
    user.phone = request.phone
    db.commit()
    return {"message": "手机号绑定成功", "phone": user.phone}