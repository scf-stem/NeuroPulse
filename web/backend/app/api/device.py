"""
Neuro Pulse - Device API
Neuro Pulse - 设备管理接口

完整实现设备的注册、管理和状态更新
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.i18n import get_locale, msg
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.device import Device

router = APIRouter()


# ============================================================
# Pydantic Schemas
# ============================================================

class DeviceRegister(BaseModel):
    """设备注册"""
    device_id: str
    name: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    mac_address: Optional[str] = None


class DeviceUpdate(BaseModel):
    """设备更新"""
    name: Optional[str] = None


class DeviceResponse(BaseModel):
    """设备响应"""
    id: int
    device_id: str
    name: Optional[str]
    firmware_version: Optional[str]
    hardware_version: Optional[str]
    mac_address: Optional[str]
    is_online: bool
    battery_level: Optional[float]
    last_seen: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceHeartbeat(BaseModel):
    """设备心跳"""
    device_id: str
    battery_level: Optional[float] = None
    firmware_version: Optional[str] = None


# ============================================================
# API Endpoints
# ============================================================

@router.post("/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    request: Request,
    device_data: DeviceRegister,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """
    注册新设备

    将设备绑定到当前用户账户
    """
    # 检查设备是否已存在
    result = await db.execute(
        select(Device).where(Device.device_id == device_data.device_id)
    )
    existing_device = result.scalar_one_or_none()

    if existing_device:
        # 设备已存在，检查是否已绑定到其他用户
        if existing_device.owner_id and existing_device.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg(get_locale(request), "device.bound_elsewhere")
            )
        # 更新设备绑定
        existing_device.owner_id = current_user.id
        existing_device.name = device_data.name or existing_device.name
        if device_data.firmware_version:
            existing_device.firmware_version = device_data.firmware_version
        if device_data.hardware_version:
            existing_device.hardware_version = device_data.hardware_version
        if device_data.mac_address:
            existing_device.mac_address = device_data.mac_address
        existing_device.last_seen = datetime.utcnow()

        await db.flush()
        await db.refresh(existing_device)
        return DeviceResponse.model_validate(existing_device)

    # 创建新设备
    new_device = Device(
        device_id=device_data.device_id,
        name=device_data.name or msg(get_locale(request), "device.default_name", suffix=device_data.device_id[-6:]),
        firmware_version=device_data.firmware_version,
        hardware_version=device_data.hardware_version,
        mac_address=device_data.mac_address,
        owner_id=current_user.id,
        is_online=True,
        last_seen=datetime.utcnow()
    )
    db.add(new_device)
    await db.flush()
    await db.refresh(new_device)

    return DeviceResponse.model_validate(new_device)


@router.get("/list", response_model=List[DeviceResponse])
async def list_devices(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有设备"""
    result = await db.execute(
        select(Device)
        .where(Device.owner_id == current_user.id)
        .order_by(Device.last_seen.desc())
    )
    devices = result.scalars().all()

    return [DeviceResponse.model_validate(d) for d in devices]


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    request: Request,
    device_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取设备详情"""
    result = await db.execute(
        select(Device).where(
            and_(
                Device.device_id == device_id,
                Device.owner_id == current_user.id
            )
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "device.not_found")
        )

    return DeviceResponse.model_validate(device)


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    request: Request,
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """更新设备信息"""
    result = await db.execute(
        select(Device).where(
            and_(
                Device.device_id == device_id,
                Device.owner_id == current_user.id
            )
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "device.not_found")
        )

    # 更新设备信息
    if device_data.name is not None:
        device.name = device_data.name

    await db.flush()
    await db.refresh(device)

    return DeviceResponse.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    request: Request,
    device_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """删除设备绑定"""
    result = await db.execute(
        select(Device).where(
            and_(
                Device.device_id == device_id,
                Device.owner_id == current_user.id
            )
        )
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "device.not_found")
        )

    # 解绑设备（不删除设备记录）
    device.owner_id = None
    await db.flush()

    return None


@router.post("/heartbeat")
async def device_heartbeat(
    heartbeat: DeviceHeartbeat,
    db: AsyncSession = Depends(get_db)
):
    """
    设备心跳

    设备定期调用此接口报告在线状态
    """
    result = await db.execute(
        select(Device).where(Device.device_id == heartbeat.device_id)
    )
    device = result.scalar_one_or_none()

    if device:
        device.is_online = True
        device.last_seen = datetime.utcnow()
        if heartbeat.battery_level is not None:
            device.battery_level = heartbeat.battery_level
        if heartbeat.firmware_version:
            device.firmware_version = heartbeat.firmware_version
        await db.flush()

    return {
        "status": "ok",
        "timestamp": datetime.utcnow(),
        "device_id": heartbeat.device_id
    }


@router.get("/status/{device_id}")
async def get_device_status(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取设备状态（无需认证，用于设备检查）"""
    result = await db.execute(
        select(Device).where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device:
        return {
            "exists": False,
            "device_id": device_id
        }

    return {
        "exists": True,
        "device_id": device_id,
        "is_bound": device.owner_id is not None,
        "is_online": device.is_online,
        "last_seen": device.last_seen
    }
