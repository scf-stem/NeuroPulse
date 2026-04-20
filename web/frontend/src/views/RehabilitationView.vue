<script setup lang="ts">
/**
 * Neuro Pulse - Rehabilitation View
 */

import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useRehabilitationStore } from '@/stores/rehabilitation'
import { EXERCISE_CATEGORY_LABELS, DIFFICULTY_LABELS } from '@/types'
import type { Exercise, TrainingPlan, TrainingPlanExercise } from '@/types'
import { t } from '@/i18n'

const rehabilitationStore = useRehabilitationStore()

// Tab 状态
const activeTab = ref<'exercises' | 'plans' | 'checkin' | 'stats'>('exercises')

// 筛选状态
const selectedCategory = ref<string>('')
const selectedDifficulty = ref<string>('')

// Tab 配置
const tabs = computed(() => [
  { key: 'exercises', name: t('rehabilitation.tabs.exercises'), icon: 'library' },
  { key: 'plans', name: t('rehabilitation.tabs.plans'), icon: 'calendar' },
  { key: 'checkin', name: t('rehabilitation.tabs.checkin'), icon: 'check' },
  { key: 'stats', name: t('rehabilitation.tabs.stats'), icon: 'chart' },
])

// 分类选项
const categories = Object.entries(EXERCISE_CATEGORY_LABELS).map(([key, label]) => ({
  key,
  label,
}))

// 难度选项
const difficulties = Object.entries(DIFFICULTY_LABELS).map(([key, label]) => ({
  key,
  label,
}))

// 筛选后的运动列表
const filteredExercises = computed(() => {
  return rehabilitationStore.exercises.filter((e) => {
    if (selectedCategory.value && e.category !== selectedCategory.value) return false
    if (selectedDifficulty.value && e.difficulty !== selectedDifficulty.value) return false
    return true
  })
})

// ============================================================
// 运动详情相关
// ============================================================
const showExerciseModal = ref(false)
const selectedExercise = ref<Exercise | null>(null)

function openExerciseModal(exercise: Exercise) {
  selectedExercise.value = exercise
  showExerciseModal.value = true
}

function getDifficultyColor(difficulty: string) {
  const colors: Record<string, string> = {
    beginner: 'bg-mint-100 text-mint-700',
    intermediate: 'bg-primary-100 text-primary-700',
    advanced: 'bg-red-100 text-red-700',
  }
  return colors[difficulty] || 'bg-gray-100 text-gray-700'
}

function getCategoryColor(category: string) {
  const colors: Record<string, string> = {
    stretching: 'bg-blue-100 text-blue-700',
    balance: 'bg-purple-100 text-purple-700',
    strength: 'bg-red-100 text-red-700',
    coordination: 'bg-yellow-100 text-yellow-700',
    facial: 'bg-pink-100 text-pink-700',
    voice: 'bg-indigo-100 text-indigo-700',
    walking: 'bg-green-100 text-green-700',
    tai_chi: 'bg-teal-100 text-teal-700',
    yoga: 'bg-orange-100 text-orange-700',
    breathing: 'bg-cyan-100 text-cyan-700',
  }
  return colors[category] || 'bg-gray-100 text-gray-700'
}

// ============================================================
// 训练计划相关
// ============================================================
const showPlanModal = ref(false)
const editingPlan = ref<TrainingPlan | null>(null)
const planForm = reactive<{
  name: string
  description: string
  exercises: TrainingPlanExercise[]
  schedule: {
    days_of_week: number[]
    time_of_day: string
  }
  is_active: boolean
}>({
  name: '',
  description: '',
  exercises: [],
  schedule: {
    days_of_week: [],
    time_of_day: '08:00',
  },
  is_active: false,
})

const weekDays = [
  { value: 0, label: 'Sun' },
  { value: 1, label: 'Mon' },
  { value: 2, label: 'Tue' },
  { value: 3, label: 'Wed' },
  { value: 4, label: 'Thu' },
  { value: 5, label: 'Fri' },
  { value: 6, label: 'Sat' },
]

function openPlanModal(plan?: TrainingPlan) {
  if (plan) {
    editingPlan.value = plan
    Object.assign(planForm, {
      name: plan.name,
      description: plan.description || '',
      exercises: [...plan.exercises],
      schedule: { ...plan.schedule },
      is_active: plan.is_active,
    })
  } else {
    editingPlan.value = null
    Object.assign(planForm, {
      name: '',
      description: '',
      exercises: [],
      schedule: {
        days_of_week: [1, 3, 5], // 周一三五
        time_of_day: '08:00',
      },
      is_active: false,
    })
  }
  showPlanModal.value = true
}

