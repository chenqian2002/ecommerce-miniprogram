# 认证 API 路由

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import httpx

from app.database.database import get_db
from app.database.models import UserModel
from app.core.config import settings
from app.core.security import hash_password, verify_password

router = APIRouter()

# 请求响应模型
class LoginRequest(BaseModel):
    phone: str
    password: str

class WechatLoginRequest(BaseModel):
    code: str
    userInfo: dict

class TokenResponse(BaseModel):
    token: str
    user: dict

# 生成 JWT Token
def create_access_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    账号密码登录
    
    测试数据：
    - 账号: 13800138000
    - 密码: 123456
    """
    print(f"📱 登录请求: {request.phone}")
    
    user = db.query(UserModel).filter(UserModel.phone == request.phone).first()
    
    if not user:
        print(f"❌ 用户不存在: {request.phone}")
        raise HTTPException(status_code=401, detail="账号或密码错误")
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        print(f"❌ 密码错误: {request.phone}")
        raise HTTPException(status_code=401, detail="账号或密码错误")
    
    print(f"✅ 登录成功: {request.phone}")
    
    token = create_access_token(user.id)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar": user.avatar
        }
    }

@router.post("/auth/wechat-login", response_model=TokenResponse)
async def wechat_login(request: WechatLoginRequest, db: Session = Depends(get_db)):
    """
    微信授权登录
    """
    # 向微信服务器验证 code
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": settings.WECHAT_APPID,
                "secret": settings.WECHAT_APPSECRET,
                "js_code": request.code,
                "grant_type": "authorization_code"
            }
        )
        data = resp.json()
    
    if "errcode" in data:
        raise HTTPException(status_code=400, detail="微信验证失败")
    
    openid = data.get("openid")
    
    # 查询或创建用户
    user = db.query(UserModel).filter(UserModel.openid == openid).first()
    
    if not user:
        user = UserModel(
            openid=openid,
            nickname=request.userInfo.get("nickName"),
            avatar=request.userInfo.get("avatarUrl")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    token = create_access_token(user.id)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar": user.avatar
        }
    }

@router.post("/auth/logout")
def logout():
    """
    登出（客户端删除本地 token）
    """
    return {"message": "登出成功"}
