"""
Tremor Guard - User Model
震颤卫士 - 用户模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)

    # 用户角色: user, doctor, admin
    role = Column(String(50), default="user")

    # 状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 关系
    devices = relationship("Device", back_populates="owner")
    tremor_sessions = relationship("TremorSession", back_populates="user")
    medications = relationship("Medication", back_populates="user")
    dosage_records = relationship("DosageRecord", back_populates="user")
    training_plans = relationship("TrainingPlan", back_populates="user")
    training_check_ins = relationship("TrainingCheckIn", back_populates="user")
