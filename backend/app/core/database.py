"""
Tremor Guard - Database Configuration
震颤卫士 - 数据库配置

SQLAlchemy 异步数据库连接
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

is_serverless_runtime = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,
}

if is_serverless_runtime:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 声明基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    获取数据库会话 (依赖注入)

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库 (创建所有表)"""
    # 导入所有模型以注册到 Base
    from app.models import device, health, medication, rehabilitation, tremor_data, user
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
