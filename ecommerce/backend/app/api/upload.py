# 图片上传 API 路由

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import os

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """上传商品图片，返回可访问 URL"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")

    suffix = Path(file.filename).suffix if file.filename else ".jpg"
    safe_name = f"{uuid4().hex}{suffix}"
    save_path = UPLOAD_DIR / safe_name

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="空文件无法上传")

    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "message": "上传成功",
        "url": f"/uploads/{safe_name}",
        "filename": safe_name
    }
