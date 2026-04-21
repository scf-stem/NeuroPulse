"""
Tremor Guard - Health Profile Models
震颤卫士 - 健康档案模型
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String, Text

from app.core.database import Base


class HealthProfile(Base):
    """健康档案表"""

    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    blood_type = Column(String(20), nullable=True)
    diagnosis_date = Column(Date, nullable=True)
    hoehn_yahr_stage = Column(Integer, nullable=True)
    primary_symptoms = Column(JSON, default=list, nullable=False)
    affected_side = Column(String(20), nullable=True)
    allergies = Column(JSON, default=list, nullable=False)
    chronic_conditions = Column(JSON, default=list, nullable=False)
    emergency_contact = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MedicalRecord(Base):
    """病历记录表"""

    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    record_date = Column(Date, nullable=False)
    record_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(JSON, default=list, nullable=True)
    diagnosis = Column(String(255), nullable=True)
    severity = Column(Integer, nullable=True)
    attachments = Column(JSON, default=list, nullable=True)
    doctor_name = Column(String(255), nullable=True)
    hospital_name = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class FamilyHistory(Base):
    """家族病史表"""

    __tablename__ = "family_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    relationship = Column(String(50), nullable=False)
    relationship_detail = Column(String(255), nullable=True)
    condition = Column(String(255), nullable=False)
    has_parkinsons = Column(Boolean, default=False, nullable=False)
    onset_age = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class VisitRecord(Base):
    """就诊记录表"""

    __tablename__ = "visit_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    visit_date = Column(Date, nullable=False)
    hospital_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    doctor_name = Column(String(255), nullable=True)
    visit_type = Column(String(50), nullable=False)
    chief_complaint = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    prescriptions = Column(JSON, default=list, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
