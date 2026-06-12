/**
 * Tremor Guard - AI API
 * 震颤卫士 - AI API（仅包含后端已实现的接口）
 */

import apiClient from './index'
import type { ChatMessage, AIActionCard } from '@/types'

export interface ChatRequest {
  message: string
  conversation_history?: ChatMessage[]
}

export interface ChatResponse {
  response: string
  suggestions: string[]
  action_card?: AIActionCard | null
}

export interface AIActionExecutionResponse {
  message: string
  action_card?: AIActionCard | null
  route?: string | null
  report_data?: Record<string, unknown> | null
}

export interface AnalysisResponse {
  summary: string
  key_findings: string[]
  recommendations: string[]
  risk_level: string
}

export interface InsightsResponse {
  insights: string[]
  generated_at: string
  period_days: number
  data_summary?: Record<string, unknown>
}

export interface HealthTipsResponse {
  tips: string[]
  personalized: boolean
  generated_at: string
}

export const aiApi = {
  async chat(message: string, history?: ChatMessage[]): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/ai/chat', {
      message,
      conversation_history: history,
    })
    return response.data
  },

  async executeAction(actionPath: string): Promise<AIActionExecutionResponse> {
    const response = await apiClient.post<AIActionExecutionResponse>(actionPath)
    return response.data
  },

  async downloadActionPdf(actionPath: string): Promise<Blob> {
    const response = await apiClient.get(actionPath, { responseType: 'blob' })
    return response.data
  },

  async analyze(days = 7): Promise<AnalysisResponse> {
    const response = await apiClient.post<AnalysisResponse>('/ai/analyze', { days })
    return response.data
  },

  async getInsights(days = 7): Promise<InsightsResponse> {
    const response = await apiClient.get<InsightsResponse>('/ai/insights', { params: { days } })
    return response.data
  },

  async getHealthTips(): Promise<HealthTipsResponse> {
    const response = await apiClient.get<HealthTipsResponse>('/ai/health-tips')
    return response.data
  },

  async getDailyAnalysis(date?: string): Promise<DailyAnalysisResponse> {
    const response = await apiClient.get<DailyAnalysisResponse>('/ai/daily-analysis', {
      params: date ? { date } : undefined,
    })
    return response.data
  },

  async generateDoctorReport(payload: DoctorReportRequest): Promise<DoctorVisitReportResponse> {
    const response = await apiClient.post<DoctorVisitReportResponse>('/ai/doctor-report', payload)
    return response.data
  },

  async checkSymptoms(payload: SymptomCheckRequest): Promise<SymptomCheckResponse> {
    const response = await apiClient.post<SymptomCheckResponse>('/ai/symptom-check', payload)
    return response.data
  },
}

export interface DailyAnalysisResponse {
  date: string
  summary: string
  tremor_summary: {
    total_detections: number
    avg_severity: number
    max_severity: number
    trend: 'better' | 'same' | 'worse'
    comparison_text: string
  }
  key_observations: string[]
  concerns: string[]
  positive_notes: string[]
  recommendations: string[]
  medication_notes?: string | null
  exercise_notes?: string | null
  generated_at: string
}

export interface DoctorReportRequest {
  start_date: string
  end_date: string
}

export interface DoctorVisitReportResponse {
  report_id: string
  generated_at: string
  period: { start: string; end: string; days: number }
  patient_info: { name: string; age?: number }
  summary: {
    executive_summary: string
    key_metrics: { metric: string; value: string; trend: string }[]
  }
  tremor_analysis: {
    frequency_analysis: string
    severity_distribution: Record<string, number>
    peak_times: string[]
    notable_patterns: string[]
  }
  medication_analysis?: {
    current_medications: string[]
    effectiveness_summary: string
    concerns: string[]
  } | null
  ai_observations: string[]
  questions_for_doctor: string[]
  data_appendix: {
    daily_summaries: { date: string; detections: number; avg_severity: number }[]
  }
}

export interface SymptomCheckRequest {
  symptoms: string[]
  duration: string
  severity: number
  associated_factors?: string[]
}

export interface SymptomCheckResponse {
  assessment: string
  possible_causes: string[]
  urgency_level: 'routine' | 'soon' | 'urgent'
  recommendations: string[]
  should_see_doctor: boolean
  related_to_parkinsons_likelihood: 'low' | 'medium' | 'high'
}
