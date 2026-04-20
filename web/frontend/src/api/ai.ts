/**
 * Tremor Guard - AI API
 * 震颤卫士 - AI API (增强版)
 */

import apiClient from './index'
import type {
  DailyAnalysis,
  PersonalizedAdvice,
  DoctorVisitReport,
  AIConversationContext,
  SymptomCheckRequest,
  SymptomCheckResponse,
  ChatMessage,
  AIActionCard,
} from '@/types'

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
  // ============================================================
  // 基础对话功能
  // ============================================================

  /**
   * AI 对话
   */
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
    const response = await apiClient.get(actionPath, {
      responseType: 'blob',
    })
    return response.data
  },

  /**
   * AI 分析
   */
  async analyze(days = 7): Promise<AnalysisResponse> {
    const response = await apiClient.post<AnalysisResponse>('/ai/analyze', {
      days,
    })
    return response.data
  },

  /**
   * 获取洞察
   */
  async getInsights(days = 7): Promise<InsightsResponse> {
    const response = await apiClient.get<InsightsResponse>('/ai/insights', {
      params: { days },
    })
    return response.data
  },

  /**
   * 获取健康提示
   */
  async getHealthTips(): Promise<HealthTipsResponse> {
    const response = await apiClient.get<HealthTipsResponse>('/ai/health-tips')
    return response.data
  },

  // ============================================================
  // 增强功能：今日智能解读
  // ============================================================

  /**
   * 获取今日/指定日期的智能解读
   */
  async getDailyAnalysis(date?: string): Promise<DailyAnalysis> {
    const response = await apiClient.get<DailyAnalysis>('/ai/daily-analysis', {
      params: { date },
    })
    return response.data
  },

  /**
   * 刷新今日解读（重新生成）
   */
  async refreshDailyAnalysis(date?: string): Promise<DailyAnalysis> {
    const response = await apiClient.post<DailyAnalysis>('/ai/daily-analysis/refresh', {
      date,
    })
    return response.data
  },

  // ============================================================
  // 增强功能：个性化建议
  // ============================================================

  /**
   * 获取个性化建议
   */
  async getPersonalizedAdvice(params?: {
    categories?: string[]
    limit?: number
  }): Promise<PersonalizedAdvice[]> {
    const response = await apiClient.get<PersonalizedAdvice[]>('/ai/personalized-advice', {
      params,
    })
    return response.data
  },

  /**
   * 刷新个性化建议
   */
  async refreshAdvice(): Promise<PersonalizedAdvice[]> {
    const response = await apiClient.post<PersonalizedAdvice[]>('/ai/personalized-advice/refresh')
    return response.data
  },

  /**
   * 标记建议已读/已采纳
   */
  async markAdviceActioned(adviceId: string): Promise<void> {
    await apiClient.post(`/ai/personalized-advice/${adviceId}/action`)
  },

  // ============================================================
  // 增强功能：就诊报告生成
  // ============================================================

  /**
   * 生成就诊报告
   */
  async generateDoctorReport(params: {
    startDate: string
    endDate: string
    includeMedication?: boolean
    includeExercise?: boolean
    language?: 'zh' | 'en'
  }): Promise<DoctorVisitReport> {
    const response = await apiClient.post<DoctorVisitReport>('/ai/doctor-report', params)
    return response.data
  },

  /**
   * 获取已生成的报告列表
   */
  async listDoctorReports(): Promise<
    {
      report_id: string
      generated_at: string
      period_start: string
      period_end: string
    }[]
  > {
    const response = await apiClient.get('/ai/doctor-reports')
    return response.data
  },

  /**
   * 获取指定报告
   */
  async getDoctorReport(reportId: string): Promise<DoctorVisitReport> {
    const response = await apiClient.get<DoctorVisitReport>(`/ai/doctor-reports/${reportId}`)
    return response.data
  },

  /**
   * 导出报告为 PDF
   */
  async exportDoctorReportPDF(reportId: string): Promise<Blob> {
    const response = await apiClient.get(`/ai/doctor-reports/${reportId}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  // ============================================================
  // 增强功能：上下文感知对话
  // ============================================================

  /**
   * 带上下文的对话
   */
  async chatWithContext(
    message: string,
    context: AIConversationContext,
    history?: ChatMessage[]
  ): Promise<ChatResponse & { context_used: string[] }> {
    const response = await apiClient.post('/ai/chat/context', {
      message,
      context,
      conversation_history: history,
    })
    return response.data
  },

  /**
   * 获取上下文建议问题
   */
  async getContextualQuestions(): Promise<
    {
      category: string
      questions: string[]
    }[]
  > {
    const response = await apiClient.get('/ai/contextual-questions')
    return response.data
  },

  // ============================================================
  // 增强功能：症状自查
  // ============================================================

  /**
   * 症状自查
   */
  async checkSymptoms(data: SymptomCheckRequest): Promise<SymptomCheckResponse> {
    const response = await apiClient.post<SymptomCheckResponse>('/ai/symptom-check', data)
    return response.data
  },

  // ============================================================
  // 增强功能：用药分析
  // ============================================================

  /**
   * 分析用药效果
   */
  async analyzeMedicationEffectiveness(medicationId?: number): Promise<{
    summary: string
    effectiveness_score: number
    optimal_timing: string
    insights: string[]
    suggestions: string[]
  }> {
    const response = await apiClient.get('/ai/medication-analysis', {
      params: { medication_id: medicationId },
    })
    return response.data
  },

  // ============================================================
  // Dashboard 集成
  // ============================================================

  /**
   * 获取今日 AI 提示（用于 Dashboard）
   */
  async getTodayTips(): Promise<{
    greeting: string
    daily_summary?: string
    quick_tips: string[]
    alerts: { type: 'info' | 'warning' | 'success'; message: string }[]
  }> {
    const response = await apiClient.get('/ai/today-tips')
    return response.data
  },
}
