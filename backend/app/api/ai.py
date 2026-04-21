"""
Neuro Pulse - AI API
Neuro Pulse - AI 分析接口 (Qwen)

增强为支持聊天动作卡片：
- 先返回康复计划 / AI 健康报告摘要卡片
- 用户确认后再生成详细计划或详细报告
"""

from __future__ import annotations

import io
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, List, Literal, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_from_token
from app.core.config import settings
from app.core.database import get_db
from app.core.i18n import get_locale, msg
from app.models.medication import DosageRecord, Medication
from app.models.rehabilitation import Exercise, TrainingPlan
from app.models.tremor_data import TremorData, TremorSession
from app.models.user import User

router = APIRouter()

DEMO_USER_ID = 999
AI_REPORT_STORAGE: dict[str, dict[str, Any]] = {}


class ChatMessage(BaseModel):
    role: str
    content: str


class AIAction(BaseModel):
    type: Literal[
        "confirm_rehab_plan",
        "view_rehab_page",
        "download_rehab_pdf",
        "confirm_health_report",
        "view_health_report",
        "download_health_report_pdf",
    ]
    label: str
    api_path: Optional[str] = None
    route: Optional[str] = None


class AIActionCard(BaseModel):
    kind: Literal["rehab_plan", "health_report"]
    title: str
    summary: str
    status: Literal["preview", "generated"]
    payload: Optional[dict[str, Any]] = None
    actions: List[AIAction]


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    action_card: Optional[AIActionCard] = None


class AIActionExecutionResponse(BaseModel):
    message: str
    action_card: Optional[AIActionCard] = None
    route: Optional[str] = None
    report_data: Optional[dict[str, Any]] = None


class AnalysisRequest(BaseModel):
    days: int = 7


class AnalysisResponse(BaseModel):
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    risk_level: str


REHAB_KEYWORDS = ("康复", "训练计划", "训练方案", "康复计划", "生成康复")
REPORT_KEYWORDS = ("健康报告", "监测摘要", "摘要报告", "报告", "生成报告")


async def get_user_data_summary(db: AsyncSession, user_id: int, days: int = 7) -> dict:
    if user_id == DEMO_USER_ID:
        return {
            "has_data": False,
            "days": days,
            "total_sessions": 0,
            "total_analyses": 0,
            "tremor_count": 0,
            "detection_rate": 0,
            "avg_severity": 0,
            "max_severity": 0,
        }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    sessions_result = await db.execute(
        select(TremorSession).where(
            and_(
                TremorSession.user_id == user_id,
                TremorSession.start_time >= start_date,
            )
        )
    )
    sessions = sessions_result.scalars().all()
    session_ids = [s.id for s in sessions]

    if not session_ids:
        return {
            "has_data": False,
            "days": days,
            "total_sessions": 0,
            "total_analyses": 0,
            "tremor_count": 0,
            "detection_rate": 0,
            "avg_severity": 0,
            "max_severity": 0,
        }

    stats_result = await db.execute(
        select(
            func.count(TremorData.id).label("total"),
            func.count(TremorData.id).filter(TremorData.detected == True).label("tremor_count"),
            func.avg(TremorData.frequency).filter(TremorData.detected == True).label("avg_freq"),
            func.avg(TremorData.rms_amplitude).label("avg_amp"),
            func.avg(TremorData.severity).filter(TremorData.detected == True).label("avg_sev"),
            func.max(TremorData.severity).label("max_sev"),
        ).where(TremorData.session_id.in_(session_ids))
    )
    stats = stats_result.one()

    total = stats.total or 0
    tremor_count = stats.tremor_count or 0
    detection_rate = (tremor_count / total * 100) if total > 0 else 0

    return {
        "has_data": True,
        "days": days,
        "total_sessions": len(sessions),
        "total_analyses": total,
        "tremor_count": tremor_count,
        "detection_rate": round(detection_rate, 1),
        "avg_frequency": round(float(stats.avg_freq), 2) if stats.avg_freq else None,
        "avg_amplitude": round(float(stats.avg_amp), 4) if stats.avg_amp else None,
        "avg_severity": round(float(stats.avg_sev), 2) if stats.avg_sev else 0,
        "max_severity": stats.max_sev or 0,
    }


