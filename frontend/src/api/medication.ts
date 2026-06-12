/**
 * Tremor Guard - Medication API
 * 震颤卫士 - 用药管理 API（仅包含后端已实现的接口）
 */

import apiClient from './index'
import type { Medication, MedicationCreateRequest, DosageRecord, DosageRecordCreateRequest } from '@/types'

export const medicationApi = {
  async list(): Promise<Medication[]> {
    const response = await apiClient.get<Medication[]>('/medication')
    return response.data
  },

  async getActive(): Promise<Medication[]> {
    const response = await apiClient.get<Medication[]>('/medication/active')
    return response.data
  },

  async get(id: number): Promise<Medication> {
    const response = await apiClient.get<Medication>(`/medication/${id}`)
    return response.data
  },

  async create(data: MedicationCreateRequest): Promise<Medication> {
    const response = await apiClient.post<Medication>('/medication', data)
    return response.data
  },

  async update(id: number, data: Partial<MedicationCreateRequest>): Promise<Medication> {
    const response = await apiClient.put<Medication>(`/medication/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/medication/${id}`)
  },

  async setActive(id: number, isActive: boolean): Promise<Medication> {
    const response = await apiClient.patch<Medication>(`/medication/${id}/active`, {
      is_active: isActive,
    })
    return response.data
  },

  async getTodayRecords(): Promise<DosageRecord[]> {
    const response = await apiClient.get<DosageRecord[]>('/medication/records/today')
    return response.data
  },

  async recordDosage(data: DosageRecordCreateRequest): Promise<DosageRecord> {
    const response = await apiClient.post<DosageRecord>('/medication/records', data)
    return response.data
  },

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
}
