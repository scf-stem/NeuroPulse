"""
Tremor Guard - Rehabilitation Models
震颤卫士 - 康复训练模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Exercise(Base):
    """运动库表"""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String(200), nullable=False)          # 运动名称
    category = Column(String(50), index=True)           # 分类: flexibility, strength, balance, coordination
    difficulty = Column(String(20))                     # 难度: easy, medium, hard
    
    description = Column(Text)                          # 描述
    instructions = Column(Text)                         # 指导步骤
    video_url = Column(String(500))                     # 教学视频链接
    image_url = Column(String(500))                     # 封面图链接
    
    duration_minutes = Column(Integer, default=5)       # 建议时长
    calories = Column(Integer, default=0)               # 消耗卡路里
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingPlan(Base):
    """个人训练计划表"""
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(200), nullable=False)          # 计划名称
    description = Column(Text)                          # 计划描述
    
    # 包含的运动 ID 列表 (JSON array of integers)
    exercise_ids = Column(JSON, default=list)
    
    daily_goal_minutes = Column(Integer, default=30)    # 每日目标时长
    difficulty_level = Column(String(20))               # 整体难度
    
    is_active = Column(Boolean, default=False)          # 是否为当前启用计划
    
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="training_plans")
    check_ins = relationship("TrainingCheckIn", back_populates="plan", cascade="all, delete-orphan")


class TrainingCheckIn(Base):
    """训练打卡记录表"""
    __tablename__ = "training_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=True) # 可以是不关联计划的自由训练
    
    check_in_date = Column(DateTime, default=datetime.utcnow) # 打卡时间
    
    duration_minutes = Column(Integer, nullable=False)  # 训练时长
    exercises_completed = Column(Integer, default=0)    # 完成动作数
    
    feeling = Column(String(50))                        # 感受: good, tired, pain, easy
    notes = Column(Text)                                # 备注
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="training_check_ins")
    plan = relationship("TrainingPlan", back_populates="check_ins")