async def get_medication_summary(db: AsyncSession, user_id: int, days: int = 7) -> dict[str, Any]:
    if user_id == DEMO_USER_ID:
        return {
            "current_medications": [],
            "record_count": 0,
            "adherence_label": "演示模式未连接真实用药记录",
        }

    start_date = datetime.now() - timedelta(days=days)
    meds_result = await db.execute(
        select(Medication).where(Medication.user_id == user_id, Medication.is_active == True)
    )
    medications = meds_result.scalars().all()
    records_result = await db.execute(
        select(DosageRecord).where(
            DosageRecord.user_id == user_id,
            DosageRecord.taken_at >= start_date,
        )
    )
    records = records_result.scalars().all()
    return {
        "current_medications": [med.name for med in medications],
        "record_count": len(records),
        "adherence_label": "有持续记录" if records else "记录不足",
    }


def _matches_keyword(message: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in message for keyword in keywords)


def _pdf_escape_hex(text: str) -> str:
    return text.encode("utf-16-be").hex().upper()


def _wrap_text(text: str, limit: int = 28) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= limit:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines or [""]


def build_pdf_bytes(title: str, sections: list[tuple[str, list[str]]]) -> bytes:
    lines = [title, "本内容仅供健康管理参考，请以专业医生意见为准。", ""]
    for heading, items in sections:
        lines.append(heading)
        for item in items:
            lines.extend(_wrap_text(f"• {item}"))
        lines.append("")

    content_lines = ["BT", "/F1 16 Tf", "48 792 Td", "20 TL"]
    first = True
    for line in lines:
        safe_line = line or " "
        if first:
            content_lines.append(f"<{_pdf_escape_hex(safe_line)}> Tj")
            first = False
        else:
            content_lines.append("T*")
            content_lines.append(f"<{_pdf_escape_hex(safe_line)}> Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1") + content_stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts [6 0 R] >>",
        b"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 4 >> /DW 1000 >>",
    ]

    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part) for part in chunks))
        chunks.append(f"{index} 0 obj\n".encode("latin-1"))
        chunks.append(obj)
        chunks.append(b"\nendobj\n")

    xref_offset = sum(len(part) for part in chunks)
    xref = [f"xref\n0 {len(objects) + 1}\n".encode("latin-1"), b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode(
            "latin-1"
        )
    )
    return b"".join(chunks + xref + [trailer])


def _extract_chat_text(result: dict[str, Any]) -> str:
    choices = result.get("choices") or []
    if not choices:
        raise ValueError("Qwen API returned no choices")

    message = (choices[0] or {}).get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text" and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
            elif isinstance(part.get("content"), str):
                text_parts.append(part["content"])

        if text_parts:
            return "".join(text_parts)

    raise ValueError("Qwen API returned an unsupported message format")


async def call_qwen_api(
    messages: list[dict[str, str]],
    system_prompt: str,
    locale: str,
    response_format: Optional[dict[str, str]] = None,
) -> str:
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=msg(locale, "ai.not_configured"),
        )

    endpoint = f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
    }
    request_messages = [{"role": "system", "content": system_prompt}, *messages]
    payload: dict[str, Any] = {
        "model": settings.DASHSCOPE_MODEL,
        "max_tokens": 1024,
        "messages": request_messages,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, headers=headers, json=payload, timeout=30.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=msg(locale, "ai.gateway_error", status_code=response.status_code),
                )
            result = response.json()
            return _extract_chat_text(result)
    except httpx.TimeoutException:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=msg(locale, "ai.timeout"))
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=msg(locale, "ai.error", error=str(e)),
        )


