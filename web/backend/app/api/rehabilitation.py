"""
Tremor Guard - Rehabilitation API
震颤卫士 - 运动康复接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.api.auth import get_current_user_from_token
from app.models.user import User
from app.models.rehabilitation import Exercise, TrainingPlan, TrainingCheckIn

router = APIRouter()

# ============================================================
# Pydantic Schemas
# ============================================================

class ExerciseResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    difficulty: Optional[str]
    description: Optional[str]
    instructions: Optional[str]
    video_url: Optional[str]
    image_url: Optional[str]
    duration_minutes: int
    calories: int
    is_active: bool

    class Config:
        from_attributes = True

class TrainingPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    exercise_ids: List[int] = []
    daily_goal_minutes: int = 30
    difficulty_level: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None

class TrainingPlanCreate(TrainingPlanBase):
    pass

class TrainingPlanResponse(TrainingPlanBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CheckInCreate(BaseModel):
    plan_id: Optional[int] = None
    check_in_date: datetime = datetime.utcnow()
    duration_minutes: int
    exercises_completed: int = 0
    feeling: Optional[str] = None
    notes: Optional[str] = None

class CheckInResponse(CheckInCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingStats(BaseModel):
    total_check_ins: int
    total_minutes: int
    streak_days: int
    last_check_in: Optional[datetime]

# ============================================================
# Exercise Endpoints
# ============================================================

@router.get("/exercises", response_model=List[ExerciseResponse])
async def list_exercises(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """获取运动库列表"""
    query = select(Exercise).where(Exercise.is_active == True)
    
    if category:
        query = query.where(Exercise.category == category)
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
        
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/exercises/{ex_id}", response_model=ExerciseResponse)
async def get_exercise(
    ex_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个运动详情"""
    result = await db.execute(select(Exercise).where(Exercise.id == ex_id))
    ex = result.scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ex

@router.get("/exercises/recommended", response_model=List[ExerciseResponse])
async def get_recommended_exercises(
    db: AsyncSession = Depends(get_db)
):
    """获取推荐运动 (Mock)"""
    # 简单实现：随机返回几个容易的动作
    result = await db.execute(
        select(Exercise)
        .where(Exercise.difficulty == "easy")
        .limit(3)
    )
    return result.scalars().all()

# ============================================================
# Training Plan Endpoints
# ============================================================

@router.get("/plans", response_model=List[TrainingPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的训练计划"""
    result = await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id)
        .order_by(desc(TrainingPlan.created_at))
    )
    return result.scalars().all()

@router.post("/plans", response_model=TrainingPlanResponse)
async def create_plan(
    plan_data: TrainingPlanCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """创建训练计划"""
    new_plan = TrainingPlan(
        user_id=current_user.id,
        is_active=False, # 默认不激活，需手动激活
        **plan_data.model_dump()
    )
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    return new_plan

@router.get("/plans/active", response_model=TrainingPlanResponse)
async def get_active_plan(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取当前活跃的计划"""
    result = await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id, TrainingPlan.is_active == True)
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")
    return plan

@router.post("/plans/{plan_id}/activate", response_model=TrainingPlanResponse)
async def activate_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """激活某个计划 (同时停用其他计划)"""
    # 1. 停用所有
    await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id)
        .execution_options(synchronize_session=False)
    )
    # SQLAlchemy update syntax is a bit different for execution, better iterate or specific update
    # Simplified: Get the target plan first
    
    result = await db.execute(
        select(TrainingPlan).where(TrainingPlan.id == plan_id, TrainingPlan.user_id == current_user.id)
    )
    target_plan = result.scalar_one_or_none()
    if not target_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Deactivate others
    plans_result = await db.execute(select(TrainingPlan).where(TrainingPlan.user_id == current_user.id))
    all_plans = plans_result.scalars().all()
    for p in all_plans:
        p.is_active = (p.id == plan_id)
    
    await db.commit()
    await db.refresh(target_plan)
    return target_plan

# ============================================================
# Check-in Endpoints
# ============================================================

@router.get("/check-ins", response_model=List[CheckInResponse])
async def list_check_ins(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取打卡记录"""
    result = await db.execute(
        select(TrainingCheckIn)
        .where(TrainingCheckIn.user_id == current_user.id)
        .order_by(desc(TrainingCheckIn.check_in_date))
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/check-ins", response_model=CheckInResponse)
async def check_in(
    check_in_data: CheckInCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """提交打卡"""
    new_check_in = TrainingCheckIn(
        user_id=current_user.id,
        **check_in_data.model_dump()
    )
    db.add(new_check_in)
    await db.commit()
    await db.refresh(new_check_in)
    return new_check_in

@router.get("/check-ins/today", response_model=CheckInResponse)
async def get_today_check_in(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取今日打卡记录"""
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    result = await db.execute(
        select(TrainingCheckIn)
        .where(
            TrainingCheckIn.user_id == current_user.id,
            TrainingCheckIn.check_in_date >= today_start,
            TrainingCheckIn.check_in_date <= today_end
        )
        .limit(1)
    )
    check_in = result.scalar_one_or_none()
    # Frontend handles 404 as null
    if not check_in:
        raise HTTPException(status_code=404, detail="No check-in today")
    return check_in

@router.get("/stats", response_model=TrainingStats)
async def get_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
):
    """获取训练统计"""
    # 简单统计逻辑
    result = await db.execute(
        select(TrainingCheckIn).where(TrainingCheckIn.user_id == current_user.id)
    )
    all_check_ins = result.scalars().all()
    
    total_minutes = sum(c.duration_minutes for c in all_check_ins)
    total_check_ins = len(all_check_ins)
    
    # 连续打卡天数计算 (简化: 只是个 Mock值或者简单计算)
    streak = 0 
    
    last_check_in = all_check_ins[0].check_in_date if all_check_ins else None
    
    return TrainingStats(
        total_check_ins=total_check_ins,
        total_minutes=total_minutes,
        streak_days=streak,
        last_check_in=last_check_in
    )
