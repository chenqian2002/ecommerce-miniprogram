from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.database.models import MerchantSettingsModel, UserModel

router = APIRouter()


def require_merchant(user: UserModel):
    if user.phone != '13859631156':
        raise HTTPException(status_code=403, detail='仅商家账号可操作商家设置')


class MerchantSettingsRequest(BaseModel):
    merchant_id: str = ''
    official_appid: str = ''
    official_secret: str = ''
    customer_service_wechat: str = 'kefu888888'
    customer_service_qr_code: str = '/images/kefu-qrcode.png'


class MerchantSettingsResponse(BaseModel):
    merchant_id: str = ''
    official_appid: str = ''
    official_secret: str = ''
    customer_service_wechat: str = 'kefu888888'
    customer_service_qr_code: str = '/images/kefu-qrcode.png'

    class Config:
        from_attributes = True


def get_or_create_settings(db: Session) -> MerchantSettingsModel:
    settings = db.query(MerchantSettingsModel).first()
    if settings:
        return settings

    settings = MerchantSettingsModel(
        merchant_id='',
        official_appid='',
        official_secret='',
        customer_service_wechat='kefu888888',
        customer_service_qr_code='/images/kefu-qrcode.png'
    )
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.get('/merchant/settings', response_model=MerchantSettingsResponse)
def get_merchant_settings(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_merchant(user)
    return get_or_create_settings(db)


@router.put('/merchant/settings', response_model=MerchantSettingsResponse)
def update_merchant_settings(
    request: MerchantSettingsRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_merchant(user)
    settings = get_or_create_settings(db)
    settings.merchant_id = (request.merchant_id or '').strip()
    settings.official_appid = (request.official_appid or '').strip()
    settings.official_secret = (request.official_secret or '').strip()
    settings.customer_service_wechat = (request.customer_service_wechat or '').strip() or 'kefu888888'
    settings.customer_service_qr_code = (request.customer_service_qr_code or '').strip() or '/images/kefu-qrcode.png'
    settings.updated_by = user.id
    db.commit()
    db.refresh(settings)
    return settings


@router.get('/settings/public')
def get_public_settings(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    return {
        'customer_service_wechat': settings.customer_service_wechat or 'kefu888888',
        'customer_service_qr_code': settings.customer_service_qr_code or '/images/kefu-qrcode.png'
    }