async def build_rehab_preview_card(db: AsyncSession, current_user: User) -> AIActionCard:
    user_data = await get_user_data_summary(db, current_user.id, 7)
    med_summary = await get_medication_summary(db, current_user.id, 7)
    summary = (
        f"基于最近7天监测：震颤检出率 {user_data['detection_rate']}%，平均严重度 {user_data['avg_severity']}；"
        f"当前用药记录状态：{med_summary['adherence_label']}。建议先确认是否生成康复训练计划，确认后系统会生成详细计划并同步到康复页面。"
    )
    return AIActionCard(
        kind="rehab_plan",
        title="康复训练计划摘要",
        summary=summary,
        status="preview",
        payload={"days": 7},
        actions=[
            AIAction(type="confirm_rehab_plan", label="确认生成计划", api_path="/api/ai/actions/rehab-plan/confirm"),
        ],
    )


async def build_health_report_preview_card(db: AsyncSession, current_user: User) -> AIActionCard:
    user_data = await get_user_data_summary(db, current_user.id, 30)
    summary = (
        f"基于最近30天监测：共 {user_data['total_sessions']} 次会话，震颤检出率 {user_data['detection_rate']}%，"
        f"最高严重度 {user_data['max_severity']}。确认后系统将生成 AI 健康报告详情，并同步到报告页面，同时支持 PDF 下载。"
    )
    return AIActionCard(
        kind="health_report",
        title="AI健康报告摘要",
        summary=summary,
        status="preview",
        payload={"days": 30},
        actions=[
            AIAction(type="confirm_health_report", label="确认生成报告", api_path="/api/ai/actions/health-report/confirm"),
        ],
    )


async def generate_health_report_data(db: AsyncSession, current_user: User, days: int = 30) -> dict[str, Any]:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    session_query = select(TremorSession).where(
        and_(
            TremorSession.user_id == current_user.id,
            TremorSession.start_time >= start_date,
            TremorSession.start_time <= end_date,
        )
    ).order_by(TremorSession.start_time.desc())
    result = await db.execute(session_query)
    sessions = result.scalars().all()

    data_query = select(TremorData).where(
        and_(
            TremorData.timestamp >= start_date,
            TremorData.timestamp <= end_date,
            TremorData.session_id.in_([s.id for s in sessions] or [-1]),
        )
    )
    result = await db.execute(data_query)
    tremor_data = result.scalars().all()

    total_analyses = len(tremor_data)
    tremor_detections = sum(1 for d in tremor_data if d.detected)
    detection_rate = (tremor_detections / total_analyses * 100) if total_analyses > 0 else 0
    severities = [d.severity for d in tremor_data if d.detected and d.severity is not None]
    avg_severity = round(sum(severities) / len(severities), 2) if severities else 0
    max_severity = max(severities) if severities else 0

    daily_breakdown: dict[str, dict[str, Any]] = {}
    for d in tremor_data:
        day_key = d.timestamp.strftime("%Y-%m-%d")
        bucket = daily_breakdown.setdefault(
            day_key, {"date": day_key, "total": 0, "tremors": 0, "avg_severity": 0, "severities": []}
        )
        bucket["total"] += 1
        if d.detected:
            bucket["tremors"] += 1
            if d.severity is not None:
                bucket["severities"].append(d.severity)
    daily_list = []
    for _, day_data in sorted(daily_breakdown.items()):
        values = day_data.pop("severities")
        day_data["avg_severity"] = round(sum(values) / len(values), 2) if values else 0
        daily_list.append(day_data)

    severity_dist = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for d in tremor_data:
        if d.severity is not None and d.severity in severity_dist:
            severity_dist[d.severity] += 1

    hourly_pattern = {h: {"hour": h, "count": 0, "tremors": 0} for h in range(24)}
    for d in tremor_data:
        hour = d.timestamp.hour
        hourly_pattern[hour]["count"] += 1
        if d.detected:
            hourly_pattern[hour]["tremors"] += 1

    return {
        "report_id": str(uuid.uuid4()),
        "report_type": "monthly" if days >= 30 else "weekly",
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_sessions": len(sessions),
            "total_analyses": total_analyses,
            "tremor_detections": tremor_detections,
            "detection_rate": round(detection_rate, 1),
            "avg_severity": avg_severity,
            "max_severity": max_severity,
            "total_duration_minutes": round(sum((s.duration_seconds or 0) for s in sessions) / 60),
        },
        "daily_breakdown": daily_list,
        "severity_distribution": severity_dist,
        "hourly_pattern": list(hourly_pattern.values()),
        "sessions": [
            {
                "id": s.id,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_seconds": s.duration_seconds,
                "total_analyses": s.total_analyses,
                "tremor_count": s.tremor_count,
                "avg_severity": s.avg_severity,
                "max_severity": s.max_severity,
            }
            for s in sessions
        ],
    }


