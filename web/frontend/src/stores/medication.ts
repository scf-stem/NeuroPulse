/**
 * Tremor Guard - Medication Store
 * 震颤卫士 - 用药管理状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Medication, DosageRecord } from '@/types'
import { medicationApi } from '@/api/medication'

export const useMedicationStore = defineStore('medication', () => {
  // ============================================================
  // State
  // ============================================================
  const medications = ref<Medication[]>([])
  const activeMedications = ref<Medication[]>([])
  const todayRecords = ref<DosageRecord[]>([])
  const todaySchedule = ref<
    {
      medication: Medication
      scheduled_time: string
      status: 'pending' | 'taken' | 'missed'
      record?: DosageRecord
    }[]
  >([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================
  // Getters
  // ============================================================

  /**
   * 今日待服药列表
   */
  const pendingDosages = computed(() => {
    return todaySchedule.value.filter((item) => item.status === 'pending')
  })

  /**
   * 今日已服药列表
   */
  const takenDosages = computed(() => {
    return todaySchedule.value.filter((item) => item.status === 'taken')
  })

  /**
   * 今日漏服列表
   */
  const missedDosages = computed(() => {
    return todaySchedule.value.filter((item) => item.status === 'missed')
  })

  /**
   * 今日服药完成率
   */
  const todayCompletionRate = computed(() => {
    if (todaySchedule.value.length === 0) return 100
    const taken = todaySchedule.value.filter((item) => item.status === 'taken').length
    return Math.round((taken / todaySchedule.value.length) * 100)
  })

  /**
   * 是否有待服药
   */
  const hasPendingDosages = computed(() => pendingDosages.value.length > 0)

  // ============================================================
  // Actions
  // ============================================================

  /**
   * 获取所有药物
   */
  async function fetchMedications() {
    loading.value = true
    error.value = null
    try {
      medications.value = await medicationApi.list()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取药物列表失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前使用的药物
   */
  async function fetchActiveMedications() {
    try {
      activeMedications.value = await medicationApi.getActive()
    } catch (e: any) {
      console.error('获取活跃药物失败:', e)
    }
  }

  /**
   * 获取今日服药记录
   */
  async function fetchTodayRecords() {
    try {
      todayRecords.value = await medicationApi.getTodayRecords()
    } catch (e: any) {
      console.error('获取今日记录失败:', e)
    }
  }

  /**
   * 获取今日服药计划
   */
  async function fetchTodaySchedule() {
    loading.value = true
    try {
      todaySchedule.value = await medicationApi.getTodaySchedule()
    } catch (e: any) {
      console.error('获取今日计划失败:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 添加新药物
   */
  async function addMedication(data: Parameters<typeof medicationApi.create>[0]) {
    loading.value = true
    error.value = null
    try {
      const medication = await medicationApi.create(data)
      medications.value.push(medication)
      if (medication.is_active) {
        activeMedications.value.push(medication)
      }
      return medication
    } catch (e: any) {
      error.value = e.response?.data?.detail || '添加药物失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新药物
   */
  async function updateMedication(id: number, data: Parameters<typeof medicationApi.update>[1]) {
    loading.value = true
    error.value = null
    try {
      const updated = await medicationApi.update(id, data)
      const index = medications.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        medications.value[index] = updated
      }
      // 更新活跃列表
      await fetchActiveMedications()
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新药物失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除药物
   */
  async function deleteMedication(id: number) {
    loading.value = true
    error.value = null
    try {
      await medicationApi.delete(id)
      medications.value = medications.value.filter((m) => m.id !== id)
      activeMedications.value = activeMedications.value.filter((m) => m.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '删除药物失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 记录服药
   */
  async function recordDosage(data: Parameters<typeof medicationApi.recordDosage>[0]) {
    loading.value = true
    error.value = null
    try {
      const record = await medicationApi.recordDosage(data)
      todayRecords.value.push(record)
      // 刷新今日计划
      await fetchTodaySchedule()
      return record
    } catch (e: any) {
      error.value = e.response?.data?.detail || '记录服药失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 快速标记服药
   */
  async function quickTakeMedication(medicationId: number, scheduledTime: string) {
    const medication = activeMedications.value.find((m) => m.id === medicationId)
    if (!medication) return

    return recordDosage({
      medication_id: medicationId,
      dosage_taken: medication.dosage,
      scheduled_time: scheduledTime,
      status: 'taken',
    })
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
      fetchMedications(),
      fetchActiveMedications(),
      fetchTodayRecords(),
      fetchTodaySchedule(),
    ])
  }

  return {
    // State
    medications,
    activeMedications,
    todayRecords,
    todaySchedule,
    loading,
    error,

    // Getters
    pendingDosages,
    takenDosages,
    missedDosages,
    todayCompletionRate,
    hasPendingDosages,

    // Actions
    fetchMedications,
    fetchActiveMedications,
    fetchTodayRecords,
    fetchTodaySchedule,
    addMedication,
    updateMedication,
    deleteMedication,
    recordDosage,
    quickTakeMedication,
    clearError,
    initialize,
  }
})
