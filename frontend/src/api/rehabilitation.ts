/**
 * Tremor Guard - Rehabilitation API
 * 震颤卫士 - 运动康复 API
 */

import apiClient from './index'
import type {
  Exercise,
  ExerciseCategory,
  TrainingPlan,
  TrainingCheckIn,
  TrainingStats,
} from '@/types'

export const rehabilitationApi = {
  // ============================================================
  // 运动库
  // ============================================================

  /**
   * 获取运动列表
   */
  async listExercises(params?: {
    category?: ExerciseCategory
    difficulty?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<Exercise[]> {
    const response = await apiClient.get<Exercise[]>('/rehabilitation/exercises', { params })
    return response.data
  },

  /**
   * 获取单个运动详情
   */
  async getExercise(id: number): Promise<Exercise> {
    const response = await apiClient.get<Exercise>(`/rehabilitation/exercises/${id}`)
    return response.data
  },

  /**
   * 获取推荐运动（基于用户健康档案）
   */
  async getRecommendedExercises(): Promise<Exercise[]> {
    const response = await apiClient.get<Exercise[]>('/rehabilitation/exercises/recommended')
    return response.data
  },

  /**
   * 按分类获取运动
   */
  async getExercisesByCategory(category: ExerciseCategory): Promise<Exercise[]> {
    const response = await apiClient.get<Exercise[]>(
      `/rehabilitation/exercises/category/${category}`
    )
    return response.data
  },

  // ============================================================
  // 训练计划
  // ============================================================

  /**
   * 获取用户的训练计划列表
   */
  async listPlans(): Promise<TrainingPlan[]> {
    const response = await apiClient.get<TrainingPlan[]>('/rehabilitation/plans')
    return response.data
  },

  /**
   * 获取单个训练计划
   */
  async getPlan(id: number): Promise<TrainingPlan> {
    const response = await apiClient.get<TrainingPlan>(`/rehabilitation/plans/${id}`)
    return response.data
  },

  /**
   * 创建训练计划
   */
  async createPlan(
    data: Omit<TrainingPlan, 'id' | 'user_id' | 'created_at' | 'updated_at'>
  ): Promise<TrainingPlan> {
    const response = await apiClient.post<TrainingPlan>('/rehabilitation/plans', data)
    return response.data
  },

  /**
   * 更新训练计划
   */
  async updatePlan(id: number, data: Partial<TrainingPlan>): Promise<TrainingPlan> {
    const response = await apiClient.put<TrainingPlan>(`/rehabilitation/plans/${id}`, data)
    return response.data
  },

  /**
   * 删除训练计划
   */
  async deletePlan(id: number): Promise<void> {
    await apiClient.delete(`/rehabilitation/plans/${id}`)
  },

  /**
   * 设置活跃计划
   */
  async setActivePlan(id: number): Promise<TrainingPlan> {
    const response = await apiClient.post<TrainingPlan>(`/rehabilitation/plans/${id}/activate`)
    return response.data
  },

  /**
   * 获取当前活跃计划
   */
  async getActivePlan(): Promise<TrainingPlan | null> {
    try {
      const response = await apiClient.get<TrainingPlan>('/rehabilitation/plans/active')
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * 获取今日应做运动
   */
  async getTodayExercises(): Promise<
    {
      exercise: Exercise
      sets?: number
      reps?: number
      duration_minutes?: number
      completed: boolean
    }[]
  > {
    const response = await apiClient.get('/rehabilitation/plans/today')
    return response.data
  },

  // ============================================================
  // 训练打卡
  // ============================================================

  /**
   * 获取打卡记录列表
   */
  async listCheckIns(params?: {
    startDate?: string
    endDate?: string
    planId?: number
    limit?: number
    offset?: number
  }): Promise<TrainingCheckIn[]> {
    const response = await apiClient.get<TrainingCheckIn[]>('/rehabilitation/check-ins', {
      params,
    })
    return response.data
  },

  /**
   * 提交打卡
   */
  async checkIn(data: Omit<TrainingCheckIn, 'id' | 'user_id' | 'created_at'>): Promise<TrainingCheckIn> {
    const response = await apiClient.post<TrainingCheckIn>('/rehabilitation/check-ins', data)
    return response.data
  },

  /**
   * 更新打卡记录
   */
  async updateCheckIn(id: number, data: Partial<TrainingCheckIn>): Promise<TrainingCheckIn> {
    const response = await apiClient.put<TrainingCheckIn>(`/rehabilitation/check-ins/${id}`, data)
    return response.data
  },

  /**
   * 获取今日打卡
   */
  async getTodayCheckIn(): Promise<TrainingCheckIn | null> {
    try {
      const response = await apiClient.get<TrainingCheckIn>('/rehabilitation/check-ins/today')
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  /**
   * 获取打卡日历数据
   */
  async getCheckInCalendar(
    year: number,
    month: number
  ): Promise<
    {
      date: string
      has_check_in: boolean
      duration_minutes?: number
      exercises_count?: number
    }[]
  > {
    const response = await apiClient.get('/rehabilitation/check-ins/calendar', {
      params: { year, month },
    })
    return response.data
  },

  // ============================================================
  // 统计分析
  // ============================================================

  /**
   * 获取训练统计
   */
  async getStats(days?: number): Promise<TrainingStats> {
    const response = await apiClient.get<TrainingStats>('/rehabilitation/stats', {
      params: { days },
    })
    return response.data
  },

  /**
   * 获取特定运动的进度
   */
  async getExerciseProgress(exerciseId: number): Promise<{
    dates: string[]
    durations: number[]
    ratings: number[]
    total_sessions: number
    avg_duration: number
  }> {
    const response = await apiClient.get(`/rehabilitation/exercises/${exerciseId}/progress`)
    return response.data
  },

  /**
   * 获取周报
   */
  async getWeeklyReport(weekOffset?: number): Promise<{
    week_start: string
    week_end: string
    days_trained: number
    total_minutes: number
    exercises_completed: number
    streak_days: number
    mood_trend: number[]
    tremor_trend: number[]
    achievements: string[]
  }> {
    const response = await apiClient.get('/rehabilitation/stats/weekly', {
      params: { week_offset: weekOffset },
    })
    return response.data
  },
}