async def create_rehab_plan(db: AsyncSession, current_user: User) -> tuple[TrainingPlan, list[Exercise]]:
    exercise_result = await db.execute(
        select(Exercise)
        .where(Exercise.is_active == True)
        .order_by(Exercise.duration_minutes.asc(), Exercise.id.asc())
        .limit(3)
    )
    exercises = exercise_result.scalars().all()
    if not exercises:
        raise HTTPException(status_code=404, detail="暂无可用训练动作，无法生成康复计划。")

    all_plans_result = await db.execute(select(TrainingPlan).where(TrainingPlan.user_id == current_user.id))
    for plan in all_plans_result.scalars().all():
        plan.is_active = False

    new_plan = TrainingPlan(
        user_id=current_user.id,
        name=f"AI康复训练计划 {datetime.utcnow().strftime('%Y-%m-%d')}",
        description="基于近期监测数据与用药记录生成的辅助康复训练计划。",
        exercise_ids=[exercise.id for exercise in exercises],
        daily_goal_minutes=sum(ex.duration_minutes for ex in exercises),
        difficulty_level="easy",
        start_date=datetime.utcnow(),
        is_active=True,
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    return new_plan, exercises


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request_http: Request,
    request: ChatRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    message = request.message.strip()
    if _matches_keyword(message, REHAB_KEYWORDS):
        return ChatResponse(
            response="已根据近期多维数据整理出康复训练计划摘要。请先确认，确认后我再生成详细计划并同步到康复训练页面。",
            suggestions=["确认生成计划", "先看摘要", "暂不生成"],
            action_card=await build_rehab_preview_card(db, current_user),
        )

    if _matches_keyword(message, REPORT_KEYWORDS):
        return ChatResponse(
            response="已根据近期监测与用药情况整理出 AI 健康报告摘要。请先确认，确认后我再生成详细报告并同步到 AI 健康报告页面。",
            suggestions=["确认生成报告", "先看摘要", "暂不生成"],
            action_card=await build_health_report_preview_card(db, current_user),
        )

    user_data = await get_user_data_summary(db, current_user.id, 7)
    locale = get_locale(request_http)
    system_prompt = f"""{msg(locale, 'ai.chat_intro')}

Recent 7-day signal summary:
- Sessions: {user_data['total_sessions']}
- Analyses: {user_data['total_analyses']}
- Tremor events: {user_data['tremor_count']}
- Detection rate: {user_data['detection_rate']}%
- Average severity: {user_data['avg_severity']}
- Max severity: {user_data['max_severity']}

Important:
- {msg(locale, 'ai.chat_reminder_1')}
- {msg(locale, 'ai.chat_reminder_2')}
- {msg(locale, 'ai.chat_reminder_3')}"""

    messages = []
    if request.conversation_history:
        for history in request.conversation_history[-6:]:
            messages.append({"role": history.role, "content": history.content})
    messages.append({"role": "user", "content": message})
    response_text = await call_qwen_api(messages, system_prompt, locale)

    return ChatResponse(
        response=response_text,
        suggestions=[msg(locale, "ai.suggestion_1"), msg(locale, "ai.suggestion_2"), msg(locale, "ai.suggestion_3")],
    )


@router.post("/actions/rehab-plan/confirm", response_model=AIActionExecutionResponse)
async def confirm_rehab_plan(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    plan, exercises = await create_rehab_plan(db, current_user)
    return AIActionExecutionResponse(
        message="康复训练计划已生成并同步到康复训练页面。你现在可以前往查看完整计划，或下载 PDF。",
        route="/rehabilitation",
        action_card=AIActionCard(
            kind="rehab_plan",
            title=plan.name,
            summary=f"已生成 {len(exercises)} 个训练动作，总目标时长 {plan.daily_goal_minutes} 分钟。",
            status="generated",
            payload={"plan_id": plan.id},
            actions=[
                AIAction(type="view_rehab_page", label="查看康复计划", route="/rehabilitation"),
                AIAction(
                    type="download_rehab_pdf",
                    label="下载 PDF",
                    api_path=f"/api/ai/actions/rehab-plan/{plan.id}/pdf",
                ),
            ],
        ),
    )


@router.get("/actions/rehab-plan/{plan_id}/pdf")
async def download_rehab_plan_pdf(
    plan_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrainingPlan).where(TrainingPlan.id == plan_id, TrainingPlan.user_id == current_user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="训练计划不存在")

    exercises_result = await db.execute(select(Exercise).where(Exercise.id.in_(plan.exercise_ids or [])))
    exercises = exercises_result.scalars().all()
    sections = [
        ("计划概览", [plan.description or "", f"每日目标时长：{plan.daily_goal_minutes} 分钟"]),
        (
            "训练动作",
            [
                f"{idx + 1}. {ex.name}，建议 {ex.duration_minutes} 分钟，说明：{ex.description or '无'}"
                for idx, ex in enumerate(exercises)
            ],
        ),
    ]
    pdf_bytes = build_pdf_bytes(plan.name, sections)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="rehab-plan-{plan_id}.pdf"'},
    )


@router.post("/actions/health-report/confirm", response_model=AIActionExecutionResponse)
async def confirm_health_report(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    report_data = await generate_health_report_data(db, current_user, 30)
    AI_REPORT_STORAGE[report_data["report_id"]] = report_data
    return AIActionExecutionResponse(
        message="AI 健康报告已生成并同步到报告页面。你现在可以在线查看，或直接下载 PDF。",
        route="/reports",
        report_data=report_data,
        action_card=AIActionCard(
            kind="health_report",
            title="AI健康报告",
            summary=f"已生成最近30天的健康报告，震颤检出率 {report_data['summary']['detection_rate']}%，最高严重度 {report_data['summary']['max_severity']}。",
            status="generated",
            payload={"report_id": report_data["report_id"]},
            actions=[
                AIAction(type="view_health_report", label="查看报告页面", route="/reports"),
                AIAction(
                    type="download_health_report_pdf",
                    label="下载 PDF",
                    api_path=f"/api/ai/actions/health-report/{report_data['report_id']}/pdf",
                ),
            ],
        ),
    )


@router.get("/actions/health-report/{report_id}/pdf")
async def download_health_report_pdf(
    report_id: str,
    current_user: User = Depends(get_current_user_from_token),
):
    report_data = AI_REPORT_STORAGE.get(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="报告不存在或已过期")

    sections = [
        (
            "摘要",
            [
                f"报告周期：{report_data['summary']['period_start']} 至 {report_data['summary']['period_end']}",
                f"总会话数：{report_data['summary']['total_sessions']}",
                f"总检测数：{report_data['summary']['total_analyses']}",
                f"震颤检出率：{report_data['summary']['detection_rate']}%",
                f"平均严重度：{report_data['summary']['avg_severity']}",
                f"最高严重度：{report_data['summary']['max_severity']}",
            ],
        ),
        (
            "按日概览",
            [
                f"{item['date']}：检测 {item['total']} 次，震颤 {item['tremors']} 次，平均严重度 {item['avg_severity']}"
                for item in report_data.get("daily_breakdown", [])[:10]
            ],
        ),
    ]
    pdf_bytes = build_pdf_bytes("AI健康报告", sections)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ai-health-report-{report_id}.pdf"'},
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def ai_analyze(
    request_http: Request,
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_data_summary(db, current_user.id, request.days)
    if not user_data["has_data"]:
        return AnalysisResponse(
            summary="暂无足够的数据进行分析。",
            key_findings=["尚未检测到足够的数据"],
            recommendations=["确保设备已正确佩戴", "尝试进行几次检测会话"],
            risk_level="未知",
        )

    analysis_prompt = f"""请分析以下震颤检测数据（最近{request.days}天）:
- 检测会话数: {user_data['total_sessions']}
- 总检测次数: {user_data['total_analyses']}
- 震颤次数: {user_data['tremor_count']}
- 震颤检出率: {user_data['detection_rate']}%
- 平均严重度: {user_data['avg_severity']}
- 最高严重度: {user_data['max_severity']}
请给出 JSON 格式分析。"""
    response_text = await call_qwen_api(
        [{"role": "user", "content": analysis_prompt}],
        "你是一个专业的帕金森病震颤数据分析助手。不要做医学诊断，只分析数据趋势。",
        get_locale(request_http),
        response_format={"type": "json_object"},
    )
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        parsed = json.loads(response_text[json_start:json_end])
        return AnalysisResponse(
            summary=parsed.get("summary", "分析完成"),
            key_findings=parsed.get("key_findings", []),
            recommendations=parsed.get("recommendations", []),
            risk_level=parsed.get("risk_level", "中"),
        )
    except Exception:  # noqa: BLE001
        return AnalysisResponse(
            summary=response_text[:500],
            key_findings=["AI 分析已完成"],
            recommendations=["建议定期监测", "如有异常请咨询医生"],
            risk_level="中",
        )


@router.get("/insights")
async def get_ai_insights(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    days: int = 7,
):
    user_data = await get_user_data_summary(db, current_user.id, days)
    if not user_data["has_data"]:
        return {"insights": ["开始监测后将生成数据洞察"], "generated_at": datetime.utcnow(), "period_days": days}

    insights = []
    if user_data["detection_rate"] > 50:
        insights.append(f"最近{days}天震颤检出率较高（{user_data['detection_rate']}%），建议关注")
    elif user_data["detection_rate"] < 20:
        insights.append(f"最近{days}天震颤检出率较低（{user_data['detection_rate']}%），状态良好")
    if user_data["avg_severity"] >= 2:
        insights.append(f"平均严重度为 {user_data['avg_severity']}，建议咨询医生")
    elif user_data["avg_severity"] > 0:
        insights.append(f"平均严重度为 {user_data['avg_severity']}，属于轻度范围")
    if user_data["max_severity"] >= 3:
        insights.append(f"检测到最高严重度 {user_data['max_severity']}，请注意观察")
    if user_data["total_sessions"] > 0:
        insights.append(f"共完成 {user_data['total_sessions']} 次检测会话")
    if not insights:
        insights.append("数据正常，继续保持监测习惯")
    return {"insights": insights, "generated_at": datetime.utcnow(), "period_days": days, "data_summary": user_data}


@router.get("/health-tips")
async def get_health_tips(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    user_data = await get_user_data_summary(db, current_user.id, 7)
    tips = ["保持规律作息有助于减轻震颤症状", "适度运动可以改善运动功能", "避免过度疲劳和压力"]
    personalized = False
    if user_data["has_data"]:
        personalized = True
        if user_data["avg_severity"] >= 2:
            tips.insert(0, "您的震颤症状需要关注，建议咨询医生调整治疗方案")
        if user_data["detection_rate"] > 40:
            tips.insert(0, "震颤较为频繁，建议记录发作时间和环境因素")
    return {"tips": tips, "personalized": personalized, "generated_at": datetime.utcnow()}
