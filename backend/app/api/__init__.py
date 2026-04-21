"""
Tremor Guard - API Routes
震颤卫士 - API 路由
"""

from fastapi import APIRouter

from app.api import analysis, ai, auth, data, device, health, medication, rehabilitation, report

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(device.router, prefix="/device", tags=["设备"])
api_router.include_router(data.router, prefix="/data", tags=["数据"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["分析"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(report.router, prefix="/report", tags=["报告"])
api_router.include_router(medication.router, prefix="/medication", tags=["用药"])
api_router.include_router(rehabilitation.router, prefix="/rehabilitation", tags=["康复"])
api_router.include_router(health.router, prefix="/health", tags=["健康档案"])
