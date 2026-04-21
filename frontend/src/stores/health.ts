/**
 * Tremor Guard - Health Store
 * 震颤卫士 - 健康档案状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { HealthProfile, MedicalRecord, FamilyHistory, VisitRecord } from '@/types'
import { healthApi } from '@/api/health'

export const useHealthStore = defineStore('health', () => {
  // ============================================================
  // State
  // ============================================================
  const profile = ref<HealthProfile | null>(null)
  const medicalRecords = ref<MedicalRecord[]>([])
  const familyHistory = ref<FamilyHistory[]>([])
  const visitRecords = ref<VisitRecord[]>([])
  const upcomingFollowUps = ref<VisitRecord[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================
  // Getters
  // ============================================================

  /**
   * 是否已创建健康档案
   */
  const hasProfile = computed(() => profile.value !== null)

  /**
   * Hoehn-Yahr 分期
   */
  const hoehYahrStage = computed(() => profile.value?.hoehn_yahr_stage)

  /**
   * 确诊年数
   */
  const diagnosisYears = computed(() => {
    if (!profile.value?.diagnosis_date) return null
    const diagnosisDate = new Date(profile.value.diagnosis_date)
    const now = new Date()
    return Math.floor((now.getTime() - diagnosisDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
  })

  /**
   * 年龄
   */
  const age = computed(() => {
    if (!profile.value?.birth_date) return null
    const birthDate = new Date(profile.value.birth_date)
    const now = new Date()
    return Math.floor((now.getTime() - birthDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
  })

  /**
   * 是否有家族帕金森病史
   */
  const hasFamilyParkinsons = computed(() => {
    return familyHistory.value.some((h) => h.has_parkinsons)
  })

  /**
   * 最近的就诊记录
   */
  const latestVisit = computed(() => {
    if (visitRecords.value.length === 0) return null
    return visitRecords.value.sort(
      (a, b) => new Date(b.visit_date).getTime() - new Date(a.visit_date).getTime()
    )[0]
  })

  /**
   * 有即将到来的复诊
   */
  const hasUpcomingFollowUp = computed(() => upcomingFollowUps.value.length > 0)

  // ============================================================
  // Actions
  // ============================================================

  /**
   * 获取健康档案
   */
  async function fetchProfile() {
    loading.value = true
    error.value = null
    try {
      profile.value = await healthApi.getProfile()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取健康档案失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建健康档案
   */
  async function createProfile(data: Parameters<typeof healthApi.createProfile>[0]) {
    loading.value = true
    error.value = null
    try {
      profile.value = await healthApi.createProfile(data)
      return profile.value
    } catch (e: any) {
      error.value = e.response?.data?.detail || '创建健康档案失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新健康档案
   */
  async function updateProfile(data: Partial<HealthProfile>) {
    loading.value = true
    error.value = null
    try {
      profile.value = await healthApi.updateProfile(data)
      return profile.value
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新健康档案失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取病历记录
   */
  async function fetchMedicalRecords(params?: Parameters<typeof healthApi.listMedicalRecords>[0]) {
    loading.value = true
    try {
      medicalRecords.value = await healthApi.listMedicalRecords(params)
    } catch (e: any) {
      console.error('获取病历记录失败:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加病历记录
   */
  async function addMedicalRecord(data: Parameters<typeof healthApi.createMedicalRecord>[0]) {
    loading.value = true
    error.value = null
    try {
      const record = await healthApi.createMedicalRecord(data)
      medicalRecords.value.unshift(record)
      return record
    } catch (e: any) {
      error.value = e.response?.data?.detail || '添加病历记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新病历记录
   */
  async function updateMedicalRecord(id: number, data: Partial<MedicalRecord>) {
    loading.value = true
    error.value = null
    try {
      const updated = await healthApi.updateMedicalRecord(id, data)
      const index = medicalRecords.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        medicalRecords.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新病历记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除病历记录
   */
  async function deleteMedicalRecord(id: number) {
    loading.value = true
    try {
      await healthApi.deleteMedicalRecord(id)
      medicalRecords.value = medicalRecords.value.filter((r) => r.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '删除病历记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取家族病史
   */
  async function fetchFamilyHistory() {
    loading.value = true
    try {
      familyHistory.value = await healthApi.listFamilyHistory()
    } catch (e: any) {
      console.error('获取家族病史失败:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加家族病史
   */
  async function addFamilyHistory(data: Parameters<typeof healthApi.createFamilyHistory>[0]) {
    loading.value = true
    error.value = null
    try {
      const record = await healthApi.createFamilyHistory(data)
      familyHistory.value.push(record)
      return record
    } catch (e: any) {
      error.value = e.response?.data?.detail || '添加家族病史失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除家族病史
   */
  async function deleteFamilyHistory(id: number) {
    loading.value = true
    try {
      await healthApi.deleteFamilyHistory(id)
      familyHistory.value = familyHistory.value.filter((h) => h.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '删除家族病史失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取就诊记录
   */
  async function fetchVisitRecords(params?: Parameters<typeof healthApi.listVisitRecords>[0]) {
    loading.value = true
    try {
      visitRecords.value = await healthApi.listVisitRecords(params)
    } catch (e: any) {
      console.error('获取就诊记录失败:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加就诊记录
   */
  async function addVisitRecord(data: Parameters<typeof healthApi.createVisitRecord>[0]) {
    loading.value = true
    error.value = null
    try {
      const record = await healthApi.createVisitRecord(data)
      visitRecords.value.unshift(record)
      return record
    } catch (e: any) {
      error.value = e.response?.data?.detail || '添加就诊记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新就诊记录
   */
  async function updateVisitRecord(id: number, data: Partial<VisitRecord>) {
    loading.value = true
    error.value = null
    try {
      const updated = await healthApi.updateVisitRecord(id, data)
      const index = visitRecords.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        visitRecords.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新就诊记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除就诊记录
   */
  async function deleteVisitRecord(id: number) {
    loading.value = true
    try {
      await healthApi.deleteVisitRecord(id)
      visitRecords.value = visitRecords.value.filter((r) => r.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '删除就诊记录失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取即将到来的复诊
   */
  async function fetchUpcomingFollowUps() {
    try {
      upcomingFollowUps.value = await healthApi.getUpcomingFollowUps()
    } catch (e: any) {
      console.error('获取复诊提醒失败:', e)
    }
  }

  /**
   * 清除错误
   */
  function clearError() {
    error.value = null
  }

  /**
   * 初始化数据
   */
  async function initialize() {
    await Promise.all([
      fetchProfile(),
      fetchMedicalRecords(),
      fetchFamilyHistory(),
      fetchVisitRecords(),
      fetchUpcomingFollowUps(),
    ])
  }

  return {
    // State
    profile,
    medicalRecords,
    familyHistory,
    visitRecords,
    upcomingFollowUps,
    loading,
    error,

    // Getters
    hasProfile,
    hoehYahrStage,
    diagnosisYears,
    age,
    hasFamilyParkinsons,
    latestVisit,
    hasUpcomingFollowUp,

    // Actions
    fetchProfile,
    createProfile,
    updateProfile,
    fetchMedicalRecords,
    addMedicalRecord,
    updateMedicalRecord,
    deleteMedicalRecord,
    fetchFamilyHistory,
    addFamilyHistory,
    deleteFamilyHistory,
    fetchVisitRecords,
    addVisitRecord,
    updateVisitRecord,
    deleteVisitRecord,
    fetchUpcomingFollowUps,
    clearError,
    initialize,
  }
})
