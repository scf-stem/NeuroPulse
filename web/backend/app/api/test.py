"""
Tremor Guard - Test API
震颤卫士 - 测试接口

用于接收和存储 ESP32 发送的所有数据包，用于调试和测试
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any
import json

router = APIRouter()

# 内存存储，用于测试（生产环境应使用数据库）
received_packets: List[dict] = []
MAX_PACKETS = 500  # 最多保存 500 条


class GenericPacket(BaseModel):
    """通用数据包 - 接收任意 JSON 数据"""
    class Config:
        extra = "allow"  # 允许额外字段


# ============================================================
# 测试接口
# ============================================================

@router.post("/receive")
async def receive_packet(request: Request):
    """
    接收任意 JSON 数据包

    ESP32 可以发送任何格式的 JSON 数据到这个接口
    """
    global received_packets

    try:
        # 尝试解析 JSON
        body = await request.json()
    except:
        # 如果不是 JSON，读取原始 body
        raw_body = await request.body()
        body = {"raw": raw_body.decode('utf-8', errors='ignore')}

    # 构建数据包记录
    packet = {
        "id": len(received_packets) + 1,
        "received_at": datetime.now().isoformat(),
        "client_ip": request.client.host if request.client else "unknown",
        "headers": dict(request.headers),
        "data": body
    }

    # 添加到列表
    received_packets.append(packet)

    # 限制数量，删除最旧的
    if len(received_packets) > MAX_PACKETS:
        received_packets = received_packets[-MAX_PACKETS:]

    return {
        "status": "ok",
        "message": "数据已接收",
        "packet_id": packet["id"],
        "server_time": datetime.now().isoformat()
    }


@router.post("/heartbeat")
async def receive_heartbeat(request: Request):
    """
    接收设备心跳
    """
    global received_packets

    try:
        body = await request.json()
    except:
        body = {}

    packet = {
        "id": len(received_packets) + 1,
        "received_at": datetime.now().isoformat(),
        "type": "heartbeat",
        "client_ip": request.client.host if request.client else "unknown",
        "data": body
    }

    received_packets.append(packet)

    if len(received_packets) > MAX_PACKETS:
        received_packets = received_packets[-MAX_PACKETS:]

    return {
        "status": "ok",
        "type": "heartbeat_ack",
        "server_time": datetime.now().isoformat()
    }


@router.post("/batch")
async def receive_batch(request: Request):
    """
    接收批量数据
    """
    global received_packets

    try:
        body = await request.json()
    except:
        raw_body = await request.body()
        body = {"raw": raw_body.decode('utf-8', errors='ignore')}

    # 记录批量数据
    packet = {
        "id": len(received_packets) + 1,
        "received_at": datetime.now().isoformat(),
        "type": "batch",
        "client_ip": request.client.host if request.client else "unknown",
        "data": body,
        "item_count": len(body.get("data", [])) if isinstance(body, dict) else 0
    }

    received_packets.append(packet)

    if len(received_packets) > MAX_PACKETS:
        received_packets = received_packets[-MAX_PACKETS:]

    return {
        "status": "ok",
        "message": "批量数据已接收",
        "packet_id": packet["id"],
        "received_count": packet["item_count"],
        "server_time": datetime.now().isoformat()
    }


@router.get("/packets")
async def get_packets(
    limit: int = 50,
    offset: int = 0,
    type_filter: Optional[str] = None
):
    """
    获取接收到的数据包列表

    用于前端测试页面显示
    """
    packets = received_packets.copy()
    packets.reverse()  # 最新的在前面

    # 类型过滤
    if type_filter:
        packets = [p for p in packets if p.get("type") == type_filter]

    # 分页
    total = len(packets)
    packets = packets[offset:offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "packets": packets
    }


@router.get("/packets/{packet_id}")
async def get_packet_detail(packet_id: int):
    """
    获取单个数据包详情
    """
    for packet in received_packets:
        if packet["id"] == packet_id:
            return packet

    return {"error": "Packet not found", "packet_id": packet_id}


@router.delete("/packets")
async def clear_packets():
    """
    清空所有数据包
    """
    global received_packets
    count = len(received_packets)
    received_packets = []

    return {
        "status": "ok",
        "message": f"已清空 {count} 条数据包"
    }


@router.get("/stats")
async def get_stats():
    """
    获取统计信息
    """
    total = len(received_packets)

    # 按类型统计
    type_counts = {}
    for p in received_packets:
        t = p.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    # 最近的设备 IP
    recent_ips = set()
    for p in received_packets[-20:]:
        recent_ips.add(p.get("client_ip", "unknown"))

    return {
        "total_packets": total,
        "max_packets": MAX_PACKETS,
        "type_counts": type_counts,
        "recent_client_ips": list(recent_ips),
        "oldest_packet": received_packets[0]["received_at"] if received_packets else None,
        "newest_packet": received_packets[-1]["received_at"] if received_packets else None
    }
