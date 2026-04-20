/**
 * Tremor Guard - Rehabilitation Store
 * 震颤卫士 - 运动康复状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Exercise,
  ExerciseCategory,
  TrainingPlan,
  TrainingCheckIn,
  TrainingStats,
} from '@/types'
import { rehabilitationApi } from '@/api/rehabilitation'

export const useRehabilitationStore = defineStore('rehabilitation', () => {
  // ============================================================
  // State
  // ============================================================
  const exercises = ref<Exercise[]>([])
  const recommendedExercises = ref<Exercise[]>([])
  const plans = ref<TrainingPlan[]>([])
  const activePlan = ref<TrainingPlan | null>(null)
  const todayExercises = ref<
    {
      exercise: Exercise
      sets?: number
      reps?: number
      duration_minutes?: number
      completed: boolean
    }[]
  >([])
  const todayCheckIn = ref<TrainingCheckIn | null>(null)
  const stats = ref<TrainingStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ============================================================
  // Getters
  // ============================================================

  /**
   * 是否有活跃计划
   */
  const hasActivePlan = computed(() => activePlan.value !== null)

  /**
   * 今日是否已打卡
   */
  const hasCheckedInToday = computed(() => todayCheckIn.value !== null)

  /**
   * 当前连续天数
   */
  const currentStreak = computed(() => stats.value?.current_streak || 0)

  /**
   * 今日待完成运动数
   */
  const pendingExercisesCount = computed(() => {
    return todayExercises.value.filter((e) => !e.completed).length
  })

  /**
   * 今日已完成运动数
   */
  const completedExercisesCount = computed(() => {
    return todayExercises.value.filter((e) => e.completed).length
  })

  /**
   * 今日完成率
   */
  const todayCompletionRate = computed(() => {
    if (todayExercises.value.length === 0) return 0
    return Math.round((completedExercisesCount.value / todayExercises.value.length) * 100)
  })

  /**
   * 按分类分组的运动
   */
  const exercisesByCategory = computed(() => {
    const grouped: Record<ExerciseCategory, Exercise[]> = {} as Record<ExerciseCategory, Exercise[]>
    exercises.value.forEach((exercise) => {
      if (!grouped[exercise.category]) {
        grouped[exercise.category] = []
      }
      grouped[exercise.category].push(exercise)
    })
    return grouped
  })

  // ============================================================
  // Actions
  // ============================================================

  /**
   * 获取运动列表
   */
  async function fetchExercises(params?: Parameters<typeof rehabilitationApi.listExercises>[0]) {
    loading.value = true
    error.value = null
    try {
      exercises.value = await rehabilitationApi.listExercises(params)
    } catch (e: any) {
      error.value = e.response?.data?.detail || '获取运动列表失败'
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取推荐运动
   */
  async function fetchRecommendedExercises() {
    try {
      recommendedExercises.value = await rehabilitationApi.getRecommendedExercises()
    } catch (e: any) {
      console.error('获取推荐运动失败:', e)
    }
  }

  /**
   * 获取用户的训练计划
   */
  async function fetchPlans() {
    loading.value = true
    try {
      plans.value = await rehabilitationApi.listPlans()
    } catch (e: any) {
      console.error('获取训练计划失败:', e)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取活跃计划
   */
  async function fetchActivePlan() {
    try {
      activePlan.value = await rehabilitationApi.getActivePlan()
    } catch (e: any) {
      console.error('获取活跃计划失败:', e)
    }
  }

  /**
   * 创建训练计划
   */
  async function createPlan(data: Parameters<typeof rehabilitationApi.createPlan>[0]) {
    loading.value = true
    error.value = null
    try {
      const plan = await rehabilitationApi.createPlan(data)
      plans.value.push(plan)
      if (plan.is_active) {
        activePlan.value = plan
      }
      return plan
    } catch (e: any) {
      error.value = e.response?.data?.detail || '创建训练计划失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新训练计划
   */
  async function updatePlan(id: number, data: Partial<TrainingPlan>) {
    loading.value = true
    error.value = null
    try {
      const updated = await rehabilitationApi.updatePlan(id, data)
      const index = plans.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        plans.value[index] = updated
      }
      if (activePlan.value?.id === id) {
        activePlan.value = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新训练计划失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除训练计划
   */
  async function deletePlan(id: number) {
    loading.value = true
    try {
      await rehabilitationApi.deletePlan(id)
      plans.value = plans.value.filter((p) => p.id !== id)
      if (activePlan.value?.id === id) {
        activePlan.value = null
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || '删除训练计划失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置活跃计划
   */
  async function setActivePlan(id: number) {
    loading.value = true
    try {
      activePlan.value = await rehabilitationApi.setActivePlan(id)
      // 更新计划列表中的状态
      plans.value.forEach((p) => {
        p.is_active = p.id === id
      })
      // 刷新今日运动
      await fetchTodayExercises()
    } catch (e: any) {
      error.value = e.response?.data?.detail || '设置活跃计划失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取今日应做运动
   */
  async function fetchTodayExercises() {
    try {
      todayExercises.value = await rehabilitationApi.getTodayExercises()
    } catch (e: any) {
      console.error('获取今日运动失败:', e)
    }
  }

  /**
   * 获取今日打卡记录
   */
  async function fetchTodayCheckIn() {
    try {
      todayCheckIn.value = await rehabilitationApi.getTodayCheckIn()
    } catch (e: any) {
      console.error('获取今日打卡失败:', e)
    }
  }

  /**
   * 提交打卡
   */
  async function checkIn(data: Parameters<typeof rehabilitationApi.checkIn>[0]) {
    loading.value = true
    error.value = null
    try {
      todayCheckIn.value = await rehabilitationApi.checkIn(data)
      // 刷新统计
      await fetchStats()
      return todayCheckIn.value
    } catch (e: any) {
      error.value = e.response?.data?.detail || '打卡失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新打卡记录
   */
  async function updateCheckIn(id: number, data: Partial<TrainingCheckIn>) {
    loading.value = true
    try {
      const updated = await rehabilitationApi.updateCheckIn(id, data)
      if (todayCheckIn.value?.id === id) {
        todayCheckIn.value = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || '更新打卡失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取训练统计
   */
  async function fetchStats(days?: number) {
    try {
      stats.value = await rehabilitationApi.getStats(days)
    } catch (e: any) {
      console.error('获取训练统计失败:', e)
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
      fetchExercises(),
      fetchRecommendedExercises(),
      fetchPlans(),
      fetchActivePlan(),
      fetchTodayExercises(),
      fetchTodayCheckIn(),
      fetchStats(),
    ])
  }

  return {
    // State
    exercises,
    recommendedExercises,
    plans,
    activePlan,
    todayExercises,
    todayCheckIn,
    stats,
    loading,
    error,

    // Getters
    hasActivePlan,
    hasCheckedInToday,
    currentStreak,
    pendingExercisesCount,
    completedExercisesCount,
    todayCompletionRate,
    exercisesByCategory,

    // Actions
    fetchExercises,
    fetchRecommendedExercises,
    fetchPlans,
    fetchActivePlan,
    createPlan,
    updatePlan,
    deletePlan,
    setActivePlan,
    fetchTodayExercises,
    fetchTodayCheckIn,
    checkIn,
    updateCheckIn,
    fetchStats,
    clearError,
    initialize,
  }
})
