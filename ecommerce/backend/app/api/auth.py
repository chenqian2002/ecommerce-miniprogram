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

# 商家手机号列表（可通过数据库 role 字段判断）
MERCHANT_PHONES = ['13859631156']

# 开发模式下允许测试买家账密登录的手机号
DEV_BUYER_PHONES = ['13800138001', '13800138002']

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


def is_merchant_user(user: UserModel) -> bool:
    """判断用户是否为商家：优先看 role 字段，回退到手机号判断"""
    if hasattr(user, 'role') and user.role == 'merchant':
        return True
    if hasattr(user, 'isMerchant') and user.isMerchant:
        return True
    return user.phone in MERCHANT_PHONES


def build_user_info(user: UserModel) -> dict:
    """构建用户信息响应"""
    merchant = is_merchant_user(user)
    return {
        "id": user.id,
        "phone": user.phone or "",
        "openid": user.openid or "",
        "nickname": user.nickname or "微信用户",
        "avatar": user.avatar or "",
        "role": "merchant" if merchant else "customer",
        "isMerchant": merchant
    }


@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    账号密码登录
    - 商家账号：任何环境都可以登录
    - 买家测试账号：开发模式下可以登录
    """
    user = db.query(UserModel).filter(UserModel.phone == request.phone).first()

    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 验证密码
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 开发阶段：任何账号都可以用账密登录
    # 上线前改回来：只允许商家使用账密登录

    token = create_access_token(user.id)

    return {
        "token": token,
        "user": build_user_info(user)
    }

@router.post("/auth/wechat-login", response_model=TokenResponse)
async def wechat_login(request: WechatLoginRequest, db: Session = Depends(get_db)):
    """
    微信授权登录（普通用户）
    """
    # 开发环境：如果 code 是 "test_code"，跳过微信验证（方便本地测试）
    openid = None
    if request.code == "test_code":
        openid = f"test_openid_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
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

        if "errcode" in data and data["errcode"] != 0:
            raise HTTPException(status_code=400, detail="微信验证失败")
        openid = data.get("openid")

    if not openid:
        raise HTTPException(status_code=400, detail="无法获取微信用户标识")

    # 查询或创建用户
    user = db.query(UserModel).filter(UserModel.openid == openid).first()

    if not user:
        user = UserModel(
            openid=openid,
            nickname=request.userInfo.get("nickName") or "微信用户",
            avatar=request.userInfo.get("avatarUrl") or "",
            role="customer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)

    return {
        "token": token,
        "user": build_user_info(user)
    }

@router.post("/auth/logout")
def logout():
    """
    登出（客户端删除本地 token）
    """
    return {"message": "登出成功"}