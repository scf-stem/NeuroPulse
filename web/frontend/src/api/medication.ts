/**
 * Tremor Guard - Medication API
 * 震颤卫士 - 用药管理 API
 */

import apiClient from './index'
import type {
  Medication,
  MedicationCreateRequest,
  DosageRecord,
  DosageRecordCreateRequest,
  MedicationReminder,
  MedicationEffectiveness,
} from '@/types'

export const medicationApi = {
  // ============================================================
  // 药物管理
  // ============================================================

  /**
   * 获取用户的所有药物
   */
  async list(): Promise<Medication[]> {
    const response = await apiClient.get<Medication[]>('/medication')
    return response.data
  },

  /**
   * 获取单个药物详情
   */
  async get(id: number): Promise<Medication> {
    const response = await apiClient.get<Medication>(`/medication/${id}`)
    return response.data
  },

  /**
   * 添加新药物
   */
  async create(data: MedicationCreateRequest): Promise<Medication> {
    const response = await apiClient.post<Medication>('/medication', data)
    return response.data
  },

  /**
   * 更新药物信息
   */
  async update(id: number, data: Partial<MedicationCreateRequest>): Promise<Medication> {
    const response = await apiClient.put<Medication>(`/medication/${id}`, data)
    return response.data
  },

  /**
   * 删除药物
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/medication/${id}`)
  },

  /**
   * 设置药物启用/停用状态
   */
  async setActive(id: number, isActive: boolean): Promise<Medication> {
    const response = await apiClient.patch<Medication>(`/medication/${id}/active`, {
      is_active: isActive,
    })
    return response.data
  },

  /**
   * 获取当前使用的药物列表
   */
  async getActive(): Promise<Medication[]> {
    const response = await apiClient.get<Medication[]>('/medication/active')
    return response.data
  },

  // ============================================================
  // 服药记录
  // ============================================================

  /**
   * 获取服药记录列表
   */
  async listRecords(params?: {
    medicationId?: number
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<DosageRecord[]> {
    const response = await apiClient.get<DosageRecord[]>('/medication/records', { params })
    return response.data
  },

  /**
   * 记录一次服药
   */
  async recordDosage(data: DosageRecordCreateRequest): Promise<DosageRecord> {
    const response = await apiClient.post<DosageRecord>('/medication/records', data)
    return response.data
  },

  /**
   * 更新服药记录
   */
  async updateRecord(id: number, data: Partial<DosageRecordCreateRequest>): Promise<DosageRecord> {
    const response = await apiClient.put<DosageRecord>(`/medication/records/${id}`, data)
    return response.data
  },

  /**
   * 删除服药记录
   */
  async deleteRecord(id: number): Promise<void> {
    await apiClient.delete(`/medication/records/${id}`)
  },

  /**
   * 获取今日服药记录
   */
  async getTodayRecords(): Promise<DosageRecord[]> {
    const response = await apiClient.get<DosageRecord[]>('/medication/records/today')
    return response.data
  },

  /**
   * 获取今日待服药列表
   */
  async getTodaySchedule(): Promise<
    {
      medication: Medication
      scheduled_time: string
      status: 'pending' | 'taken' | 'missed'
      record?: DosageRecord
    }[]
  > {
    const response = await apiClient.get('/medication/schedule/today')
    return response.data
  },

  // ============================================================
  // 提醒管理
  // ============================================================

  /**
   * 获取药物的提醒设置
   */
  async listReminders(medicationId: number): Promise<MedicationReminder[]> {
    const response = await apiClient.get<MedicationReminder[]>(
      `/medication/${medicationId}/reminders`
    )
    return response.data
  },

  /**
   * 创建提醒
   */
  async createReminder(
    data: Omit<MedicationReminder, 'id' | 'created_at'>
  ): Promise<MedicationReminder> {
    const response = await apiClient.post<MedicationReminder>('/medication/reminders', data)
    return response.data
  },

  /**
   * 更新提醒
   */
  async updateReminder(
    id: number,
    data: Partial<MedicationReminder>
  ): Promise<MedicationReminder> {
    const response = await apiClient.put<MedicationReminder>(`/medication/reminders/${id}`, data)
    return response.data
  },

  /**
   * 删除提醒
   */
  async deleteReminder(id: number): Promise<void> {
    await apiClient.delete(`/medication/reminders/${id}`)
  },

  /**
   * 启用/禁用提醒
   */
  async enableReminder(id: number, enabled: boolean): Promise<MedicationReminder> {
    const response = await apiClient.patch<MedicationReminder>(
      `/medication/reminders/${id}/enable`,
      { is_enabled: enabled }
    )
    return response.data
  },

  // ============================================================
  // 药效分析
  // ============================================================

  /**
   * 获取药效分析数据
   */
  async getEffectivenessAnalysis(params: {
    medicationId?: number
    startDate: string
    endDate: string
  }): Promise<MedicationEffectiveness[]> {
    const response = await apiClient.get<MedicationEffectiveness[]>(
      '/medication/analysis/effectiveness',
      { params }
    )
    return response.data
  },

  /**
   * 获取药物与震颤的关联分析
   */
  async getMedicationTremorCorrelation(
    medicationId: number,
    days?: number
  ): Promise<{
    correlation_score: number
    peak_effect_hours: number
    duration_hours: number
    optimal_timing: string[]
    insights: string[]
  }> {
    const response = await apiClient.get(`/medication/${medicationId}/correlation`, {
      params: { days },
    })
    return response.data
  },
}