async function savePlan() {
  try {
    if (editingPlan.value) {
      await rehabilitationStore.updatePlan(editingPlan.value.id, planForm)
    } else {
      await rehabilitationStore.createPlan(planForm as any)
    }
    showPlanModal.value = false
  } catch (e) {
    console.error('保存计划失败:', e)
  }
}

async function deletePlan(id: number) {
  if (confirm(t('rehabilitation.deleteConfirm'))) {
    try {
      await rehabilitationStore.deletePlan(id)
    } catch (e) {
      console.error('删除计划失败:', e)
    }
  }
}

async function setActivePlan(id: number) {
  try {
    await rehabilitationStore.setActivePlan(id)
  } catch (e) {
    console.error('设置活跃计划失败:', e)
  }
}

function toggleWeekDay(day: number) {
  const idx = planForm.schedule.days_of_week.indexOf(day)
  if (idx === -1) {
    planForm.schedule.days_of_week.push(day)
    planForm.schedule.days_of_week.sort()
  } else {
    planForm.schedule.days_of_week.splice(idx, 1)
  }
}

function addExerciseToPlan(exercise: Exercise) {
  if (!planForm.exercises.find((e) => e.exercise_id === exercise.id)) {
    planForm.exercises.push({
      exercise_id: exercise.id,
      exercise: exercise,
      order: planForm.exercises.length + 1,
      sets: 1,
      duration_minutes: exercise.duration_minutes,
    })
  }
}

function removeExerciseFromPlan(index: number) {
  planForm.exercises.splice(index, 1)
  // 重新排序
  planForm.exercises.forEach((e, i) => {
    e.order = i + 1
  })
}

function getScheduleDays(plan: TrainingPlan) {
  return plan.schedule.days_of_week.map((d) => weekDays.find((w) => w.value === d)?.label).join(', ')
}

// ============================================================
// 训练打卡相关
// ============================================================
const showCheckInModal = ref(false)
const checkInForm = reactive<{
  exercises_completed: {
    exercise_id: number
    exercise_name: string
    completed: boolean
    sets_done: number
    duration_minutes: number
    difficulty_rating: number
    notes: string
  }[]
  mood_before: number
  mood_after: number
  tremor_before: number
  tremor_after: number
  overall_rating: number
  notes: string
}>({
  exercises_completed: [],
  mood_before: 3,
  mood_after: 3,
  tremor_before: 3,
  tremor_after: 3,
  overall_rating: 3,
  notes: '',
})

function openCheckInModal() {
  // 初始化打卡表单
  checkInForm.exercises_completed = rehabilitationStore.todayExercises.map((e) => ({
    exercise_id: e.exercise.id,
    exercise_name: e.exercise.name,
    completed: e.completed,
    sets_done: e.sets || 1,
    duration_minutes: e.duration_minutes || e.exercise.duration_minutes,
    difficulty_rating: 3,
    notes: '',
  }))
  checkInForm.mood_before = 3
  checkInForm.mood_after = 3
  checkInForm.tremor_before = 3
  checkInForm.tremor_after = 3
  checkInForm.overall_rating = 3
  checkInForm.notes = ''
  showCheckInModal.value = true
}

async function submitCheckIn() {
  try {
    const totalDuration = checkInForm.exercises_completed
      .filter((e) => e.completed)
      .reduce((sum, e) => sum + e.duration_minutes, 0)

    await rehabilitationStore.checkIn({
      plan_id: rehabilitationStore.activePlan?.id,
      date: new Date().toISOString().split('T')[0],
      exercises_completed: checkInForm.exercises_completed,
      total_duration_minutes: totalDuration,
      mood_before: checkInForm.mood_before,
      mood_after: checkInForm.mood_after,
      tremor_before: checkInForm.tremor_before,
      tremor_after: checkInForm.tremor_after,
      overall_rating: checkInForm.overall_rating,
      notes: checkInForm.notes,
    })
    showCheckInModal.value = false
  } catch (e) {
    console.error('打卡失败:', e)
  }
}

function toggleExerciseComplete(index: number) {
  checkInForm.exercises_completed[index].completed = !checkInForm.exercises_completed[index].completed
}

// Get rating label
function getRatingLabel(rating: number, type: 'mood' | 'tremor' | 'overall') {
  if (type === 'mood') {
    const labels = ['', 'Very Poor', 'Poor', 'Fair', 'Good', 'Very Good']
    return labels[rating] || ''
  } else if (type === 'tremor') {
    const labels = ['', 'Severe', 'Moderate', 'Mild', 'Very Mild', 'No Tremor']
    return labels[rating] || ''
  } else {
    const labels = ['', 'Very Tired', 'Tired', 'Neutral', 'Energetic', 'Very Energetic']
    return labels[rating] || ''
  }
}

