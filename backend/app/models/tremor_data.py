"""
Tremor Guard - Tremor Data Models
震颤卫士 - 震颤数据模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class TremorSession(Base):
    """震颤检测会话 - 一次完整的检测过程"""
    __tablename__ = "tremor_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # 关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    user = relationship("User", back_populates="tremor_sessions")
    device = relationship("Device", back_populates="tremor_sessions")

    # 会话信息
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # 汇总统计
    total_analyses = Column(Integer, default=0)  # 总分析次数
    tremor_count = Column(Integer, default=0)  # 检测到震颤次数
    avg_frequency = Column(Float, nullable=True)  # 平均频率 Hz
    avg_amplitude = Column(Float, nullable=True)  # 平均幅度 g
    max_severity = Column(Integer, default=0)  # 最高严重度 0-4
    avg_severity = Column(Float, nullable=True)  # 平均严重度

    # 状态
    is_active = Column(Boolean, default=True)

    # 关系
    tremor_data = relationship("TremorData", back_populates="session")


class TremorData(Base):
    """单次震颤检测数据"""
    __tablename__ = "tremor_data"

    id = Column(Integer, primary_key=True, index=True)

    # 关联会话
    session_id = Column(Integer, ForeignKey("tremor_sessions.id"), nullable=False)
    session = relationship("TremorSession", back_populates="tremor_data")

    # 检测时间
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 检测结果
    detected = Column(Boolean, default=False)  # 是否检测到震颤
    valid = Column(Boolean, default=True)  # 测试是否有效
    out_of_range = Column(Boolean, default=False)  # RMS是否超出上限

    # 频率特征
    frequency = Column(Float, nullable=True)  # 主频 Hz
    peak_power = Column(Float, nullable=True)  # 峰值功率
    band_power = Column(Float, nullable=True)  # 4-6Hz 频段功率

    # 幅度特征
    amplitude = Column(Float, nullable=True)  # 幅度 g
    rms_amplitude = Column(Float, nullable=True)  # RMS 幅度 g

    # 严重度评估
    severity = Column(Integer, default=0)  # 0-4
    severity_label = Column(String(50), nullable=True)

    # 原始频谱数据 (可选，用于后续分析)
    spectrum_data = Column(JSON, nullable=True)

    # 索引优化
    __table_args__ = (
        # 复合索引用于时间范围查询
    )
