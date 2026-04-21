"""
Tremor Guard - Medication Models
震颤卫士 - 药物模型
"""

from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Text, JSON, Time
from sqlalchemy.orm import relationship

from app.core.database import Base


class Medication(Base):
    """药物表"""
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(200), nullable=False)          # 药物名称
    generic_name = Column(String(200))                  # 通用名
    dosage = Column(String(100))                        # 剂量 (e.g., "250mg")
    frequency = Column(String(50))                      # 频率 (e.g., "tid", "qid")
    
    # 计划服药时间 (JSON list of strings "HH:MM")
    scheduled_times = Column(JSON, default=list)
    
    start_date = Column(Date, default=datetime.utcnow)  # 开始服用日期
    end_date = Column(Date, nullable=True)              # 结束日期
    
    purpose = Column(String(255))                       # 用途
    notes = Column(Text)                                # 备注
    
    is_active = Column(Boolean, default=True)           # 是否正在服用
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="medications")
    records = relationship("DosageRecord", back_populates="medication", cascade="all, delete-orphan")
    reminders = relationship("MedicationReminder", back_populates="medication", cascade="all, delete-orphan")


class DosageRecord(Base):
    """服药记录表"""
    __tablename__ = "dosage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    
    taken_at = Column(DateTime, default=datetime.utcnow) # 实际服药时间
    scheduled_time = Column(String(10))                  # 计划时间 (HH:MM)，如果是按计划服药
    dosage_taken = Column(String(100))                   # 实际服用剂量
    
    status = Column(String(50), default="taken")         # taken, missed, skipped
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="dosage_records")
    medication = relationship("Medication", back_populates="records")


class MedicationReminder(Base):
    """服药提醒配置"""
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    
    reminder_time = Column(String(10))                   # 提醒时间 HH:MM
    is_enabled = Column(Boolean, default=True)           # 是否启用
    
    # 提醒设置
    advance_minutes = Column(Integer, default=15)        # 提前几分钟提醒
    repeat_daily = Column(Boolean, default=True)         # 每日重复
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    medication = relationship("Medication", back_populates="reminders")
