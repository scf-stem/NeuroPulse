"""
Neuro Pulse - Report API
Neuro Pulse - 报告生成接口

完整实现报告生成、导出功能
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List
from enum import Enum
import io
import csv
import json
import uuid

from app.core.database import get_db
from app.core.i18n import get_locale, msg
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.tremor import TremorData, TremorSession

router = APIRouter()


# ============================================================
# Enums
# ============================================================

class ReportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# ============================================================
# Pydantic Schemas
# ============================================================

class ReportRequest(BaseModel):
    """报告生成请求"""
    report_type: ReportType = ReportType.WEEKLY
    format: ReportFormat = ReportFormat.JSON
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    device_id: Optional[str] = None
    include_ai_analysis: bool = True


class ReportSummary(BaseModel):
    """报告摘要"""
    period_start: datetime
    period_end: datetime
    total_sessions: int
    total_analyses: int
    tremor_detections: int
    detection_rate: float
    avg_severity: float
    max_severity: int
    total_duration_minutes: int


class ReportData(BaseModel):
    """完整报告数据"""
    report_id: str
    report_type: ReportType
    generated_at: datetime
    summary: ReportSummary
    daily_breakdown: List[dict]
    severity_distribution: dict
    hourly_pattern: List[dict]
    sessions: List[dict]


# ============================================================
# Helper Functions
# ============================================================

def get_date_range(report_type: ReportType, start_date: Optional[datetime], end_date: Optional[datetime]):
    """根据报告类型获取日期范围"""
    now = datetime.utcnow()

    if report_type == ReportType.DAILY:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif report_type == ReportType.WEEKLY:
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif report_type == ReportType.MONTHLY:
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif report_type == ReportType.CUSTOM:
        if not start_date or not end_date:
            raise ValueError("自定义报告需要指定起止日期")
        start = start_date
        end = end_date

    return start, end


# ============================================================
# API Endpoints
# ============================================================

@router.post("/generate", response_model=ReportData)
async def generate_report(
    request_http: Request,
    request: ReportRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """
    生成报告

    根据指定参数生成震颤分析报告
    """
    try:
        start_date, end_date = get_date_range(
            request.report_type,
            request.start_date,
            request.end_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg(get_locale(request_http), "report.custom_dates_required")
        )

    # 查询会话数据
    session_query = select(TremorSession).where(
        and_(
            TremorSession.user_id == current_user.id,
            TremorSession.start_time >= start_date,
            TremorSession.start_time <= end_date
        )
    ).order_by(TremorSession.start_time.desc())

    result = await db.execute(session_query)
    sessions = result.scalars().all()

    # 查询震颤数据
    data_query = select(TremorData).where(
        and_(
            TremorData.user_id == current_user.id,
            TremorData.timestamp >= start_date,
            TremorData.timestamp <= end_date
        )
    )

    result = await db.execute(data_query)
    tremor_data = result.scalars().all()

    # 计算统计数据
    total_analyses = len(tremor_data)
    tremor_detections = sum(1 for d in tremor_data if d.detected)
    detection_rate = (tremor_detections / total_analyses * 100) if total_analyses > 0 else 0

    severities = [d.severity for d in tremor_data if d.detected and d.severity is not None]
    avg_severity = sum(severities) / len(severities) if severities else 0
    max_severity = max(severities) if severities else 0

    total_duration = sum(s.duration_seconds or 0 for s in sessions)

    # 按日分组统计
    daily_breakdown = {}
    for d in tremor_data:
        day_key = d.timestamp.strftime('%Y-%m-%d')
        if day_key not in daily_breakdown:
            daily_breakdown[day_key] = {
                'date': day_key,
                'total': 0,
                'tremors': 0,
                'avg_severity': 0,
                'severities': []
            }
        daily_breakdown[day_key]['total'] += 1
        if d.detected:
            daily_breakdown[day_key]['tremors'] += 1
            if d.severity is not None:
                daily_breakdown[day_key]['severities'].append(d.severity)

    # 计算每日平均严重度
    daily_list = []
    for day_key, day_data in sorted(daily_breakdown.items()):
        severities = day_data.pop('severities')
        day_data['avg_severity'] = sum(severities) / len(severities) if severities else 0
        daily_list.append(day_data)

    # 严重度分布
    severity_dist = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for d in tremor_data:
        if d.severity is not None and d.severity in severity_dist:
            severity_dist[d.severity] += 1

    # 小时分布
    hourly_pattern = {h: {'hour': h, 'count': 0, 'tremors': 0} for h in range(24)}
    for d in tremor_data:
        hour = d.timestamp.hour
        hourly_pattern[hour]['count'] += 1
        if d.detected:
            hourly_pattern[hour]['tremors'] += 1
    hourly_list = list(hourly_pattern.values())

    # 构建会话列表
    sessions_list = []
    for s in sessions:
        sessions_list.append({
            'id': s.id,
            'start_time': s.start_time.isoformat(),
            'end_time': s.end_time.isoformat() if s.end_time else None,
            'duration_seconds': s.duration_seconds,
            'total_analyses': s.total_analyses,
            'tremor_count': s.tremor_count,
            'avg_severity': s.avg_severity,
            'max_severity': s.max_severity
        })

    # 构建报告
    report = ReportData(
        report_id=str(uuid.uuid4()),
        report_type=request.report_type,
        generated_at=datetime.utcnow(),
        summary=ReportSummary(
            period_start=start_date,
            period_end=end_date,
            total_sessions=len(sessions),
            total_analyses=total_analyses,
            tremor_detections=tremor_detections,
            detection_rate=round(detection_rate, 2),
            avg_severity=round(avg_severity, 2),
            max_severity=max_severity,
            total_duration_minutes=total_duration // 60
        ),
        daily_breakdown=daily_list,
        severity_distribution=severity_dist,
        hourly_pattern=hourly_list,
        sessions=sessions_list
    )

    return report


@router.get("/export/csv")
async def export_csv(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="开始日期"),
    end_date: datetime = Query(..., description="结束日期"),
    device_id: Optional[str] = None
):
    """
    导出 CSV 数据

    导出指定时间范围内的原始震颤数据
    """
    # 构建查询
    conditions = [
        TremorData.user_id == current_user.id,
        TremorData.timestamp >= start_date,
        TremorData.timestamp <= end_date
    ]

    if device_id:
        conditions.append(TremorData.device_id == device_id)

    query = select(TremorData).where(and_(*conditions)).order_by(TremorData.timestamp)
    result = await db.execute(query)
    data = result.scalars().all()

    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        'timestamp', 'device_id', 'detected', 'frequency',
        'rms_amplitude', 'peak_amplitude', 'severity',
        'accel_x', 'accel_y', 'accel_z'
    ])

    # 写入数据
    for d in data:
        writer.writerow([
            d.timestamp.isoformat(),
            d.device_id,
            d.detected,
            d.frequency,
            d.rms_amplitude,
            d.peak_amplitude,
            d.severity,
            d.accel_x,
            d.accel_y,
            d.accel_z
        ])

    output.seek(0)

    # 生成文件名
    filename = f"tremor_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/json")
async def export_json(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    start_date: datetime = Query(..., description="开始日期"),
    end_date: datetime = Query(..., description="结束日期"),
    device_id: Optional[str] = None
):
    """
    导出 JSON 数据

    导出指定时间范围内的原始震颤数据（JSON 格式）
    """
    # 构建查询
    conditions = [
        TremorData.user_id == current_user.id,
        TremorData.timestamp >= start_date,
        TremorData.timestamp <= end_date
    ]

    if device_id:
        conditions.append(TremorData.device_id == device_id)

    query = select(TremorData).where(and_(*conditions)).order_by(TremorData.timestamp)
    result = await db.execute(query)
    data = result.scalars().all()

    # 构建 JSON 数据
    json_data = {
        "export_info": {
            "generated_at": datetime.utcnow().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_records": len(data)
        },
        "data": []
    }

    for d in data:
        json_data["data"].append({
            "timestamp": d.timestamp.isoformat(),
            "device_id": d.device_id,
            "detected": d.detected,
            "frequency": d.frequency,
            "rms_amplitude": d.rms_amplitude,
            "peak_amplitude": d.peak_amplitude,
            "severity": d.severity,
            "accelerometer": {
                "x": d.accel_x,
                "y": d.accel_y,
                "z": d.accel_z
            }
        })

    # 生成文件名
    filename = f"tremor_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"

    return StreamingResponse(
        iter([json.dumps(json_data, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/summary/doctor")
async def get_doctor_summary(
    request: Request,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="统计天数")
):
    """
    医生摘要报告

    生成适合医生查看的简洁摘要，包含关键指标和趋势变化
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # 前一个周期，用于对比
    prev_end_date = start_date
    prev_start_date = prev_end_date - timedelta(days=days)

    # 当前周期数据
    query = select(TremorData).where(
        and_(
            TremorData.user_id == current_user.id,
            TremorData.timestamp >= start_date,
            TremorData.timestamp <= end_date
        )
    )
    result = await db.execute(query)
    current_data = result.scalars().all()

    # 前一周期数据
    query = select(TremorData).where(
        and_(
            TremorData.user_id == current_user.id,
            TremorData.timestamp >= prev_start_date,
            TremorData.timestamp <= prev_end_date
        )
    )
    result = await db.execute(query)
    prev_data = result.scalars().all()

    # 计算当前周期统计
    current_tremors = sum(1 for d in current_data if d.detected)
    current_severities = [d.severity for d in current_data if d.detected and d.severity]
    current_avg_severity = sum(current_severities) / len(current_severities) if current_severities else 0

    # 计算前一周期统计
    prev_tremors = sum(1 for d in prev_data if d.detected)
    prev_severities = [d.severity for d in prev_data if d.detected and d.severity]
    prev_avg_severity = sum(prev_severities) / len(prev_severities) if prev_severities else 0

    # 判断趋势
    if current_avg_severity > prev_avg_severity * 1.1:
        severity_trend = "worsening"
    elif current_avg_severity < prev_avg_severity * 0.9:
        severity_trend = "improving"
    else:
        severity_trend = "stable"

    if current_tremors > prev_tremors * 1.2:
        frequency_trend = "increasing"
    elif current_tremors < prev_tremors * 0.8:
        frequency_trend = "decreasing"
    else:
        frequency_trend = "stable"

    # 生成观察结论
    observations = []
    if severity_trend == "worsening":
        observations.append(msg(get_locale(request), "report.observation.severity_up"))
    elif severity_trend == "improving":
        observations.append(msg(get_locale(request), "report.observation.severity_down"))

    if frequency_trend == "increasing":
        observations.append(msg(get_locale(request), "report.observation.frequency_up"))
    elif frequency_trend == "decreasing":
        observations.append(msg(get_locale(request), "report.observation.frequency_down"))

    # 严重程度 3 或 4 的次数
    severe_count = sum(1 for d in current_data if d.detected and d.severity and d.severity >= 3)
    if severe_count > 0:
        observations.append(msg(get_locale(request), "report.observation.severe_count", count=severe_count, days=days))

    # 生成建议
    recommendations = []
    if severity_trend == "worsening" or severe_count > 5:
        recommendations.append(msg(get_locale(request), "report.recommendation.medication"))
    if current_avg_severity > 2:
        recommendations.append(msg(get_locale(request), "report.recommendation.monitoring"))
    if len(current_data) < days * 10:  # 平均每天少于10条数据
        recommendations.append(msg(get_locale(request), "report.recommendation.wear_time"))

    return {
        "patient_info": {
            "username": current_user.username,
            "full_name": current_user.full_name
        },
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": days
        },
        "summary": {
            "total_monitoring_records": len(current_data),
            "tremor_episodes": current_tremors,
            "avg_severity": round(current_avg_severity, 2),
            "max_severity": max(current_severities) if current_severities else 0,
            "severe_episodes": severe_count,
            "severity_trend": severity_trend,
            "frequency_trend": frequency_trend
        },
        "comparison": {
            "prev_period_tremors": prev_tremors,
            "prev_period_avg_severity": round(prev_avg_severity, 2),
            "tremor_change_percent": round((current_tremors - prev_tremors) / prev_tremors * 100, 1) if prev_tremors > 0 else 0,
            "severity_change_percent": round((current_avg_severity - prev_avg_severity) / prev_avg_severity * 100, 1) if prev_avg_severity > 0 else 0
        },
        "key_observations": observations,
        "recommendations": recommendations
    }


