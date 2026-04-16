# 核心配置文件

from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "电商平台 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 微信配置
    WECHAT_APPID: str = ""
    WECHAT_APPSECRET: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    
    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
