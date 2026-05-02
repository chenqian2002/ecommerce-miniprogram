# 图片上传 API 路由

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from uuid import uuid4

from app.core.security import get_current_user
from app.database.models import UserModel

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    user: UserModel = Depends(get_current_user),
):
    """上传图片，返回可访问 URL（需要登录）"""
    if not file.content_type or file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="只支持 JPG/PNG/WebP/GIF 格式")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="空文件无法上传")

    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 5MB")

    suffix = Path(file.filename).suffix if file.filename else ".jpg"
    safe_name = f"{uuid4().hex}{suffix}"
    save_path = UPLOAD_DIR / safe_name

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "message": "上传成功",
        "url": f"/uploads/{safe_name}",
        "filename": safe_name,
        "size": len(content)
    }