// ============================================================
// 周历相关
// ============================================================
const currentWeekStart = ref(getWeekStart(new Date()))

function getWeekStart(date: Date) {
  const d = new Date(date)
  const day = d.getDay()
  d.setDate(d.getDate() - day)
  return d
}

function getWeekDates() {
  const dates = []
  const start = new Date(currentWeekStart.value)
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    dates.push(d)
  }
  return dates
}

function isToday(date: Date) {
  const today = new Date()
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  )
}

function previousWeek() {
  const d = new Date(currentWeekStart.value)
  d.setDate(d.getDate() - 7)
  currentWeekStart.value = d
}

function nextWeek() {
  const d = new Date(currentWeekStart.value)
  d.setDate(d.getDate() + 7)
  currentWeekStart.value = d
}

function formatWeekRange() {
  const start = new Date(currentWeekStart.value)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return `${start.getMonth() + 1}月${start.getDate()}日 - ${end.getMonth() + 1}月${end.getDate()}日`
}

// 检查某天是否是训练日
function isTrainingDay(date: Date) {
  if (!rehabilitationStore.activePlan) return false
  return rehabilitationStore.activePlan.schedule.days_of_week.includes(date.getDay())
}

// 初始化
onMounted(async () => {
  await rehabilitationStore.initialize()
})
</script>

