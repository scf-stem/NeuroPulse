/**
 * Tremor Guard - Device API
 * 震颤卫士 - 设备管理 API
 */

import apiClient from './index'
import axios from 'axios'

// 错误处理辅助函数
function handleApiError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.detail || error.message
    return new Error(message)
  }
  return error instanceof Error ? error : new Error('Unknown error')
}

// 类型定义
export interface Device {
  id: number
  device_id: string
  name: string | null
  firmware_version: string | null
  hardware_version: string | null
  mac_address: string | null
  is_online: boolean
  battery_level: number | null
  last_seen: string | null
  created_at: string
}

export interface DeviceRegisterRequest {
  device_id: string
  name?: string
  firmware_version?: string
  hardware_version?: string
  mac_address?: string
}

export interface DeviceUpdateRequest {
  name?: string
}

export interface DeviceStatus {
  exists: boolean
  device_id: string
  is_bound?: boolean
  is_online?: boolean
  last_seen?: string
}

export interface HeartbeatRequest {
  device_id: string
  battery_level?: number
  firmware_version?: string
}

export interface HeartbeatResponse {
  status: string
  timestamp: string
  device_id: string
}

// API 方法
export const deviceApi = {
  /**
   * 注册/绑定设备
   */
  async register(data: DeviceRegisterRequest): Promise<Device> {
    try {
      const response = await apiClient.post<Device>('/device/register', data)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 获取用户的所有设备
   */
  async list(): Promise<Device[]> {
    try {
      const response = await apiClient.get<Device[]>('/device/list')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 获取设备详情
   */
  async get(deviceId: string): Promise<Device> {
    try {
      const response = await apiClient.get<Device>(`/device/${deviceId}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 更新设备信息
   */
  async update(deviceId: string, data: DeviceUpdateRequest): Promise<Device> {
    try {
      const response = await apiClient.put<Device>(`/device/${deviceId}`, data)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 解绑设备
   */
  async unbind(deviceId: string): Promise<void> {
    try {
      await apiClient.delete(`/device/${deviceId}`)
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 获取设备状态（无需认证）
   */
  async getStatus(deviceId: string): Promise<DeviceStatus> {
    try {
      const response = await apiClient.get<DeviceStatus>(`/device/status/${deviceId}`)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 设备心跳（无需认证，供设备调用）
   */
  async heartbeat(data: HeartbeatRequest): Promise<HeartbeatResponse> {
    try {
      const response = await apiClient.post<HeartbeatResponse>('/device/heartbeat', data)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}
