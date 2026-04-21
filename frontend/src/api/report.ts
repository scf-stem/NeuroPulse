/**
 * Tremor Guard - Report API
 * 震颤卫士 - 报告 API
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
export type ReportType = 'daily' | 'weekly' | 'monthly' | 'custom'
export type ReportFormat = 'pdf' | 'json' | 'csv'

export interface ReportRequest {
  report_type: ReportType
  format?: ReportFormat
  start_date?: string
  end_date?: string
  device_id?: string
  include_ai_analysis?: boolean
}

export interface ReportSummary {
  period_start: string
  period_end: string
  total_sessions: number
  total_analyses: number
  tremor_detections: number
  detection_rate: number
  avg_severity: number
  max_severity: number
  total_duration_minutes: number
}

export interface DailyBreakdown {
  date: string
  total: number
  tremors: number
  avg_severity: number
}

export interface HourlyPattern {
  hour: number
  count: number
  tremors: number
}

export interface SessionData {
  id: number
  start_time: string
  end_time: string | null
  duration_seconds: number | null
  total_analyses: number
  tremor_count: number
  avg_severity: number | null
  max_severity: number
}

export interface ReportData {
  report_id: string
  report_type: ReportType
  generated_at: string
  summary: ReportSummary
  daily_breakdown: DailyBreakdown[]
  severity_distribution: Record<number, number>
  hourly_pattern: HourlyPattern[]
  sessions: SessionData[]
}

export interface QuickStats {
  today: {
    total_analyses: number
    tremor_count: number
    avg_severity: number
  }
  this_week: {
    total_analyses: number
    tremor_count: number
    avg_severity: number
  }
  this_month: {
    total_analyses: number
    tremor_count: number
    avg_severity: number
  }
}

export interface DoctorSummary {
  patient_info: {
    username: string
    full_name: string | null
  }
  period: {
    start: string
    end: string
    days: number
  }
  summary: {
    total_monitoring_records: number
    tremor_episodes: number
    avg_severity: number
    max_severity: number
    severe_episodes: number
    severity_trend: 'improving' | 'stable' | 'worsening'
    frequency_trend: 'decreasing' | 'stable' | 'increasing'
  }
  comparison: {
    prev_period_tremors: number
    prev_period_avg_severity: number
    tremor_change_percent: number
    severity_change_percent: number
  }
  key_observations: string[]
  recommendations: string[]
}

// API 方法
export const reportApi = {
  /**
   * 生成报告
   */
  async generate(request: ReportRequest): Promise<ReportData> {
    try {
      const response = await apiClient.post<ReportData>('/report/generate', request)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 获取快速统计
   */
  async getQuickStats(): Promise<QuickStats> {
    try {
      const response = await apiClient.get<QuickStats>('/report/quick-stats')
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 获取医生摘要
   */
  async getDoctorSummary(days = 7): Promise<DoctorSummary> {
    try {
      const response = await apiClient.get<DoctorSummary>('/report/summary/doctor', {
        params: { days }
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 导出 CSV
   */
  async exportCsv(startDate: string, endDate: string, deviceId?: string): Promise<Blob> {
    try {
      const response = await apiClient.get('/report/export/csv', {
        params: {
          start_date: startDate,
          end_date: endDate,
          device_id: deviceId
        },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * 导出 JSON
   */
  async exportJson(startDate: string, endDate: string, deviceId?: string): Promise<Blob> {
    try {
      const response = await apiClient.get('/report/export/json', {
        params: {
          start_date: startDate,
          end_date: endDate,
          device_id: deviceId
        },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  }
}
