"""
Neuro Pulse - Data API
Neuro Pulse - 数据接口

完整实现震颤数据的上传、存储和查询
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.i18n import get_locale, msg
from app.core.security import verify_device_key
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.device import Device
from app.models.tremor_data import TremorData, TremorSession

router = APIRouter()


# ============================================================
# Pydantic Schemas
# ============================================================

class TremorDataUpload(BaseModel):
    """震颤数据上传 (来自设备)"""
    device_id: str
    timestamp: Optional[datetime] = None

    # 检测结果
    detected: bool
    valid: bool = True
    out_of_range: bool = False

    # 频率特征
    frequency: Optional[float] = None
    peak_power: Optional[float] = None
    band_power: Optional[float] = None

    # 幅度特征
    amplitude: Optional[float] = None
    rms_amplitude: Optional[float] = None

    # 严重度
    severity: int = 0
    severity_label: Optional[str] = None

    # 可选: 原始频谱数据
    spectrum_data: Optional[dict] = None


class TremorDataResponse(BaseModel):
    """震颤数据响应"""
    id: int
    session_id: int
    timestamp: datetime
    detected: bool
    valid: bool
    out_of_range: bool
    frequency: Optional[float]
    peak_power: Optional[float]
    band_power: Optional[float]
    amplitude: Optional[float]
    rms_amplitude: Optional[float]
    severity: int
    severity_label: Optional[str]

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """创建检测会话"""
    device_id: str


class SessionResponse(BaseModel):
    """会话响应"""
    id: int
    device_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    total_analyses: int
    tremor_count: int
    avg_frequency: Optional[float]
    avg_amplitude: Optional[float]
    max_severity: int
    avg_severity: Optional[float]
    is_active: bool

    class Config:
        from_attributes = True


class BatchUpload(BaseModel):
    """批量数据上传"""
    device_id: str
    session_id: Optional[int] = None
    data: List[TremorDataUpload]


class UploadResponse(BaseModel):
    """上传响应"""
    status: str
    message: str
    session_id: Optional[int] = None
    data_id: Optional[int] = None


# ============================================================
# Helper Functions
# ============================================================

async def get_or_create_device(db: AsyncSession, device_id: str, user_id: Optional[int] = None) -> Device:
    """获取或创建设备"""
    result = await db.execute(select(Device).where(Device.device_id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        device = Device(
            device_id=device_id,
            owner_id=user_id,
            is_online=True,
            last_seen=datetime.utcnow()
        )
        db.add(device)
        await db.flush()
        await db.refresh(device)
    else:
        # 更新设备状态
        device.is_online = True
        device.last_seen = datetime.utcnow()
        if user_id and not device.owner_id:
            device.owner_id = user_id

    return device


async def get_or_create_active_session(
    db: AsyncSession,
    device: Device,
    user_id: int
) -> TremorSession:
    """获取或创建活跃会话"""
    # 查找活跃会话
    result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.device_id == device.id,
                TremorSession.user_id == user_id,
                TremorSession.is_active == True
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        # 创建新会话
        session = TremorSession(
            user_id=user_id,
            device_id=device.id,
            start_time=datetime.utcnow(),
            is_active=True,
            total_analyses=0,
            tremor_count=0,
            max_severity=0
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)

    return session


async def update_session_stats(db: AsyncSession, session: TremorSession):
    """更新会话统计数据"""
    # 统计数据
    result = await db.execute(
        select(
            func.count(TremorData.id).label('total'),
            func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
            func.avg(TremorData.frequency).filter(TremorData.detected == True).label('avg_freq'),
            func.avg(TremorData.rms_amplitude).label('avg_amp'),
            func.max(TremorData.severity).label('max_sev'),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev')
        ).where(TremorData.session_id == session.id)
    )
    stats = result.one()

    session.total_analyses = stats.total or 0
    session.tremor_count = stats.tremor_count or 0
    session.avg_frequency = float(stats.avg_freq) if stats.avg_freq else None
    session.avg_amplitude = float(stats.avg_amp) if stats.avg_amp else None
    session.max_severity = stats.max_sev or 0
    session.avg_severity = float(stats.avg_sev) if stats.avg_sev else None


# ============================================================
# API Endpoints
# ============================================================

@router.post("/session/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """
    开始新的检测会话

    设备开始连续检测时调用
    """
    # 获取或创建设备
    device = await get_or_create_device(db, session_data.device_id, current_user.id)

    # 结束之前的活跃会话
    result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.device_id == device.id,
                TremorSession.user_id == current_user.id,
                TremorSession.is_active == True
            )
        )
    )
    old_sessions = result.scalars().all()
    for old_session in old_sessions:
        old_session.is_active = False
        old_session.end_time = datetime.utcnow()
        if old_session.start_time:
            old_session.duration_seconds = int(
                (old_session.end_time - old_session.start_time).total_seconds()
            )

    # 创建新会话
    new_session = TremorSession(
        user_id=current_user.id,
        device_id=device.id,
        start_time=datetime.utcnow(),
        is_active=True,
        total_analyses=0,
        tremor_count=0,
        max_severity=0
    )
    db.add(new_session)
    await db.flush()
    await db.refresh(new_session)

    return SessionResponse.model_validate(new_session)


@router.post("/session/{session_id}/end", response_model=SessionResponse)
async def end_session(
    request: Request,
    session_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """
    结束检测会话

    计算汇总统计数据
    """
    # 查找会话
    result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.id == session_id,
                TremorSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "data.session_not_found")
        )

    # 结束会话
    session.is_active = False
    session.end_time = datetime.utcnow()
    if session.start_time:
        session.duration_seconds = int(
            (session.end_time - session.start_time).total_seconds()
        )

    # 计算统计数据
    stats_result = await db.execute(
        select(
            func.count(TremorData.id).label('total'),
            func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
            func.avg(TremorData.frequency).filter(TremorData.detected == True).label('avg_freq'),
            func.avg(TremorData.rms_amplitude).label('avg_amp'),
            func.max(TremorData.severity).label('max_sev'),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev')
        ).where(TremorData.session_id == session.id)
    )
    stats = stats_result.one()

    session.total_analyses = stats.total or 0
    session.tremor_count = stats.tremor_count or 0
    session.avg_frequency = float(stats.avg_freq) if stats.avg_freq else None
    session.avg_amplitude = float(stats.avg_amp) if stats.avg_amp else None
    session.max_severity = stats.max_sev or 0
    session.avg_severity = float(stats.avg_sev) if stats.avg_sev else None

    await db.flush()
    await db.refresh(session)

    return SessionResponse.model_validate(session)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_tremor_data(
    request: Request,
    data: TremorDataUpload,
    _: None = Depends(verify_device_key),
    db: AsyncSession = Depends(get_db)
):
    """
    上传单条震颤数据

    设备每次分析后调用此接口上传数据
    设备通过 X-Device-Key 头进行认证
    """
    # 获取或创建设备
    device = await get_or_create_device(db, data.device_id)

    # 如果设备有绑定用户，获取或创建会话
    session_id = None
    if device.owner_id:
        session = await get_or_create_active_session(db, device, device.owner_id)
        session_id = session.id

        # 创建数据记录
        tremor_data = TremorData(
            session_id=session.id,
            timestamp=data.timestamp or datetime.utcnow(),
            detected=data.detected,
            valid=data.valid,
            out_of_range=data.out_of_range,
            frequency=data.frequency,
            peak_power=data.peak_power,
            band_power=data.band_power,
            amplitude=data.amplitude,
            rms_amplitude=data.rms_amplitude,
            severity=data.severity,
            severity_label=data.severity_label,
            spectrum_data=data.spectrum_data
        )
        db.add(tremor_data)

        # 更新会话统计
        session.total_analyses += 1
        if data.detected:
            session.tremor_count += 1
        if data.severity > session.max_severity:
            session.max_severity = data.severity

        await db.flush()

        return UploadResponse(
            status="ok",
            message=msg(get_locale(request), "data.upload_received"),
            session_id=session_id,
            data_id=tremor_data.id
        )

    return UploadResponse(
        status="ok",
        message=msg(get_locale(request), "data.upload_received"),
        session_id=None,
        data_id=None
    )


@router.post("/upload/batch", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_batch_data(
    request: Request,
    batch: BatchUpload,
    _: None = Depends(verify_device_key),
    db: AsyncSession = Depends(get_db)
):
    """
    批量上传震颤数据

    设备离线时本地缓存数据，联网后批量上传
    """
    if not batch.data:
        return UploadResponse(status="ok", message=msg(get_locale(request), "data.batch_received"), session_id=None)

    # 获取或创建设备
    device = await get_or_create_device(db, batch.device_id)

    if not device.owner_id:
        return UploadResponse(
            status="ok",
            message=msg(get_locale(request), "data.batch_received"),
            session_id=None
        )

    # 获取或创建会话
    if batch.session_id:
        result = await db.execute(
            select(TremorSession).where(TremorSession.id == batch.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            session = await get_or_create_active_session(db, device, device.owner_id)
    else:
        session = await get_or_create_active_session(db, device, device.owner_id)

    # 批量插入数据
    tremor_count = 0
    max_severity = session.max_severity

    for item in batch.data:
        tremor_data = TremorData(
            session_id=session.id,
            timestamp=item.timestamp or datetime.utcnow(),
            detected=item.detected,
            valid=item.valid,
            out_of_range=item.out_of_range,
            frequency=item.frequency,
            peak_power=item.peak_power,
            band_power=item.band_power,
            amplitude=item.amplitude,
            rms_amplitude=item.rms_amplitude,
            severity=item.severity,
            severity_label=item.severity_label,
            spectrum_data=item.spectrum_data
        )
        db.add(tremor_data)

        if item.detected:
            tremor_count += 1
        if item.severity > max_severity:
            max_severity = item.severity

    # 更新会话统计
    session.total_analyses += len(batch.data)
    session.tremor_count += tremor_count
    session.max_severity = max_severity

    await db.flush()

    return UploadResponse(
        status="ok",
        message=msg(get_locale(request), "data.batch_received"),
        session_id=session.id
    )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(
    request: Request,
    session_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取会话详情"""
    result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.id == session_id,
                TremorSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "data.session_not_found")
        )

    return SessionResponse.model_validate(session)


