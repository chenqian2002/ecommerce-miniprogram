# 核心配置文件

from pydantic import field_validator
from pydantic_settings import BaseSettings

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
    
    # 微信基础配置
    WECHAT_APPID: str = ""
    WECHAT_APPSECRET: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""
    WECHAT_SUBSCRIBE_TEMPLATE_ID: str = ""
    
    # 微信支付 V3 配置
    WECHAT_PAY_MERCHANT_SERIAL_NO: str = ""
    WECHAT_PAY_PRIVATE_KEY_PATH: str = ""
    WECHAT_PAY_CERT_PATH: str = ""
    WECHAT_PAY_PLATFORM_CERT_PATH: str = ""
    WECHAT_PAY_BASE_URL: str = "https://api.mch.weixin.qq.com"
    
    # CORS 配置
    CORS_ORIGINS: list = [
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()



