"""
Neuro Pulse - Application Configuration
Neuro Pulse - 应用配置

使用 pydantic-settings 管理环境变量
支持 Zeabur 云平台部署
"""

from functools import lru_cache
import os
from pathlib import Path
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """应用配置类"""

    # ============================================================
    # 应用基础配置
    # ============================================================
    APP_NAME: str = "Neuro Pulse"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-change-this"
    AUTO_INIT_DB: bool = False

    # ============================================================
    # 服务器配置 (Zeabur 使用 PORT 环境变量)
    # ============================================================
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # ============================================================
    # 数据库配置 (Zeabur PostgreSQL)
    # 支持 Zeabur 自动注入的变量格式
    # ============================================================
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/tremor_guard"

    # Zeabur PostgreSQL 单独变量 (自动注入)
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USERNAME: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DATABASE: Optional[str] = None

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def build_database_url(cls, v, info):
        """Build an asyncpg URL from Zeabur PostgreSQL variables."""
        value = (
            os.getenv('DATABASE_URL')
            or os.getenv('POSTGRES_CONNECTION_STRING')
            or os.getenv('POSTGRES_URI')
            or os.getenv('POSTGRES_URL')
        )
        if not value:
            value = v

        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT', '5432')
        user = os.getenv('POSTGRES_USERNAME')
        password = os.getenv('POSTGRES_PASSWORD')
        database = os.getenv('POSTGRES_DATABASE')

        if not value and all([host, user, password, database]):
            value = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

        if not value:
            return value

        if value.startswith("postgresql+asyncpg://"):
            return value
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        return value

    # ============================================================
    # Redis 配置 (Zeabur Redis)
    # ============================================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # Zeabur Redis 单独变量 (自动注入)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None

    @field_validator('REDIS_URL', mode='before')
    @classmethod
    def build_redis_url(cls, v, info):
        """如果 Zeabur 注入了单独的 Redis 变量，自动构建 REDIS_URL"""
        host = os.getenv('REDIS_HOST')
        port = os.getenv('REDIS_PORT', '6379')
        password = os.getenv('REDIS_PASSWORD')

        if host:
            if password:
                return f"redis://:{password}@{host}:{port}/0"
            return f"redis://{host}:{port}/0"
        return v

    # ============================================================
    # JWT 认证配置
    # ============================================================
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============================================================
    # DashScope / Qwen API 配置
    # ============================================================
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_MODEL: str = "qwen-plus"

    # ============================================================
    # CORS 配置 (支持 Zeabur 自动域名)
    # ============================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.zeabur.app"  # Zeabur 自动分配的域名
    ]

    # Zeabur 特殊变量
    ZEABUR_WEB_URL: Optional[str] = None  # Zeabur 自动注入的前端 URL
    PUBLIC_WEB_URL: Optional[str] = None

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def add_zeabur_origin(cls, v, info):
        """自动添加 Zeabur 前端 URL 到 CORS"""
        origins = v if isinstance(v, list) else v.split(',') if isinstance(v, str) else []
        dynamic_origins = [
            os.getenv('ZEABUR_WEB_URL'),
            os.getenv('PUBLIC_WEB_URL'),
        ]

        vercel_url = os.getenv('VERCEL_URL')
        if vercel_url:
            dynamic_origins.append(f"https://{vercel_url}")

        for origin in dynamic_origins:
            if origin and origin not in origins:
                origins.append(origin)
        return origins

    # ============================================================
    # 设备认证
    # ============================================================
    DEVICE_API_KEY: str = ""

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略未定义的环境变量


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例 (缓存)"""
    return Settings()


# 全局配置实例
settings = get_settings()
