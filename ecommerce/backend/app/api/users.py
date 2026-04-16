# 用户 API 路由（框架代码）

from fastapi import APIRouter

router = APIRouter()

@router.get("/users/profile")
def get_profile():
    """获取个人信息"""
    return {"message": "获取个人信息接口"}

@router.post("/users/profile")
def update_profile():
    """更新个人信息"""
    return {"message": "更新个人信息接口"}

@router.post("/users/change-password")
def change_password():
    """修改密码"""
    return {"message": "修改密码接口"}
