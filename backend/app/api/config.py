"""
Tremor Guard - Config API
震颤卫士 - 参数配置接口

用于管理震颤检测参数的云端配置
- ESP32 通过 POST /api/config/upload 上传当前配置
- ESP32 通过 GET /api/config/current 拉取最新配置
- 前端通过 POST /api/config/save 修改配置
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

router = APIRouter()

# ============================================================
# 数据模型 (Data Models)
# ============================================================

class TremorConfig(BaseModel):
    """震颤检测配置参数"""
    # RMS 幅度阈值 (g)
    rms_min: float = Field(default=2.5, ge=0.1, le=10.0, description="RMS 下限阈值 (g)")
    rms_max: float = Field(default=5.0, ge=0.5, le=20.0, description="RMS 上限阈值 (g)")

    # 功率阈值
    power_threshold: float = Field(default=0.5, ge=0.01, le=5.0, description="功率阈值")

    # 频率范围 (Hz)
    freq_min: float = Field(default=4.0, ge=1.0, le=10.0, description="频率下限 (Hz)")
    freq_max: float = Field(default=6.0, ge=2.0, le=15.0, description="频率上限 (Hz)")

    # 严重度分级阈值 (g) - 4个值对应 1-4 级
    severity_thresholds: List[float] = Field(
        default=[2.5, 3.0, 3.5, 4.0],
        min_length=4,
        max_length=4,
        description="严重度分级阈值 [0级, 1级, 2级, 3级]"
    )


class ConfigResponse(BaseModel):
    """配置响应"""
    version: int
    updated_at: str
    params: TremorConfig


class ConfigSaveRequest(BaseModel):
    """保存配置请求"""
    rms_min: Optional[float] = None
    rms_max: Optional[float] = None
    power_threshold: Optional[float] = None
    freq_min: Optional[float] = None
    freq_max: Optional[float] = None
    severity_thresholds: Optional[List[float]] = None


class DeviceConfigUpload(BaseModel):
    """设备上传配置请求"""
    device_id: str = Field(default="esp32_001", description="设备ID")
    config_version: int = Field(default=0, description="设备当前配置版本")
    rms_min: float
    rms_max: float
    power_threshold: float
    freq_min: float
    freq_max: float
    severity_thresholds: List[float]


# ============================================================
# 全局配置存储 (Global Config Storage)
# ============================================================

# 默认配置
DEFAULT_CONFIG = TremorConfig()

# 云端配置 (用于下发给设备)
cloud_config = TremorConfig()
cloud_config_version = 1
cloud_config_updated_at = datetime.now().isoformat()
cloud_config_source = "default"  # 配置来源: default, device, web

# 设备上报的配置 (设备当前实际使用的配置)
device_config: Optional[TremorConfig] = None
device_config_version = 0
device_last_seen = None
device_ip = None
device_id = None


# ============================================================
# 设备端 API (Device API)
# ============================================================

@router.post("/upload")
async def upload_device_config(request: Request, data: DeviceConfigUpload):
    """
    设备上传当前配置

    ESP32 通过此接口将当前运行的配置上传到云端
    """
    global device_config, device_config_version, device_last_seen, device_ip, device_id
    global cloud_config, cloud_config_version, cloud_config_updated_at, cloud_config_source

    # 更新设备配置信息
    device_config = TremorConfig(
        rms_min=data.rms_min,
        rms_max=data.rms_max,
        power_threshold=data.power_threshold,
        freq_min=data.freq_min,
        freq_max=data.freq_max,
        severity_thresholds=data.severity_thresholds
    )
    device_config_version = data.config_version
    device_last_seen = datetime.now().isoformat()
    device_ip = request.client.host if request.client else "unknown"
    device_id = data.device_id

    # 如果云端配置是默认的，则用设备配置初始化
    if cloud_config_source == "default":
        cloud_config = device_config.model_copy()
        cloud_config_version = device_config_version + 1
        cloud_config_updated_at = datetime.now().isoformat()
        cloud_config_source = "device"

    # 检查是否有新配置需要下发
    need_update = cloud_config_version > device_config_version

    return {
        "status": "ok",
        "message": "配置已接收",
        "device_version": device_config_version,
        "cloud_version": cloud_config_version,
        "need_update": need_update,
        "server_time": datetime.now().isoformat()
    }


@router.get("/current", response_model=ConfigResponse)
async def get_current_config():
    """
    获取当前云端配置

    ESP32 设备通过此接口拉取最新的震颤检测参数
    """
    return ConfigResponse(
        version=cloud_config_version,
        updated_at=cloud_config_updated_at,
        params=cloud_config
    )


# ============================================================
# 前端 API (Web API)
# ============================================================

@router.get("/status")
async def get_config_status():
    """
    获取配置状态概览

    前端用于显示设备和云端配置状态
    """
    return {
        "cloud": {
            "version": cloud_config_version,
            "updated_at": cloud_config_updated_at,
            "source": cloud_config_source,
            "params": cloud_config.model_dump()
        },
        "device": {
            "connected": device_last_seen is not None,
            "version": device_config_version,
            "last_seen": device_last_seen,
            "ip": device_ip,
            "device_id": device_id,
            "params": device_config.model_dump() if device_config else None,
            "synced": device_config_version >= cloud_config_version if device_config else False
        }
    }


@router.post("/save")
async def save_config(request: ConfigSaveRequest):
    """
    保存配置参数 (前端调用)

    前端调用此接口保存修改后的参数
    只更新提供的字段，未提供的保持原值
    """
    global cloud_config, cloud_config_version, cloud_config_updated_at, cloud_config_source

    # 更新配置 (只更新提供的字段)
    update_data = request.model_dump(exclude_none=True)

    if update_data:
        # 创建新配置
        current_data = cloud_config.model_dump()
        current_data.update(update_data)
        cloud_config = TremorConfig(**current_data)

        # 更新版本和时间
        cloud_config_version += 1
        cloud_config_updated_at = datetime.now().isoformat()
        cloud_config_source = "web"

    return {
        "status": "ok",
        "message": "配置已保存，设备需执行 update 命令同步",
        "version": cloud_config_version,
        "updated_at": cloud_config_updated_at
    }


@router.post("/reset")
async def reset_config():
    """
    重置为默认配置
    """
    global cloud_config, cloud_config_version, cloud_config_updated_at, cloud_config_source

    cloud_config = TremorConfig()
    cloud_config_version += 1
    cloud_config_updated_at = datetime.now().isoformat()
    cloud_config_source = "default"

    return {
        "status": "ok",
        "message": "配置已重置为默认值",
        "version": cloud_config_version,
        "updated_at": cloud_config_updated_at
    }


@router.get("/defaults")
async def get_default_config():
    """
    获取默认配置值

    用于前端显示默认值参考
    """
    return {
        "params": DEFAULT_CONFIG.model_dump(),
        "description": {
            "rms_min": "RMS 幅度下限阈值 (g) - 低于此值不判定为震颤",
            "rms_max": "RMS 幅度上限阈值 (g) - 高于此值判定为超出范围",
            "power_threshold": "频带功率阈值 - 震颤频段的功率需超过此值",
            "freq_min": "震颤频率下限 (Hz) - 帕金森震颤典型为 4-6Hz",
            "freq_max": "震颤频率上限 (Hz)",
            "severity_thresholds": "严重度分级阈值 (g) - [0级/1级/2级/3级分界点]"
        }
    }
