# 公告 API 路由

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import AnnouncementModel, UserModel

router = APIRouter()


class AnnouncementUpdateRequest(BaseModel):
    title: str = "平台公告"
    content: str
    is_active: bool = True


@router.get("/announcement")
def get_announcement(db: Session = Depends(get_db)):
    """获取当前生效公告"""
    announcement = db.query(AnnouncementModel).filter(AnnouncementModel.is_active == True).order_by(AnnouncementModel.updated_at.desc()).first()
    if not announcement:
        return {"title": "平台公告", "content": "暂无公告", "is_active": False}

    return {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "is_active": announcement.is_active,
        "updated_at": announcement.updated_at,
    }


@router.post("/announcement")
def upsert_announcement(
    request: AnnouncementUpdateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """商家更新公告"""
    if user.phone != '13859631156':
        raise HTTPException(status_code=403, detail='仅商家账号可设置公告')

    announcement = db.query(AnnouncementModel).filter(AnnouncementModel.is_active == True).order_by(AnnouncementModel.updated_at.desc()).first()
    if not announcement:
        announcement = AnnouncementModel()
        db.add(announcement)

    announcement.title = request.title or '平台公告'
    announcement.content = request.content
    announcement.is_active = request.is_active
    announcement.updated_by = user.id

    db.commit()
    db.refresh(announcement)
    return {
        "message": "公告已保存",
        "announcement": {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "is_active": announcement.is_active,
        },
    }
