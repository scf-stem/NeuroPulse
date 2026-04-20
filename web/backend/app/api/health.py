"""
Tremor Guard - Health Profile API
震颤卫士 - 健康档案接口
"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user_from_token
from app.core.database import get_db
from app.models.health import FamilyHistory, HealthProfile, MedicalRecord, VisitRecord
from app.models.user import User

router = APIRouter()


class EmergencyContact(BaseModel):
    name: str = ""
    phone: str = ""
    relationship: str = ""


class HealthProfileBase(BaseModel):
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    blood_type: Optional[str] = None
    diagnosis_date: Optional[date] = None
    hoehn_yahr_stage: Optional[int] = None
    primary_symptoms: List[str] = []
    affected_side: Optional[str] = None
    allergies: List[str] = []
    chronic_conditions: List[str] = []
    emergency_contact: Optional[EmergencyContact] = None
    notes: Optional[str] = None


class HealthProfileCreate(HealthProfileBase):
    pass


class HealthProfileUpdate(HealthProfileBase):
    pass


class HealthProfileResponse(HealthProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordBase(BaseModel):
    record_date: date
    record_type: str
    title: str
    description: str
    symptoms: List[str] = []
    diagnosis: Optional[str] = None
    severity: Optional[int] = None
    attachments: List[str] = []
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(MedicalRecordBase):
    pass


class MedicalRecordResponse(MedicalRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyHistoryBase(BaseModel):
    relationship: str
    relationship_detail: Optional[str] = None
    condition: str
    has_parkinsons: bool = False
    onset_age: Optional[int] = None
    notes: Optional[str] = None


class FamilyHistoryCreate(FamilyHistoryBase):
    pass


class FamilyHistoryUpdate(FamilyHistoryBase):
    pass


class FamilyHistoryResponse(FamilyHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrescriptionItem(BaseModel):
    medication: str
    dosage: str
    frequency: str
    duration: Optional[str] = None


class VisitRecordBase(BaseModel):
    visit_date: date
    hospital_name: str
    department: Optional[str] = None
    doctor_name: Optional[str] = None
    visit_type: str
    chief_complaint: str
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescriptions: List[PrescriptionItem] = []
    follow_up_date: Optional[date] = None
    notes: Optional[str] = None
    attachments: List[str] = []


class VisitRecordCreate(VisitRecordBase):
    pass


class VisitRecordUpdate(VisitRecordBase):
    pass


class VisitRecordResponse(VisitRecordBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


async def _get_profile_or_404(db: AsyncSession, user_id: int) -> HealthProfile:
    result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    return profile


@router.get("/profile", response_model=Optional[HealthProfileResponse])
async def get_profile(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    return result.scalar_one_or_none()


@router.post("/profile", response_model=HealthProfileResponse)
async def create_profile(
    profile_data: HealthProfileCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    profile = existing.scalar_one_or_none()
    if profile:
        raise HTTPException(status_code=400, detail="Health profile already exists")

    profile = HealthProfile(
        user_id=current_user.id,
        **profile_data.model_dump(),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.put("/profile", response_model=HealthProfileResponse)
async def update_profile(
    profile_data: HealthProfileUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    profile = await _get_profile_or_404(db, current_user.id)
    for key, value in profile_data.model_dump().items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/medical-records", response_model=List[MedicalRecordResponse])
async def list_medical_records(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.user_id == current_user.id)
        .order_by(desc(MedicalRecord.record_date), desc(MedicalRecord.created_at))
    )
    return result.scalars().all()


@router.post("/medical-records", response_model=MedicalRecordResponse)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    record = MedicalRecord(user_id=current_user.id, **record_data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.put("/medical-records/{record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    record_id: int,
    record_data: MedicalRecordUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalRecord).where(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    for key, value in record_data.model_dump().items():
        setattr(record, key, value)
    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/medical-records/{record_id}")
async def delete_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalRecord).where(
            MedicalRecord.id == record_id,
            MedicalRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    await db.delete(record)
    await db.commit()
    return {"message": "Medical record deleted"}


@router.get("/family-history", response_model=List[FamilyHistoryResponse])
async def list_family_history(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyHistory)
        .where(FamilyHistory.user_id == current_user.id)
        .order_by(desc(FamilyHistory.created_at))
    )
    return result.scalars().all()


@router.post("/family-history", response_model=FamilyHistoryResponse)
async def create_family_history(
    record_data: FamilyHistoryCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    record = FamilyHistory(user_id=current_user.id, **record_data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.put("/family-history/{record_id}", response_model=FamilyHistoryResponse)
async def update_family_history(
    record_id: int,
    record_data: FamilyHistoryUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyHistory).where(
            FamilyHistory.id == record_id,
            FamilyHistory.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Family history record not found")

    for key, value in record_data.model_dump().items():
        setattr(record, key, value)
    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/family-history/{record_id}")
async def delete_family_history(
    record_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyHistory).where(
            FamilyHistory.id == record_id,
            FamilyHistory.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Family history record not found")

    await db.delete(record)
    await db.commit()
    return {"message": "Family history record deleted"}


@router.get("/visit-records", response_model=List[VisitRecordResponse])
async def list_visit_records(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VisitRecord)
        .where(VisitRecord.user_id == current_user.id)
        .order_by(desc(VisitRecord.visit_date), desc(VisitRecord.created_at))
    )
    return result.scalars().all()


@router.post("/visit-records", response_model=VisitRecordResponse)
async def create_visit_record(
    record_data: VisitRecordCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    record = VisitRecord(user_id=current_user.id, **record_data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.put("/visit-records/{record_id}", response_model=VisitRecordResponse)
async def update_visit_record(
    record_id: int,
    record_data: VisitRecordUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VisitRecord).where(
            VisitRecord.id == record_id,
            VisitRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Visit record not found")

    for key, value in record_data.model_dump().items():
        setattr(record, key, value)
    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/visit-records/{record_id}")
async def delete_visit_record(
    record_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VisitRecord).where(
            VisitRecord.id == record_id,
            VisitRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Visit record not found")

    await db.delete(record)
    await db.commit()
    return {"message": "Visit record deleted"}


@router.get("/visit-records/upcoming", response_model=List[VisitRecordResponse])
async def get_upcoming_follow_ups(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    result = await db.execute(
        select(VisitRecord)
        .where(
            VisitRecord.user_id == current_user.id,
            VisitRecord.follow_up_date.is_not(None),
            VisitRecord.follow_up_date >= today,
        )
        .order_by(asc(VisitRecord.follow_up_date), desc(VisitRecord.created_at))
    )
    return result.scalars().all()