@router.get("/session/{session_id}/data", response_model=List[TremorDataResponse])
async def get_session_data(
    request: Request,
    session_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """获取会话中的震颤数据"""
    # 验证会话所有权
    session_result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.id == session_id,
                TremorSession.user_id == current_user.id
            )
        )
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg(get_locale(request), "data.session_not_found")
        )

    # 查询数据
    result = await db.execute(
        select(TremorData)
        .where(TremorData.session_id == session_id)
        .order_by(TremorData.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )
    data_list = result.scalars().all()

    return [TremorDataResponse.model_validate(d) for d in data_list]


@router.get("/history", response_model=List[SessionResponse])
async def get_history(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    device_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    获取历史检测会话

    支持按时间范围和设备筛选
    """
    query = select(TremorSession).where(TremorSession.user_id == current_user.id)

    # 时间筛选
    if start_date:
        query = query.where(TremorSession.start_time >= start_date)
    if end_date:
        query = query.where(TremorSession.start_time <= end_date)

    # 设备筛选
    if device_id:
        device_result = await db.execute(
            select(Device).where(Device.device_id == device_id)
        )
        device = device_result.scalar_one_or_none()
        if device:
            query = query.where(TremorSession.device_id == device.id)

    # 排序和分页
    query = query.order_by(TremorSession.start_time.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/recent", response_model=List[TremorDataResponse])
async def get_recent_data(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
):
    """
    获取最近的震颤数据

    跨会话获取最新数据
    """
    # 获取用户所有会话的ID
    sessions_result = await db.execute(
        select(TremorSession.id).where(TremorSession.user_id == current_user.id)
    )
    session_ids = list(sessions_result.scalars().all())

    if not session_ids:
        return []

    # 查询最近数据
    result = await db.execute(
        select(TremorData)
        .where(TremorData.session_id.in_(session_ids))
        .order_by(TremorData.timestamp.desc())
        .limit(limit)
    )
    data_list = result.scalars().all()

    return [TremorDataResponse.model_validate(d) for d in data_list]


@router.get("/stats/today")
async def get_today_stats(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取今日统计"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取用户今日会话
    sessions_result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.user_id == current_user.id,
                TremorSession.start_time >= today_start
            )
        )
    )
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]

    if not session_ids:
        return {
            "date": today_start.date().isoformat(),
            "total_sessions": 0,
            "total_analyses": 0,
            "tremor_detections": 0,
            "detection_rate": 0,
            "avg_severity": 0,
            "max_severity": 0
        }

    # 统计数据
    stats_result = await db.execute(
        select(
            func.count(TremorData.id).label('total'),
            func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
            func.max(TremorData.severity).label('max_sev'),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev')
        ).where(TremorData.session_id.in_(session_ids))
    )
    stats = stats_result.one()

    total = stats.total or 0
    tremor_count = stats.tremor_count or 0
    detection_rate = (tremor_count / total * 100) if total > 0 else 0

    return {
        "date": today_start.date().isoformat(),
        "total_sessions": len(sessions),
        "total_analyses": total,
        "tremor_detections": tremor_count,
        "detection_rate": round(detection_rate, 1),
        "avg_severity": round(float(stats.avg_sev or 0), 2),
        "max_severity": stats.max_sev or 0
    }