<template>
  <AppLayout>
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div
            class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl shadow-soft flex items-center justify-center"
          >
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('rehabilitation.title') }}</h1>
          <p class="text-gray-500">{{ t('rehabilitation.subtitle') }}</p>
          </div>
        </div>
        <!-- 快捷操作 -->
        <div class="flex items-center gap-3">
          <button
            v-if="!rehabilitationStore.hasCheckedInToday && rehabilitationStore.todayExercises.length > 0"
            class="btn btn-primary"
            @click="openCheckInModal"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Check In Today
          </button>
          <span
            v-else-if="rehabilitationStore.hasCheckedInToday"
            class="px-4 py-2 bg-mint-100 text-mint-700 rounded-xl font-medium flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Checked In Today
          </span>
        </div>
      </div>

      <!-- Today's Training Overview -->
      <div class="grid gap-4 md:grid-cols-4">
        <!-- Current Streak -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Current Streak</p>
              <p class="text-xl font-bold text-gray-800">
                {{ rehabilitationStore.currentStreak }} <span class="text-sm font-normal">days</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Today's Progress -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-mint-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Today's Progress</p>
              <p class="text-xl font-bold text-gray-800">
                {{ rehabilitationStore.completedExercisesCount }}/{{ rehabilitationStore.todayExercises.length }}
              </p>
            </div>
          </div>
        </div>

        <!-- Completion Rate -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-lavender-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Completion Rate</p>
              <p class="text-xl font-bold text-gray-800">{{ rehabilitationStore.todayCompletionRate }}%</p>
            </div>
          </div>
        </div>

        <!-- Total Duration -->
        <div class="card-gradient p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-warmGray-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-warmGray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-500">Total Duration</p>
              <p class="text-xl font-bold text-gray-800">
                {{ rehabilitationStore.stats?.total_duration_minutes || 0 }}
                <span class="text-sm font-normal">minutes</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 导航 -->
      <div class="card-gradient p-1.5">
        <div class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key as any"
            :class="[
              'flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
              activeTab === tab.key
                ? 'bg-white text-primary-600 shadow-soft'
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
            ]"
          >
            <!-- Tab 图标 -->
            <svg v-if="tab.icon === 'library'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <svg v-else-if="tab.icon === 'calendar'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <svg v-else-if="tab.icon === 'check'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <svg v-else-if="tab.icon === 'chart'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Tab 内容 -->
      <div class="card-gradient p-6">
        <!-- 加载状态 -->
        <div v-if="rehabilitationStore.loading" class="flex items-center justify-center py-12">
          <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        </div>

        <!-- 训练库 Tab -->
        <div v-else-if="activeTab === 'exercises'">
          <!-- 筛选 -->
          <div class="mb-6 space-y-4">
            <!-- Category Filter -->
            <div>
              <p class="text-sm font-medium text-gray-600 mb-2">{{ t('rehabilitation.categories') }}</p>
              <div class="flex flex-wrap gap-2">
                <button
                  @click="selectedCategory = ''"
                  :class="[
                    'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    selectedCategory === '' ? 'bg-primary-500 text-white' : 'bg-warmGray-100 text-gray-600 hover:bg-warmGray-200',
                  ]"
                >
                  All
                </button>
                <button
                  v-for="cat in categories"
                  :key="cat.key"
                  @click="selectedCategory = cat.key"
                  :class="[
                    'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    selectedCategory === cat.key
                      ? 'bg-primary-500 text-white'
                      : 'bg-warmGray-100 text-gray-600 hover:bg-warmGray-200',
                  ]"
                >
                  {{ cat.label }}
                </button>
              </div>
            </div>

            <!-- Difficulty Filter -->
            <div>
              <p class="text-sm font-medium text-gray-600 mb-2">{{ t('rehabilitation.difficulty') }}</p>
              <div class="flex flex-wrap gap-2">
                <button
                  @click="selectedDifficulty = ''"
                  :class="[
                    'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    selectedDifficulty === ''
                      ? 'bg-primary-500 text-white'
                      : 'bg-warmGray-100 text-gray-600 hover:bg-warmGray-200',
                  ]"
                >
                  All
                </button>
                <button
                  v-for="diff in difficulties"
                  :key="diff.key"
                  @click="selectedDifficulty = diff.key"
                  :class="[
                    'px-4 py-2 rounded-xl text-sm font-medium transition-colors',
                    selectedDifficulty === diff.key
                      ? 'bg-primary-500 text-white'
                      : 'bg-warmGray-100 text-gray-600 hover:bg-warmGray-200',
                  ]"
                >
                  {{ diff.label }}
                </button>
              </div>
            </div>
          </div>

          <!-- 运动列表 -->
          <div v-if="filteredExercises.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">No exercise content yet</h3>
            <p class="text-gray-500">The showcase library will expand with additional guided routines.</p>
          </div>

          <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="exercise in filteredExercises"
              :key="exercise.id"
              class="p-4 bg-white rounded-xl border border-warmGray-100 hover:shadow-soft transition-shadow cursor-pointer"
              @click="openExerciseModal(exercise)"
            >
              <!-- 缩略图 -->
              <div class="aspect-video bg-warmGray-100 rounded-lg mb-4 flex items-center justify-center overflow-hidden">
                <img
                  v-if="exercise.thumbnail_url"
                  :src="exercise.thumbnail_url"
                  :alt="exercise.name"
                  class="w-full h-full object-cover"
                />
                <svg v-else class="w-12 h-12 text-warmGray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>

              <div class="flex items-start justify-between mb-2">
                <h4 class="font-semibold text-gray-800">{{ exercise.name }}</h4>
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', getDifficultyColor(exercise.difficulty)]">
                  {{ DIFFICULTY_LABELS[exercise.difficulty] }}
                </span>
              </div>

              <p class="text-sm text-gray-500 mb-3 line-clamp-2">{{ exercise.description }}</p>

              <div class="flex items-center justify-between text-sm">
                <span :class="['px-2 py-0.5 rounded text-xs', getCategoryColor(exercise.category)]">
                  {{ EXERCISE_CATEGORY_LABELS[exercise.category] }}
                </span>
                <span class="text-gray-500">{{ exercise.duration_minutes }} minutes</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的计划 Tab -->
        <div v-else-if="activeTab === 'plans'">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">{{ t('rehabilitation.tabs.plans') }}</h3>
            <button class="btn btn-primary" @click="openPlanModal()">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ t('rehabilitation.createPlan') }}
            </button>
          </div>

          <div v-if="rehabilitationStore.plans.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">No active plans yet</h3>
            <p class="text-gray-500">Create a structured routine to begin consistent rehabilitation work.</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="plan in rehabilitationStore.plans"
              :key="plan.id"
              class="p-4 bg-white rounded-xl border border-warmGray-100 hover:shadow-soft transition-shadow"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <h4 class="font-semibold text-gray-800">{{ plan.name }}</h4>
                    <span
                      v-if="plan.is_active"
                      class="px-2 py-0.5 bg-mint-100 text-mint-700 rounded-full text-xs font-medium"
                    >
                      Current Plan
                    </span>
                  </div>
                  <p v-if="plan.description" class="text-sm text-gray-500 mb-3">{{ plan.description }}</p>
                  <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                    <span class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        />
                      </svg>
                      {{ plan.exercises.length }} exercises
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                      {{ getScheduleDays(plan) }}
                    </span>
                    <span v-if="plan.schedule.time_of_day" class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      {{ plan.schedule.time_of_day }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button
                    v-if="!plan.is_active"
                    class="px-3 py-1.5 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    @click="setActivePlan(plan.id)"
                  >
                    Set as Current
                  </button>
                  <button
                    class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    @click="openPlanModal(plan)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                      />
                    </svg>
                  </button>
                  <button
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    @click="deletePlan(plan.id)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 训练打卡 Tab -->
        <div v-else-if="activeTab === 'checkin'">
          <!-- 周历 -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-4">
              <button class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg" @click="previousWeek">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h3 class="text-lg font-semibold text-gray-800">{{ formatWeekRange() }}</h3>
              <button class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg" @click="nextWeek">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            <div class="grid grid-cols-7 gap-2">
              <div v-for="(date, idx) in getWeekDates()" :key="idx" class="text-center">
                <p class="text-xs text-gray-500 mb-1">{{ weekDays[idx].label }}</p>
                <div
                  :class="[
                    'w-10 h-10 mx-auto rounded-full flex items-center justify-center text-sm font-medium transition-colors',
                    isToday(date)
                      ? 'bg-primary-500 text-white'
                      : isTrainingDay(date)
                        ? 'bg-primary-100 text-primary-700'
                        : 'bg-gray-100 text-gray-500',
                  ]"
                >
                  {{ date.getDate() }}
                </div>
                <div v-if="isTrainingDay(date)" class="mt-1">
                  <div class="w-1.5 h-1.5 bg-primary-500 rounded-full mx-auto"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 今日训练 -->
          <div v-if="rehabilitationStore.todayExercises.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">No Training Today</h3>
            <p class="text-gray-500">Today is not a training day, take a good rest</p>
          </div>

          <div v-else class="space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-800">Today's Training</h3>
              <button
                v-if="!rehabilitationStore.hasCheckedInToday"
                class="btn btn-primary"
                @click="openCheckInModal"
              >
                Start Check-in
              </button>
            </div>

            <div class="space-y-3">
              <div
                v-for="(item, idx) in rehabilitationStore.todayExercises"
                :key="idx"
                :class="[
                  'p-4 rounded-xl border transition-colors',
                  item.completed ? 'bg-mint-50 border-mint-200' : 'bg-white border-warmGray-100',
                ]"
              >
                <div class="flex items-center gap-4">
                  <div
                    :class="[
                      'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                      item.completed ? 'bg-mint-500 text-white' : 'bg-gray-100 text-gray-400',
                    ]"
                  >
                    <svg v-if="item.completed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span v-else class="text-sm font-medium">{{ idx + 1 }}</span>
                  </div>
                  <div class="flex-1">
                    <h4 :class="['font-medium', item.completed ? 'text-mint-700' : 'text-gray-800']">
                      {{ item.exercise.name }}
                    </h4>
                    <div class="flex items-center gap-3 text-sm text-gray-500 mt-1">
                      <span>{{ item.duration_minutes || item.exercise.duration_minutes }} 分钟</span>
                      <span v-if="item.sets">{{ item.sets }} 组</span>
                    </div>
                  </div>
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      getDifficultyColor(item.exercise.difficulty),
                    ]"
                  >
                    {{ DIFFICULTY_LABELS[item.exercise.difficulty] }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 进度统计 Tab -->
        <div v-else-if="activeTab === 'stats'">
          <div v-if="!rehabilitationStore.stats || rehabilitationStore.stats.total_check_ins === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">No Training Data Yet</h3>
            <p class="text-gray-500">Start training and check-ins to track your rehabilitation progress</p>
          </div>

          <div v-else class="space-y-6">
            <!-- 总览卡片 -->
            <div class="grid gap-4 md:grid-cols-4">
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <p class="text-sm text-gray-500 mb-1">总打卡次数</p>
                <p class="text-2xl font-bold text-gray-800">{{ rehabilitationStore.stats.total_check_ins }}</p>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <p class="text-sm text-gray-500 mb-1">当前连续</p>
                <p class="text-2xl font-bold text-primary-600">{{ rehabilitationStore.stats.current_streak }} 天</p>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <p class="text-sm text-gray-500 mb-1">最长连续</p>
                <p class="text-2xl font-bold text-gray-800">{{ rehabilitationStore.stats.longest_streak }} 天</p>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <p class="text-sm text-gray-500 mb-1">累计训练</p>
                <p class="text-2xl font-bold text-gray-800">{{ rehabilitationStore.stats.total_duration_minutes }} 分钟</p>
              </div>
            </div>

            <!-- 改善效果 -->
            <div class="grid gap-4 md:grid-cols-2">
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <h4 class="font-medium text-gray-800 mb-3">心情改善</h4>
                <div class="flex items-center gap-4">
                  <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      class="h-full bg-primary-500 rounded-full"
                      :style="{ width: `${Math.max(0, rehabilitationStore.stats.avg_mood_improvement * 20)}%` }"
                    ></div>
                  </div>
                  <span class="text-lg font-bold text-primary-600">
                    +{{ rehabilitationStore.stats.avg_mood_improvement.toFixed(1) }}
                  </span>
                </div>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <h4 class="font-medium text-gray-800 mb-3">震颤改善</h4>
                <div class="flex items-center gap-4">
                  <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      class="h-full bg-mint-500 rounded-full"
                      :style="{ width: `${Math.max(0, rehabilitationStore.stats.avg_tremor_improvement * 20)}%` }"
                    ></div>
                  </div>
                  <span class="text-lg font-bold text-mint-600">
                    +{{ rehabilitationStore.stats.avg_tremor_improvement.toFixed(1) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 常练运动 -->
            <div v-if="rehabilitationStore.stats.favorite_exercises?.length" class="p-4 bg-white rounded-xl border border-warmGray-100">
              <h4 class="font-medium text-gray-800 mb-4">常练运动 TOP5</h4>
              <div class="space-y-3">
                <div
                  v-for="(fav, idx) in rehabilitationStore.stats.favorite_exercises.slice(0, 5)"
                  :key="fav.exercise_id"
                  class="flex items-center gap-3"
                >
                  <span
                    :class="[
                      'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                      idx === 0
                        ? 'bg-yellow-100 text-yellow-700'
                        : idx === 1
                          ? 'bg-gray-200 text-gray-700'
                          : idx === 2
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-gray-100 text-gray-500',
                    ]"
                  >
                    {{ idx + 1 }}
                  </span>
                  <span class="flex-1 text-gray-800">{{ fav.exercise_name }}</span>
                  <span class="text-sm text-gray-500">{{ fav.count }} 次</span>
                </div>
              </div>
            </div>

            <!-- 周统计 -->
            <div v-if="rehabilitationStore.stats.weekly_summary?.length" class="p-4 bg-white rounded-xl border border-warmGray-100">
              <h4 class="font-medium text-gray-800 mb-4">近期周统计</h4>
              <div class="space-y-4">
                <div
                  v-for="week in rehabilitationStore.stats.weekly_summary.slice(0, 4)"
                  :key="week.week_start"
                  class="flex items-center gap-4"
                >
                  <span class="text-sm text-gray-500 w-24">{{ week.week_start.slice(5) }}</span>
                  <div class="flex-1 flex items-center gap-2">
                    <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        class="h-full bg-primary-500 rounded-full"
                        :style="{ width: `${(week.days_trained / 7) * 100}%` }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-600 w-16">{{ week.days_trained }}/7 天</span>
                  </div>
                  <span class="text-sm text-gray-500 w-20">{{ week.total_minutes }} 分钟</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 运动详情弹窗 -->
    <Teleport to="body">
      <div
        v-if="showExerciseModal && selectedExercise"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showExerciseModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <div class="relative">
            <!-- 视频/图片区域 -->
            <div class="aspect-video bg-warmGray-100 flex items-center justify-center">
              <img
                v-if="selectedExercise.thumbnail_url"
                :src="selectedExercise.thumbnail_url"
                :alt="selectedExercise.name"
                class="w-full h-full object-cover"
              />
              <div v-else class="text-center">
                <svg class="w-16 h-16 text-warmGray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p class="text-warmGray-400">视频加载中...</p>
              </div>
            </div>
            <!-- 关闭按钮 -->
            <button
              class="absolute top-4 right-4 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70"
              @click="showExerciseModal = false"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- 标题和标签 -->
            <div>
              <div class="flex items-start justify-between mb-2">
                <h3 class="text-xl font-bold text-gray-800">{{ selectedExercise.name }}</h3>
                <div class="flex items-center gap-2">
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', getDifficultyColor(selectedExercise.difficulty)]">
                    {{ DIFFICULTY_LABELS[selectedExercise.difficulty] }}
                  </span>
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', getCategoryColor(selectedExercise.category)]">
                    {{ EXERCISE_CATEGORY_LABELS[selectedExercise.category] }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {{ selectedExercise.duration_minutes }} 分钟
                </span>
                <span>{{ selectedExercise.recommended_frequency }}</span>
              </div>
            </div>

            <!-- 描述 -->
            <div>
              <p class="text-gray-600">{{ selectedExercise.description }}</p>
            </div>

            <!-- 益处 -->
            <div v-if="selectedExercise.benefits?.length">
              <h4 class="font-medium text-gray-800 mb-2">训练益处</h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="benefit in selectedExercise.benefits"
                  :key="benefit"
                  class="px-3 py-1 bg-mint-50 text-mint-700 rounded-full text-sm"
                >
                  {{ benefit }}
                </span>
              </div>
            </div>

            <!-- 步骤说明 -->
            <div v-if="selectedExercise.instructions?.length">
              <h4 class="font-medium text-gray-800 mb-3">动作步骤</h4>
              <ol class="space-y-2">
                <li
                  v-for="(step, idx) in selectedExercise.instructions"
                  :key="idx"
                  class="flex items-start gap-3"
                >
                  <span class="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                    {{ idx + 1 }}
                  </span>
                  <span class="text-gray-600">{{ step }}</span>
                </li>
              </ol>
            </div>

            <!-- 注意事项 -->
            <div v-if="selectedExercise.precautions?.length">
              <h4 class="font-medium text-gray-800 mb-2">注意事项</h4>
              <ul class="space-y-1">
                <li
                  v-for="(precaution, idx) in selectedExercise.precautions"
                  :key="idx"
                  class="flex items-start gap-2 text-sm text-yellow-700"
                >
                  <svg class="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  {{ precaution }}
                </li>
              </ul>
            </div>

            <!-- 所需器材 -->
            <div v-if="selectedExercise.equipment_needed?.length">
              <h4 class="font-medium text-gray-800 mb-2">所需器材</h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="equipment in selectedExercise.equipment_needed"
                  :key="equipment"
                  class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                >
                  {{ equipment }}
                </span>
              </div>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200">
            <button class="btn btn-primary w-full" @click="showExerciseModal = false">
              Close
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 训练计划弹窗 -->
    <Teleport to="body">
      <div
        v-if="showPlanModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showPlanModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">
              {{ editingPlan ? 'Edit Training Plan' : 'Create Training Plan' }}
            </h3>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Basic Information -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">Plan Name *</label>
                <input v-model="planForm.name" type="text" class="input" placeholder="e.g., Daily Rehabilitation" required />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">Plan Description</label>
                <textarea v-model="planForm.description" rows="2" class="input" placeholder="Describe the goal of this plan..."></textarea>
              </div>
            </div>

            <!-- Training Schedule -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700">Training Schedule</h4>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-2">Training Days</label>
                <div class="flex gap-2">
                  <button
                    v-for="day in weekDays"
                    :key="day.value"
                    type="button"
                    @click="toggleWeekDay(day.value)"
                    :class="[
                      'w-10 h-10 rounded-full text-sm font-medium transition-all',
                      planForm.schedule.days_of_week.includes(day.value)
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                    ]"
                  >
                    {{ day.label }}
                  </button>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-600 mb-1">训练时间</label>
                <input v-model="planForm.schedule.time_of_day" type="time" class="input w-32" />
              </div>
            </div>

            <!-- 运动选择 -->
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="font-medium text-gray-700">选择运动</h4>
                <span class="text-sm text-gray-500">已选 {{ planForm.exercises.length }} 个</span>
              </div>

              <!-- 已选运动 -->
              <div v-if="planForm.exercises.length > 0" class="space-y-2">
                <div
                  v-for="(item, idx) in planForm.exercises"
                  :key="item.exercise_id"
                  class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <span class="w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium">
                    {{ idx + 1 }}
                  </span>
                  <span class="flex-1 font-medium text-gray-800">{{ item.exercise?.name }}</span>
                  <input
                    v-model.number="item.sets"
                    type="number"
                    min="1"
                    class="w-16 px-2 py-1 border border-warmGray-200 rounded text-sm text-center"
                    placeholder="组数"
                  />
                  <span class="text-sm text-gray-500">组</span>
                  <button
                    type="button"
                    class="p-1 text-red-500 hover:bg-red-50 rounded"
                    @click="removeExerciseFromPlan(idx)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 可选运动列表 -->
              <div class="max-h-48 overflow-y-auto border border-warmGray-200 rounded-lg">
                <div
                  v-for="exercise in rehabilitationStore.exercises"
                  :key="exercise.id"
                  class="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer border-b border-warmGray-100 last:border-b-0"
                  @click="addExerciseToPlan(exercise)"
                >
                  <div
                    :class="[
                      'w-5 h-5 rounded border flex items-center justify-center',
                      planForm.exercises.find((e) => e.exercise_id === exercise.id)
                        ? 'bg-primary-500 border-primary-500 text-white'
                        : 'border-warmGray-300',
                    ]"
                  >
                    <svg
                      v-if="planForm.exercises.find((e) => e.exercise_id === exercise.id)"
                      class="w-3 h-3"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-gray-800">{{ exercise.name }}</p>
                    <p class="text-xs text-gray-500">
                      {{ EXERCISE_CATEGORY_LABELS[exercise.category] }} · {{ exercise.duration_minutes }}分钟
                    </p>
                  </div>
                  <span :class="['px-2 py-0.5 text-xs rounded-full', getDifficultyColor(exercise.difficulty)]">
                    {{ DIFFICULTY_LABELS[exercise.difficulty] }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 设为活跃 -->
            <div class="flex items-center gap-3">
              <input
                v-model="planForm.is_active"
                type="checkbox"
                id="is_active"
                class="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <label for="is_active" class="text-sm text-gray-700">设为当前活跃计划</label>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showPlanModal = false">取消</button>
            <button
              class="btn btn-primary"
              @click="savePlan"
              :disabled="rehabilitationStore.loading || !planForm.name || planForm.exercises.length === 0"
            >
              {{ rehabilitationStore.loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 打卡弹窗 -->
    <Teleport to="body">
      <div
        v-if="showCheckInModal"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        @click.self="showCheckInModal = false"
      >
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col">
          <div class="p-6 border-b border-warmGray-200">
            <h3 class="text-xl font-semibold text-gray-800">今日训练打卡</h3>
          </div>

          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- 运动完成情况 -->
            <div class="space-y-3">
              <h4 class="font-medium text-gray-700">完成情况</h4>
              <div
                v-for="(item, idx) in checkInForm.exercises_completed"
                :key="idx"
                :class="[
                  'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors',
                  item.completed ? 'bg-mint-50' : 'bg-gray-50',
                ]"
                @click="toggleExerciseComplete(idx)"
              >
                <div
                  :class="[
                    'w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors',
                    item.completed ? 'bg-mint-500 border-mint-500 text-white' : 'border-gray-300',
                  ]"
                >
                  <svg v-if="item.completed" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span :class="['flex-1', item.completed ? 'text-mint-700' : 'text-gray-600']">
                  {{ item.exercise_name }}
                </span>
              </div>
            </div>

            <!-- 训练前后对比 -->
            <div class="space-y-4">
              <h4 class="font-medium text-gray-700">训练前后对比</h4>

              <div class="grid gap-4 md:grid-cols-2">
                <div>
                  <label class="block text-sm text-gray-600 mb-2">训练前心情</label>
                  <div class="flex items-center gap-2">
                    <input v-model.number="checkInForm.mood_before" type="range" min="1" max="5" class="flex-1" />
                    <span class="text-sm text-gray-500 w-12">{{ getRatingLabel(checkInForm.mood_before, 'mood') }}</span>
                  </div>
                </div>
                <div>
                  <label class="block text-sm text-gray-600 mb-2">训练后心情</label>
                  <div class="flex items-center gap-2">
                    <input v-model.number="checkInForm.mood_after" type="range" min="1" max="5" class="flex-1" />
                    <span class="text-sm text-gray-500 w-12">{{ getRatingLabel(checkInForm.mood_after, 'mood') }}</span>
                  </div>
                </div>
                <div>
                  <label class="block text-sm text-gray-600 mb-2">训练前震颤</label>
                  <div class="flex items-center gap-2">
                    <input v-model.number="checkInForm.tremor_before" type="range" min="1" max="5" class="flex-1" />
                    <span class="text-sm text-gray-500 w-12">{{ getRatingLabel(checkInForm.tremor_before, 'tremor') }}</span>
                  </div>
                </div>
                <div>
                  <label class="block text-sm text-gray-600 mb-2">训练后震颤</label>
                  <div class="flex items-center gap-2">
                    <input v-model.number="checkInForm.tremor_after" type="range" min="1" max="5" class="flex-1" />
                    <span class="text-sm text-gray-500 w-12">{{ getRatingLabel(checkInForm.tremor_after, 'tremor') }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 整体评价 -->
            <div>
              <label class="block text-sm text-gray-600 mb-2">整体感受</label>
              <div class="flex items-center gap-2">
                <input v-model.number="checkInForm.overall_rating" type="range" min="1" max="5" class="flex-1" />
                <span class="text-sm text-gray-500 w-20">{{ getRatingLabel(checkInForm.overall_rating, 'overall') }}</span>
              </div>
            </div>

            <!-- 备注 -->
            <div>
              <label class="block text-sm text-gray-600 mb-1">备注</label>
              <textarea v-model="checkInForm.notes" rows="2" class="input" placeholder="记录今天的训练感受..."></textarea>
            </div>
          </div>

          <div class="p-6 border-t border-warmGray-200 flex justify-end gap-3">
            <button class="btn btn-secondary" @click="showCheckInModal = false">取消</button>
            <button
              class="btn btn-primary"
              @click="submitCheckIn"
              :disabled="rehabilitationStore.loading"
            >
              {{ rehabilitationStore.loading ? '提交中...' : '完成打卡' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>
