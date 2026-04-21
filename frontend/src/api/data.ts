/**
 * Tremor Guard - Data API
 * 震颤卫士 - 数据 API
 */

import apiClient from './index'
import type { TremorData, TremorSession } from '@/types'

export interface TodayStats {
  date: string
  total_sessions: number
  total_analyses: number
  tremor_detections: number
  detection_rate: number
  avg_severity: number
  max_severity: number
}

export interface SessionCreateRequest {
  device_id: string
}

export interface TremorDataUpload {
  device_id: string
  timestamp?: string
  detected: boolean
  valid?: boolean
  out_of_range?: boolean
  frequency?: number
  peak_power?: number
  band_power?: number
  amplitude?: number
  rms_amplitude?: number
  severity?: number
  severity_label?: string
  spectrum_data?: Record<string, unknown>
}

export const dataApi = {
  /**
   * 开始新会话
   */
  async startSession(deviceId: string): Promise<TremorSession> {
    const response = await apiClient.post<TremorSession>('/data/session/start', {
      device_id: deviceId
    })
    return response.data
  },

  /**
   * 结束会话
   */
  async endSession(sessionId: number): Promise<TremorSession> {
    const response = await apiClient.post<TremorSession>(`/data/session/${sessionId}/end`)
    return response.data
  },

  /**
   * 获取会话详情
   */
  async getSession(sessionId: number): Promise<TremorSession> {
    const response = await apiClient.get<TremorSession>(`/data/session/${sessionId}`)
    return response.data
  },

  /**
   * 获取会话数据
   */
  async getSessionData(
    sessionId: number,
    limit = 100,
    offset = 0
  ): Promise<TremorData[]> {
    const response = await apiClient.get<TremorData[]>(`/data/session/${sessionId}/data`, {
      params: { limit, offset }
    })
    return response.data
  },

  /**
   * 获取历史会话
   */
  async getHistory(options?: {
    startDate?: string
    endDate?: string
    deviceId?: string
    limit?: number
    offset?: number
  }): Promise<TremorSession[]> {
    const response = await apiClient.get<TremorSession[]>('/data/history', {
      params: {
        start_date: options?.startDate,
        end_date: options?.endDate,
        device_id: options?.deviceId,
        limit: options?.limit || 50,
        offset: options?.offset || 0
      }
    })
    return response.data
  },

  /**
   * 获取最近数据
   */
  async getRecentData(limit = 50): Promise<TremorData[]> {
    const response = await apiClient.get<TremorData[]>('/data/recent', {
      params: { limit }
    })
    return response.data
  },

  /**
   * 获取今日统计
   */
  async getTodayStats(): Promise<TodayStats> {
    const response = await apiClient.get<TodayStats>('/data/stats/today')
    return response.data
  },

  /**
   * 上传单条数据
   */
  async uploadData(data: TremorDataUpload): Promise<{ status: string; message: string }> {
    const response = await apiClient.post('/data/upload', data)
    return response.data
  },

  /**
   * 批量上传数据
   */
  async uploadBatch(
    deviceId: string,
    data: TremorDataUpload[],
    sessionId?: number
  ): Promise<{ status: string; message: string }> {
    const response = await apiClient.post('/data/upload/batch', {
      device_id: deviceId,
      session_id: sessionId,
      data
    })
    return response.data
  }
}
