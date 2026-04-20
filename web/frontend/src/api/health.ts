/**
 * Tremor Guard - Health Profile API
 * 震颤卫士 - 健康档案 API
 */

import apiClient from './index'
import type {
  HealthProfile,
  MedicalRecord,
  FamilyHistory,
  VisitRecord,
} from '@/types'

export const healthApi = {
  // ============================================================
  // 健康档案
  // ============================================================

  /**
   * 获取用户健康档案
   */
  async getProfile(): Promise<HealthProfile | null> {
    try {
      const response = await apiClient.get<HealthProfile>('/health/profile')
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * 创建健康档案
   */
  async createProfile(
    data: Omit<HealthProfile, 'id' | 'user_id' | 'created_at' | 'updated_at'>
  ): Promise<HealthProfile> {
    const response = await apiClient.post<HealthProfile>('/health/profile', data)
    return response.data
  },

  /**
   * 更新健康档案
   */
  async updateProfile(data: Partial<HealthProfile>): Promise<HealthProfile> {
    const response = await apiClient.put<HealthProfile>('/health/profile', data)
    return response.data
  },

  // ============================================================
  // 病历记录
  // ============================================================

  /**
   * 获取病历记录列表
   */
  async listMedicalRecords(params?: {
    recordType?: string
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<MedicalRecord[]> {
    const response = await apiClient.get<MedicalRecord[]>('/health/medical-records', { params })
    return response.data
  },

  /**
   * 获取单条病历记录
   */
  async getMedicalRecord(id: number): Promise<MedicalRecord> {
    const response = await apiClient.get<MedicalRecord>(`/health/medical-records/${id}`)
    return response.data
  },

  /**
   * 创建病历记录
   */
  async createMedicalRecord(
    data: Omit<MedicalRecord, 'id' | 'user_id' | 'created_at'>
  ): Promise<MedicalRecord> {
    const response = await apiClient.post<MedicalRecord>('/health/medical-records', data)
    return response.data
  },

  /**
   * 更新病历记录
   */
  async updateMedicalRecord(
    id: number,
    data: Partial<MedicalRecord>
  ): Promise<MedicalRecord> {
    const response = await apiClient.put<MedicalRecord>(`/health/medical-records/${id}`, data)
    return response.data
  },

  /**
   * 删除病历记录
   */
  async deleteMedicalRecord(id: number): Promise<void> {
    await apiClient.delete(`/health/medical-records/${id}`)
  },

  // ============================================================
  // 家族病史
  // ============================================================

  /**
   * 获取家族病史列表
   */
  async listFamilyHistory(): Promise<FamilyHistory[]> {
    const response = await apiClient.get<FamilyHistory[]>('/health/family-history')
    return response.data
  },

  /**
   * 创建家族病史记录
   */
  async createFamilyHistory(
    data: Omit<FamilyHistory, 'id' | 'user_id' | 'created_at'>
  ): Promise<FamilyHistory> {
    const response = await apiClient.post<FamilyHistory>('/health/family-history', data)
    return response.data
  },

  /**
   * 更新家族病史记录
   */
  async updateFamilyHistory(
    id: number,
    data: Partial<FamilyHistory>
  ): Promise<FamilyHistory> {
    const response = await apiClient.put<FamilyHistory>(`/health/family-history/${id}`, data)
    return response.data
  },

  /**
   * 删除家族病史记录
   */
  async deleteFamilyHistory(id: number): Promise<void> {
    await apiClient.delete(`/health/family-history/${id}`)
  },

  // ============================================================
  // 就诊记录
  // ============================================================

  /**
   * 获取就诊记录列表
   */
  async listVisitRecords(params?: {
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<VisitRecord[]> {
    const response = await apiClient.get<VisitRecord[]>('/health/visit-records', { params })
    return response.data
  },

  /**
   * 获取单条就诊记录
   */
  async getVisitRecord(id: number): Promise<VisitRecord> {
    const response = await apiClient.get<VisitRecord>(`/health/visit-records/${id}`)
    return response.data
  },

  /**
   * 创建就诊记录
   */
  async createVisitRecord(
    data: Omit<VisitRecord, 'id' | 'user_id' | 'created_at'>
  ): Promise<VisitRecord> {
    const response = await apiClient.post<VisitRecord>('/health/visit-records', data)
    return response.data
  },

  /**
   * 更新就诊记录
   */
  async updateVisitRecord(
    id: number,
    data: Partial<VisitRecord>
  ): Promise<VisitRecord> {
    const response = await apiClient.put<VisitRecord>(`/health/visit-records/${id}`, data)
    return response.data
  },

  /**
   * 删除就诊记录
   */
  async deleteVisitRecord(id: number): Promise<void> {
    await apiClient.delete(`/health/visit-records/${id}`)
  },

  /**
   * 获取即将到来的复诊
   */
  async getUpcomingFollowUps(): Promise<VisitRecord[]> {
    const response = await apiClient.get<VisitRecord[]>('/health/visit-records/upcoming')
    return response.data
  },

  // ============================================================
  // 附件上传
  // ============================================================

  /**
   * 上传附件
   */
  async uploadAttachment(
    file: File,
    recordType: 'medical' | 'visit'
  ): Promise<{ url: string; filename: string }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('record_type', recordType)

    const response = await apiClient.post<{ url: string; filename: string }>(
      '/health/attachments/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  /**
   * 删除附件
   */
  async deleteAttachment(url: string): Promise<void> {
    await apiClient.delete('/health/attachments', { data: { url } })
  },
}
