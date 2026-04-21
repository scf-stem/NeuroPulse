/**
 * Tremor Guard - Tremor Data Store
 * 震颤卫士 - 震颤数据状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TremorData, TremorSession } from '@/types'
import { dataApi, type TodayStats } from '@/api/data'

export const useTremorStore = defineStore('tremor', () => {
  // State
  const currentSession = ref<TremorSession | null>(null)
  const recentData = ref<TremorData[]>([])
  const sessions = ref<TremorSession[]>([])
  const todayStats = ref<TodayStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isMonitoring = computed(() => currentSession.value?.is_active ?? false)

  const latestReading = computed(() => {
    if (recentData.value.length === 0) return null
    return recentData.value[0] // 最新的在前面
  })

  const tremorDetectionRate = computed(() => {
    if (recentData.value.length === 0) return 0
    const detections = recentData.value.filter(d => d.detected).length
    return (detections / recentData.value.length) * 100
  })

  const averageSeverity = computed(() => {
    const detected = recentData.value.filter(d => d.detected)
    if (detected.length === 0) return 0
    const sum = detected.reduce((acc, d) => acc + d.severity, 0)
    return sum / detected.length
  })

  // Actions
  function addReading(data: TremorData) {
    recentData.value.unshift(data) // 添加到开头
    // 保持最近 100 条数据
    if (recentData.value.length > 100) {
      recentData.value.pop()
    }
  }

  function clearRecentData() {
    recentData.value = []
  }

  function setCurrentSession(session: TremorSession | null) {
    currentSession.value = session
  }

  async function startSession(deviceId: string) {
    loading.value = true
    error.value = null
    try {
      const session = await dataApi.startSession(deviceId)
      currentSession.value = session
      return session
    } catch (e: any) {
      error.value = e.response?.data?.detail || '创建会话失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function endSession(sessionId: number) {
    loading.value = true
    error.value = null
    try {
      const session = await dataApi.endSession(sessionId)
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
      }
      return session
    } catch (e: any) {
      error.value = e.response?.data?.detail || '结束会话失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchSessions(limit = 20) {
    loading.value = true
    error.value = null
    try {
      sessions.value = await dataApi.getHistory({ limit })
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取会话列表失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchRecentData(limit = 50) {
    loading.value = true
    error.value = null
    try {
      recentData.value = await dataApi.getRecentData(limit)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取数据失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchTodayStats() {
    loading.value = true
    error.value = null
    try {
      todayStats.value = await dataApi.getTodayStats()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取统计失败'
    } finally {
      loading.value = false
    }
  }

  async function fetchSessionData(sessionId: number, limit = 100) {
    loading.value = true
    error.value = null
    try {
      return await dataApi.getSessionData(sessionId, limit)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取会话数据失败'
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    currentSession,
    recentData,
    sessions,
    todayStats,
    loading,
    error,

    // Getters
    isMonitoring,
    latestReading,
    tremorDetectionRate,
    averageSeverity,

    // Actions
    addReading,
    clearRecentData,
    setCurrentSession,
    startSession,
    endSession,
    fetchSessions,
    fetchRecentData,
    fetchTodayStats,
    fetchSessionData,
  }
})
