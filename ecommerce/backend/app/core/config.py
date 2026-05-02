# 核心配置文件 (修正版)

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "电商平台 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 微信小程序基础配置
    WECHAT_APPID: str = ""
    WECHAT_APPSECRET: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""  # 修复了此处的缩进错误
    WECHAT_SUBSCRIBE_TEMPLATE_ID: str = ""

    # 公众号/订阅号新订单通知配置
    WECHAT_OFFICIAL_APPID: str = ""
    WECHAT_OFFICIAL_SECRET: str = ""
    WECHAT_ORDER_TEMPLATE_ID: str = ""
    WECHAT_MERCHANT_OPENID: str = ""
    
    # 微信支付 V3 配置
    WECHAT_PAY_MERCHANT_SERIAL_NO: str = ""
    WECHAT_PAY_PRIVATE_KEY_PATH: str = ""
    WECHAT_PAY_CERT_PATH: str = ""
    WECHAT_PAY_PLATFORM_CERT_PATH: str = ""
    WECHAT_PAY_BASE_URL: str = "https://api.mch.weixin.qq.com"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000"
    ]
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "y", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "n", "off", "release", "prod", "production"}:
                return False
        return bool(value)
    
    # Pydantic v2 建议使用 model_config 替代 class Config
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="allow" # 允许额外的环境变量
    )

settings = Settings()