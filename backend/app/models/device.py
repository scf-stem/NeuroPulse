"""
Tremor Guard - Device Model
震颤卫士 - 设备模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Device(Base):
    """设备表 - 震颤监测手环"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)  # 硬件唯一ID
    name = Column(String(200), nullable=True)  # 用户自定义名称

    # 设备信息
    firmware_version = Column(String(50), nullable=True)
    hardware_version = Column(String(50), nullable=True)
    mac_address = Column(String(50), nullable=True)

    # 设备状态
    is_online = Column(Boolean, default=False)
    battery_level = Column(Float, nullable=True)  # 电量百分比 0-100
    last_seen = Column(DateTime, nullable=True)

    # 关联用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="devices")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tremor_sessions = relationship("TremorSession", back_populates="device")
