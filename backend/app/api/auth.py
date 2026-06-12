"""
Neuro Pulse - Authentication API
Neuro Pulse - 认证接口

完整实现用户注册、登录、Token 管理
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.i18n import get_locale, msg
from app.models.user import User

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
DEMO_ACCESS_TOKEN = "neuro-pulse-demo-token"


def demo_token_enabled() -> bool:
    return settings.APP_ENV != "production"


# ============================================================
# Pydantic Schemas
# ============================================================

class UserCreate(BaseModel):
    """用户注册"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class PasswordChange(BaseModel):
    """密码修改"""
    current_password: str
    new_password: str


# ============================================================
# Helper Functions
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """通过邮箱获取用户"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """通过 ID 获取用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """验证用户"""
    # 清理输入
    email = email.strip()
    
    # 先尝试通过邮箱查找
    user = await get_user_by_email(db, email)
    
    # 如果没找到，尝试通过用户名查找
    if not user:
        user = await get_user_by_username(db, email)
        
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def build_demo_user() -> User:
    """构造演示模式用户（不落库）"""
    return User(
        id=999,
        email="demo@neuropulse.ai",
        username="alex.demo",
        full_name="Alex Chen",
        hashed_password="",
        role="user",
        is_active=True,
        is_verified=True,
        created_at=datetime(2026, 4, 18),
    )


async def get_current_user_from_token(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """从 Token 获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg(get_locale(request), "auth.invalid_credentials"),
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token == DEMO_ACCESS_TOKEN and demo_token_enabled():
        return build_demo_user()

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
        user_id = int(user_id_raw)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request), "auth.user_disabled")
        )
    return user


# ============================================================
# API Endpoints
# ============================================================

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    - **email**: 邮箱地址 (唯一)
    - **username**: 用户名 (唯一)
    - **password**: 密码
    - **full_name**: 全名 (可选)
    """
    # 检查邮箱是否已存在
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request), "auth.email_exists")
        )

    # 检查用户名是否已存在
    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request), "auth.username_exists")
        )

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role="user",
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    # 生成 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.id, "email": new_user.email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    使用 OAuth2 密码流程
    - **username**: 邮箱地址
    - **password**: 密码
    """
    # OAuth2PasswordRequestForm 使用 username 字段
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg(get_locale(request), "auth.login_failed"),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request), "auth.user_disabled")
        )

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    await db.flush()

    # 生成 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user_from_token)
):
    """用户登出"""
    # Token 是无状态的，客户端需要删除本地存储的 Token
    # 如需服务端失效，可以实现 Token 黑名单 (使用 Redis)
    return {"message": msg(get_locale(request), "auth.logout_success")}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """刷新 Token"""
    # 生成新 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(current_user)
    )


@router.put("/password")
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request), "auth.password_incorrect")
        )

    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    await db.flush()

    return {"message": msg(get_locale(request), "auth.password_updated")}


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """更新用户资料"""
    if full_name is not None:
        current_user.full_name = full_name

    current_user.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)
