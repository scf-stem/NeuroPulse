"""
Tremor Guard - Analysis API
震颤卫士 - 数据分析接口

完整实现震颤数据的统计分析功能
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List

from app.core.database import get_db
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.device import Device
from app.models.tremor_data import TremorData, TremorSession

router = APIRouter()


# ============================================================
# Pydantic Schemas
# ============================================================

class DailyStats(BaseModel):
    """每日统计"""
    date: date
    total_sessions: int
    total_analyses: int
    tremor_detections: int
    detection_rate: float
    avg_frequency: Optional[float]
    avg_amplitude: Optional[float]
    avg_severity: Optional[float]
    max_severity: int


class WeeklyTrend(BaseModel):
    """周趋势"""
    week_start: date
    week_end: date
    daily_stats: List[DailyStats]
    overall_detection_rate: float
    severity_trend: str


class SeverityDistribution(BaseModel):
    """严重度分布"""
    level_0: int
    level_1: int
    level_2: int
    level_3: int
    level_4: int
    total: int


class HourlyDistribution(BaseModel):
    """时段分布"""
    hour: int
    count: int
    tremor_count: int
    avg_severity: float


class AnalysisSummary(BaseModel):
    """分析摘要"""
    period_start: datetime
    period_end: datetime
    total_sessions: int
    total_analyses: int
    tremor_detections: int
    detection_rate: float
    avg_severity: float
    max_severity: int
    avg_frequency: Optional[float]
    avg_amplitude: Optional[float]
    severity_distribution: SeverityDistribution
    hourly_distribution: List[HourlyDistribution]


# ============================================================
# Helper Functions
# ============================================================

async def get_user_session_ids(
    db: AsyncSession,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[int]:
    """获取用户在指定时间范围内的会话ID"""
    query = select(TremorSession.id).where(TremorSession.user_id == user_id)

    if start_date:
        query = query.where(TremorSession.start_time >= start_date)
    if end_date:
        query = query.where(TremorSession.start_time <= end_date)

    result = await db.execute(query)
    return [row.id for row in result.all()]


# ============================================================
# API Endpoints
# ============================================================

@router.get("/daily")
async def get_daily_stats(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    target_date: Optional[date] = None
):
    """
    获取每日统计

    默认返回今天的统计数据
    """
    if not target_date:
        target_date = date.today()

    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    # 获取会话
    sessions_result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.user_id == current_user.id,
                TremorSession.start_time >= start_datetime,
                TremorSession.start_time <= end_datetime
            )
        )
    )
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]

    if not session_ids:
        return DailyStats(
            date=target_date,
            total_sessions=0,
            total_analyses=0,
            tremor_detections=0,
            detection_rate=0,
            avg_frequency=None,
            avg_amplitude=None,
            avg_severity=None,
            max_severity=0
        )

    # 统计数据
    stats_result = await db.execute(
        select(
            func.count(TremorData.id).label('total'),
            func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
            func.avg(TremorData.frequency).filter(TremorData.detected == True).label('avg_freq'),
            func.avg(TremorData.rms_amplitude).label('avg_amp'),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev'),
            func.max(TremorData.severity).label('max_sev')
        ).where(TremorData.session_id.in_(session_ids))
    )
    stats = stats_result.one()

    total = stats.total or 0
    tremor_count = stats.tremor_count or 0
    detection_rate = (tremor_count / total * 100) if total > 0 else 0

    return DailyStats(
        date=target_date,
        total_sessions=len(sessions),
        total_analyses=total,
        tremor_detections=tremor_count,
        detection_rate=round(detection_rate, 1),
        avg_frequency=round(float(stats.avg_freq), 2) if stats.avg_freq else None,
        avg_amplitude=round(float(stats.avg_amp), 4) if stats.avg_amp else None,
        avg_severity=round(float(stats.avg_sev), 2) if stats.avg_sev else None,
        max_severity=stats.max_sev or 0
    )


@router.get("/weekly")
async def get_weekly_trend(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    week_offset: int = Query(0, ge=0, le=52)
):
    """
    获取周趋势分析

    week_offset: 0=本周, 1=上周...
    """
    today = date.today()
    # 计算本周开始（周一）
    week_start = today - timedelta(days=today.weekday() + (week_offset * 7))
    week_end = week_start + timedelta(days=6)

    daily_stats_list = []
    total_analyses = 0
    total_tremors = 0
    severity_values = []

    # 获取每天的统计
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        start_datetime = datetime.combine(current_date, datetime.min.time())
        end_datetime = datetime.combine(current_date, datetime.max.time())

        # 获取会话
        sessions_result = await db.execute(
            select(TremorSession).where(
                and_(
                    TremorSession.user_id == current_user.id,
                    TremorSession.start_time >= start_datetime,
                    TremorSession.start_time <= end_datetime
                )
            )
        )
        sessions = sessions_result.scalars().all()
        session_ids = [s.id for s in sessions]

        if session_ids:
            stats_result = await db.execute(
                select(
                    func.count(TremorData.id).label('total'),
                    func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
                    func.avg(TremorData.frequency).filter(TremorData.detected == True).label('avg_freq'),
                    func.avg(TremorData.rms_amplitude).label('avg_amp'),
                    func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev'),
                    func.max(TremorData.severity).label('max_sev')
                ).where(TremorData.session_id.in_(session_ids))
            )
            stats = stats_result.one()

            day_total = stats.total or 0
            day_tremors = stats.tremor_count or 0
            detection_rate = (day_tremors / day_total * 100) if day_total > 0 else 0

            total_analyses += day_total
            total_tremors += day_tremors
            if stats.avg_sev:
                severity_values.append(float(stats.avg_sev))

            daily_stats_list.append(DailyStats(
                date=current_date,
                total_sessions=len(sessions),
                total_analyses=day_total,
                tremor_detections=day_tremors,
                detection_rate=round(detection_rate, 1),
                avg_frequency=round(float(stats.avg_freq), 2) if stats.avg_freq else None,
                avg_amplitude=round(float(stats.avg_amp), 4) if stats.avg_amp else None,
                avg_severity=round(float(stats.avg_sev), 2) if stats.avg_sev else None,
                max_severity=stats.max_sev or 0
            ))
        else:
            daily_stats_list.append(DailyStats(
                date=current_date,
                total_sessions=0,
                total_analyses=0,
                tremor_detections=0,
                detection_rate=0,
                avg_frequency=None,
                avg_amplitude=None,
                avg_severity=None,
                max_severity=0
            ))

    # 计算趋势
    overall_detection_rate = (total_tremors / total_analyses * 100) if total_analyses > 0 else 0

    # 简单趋势判断：比较前半周和后半周的平均严重度
    if len(severity_values) >= 4:
        first_half = sum(severity_values[:len(severity_values)//2]) / (len(severity_values)//2)
        second_half = sum(severity_values[len(severity_values)//2:]) / (len(severity_values) - len(severity_values)//2)

        if second_half < first_half * 0.9:
            severity_trend = "improving"
        elif second_half > first_half * 1.1:
            severity_trend = "worsening"
        else:
            severity_trend = "stable"
    else:
        severity_trend = "stable"

    return WeeklyTrend(
        week_start=week_start,
        week_end=week_end,
        daily_stats=daily_stats_list,
        overall_detection_rate=round(overall_detection_rate, 1),
        severity_trend=severity_trend
    )


@router.get("/severity-distribution")
async def get_severity_distribution(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    days: int = Query(7, ge=1, le=90)
):
    """
    获取严重度分布

    统计各严重度等级的检测次数
    """
    if not start_date:
        start_date = datetime.now() - timedelta(days=days)
    if not end_date:
        end_date = datetime.now()

    session_ids = await get_user_session_ids(db, current_user.id, start_date, end_date)

    if not session_ids:
        return SeverityDistribution(
            level_0=0,
            level_1=0,
            level_2=0,
            level_3=0,
            level_4=0,
            total=0
        )

    # 统计各严重度等级
    result = await db.execute(
        select(
            func.count(TremorData.id).filter(TremorData.severity == 0).label('level_0'),
            func.count(TremorData.id).filter(TremorData.severity == 1).label('level_1'),
            func.count(TremorData.id).filter(TremorData.severity == 2).label('level_2'),
            func.count(TremorData.id).filter(TremorData.severity == 3).label('level_3'),
            func.count(TremorData.id).filter(TremorData.severity == 4).label('level_4'),
            func.count(TremorData.id).label('total')
        ).where(TremorData.session_id.in_(session_ids))
    )
    stats = result.one()

    return SeverityDistribution(
        level_0=stats.level_0 or 0,
        level_1=stats.level_1 or 0,
        level_2=stats.level_2 or 0,
        level_3=stats.level_3 or 0,
        level_4=stats.level_4 or 0,
        total=stats.total or 0
    )


@router.get("/hourly-distribution")
async def get_hourly_distribution(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90)
):
    """
    获取时段分布

    分析一天中各时段的震颤情况
    """
    start_date = datetime.now() - timedelta(days=days)
    session_ids = await get_user_session_ids(db, current_user.id, start_date)

    if not session_ids:
        return [HourlyDistribution(hour=h, count=0, tremor_count=0, avg_severity=0) for h in range(24)]

    # 获取所有数据
    result = await db.execute(
        select(TremorData).where(TremorData.session_id.in_(session_ids))
    )
    data_list = result.scalars().all()

    # 按小时统计
    hourly_stats = {}
    for h in range(24):
        hourly_stats[h] = {'count': 0, 'tremor_count': 0, 'severity_sum': 0}

    for data in data_list:
        hour = data.timestamp.hour
        hourly_stats[hour]['count'] += 1
        if data.detected:
            hourly_stats[hour]['tremor_count'] += 1
            hourly_stats[hour]['severity_sum'] += data.severity

    distribution = []
    for h in range(24):
        stats = hourly_stats[h]
        avg_sev = (stats['severity_sum'] / stats['tremor_count']) if stats['tremor_count'] > 0 else 0
        distribution.append(HourlyDistribution(
            hour=h,
            count=stats['count'],
            tremor_count=stats['tremor_count'],
            avg_severity=round(avg_sev, 2)
        ))

    return distribution


@router.get("/summary")
async def get_analysis_summary(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90)
):
    """
    获取分析摘要

    综合统计指标
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 获取会话
    sessions_result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.user_id == current_user.id,
                TremorSession.start_time >= start_date,
                TremorSession.start_time <= end_date
            )
        )
    )
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]

    if not session_ids:
        return AnalysisSummary(
            period_start=start_date,
            period_end=end_date,
            total_sessions=0,
            total_analyses=0,
            tremor_detections=0,
            detection_rate=0,
            avg_severity=0,
            max_severity=0,
            avg_frequency=None,
            avg_amplitude=None,
            severity_distribution=SeverityDistribution(
                level_0=0, level_1=0, level_2=0, level_3=0, level_4=0, total=0
            ),
            hourly_distribution=[]
        )

    # 基础统计
    stats_result = await db.execute(
        select(
            func.count(TremorData.id).label('total'),
            func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
            func.avg(TremorData.frequency).filter(TremorData.detected == True).label('avg_freq'),
            func.avg(TremorData.rms_amplitude).label('avg_amp'),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev'),
            func.max(TremorData.severity).label('max_sev')
        ).where(TremorData.session_id.in_(session_ids))
    )
    stats = stats_result.one()

    # 严重度分布
    dist_result = await db.execute(
        select(
            func.count(TremorData.id).filter(TremorData.severity == 0).label('level_0'),
            func.count(TremorData.id).filter(TremorData.severity == 1).label('level_1'),
            func.count(TremorData.id).filter(TremorData.severity == 2).label('level_2'),
            func.count(TremorData.id).filter(TremorData.severity == 3).label('level_3'),
            func.count(TremorData.id).filter(TremorData.severity == 4).label('level_4'),
            func.count(TremorData.id).label('total')
        ).where(TremorData.session_id.in_(session_ids))
    )
    dist = dist_result.one()

    # 时段分布
    data_result = await db.execute(
        select(TremorData).where(TremorData.session_id.in_(session_ids))
    )
    data_list = data_result.scalars().all()

    hourly_stats = {}
    for h in range(24):
        hourly_stats[h] = {'count': 0, 'tremor_count': 0, 'severity_sum': 0}

    for data in data_list:
        hour = data.timestamp.hour
        hourly_stats[hour]['count'] += 1
        if data.detected:
            hourly_stats[hour]['tremor_count'] += 1
            hourly_stats[hour]['severity_sum'] += data.severity

    hourly_distribution = []
    for h in range(24):
        s = hourly_stats[h]
        avg_sev = (s['severity_sum'] / s['tremor_count']) if s['tremor_count'] > 0 else 0
        hourly_distribution.append(HourlyDistribution(
            hour=h,
            count=s['count'],
            tremor_count=s['tremor_count'],
            avg_severity=round(avg_sev, 2)
        ))

    total = stats.total or 0
    tremor_count = stats.tremor_count or 0
    detection_rate = (tremor_count / total * 100) if total > 0 else 0

    return AnalysisSummary(
        period_start=start_date,
        period_end=end_date,
        total_sessions=len(sessions),
        total_analyses=total,
        tremor_detections=tremor_count,
        detection_rate=round(detection_rate, 1),
        avg_severity=round(float(stats.avg_sev), 2) if stats.avg_sev else 0,
        max_severity=stats.max_sev or 0,
        avg_frequency=round(float(stats.avg_freq), 2) if stats.avg_freq else None,
        avg_amplitude=round(float(stats.avg_amp), 4) if stats.avg_amp else None,
        severity_distribution=SeverityDistribution(
            level_0=dist.level_0 or 0,
            level_1=dist.level_1 or 0,
            level_2=dist.level_2 or 0,
            level_3=dist.level_3 or 0,
            level_4=dist.level_4 or 0,
            total=dist.total or 0
        ),
        hourly_distribution=hourly_distribution
    )


