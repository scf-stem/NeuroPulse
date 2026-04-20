"""
Tremor Guard - Medication API
震颤卫士 - 用药管理接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime

from app.core.database import get_db
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.medication import Medication, DosageRecord, MedicationReminder

router = APIRouter()

# ============================================================
# Pydantic Schemas
# ============================================================

class MedicationBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    dosage: str
    frequency: str
    scheduled_times: List[str] = []
    start_date: date
    end_date: Optional[date] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class MedicationCreate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DosageRecordCreate(BaseModel):
    medication_id: int
    taken_at: datetime
    scheduled_time: Optional[str] = None
    dosage_taken: str
    notes: Optional[str] = None
    status: str = "taken"

class DosageRecordResponse(BaseModel):
    id: int
    medication_id: int
    taken_at: datetime
    scheduled_time: Optional[str]
    dosage_taken: str
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DosageScheduleItem(BaseModel):
    medication: MedicationResponse
    scheduled_time: str
    status: str
    record: Optional[DosageRecordResponse] = None

# ============================================================
# Medication Endpoints
# ============================================================

@router.get("", response_model=List[MedicationResponse])
async def list_medications(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取所有药物"""
    result = await db.execute(
        select(Medication)
        .where(Medication.user_id == current_user.id)
        .order_by(desc(Medication.is_active), desc(Medication.created_at))
    )
    return result.scalars().all()

@router.post("", response_model=MedicationResponse)
async def create_medication(
    med_data: MedicationCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """添加药物"""
    new_med = Medication(
        user_id=current_user.id,
        **med_data.model_dump()
    )
    db.add(new_med)
    await db.commit()
    await db.refresh(new_med)
    return new_med

@router.get("/active", response_model=List[MedicationResponse])
async def list_active_medications(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取正在使用的药物"""
    result = await db.execute(
        select(Medication)
        .where(Medication.user_id == current_user.id, Medication.is_active == True)
        .order_by(desc(Medication.created_at))
    )
    return result.scalars().all()

@router.get("/{med_id}", response_model=MedicationResponse)
async def get_medication(
    med_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取单个药物详情"""
    result = await db.execute(
        select(Medication).where(Medication.id == med_id, Medication.user_id == current_user.id)
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med

@router.put("/{med_id}", response_model=MedicationResponse)
async def update_medication(
    med_id: int,
    med_data: MedicationCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """更新药物信息"""
    result = await db.execute(
        select(Medication).where(Medication.id == med_id, Medication.user_id == current_user.id)
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    for key, value in med_data.model_dump().items():
        setattr(med, key, value)
    
    med.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(med)
    return med

@router.delete("/{med_id}")
async def delete_medication(
    med_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """删除药物"""
    result = await db.execute(
        select(Medication).where(Medication.id == med_id, Medication.user_id == current_user.id)
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    await db.delete(med)
    await db.commit()
    return {"message": "Medication deleted"}

@router.patch("/{med_id}/active", response_model=MedicationResponse)
async def toggle_medication_active(
    med_id: int,
    is_active_data: dict,  # {"is_active": bool}
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """设置药物启用/停用"""
    result = await db.execute(
        select(Medication).where(Medication.id == med_id, Medication.user_id == current_user.id)
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    med.is_active = is_active_data.get("is_active", True)
    med.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(med)
    return med

# ============================================================
# Dosage Record Endpoints
# ============================================================

@router.get("/records/today", response_model=List[DosageRecordResponse])
async def get_today_records(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取今日服药记录"""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    result = await db.execute(
        select(DosageRecord)
        .where(
            DosageRecord.user_id == current_user.id,
            DosageRecord.taken_at >= today_start,
            DosageRecord.taken_at <= today_end
        )
        .order_by(desc(DosageRecord.taken_at))
    )
    return result.scalars().all()

@router.post("/records", response_model=DosageRecordResponse)
async def record_dosage(
    record_data: DosageRecordCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """记录一次服药"""
    # 验证药物归属
    med_result = await db.execute(
        select(Medication).where(Medication.id == record_data.medication_id, Medication.user_id == current_user.id)
    )
    if not med_result.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Medication not found")

    new_record = DosageRecord(
        user_id=current_user.id,
        **record_data.model_dump()
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record

@router.get("/schedule/today", response_model=List[DosageScheduleItem])
async def get_today_schedule(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取今日服药计划 (简单的逻辑实现)"""
    # 1. 获取所有活跃药物
    active_meds_result = await db.execute(
        select(Medication)
        .where(Medication.user_id == current_user.id, Medication.is_active == True)
    )
    active_meds = active_meds_result.scalars().all()
    
    # 2. 获取今日已服记录
    today_records = await get_today_records(current_user, db)
    
    schedule_items = []
    
    # 3. 构造计划
    # 注意：这是一个简化的逻辑，只处理显式设置了 scheduled_times 的药物
    for med in active_meds:
        if not med.scheduled_times:
            continue
            
        for time_str in med.scheduled_times:
            # 查找是否已经服用 (简单匹配：同一药物，且时间接近，这里暂且不校验时间，只看是否有该时间段的记录)
            # 在实际业务中，可能需要关联 scheduled_time 字段
            
            # 此处逻辑：如果今天该药有记录，且记录的 scheduled_time 匹配当前时间点
            # 但目前 DosageRecordCreate 没有强制传 scheduled_time。
            # 我们这里做一个简单的假设：如果今天服用了该药 n 次，则前 n 个时间点算已完成。
            
            # 更好的做法是在 DosageRecord 中存储 scheduled_time。我们在模型里加了这个字段。
            
            matching_record = None
            # 查找匹配的记录
            for record in today_records:
                if record.medication_id == med.id and record.scheduled_time == time_str:
                     matching_record = record
                     break
            
            status = "taken" if matching_record else "pending"
            
            # 检查是否过期 (简单判断：当前时间 > 计划时间 + 30分钟)
            if status == "pending":
                now = datetime.now()
                sch_hour, sch_minute = map(int, time_str.split(':'))
                sch_dt = now.replace(hour=sch_hour, minute=sch_minute, second=0)
                if now > sch_dt: # 简化：只要过了时间就算过期/未服，或者可以是 missed
                     # status = "missed" # 暂不标记为 missed，保持 pending 让用户补录
                     pass

            schedule_items.append(DosageScheduleItem(
                medication=MedicationResponse.model_validate(med),
                scheduled_time=time_str,
                status=status,
                record=DosageRecordResponse.model_validate(matching_record) if matching_record else None
            ))
            
    # 按时间排序
    schedule_items.sort(key=lambda x: x.scheduled_time)
    
    return schedule_items
