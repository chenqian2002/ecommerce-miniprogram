# 地址 API 路由（框架代码）

from fastapi import APIRouter

router = APIRouter()

@router.get("/addresses")
def get_addresses():
    """获取收货地址列表"""
    return {"message": "获取地址列表接口"}

@router.post("/addresses")
def add_address():
    """新增地址"""
    return {"message": "新增地址接口"}

@router.put("/addresses/{address_id}")
def update_address(address_id: int):
    """编辑地址"""
    return {"message": "编辑地址接口"}

@router.delete("/addresses/{address_id}")
def delete_address(address_id: int):
    """删除地址"""
    return {"message": "删除地址接口"}

@router.post("/addresses/{address_id}/default")
def set_default_address(address_id: int):
    """设为默认地址"""
    return {"message": "设默认地址接口"}