@router.get("/trend")
async def get_trend(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=7, le=365)
):
    """
    获取趋势数据

    返回每日检测率和严重度用于图表
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    trend_data = []

    for i in range(days):
        current_date = (start_date + timedelta(days=i)).date()
        start_datetime = datetime.combine(current_date, datetime.min.time())
        end_datetime = datetime.combine(current_date, datetime.max.time())

        sessions_result = await db.execute(
            select(TremorSession.id).where(
                and_(
                    TremorSession.user_id == current_user.id,
                    TremorSession.start_time >= start_datetime,
                    TremorSession.start_time <= end_datetime
                )
            )
        )
        session_ids = [s.id for s in sessions_result.all()]

        if session_ids:
            stats_result = await db.execute(
                select(
                    func.count(TremorData.id).label('total'),
                    func.count(TremorData.id).filter(TremorData.detected == True).label('tremor_count'),
                    func.avg(TremorData.severity).filter(TremorData.detected == True).label('avg_sev')
                ).where(TremorData.session_id.in_(session_ids))
            )
            stats = stats_result.one()

            total = stats.total or 0
            tremor_count = stats.tremor_count or 0
            detection_rate = (tremor_count / total * 100) if total > 0 else 0

            trend_data.append({
                "date": current_date.isoformat(),
                "total_analyses": total,
                "tremor_count": tremor_count,
                "detection_rate": round(detection_rate, 1),
                "avg_severity": round(float(stats.avg_sev), 2) if stats.avg_sev else None
            })
        else:
            trend_data.append({
                "date": current_date.isoformat(),
                "total_analyses": 0,
                "tremor_count": 0,
                "detection_rate": 0,
                "avg_severity": None
            })

    return trend_data
