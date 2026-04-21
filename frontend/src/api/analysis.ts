/**
 * Tremor Guard - Analysis API
 * 震颤卫士 - 分析 API
 */

import apiClient from './index'

export interface DailyStats {
  date: string
  total_sessions: number
  total_analyses: number
  tremor_detections: number
  detection_rate: number
  avg_frequency: number | null
  avg_amplitude: number | null
  avg_severity: number | null
  max_severity: number
}

export interface WeeklyTrend {
  week_start: string
  week_end: string
  daily_stats: DailyStats[]
  overall_detection_rate: number
  severity_trend: 'improving' | 'stable' | 'worsening'
}

export interface SeverityDistribution {
  level_0: number
  level_1: number
  level_2: number
  level_3: number
  level_4: number
  total: number
}

export interface HourlyDistribution {
  hour: number
  count: number
  tremor_count: number
  avg_severity: number
}

export interface AnalysisSummary {
  period_start: string
  period_end: string
  total_sessions: number
  total_analyses: number
  tremor_detections: number
  detection_rate: number
  avg_severity: number
  max_severity: number
  avg_frequency: number | null
  avg_amplitude: number | null
  severity_distribution: SeverityDistribution
  hourly_distribution: HourlyDistribution[]
}

export interface TrendDataPoint {
  date: string
  total_analyses: number
  tremor_count: number
  detection_rate: number
  avg_severity: number | null
}

export const analysisApi = {
  /**
   * 获取每日统计
   */
  async getDailyStats(targetDate?: string): Promise<DailyStats> {
    const params = targetDate ? { target_date: targetDate } : {}
    const response = await apiClient.get<DailyStats>('/analysis/daily', { params })
    return response.data
  },

  /**
   * 获取周趋势
   */
  async getWeeklyTrend(weekOffset = 0): Promise<WeeklyTrend> {
    const response = await apiClient.get<WeeklyTrend>('/analysis/weekly', {
      params: { week_offset: weekOffset }
    })
    return response.data
  },

  /**
   * 获取严重度分布
   */
  async getSeverityDistribution(days = 7): Promise<SeverityDistribution> {
    const response = await apiClient.get<SeverityDistribution>('/analysis/severity-distribution', {
      params: { days }
    })
    return response.data
  },

  /**
   * 获取时段分布
   */
  async getHourlyDistribution(days = 7): Promise<HourlyDistribution[]> {
    const response = await apiClient.get<HourlyDistribution[]>('/analysis/hourly-distribution', {
      params: { days }
    })
    return response.data
  },

  /**
   * 获取分析摘要
   */
  async getSummary(days = 7): Promise<AnalysisSummary> {
    const response = await apiClient.get<AnalysisSummary>('/analysis/summary', {
      params: { days }
    })
    return response.data
  },

  /**
   * 获取趋势数据
   */
  async getTrend(days = 30): Promise<TrendDataPoint[]> {
    const response = await apiClient.get<TrendDataPoint[]>('/analysis/trend', {
      params: { days }
    })
    return response.data
  }
}