@router.get("/quick-stats")
async def get_quick_stats(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """
    快速统计

    返回关键统计数据，用于报告页面概览
    """
    now = datetime.utcnow()

    # 今日
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 本周
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    # 本月
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    async def get_period_stats(start: datetime, end: datetime):
        session_query = select(TremorSession.id).where(
            and_(
                TremorSession.user_id == current_user.id,
                TremorSession.start_time >= start,
                TremorSession.start_time <= end
            )
        )
        session_result = await db.execute(session_query)
        session_ids = session_result.scalars().all()

        if not session_ids:
            return {
                "total_analyses": 0,
                "tremor_count": 0,
                "avg_severity": 0,
            }

        query = select(TremorData).where(TremorData.session_id.in_(session_ids))
        result = await db.execute(query)
        data = result.scalars().all()

        total = len(data)
        tremors = sum(1 for d in data if d.detected)
        severities = [d.severity for d in data if d.detected and d.severity]
        avg_severity = sum(severities) / len(severities) if severities else 0

        return {
            "total_analyses": total,
            "tremor_count": tremors,
            "avg_severity": round(avg_severity, 2)
        }

    today_stats = await get_period_stats(today_start, now)
    week_stats = await get_period_stats(week_start, now)
    month_stats = await get_period_stats(month_start, now)

    return {
        "today": today_stats,
        "this_week": week_stats,
        "this_month": month_stats
    }
