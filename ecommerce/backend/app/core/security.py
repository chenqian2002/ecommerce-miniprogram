"""
密码加密模块 - 用于安全存储密码

这个模块解决的问题：
- 不能直接存储明文密码（太危险）
- 使用 hash 算法对密码进行加密
- 登录时比对加密后的密码
"""

import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.database.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """对密码进行加密"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return hash_password(plain_password) == hashed_password


def decode_access_token(token: str) -> int:
    """解析 JWT，返回用户ID"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("token中缺少user_id")
        return int(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的登录凭证",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """从 token 解析当前用户"""
    user_id = decode_access_token(token)
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
