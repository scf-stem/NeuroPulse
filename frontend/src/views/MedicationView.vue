<script setup lang="ts">
/**
 * Tremor Guard - Medication View
 * 震颤卫士 - 用药管理页面
 */

import { ref, computed, onMounted, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import AppLayout from '@/layouts/AppLayout.vue'
import { useMedicationStore } from '@/stores/medication'
import { medicationApi } from '@/api/medication'
import { getMedicationFrequencyLabel, type Medication, type MedicationCreateRequest, type MedicationEffectiveness } from '@/types'
import { currentLocale, formatDateTime, legacyT, localeText } from '@/i18n'
import { translateLegacyText } from '@/i18n/legacy'

// 注册 Chart.js 组件
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const medicationStore = useMedicationStore()
const lt = (en: string, zh: string) => localeText(en, zh)

// Tab 状态
const activeTab = ref<'medications' | 'records' | 'analysis' | 'reminders'>('medications')

// 模态框状态
const showMedicationForm = ref(false)
const editingMedication = ref<Medication | null>(null)
const showDosageModal = ref(false)
const selectedMedication = ref<Medication | null>(null)
const selectedScheduledTime = ref<string>('')

// 表单数据
const medicationForm = ref<MedicationCreateRequest>({
  name: '',
  generic_name: '',
  dosage: '',
  frequency: 'once_daily',
  times_per_day: 1,
  scheduled_times: ['08:00'],
  start_date: new Date().toISOString().split('T')[0],
  purpose: '',
  notes: '',
})

// 服药记录表单
const dosageForm = ref({
  notes: '',
  side_effects: '',
})

// 药效分析状态
const analysisLoading = ref(false)
const analysisDateRange = ref<'7d' | '14d' | '30d'>('7d')
const selectedAnalysisMedication = ref<number | null>(null)
const effectivenessData = ref<MedicationEffectiveness[]>([])
const correlationData = ref<{
  correlation_score: number
  peak_effect_hours: number
  duration_hours: number
  optimal_timing: string[]
  insights: string[]
} | null>(null)

// 初始化
onMounted(async () => {
  await medicationStore.initialize()
})

// Tab 配置
const tabs = [
  { key: 'medications', name: lt('My medications', '我的药物'), icon: 'pill' },
  { key: 'records', name: lt('Dose records', '服药记录'), icon: 'list' },
  { key: 'analysis', name: lt('Effectiveness analysis', '药效分析'), icon: 'chart' },
  { key: 'reminders', name: lt('Reminder settings', '提醒设置'), icon: 'bell' },
]

// 频率选项
const frequencyOptions = [
  { value: 'once_daily', label: lt('Once daily', '每日一次'), times: 1 },
  { value: 'twice_daily', label: lt('Twice daily', '每日两次'), times: 2 },
  { value: 'three_times_daily', label: lt('Three times daily', '每日三次'), times: 3 },
  { value: 'four_times_daily', label: lt('Four times daily', '每日四次'), times: 4 },
  { value: 'as_needed', label: lt('As needed', '按需服用'), times: 0 },
]

// 监听频率变化，自动调整时间
watch(() => medicationForm.value.frequency, (newFreq) => {
  const option = frequencyOptions.find(o => o.value === newFreq)
  if (option) {
    medicationForm.value.times_per_day = option.times
    // 设置默认时间
    if (option.times === 1) {
      medicationForm.value.scheduled_times = ['08:00']
    } else if (option.times === 2) {
      medicationForm.value.scheduled_times = ['08:00', '20:00']
    } else if (option.times === 3) {
      medicationForm.value.scheduled_times = ['08:00', '14:00', '20:00']
    } else if (option.times === 4) {
      medicationForm.value.scheduled_times = ['08:00', '12:00', '18:00', '22:00']
    } else {
      medicationForm.value.scheduled_times = []
    }
  }
})

// 打开添加药物表单
function openAddForm() {
  editingMedication.value = null
  medicationForm.value = {
    name: '',
    generic_name: '',
    dosage: '',
    frequency: 'once_daily',
    times_per_day: 1,
    scheduled_times: ['08:00'],
    start_date: new Date().toISOString().split('T')[0],
    purpose: '',
    notes: '',
  }
  showMedicationForm.value = true
}

// 打开编辑药物表单
function openEditForm(medication: Medication) {
  editingMedication.value = medication
  medicationForm.value = {
    name: medication.name,
    generic_name: medication.generic_name || '',
    dosage: medication.dosage,
    frequency: medication.frequency,
    times_per_day: medication.times_per_day,
    scheduled_times: [...medication.scheduled_times],
    start_date: medication.start_date,
    end_date: medication.end_date,
    purpose: medication.purpose || '',
    notes: medication.notes || '',
  }
  showMedicationForm.value = true
}

// 提交药物表单
async function submitMedicationForm() {
  try {
    if (editingMedication.value) {
      await medicationStore.updateMedication(editingMedication.value.id, medicationForm.value)
    } else {
      await medicationStore.addMedication(medicationForm.value)
    }
    showMedicationForm.value = false
  } catch (error) {
    console.error('保存药物失败:', error)
  }
}

// 删除药物
async function deleteMedication(medication: Medication) {
  if (confirm(localeText(`Delete medication "${medication.name}"?`, `确定要删除药物「${medication.name}」吗？`))) {
    try {
      await medicationStore.deleteMedication(medication.id)
    } catch (error) {
      console.error('删除药物失败:', error)
    }
  }
}

// 切换药物状态
async function toggleMedicationStatus(medication: Medication) {
  try {
    await medicationStore.updateMedication(medication.id, {
      is_active: !medication.is_active,
    } as any)
  } catch (error) {
    console.error('更新药物状态失败:', error)
  }
}

// 快速服药
async function quickTakeMedication(schedule: any) {
  selectedMedication.value = schedule.medication
  selectedScheduledTime.value = schedule.scheduled_time
  showDosageModal.value = true
}

// 确认服药
async function confirmTakeMedication() {
  if (!selectedMedication.value) return
  try {
    await medicationStore.recordDosage({
      medication_id: selectedMedication.value.id,
      dosage_taken: selectedMedication.value.dosage,
      scheduled_time: selectedScheduledTime.value,
      status: 'taken',
      notes: dosageForm.value.notes,
      side_effects: dosageForm.value.side_effects
    })
    showDosageModal.value = false
    dosageForm.value = { notes: '', side_effects: '' }
    selectedMedication.value = null
  } catch (error) {
    console.error('记录服药失败:', error)
  }
}

// 获取时间段描述
function getTimeSlot(time: string): string {
  const hour = parseInt(time.split(':')[0])
  if (hour >= 5 && hour < 9) return legacyT('早晨')
  if (hour >= 9 && hour < 12) return legacyT('上午')
  if (hour >= 12 && hour < 14) return legacyT('中午')
  if (hour >= 14 && hour < 18) return legacyT('下午')
  if (hour >= 18 && hour < 21) return legacyT('晚间')
  return legacyT('夜间')
}



// 格式化时间
function formatTime(dateStr: string): string {
  return formatDateTime(dateStr, { hour: '2-digit', minute: '2-digit' })
}

// 获取状态颜色
function getStatusColor(status: string): string {
  switch (status) {
    case 'taken': return 'bg-mint-100 text-mint-700'
    case 'missed': return 'bg-red-100 text-red-700'
    case 'skipped': return 'bg-gray-100 text-gray-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

// 获取状态文本
function getStatusText(status: string): string {
  switch (status) {
    case 'taken': return legacyT('已服用')
    case 'missed': return legacyT('已错过')
    case 'skipped': return legacyT('已跳过')
    default: return status
  }
}

// ============================================================
// 药效分析功能
// ============================================================

// 计算日期范围
function getDateRange(range: '7d' | '14d' | '30d') {
  const endDate = new Date()
  const startDate = new Date()
  switch (range) {
    case '7d':
      startDate.setDate(startDate.getDate() - 7)
      break
    case '14d':
      startDate.setDate(startDate.getDate() - 14)
      break
    case '30d':
      startDate.setDate(startDate.getDate() - 30)
      break
  }
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}

// 加载药效分析数据
async function loadEffectivenessData() {
  analysisLoading.value = true
  try {
    const { startDate, endDate } = getDateRange(analysisDateRange.value)
    effectivenessData.value = await medicationApi.getEffectivenessAnalysis({
      medicationId: selectedAnalysisMedication.value || undefined,
      startDate,
      endDate,
    })

    // 如果选择了特定药物，也加载相关性数据
    if (selectedAnalysisMedication.value) {
      const days = analysisDateRange.value === '7d' ? 7 : analysisDateRange.value === '14d' ? 14 : 30
      correlationData.value = await medicationApi.getMedicationTremorCorrelation(
        selectedAnalysisMedication.value,
        days
      )
    } else {
      correlationData.value = null
    }
  } catch (error) {
    console.error('加载药效分析失败:', error)
  } finally {
    analysisLoading.value = false
  }
}

// 监听分析参数变化
watch([analysisDateRange, selectedAnalysisMedication], () => {
  if (activeTab.value === 'analysis') {
    loadEffectivenessData()
  }
})

// Tab 切换时加载数据
watch(activeTab, (newTab) => {
  if (newTab === 'analysis' && effectivenessData.value.length === 0) {
    loadEffectivenessData()
  }
})

// 图表配置 - 震颤趋势图
const tremorChartData = computed(() => {
  if (effectivenessData.value.length === 0) {
    return { labels: [], datasets: [] }
  }

  // 合并所有日期的震颤数据
  const allData: { time: string; severity: number; date: string }[] = []
  effectivenessData.value.forEach((day) => {
    day.tremor_data.forEach((point) => {
      allData.push({
        time: point.time,
        severity: point.severity,
        date: day.date,
      })
    })
  })

  // 按小时聚合平均震颤
  const hourlyAvg: Record<number, { total: number; count: number }> = {}
  allData.forEach((point) => {
    const hour = parseInt(point.time.split(':')[0])
    if (!hourlyAvg[hour]) {
      hourlyAvg[hour] = { total: 0, count: 0 }
    }
    hourlyAvg[hour].total += point.severity
    hourlyAvg[hour].count += 1
  })

  const labels: string[] = []
  const severityData: number[] = []
  for (let h = 6; h <= 22; h++) {
    labels.push(`${h}:00`)
    if (hourlyAvg[h]) {
      severityData.push(+(hourlyAvg[h].total / hourlyAvg[h].count).toFixed(2))
    } else {
      severityData.push(0)
    }
  }

  // 获取服药时间标记
  const dosageTimes = new Set<string>()
  effectivenessData.value.forEach((day) => {
    day.dosage_times.forEach((t) => dosageTimes.add(t.split(':')[0] + ':00'))
  })

  return {
    labels,
    datasets: [
      {
        label: translateLegacyText('平均震颤严重度', currentLocale.value),
        data: severityData,
        borderColor: '#F97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: labels.map((l) =>
          dosageTimes.has(l) ? '#10B981' : '#F97316'
        ),
        pointBorderColor: labels.map((l) =>
          dosageTimes.has(l) ? '#10B981' : '#F97316'
        ),
        pointBorderWidth: labels.map((l) => (dosageTimes.has(l) ? 3 : 1)),
      },
    ],
  }
})

const tremorChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: (context: any) => translateLegacyText(`震颤严重度: ${context.raw}`, currentLocale.value),
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 4,
      title: {
        display: true,
        text: translateLegacyText('震颤严重度 (0-4)', currentLocale.value),
        color: '#6B7280',
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
    },
    x: {
      title: {
        display: true,
        text: translateLegacyText('时间', currentLocale.value),
        color: '#6B7280',
      },
      grid: {
        display: false,
      },
    },
  },
}

// 图表配置 - 药效对比图
const effectivenessChartData = computed(() => {
  if (effectivenessData.value.length === 0) {
    return { labels: [], datasets: [] }
  }

  const labels = effectivenessData.value.map((d) => {
    const date = new Date(d.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })

  return {
    labels,
    datasets: [
      {
        label: translateLegacyText('服药前平均震颤', currentLocale.value),
        data: effectivenessData.value.map((d) => d.avg_severity_before),
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
      {
        label: translateLegacyText('服药后平均震颤', currentLocale.value),
        data: effectivenessData.value.map((d) => d.avg_severity_after),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
      },
    ],
  }
})

const effectivenessChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        usePointStyle: true,
        padding: 20,
      },
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 4,
      title: {
        display: true,
        text: translateLegacyText('震颤严重度', currentLocale.value),
        color: '#6B7280',
      },
      grid: {
        color: 'rgba(0, 0, 0, 0.05)',
      },
    },
    x: {
      title: {
        display: true,
        text: translateLegacyText('日期', currentLocale.value),
        color: '#6B7280',
      },
      grid: {
        display: false,
      },
    },
  },
}

// 计算平均药效评分
const avgEffectivenessScore = computed(() => {
  if (effectivenessData.value.length === 0) return 0
  const sum = effectivenessData.value.reduce((acc, d) => acc + d.effectiveness_score, 0)
  return Math.round(sum / effectivenessData.value.length)
})

// 计算震颤改善率
const tremorImprovementRate = computed(() => {
  if (effectivenessData.value.length === 0) return 0
  let improved = 0
  effectivenessData.value.forEach((d) => {
    if (d.avg_severity_after < d.avg_severity_before) {
      improved++
    }
  })
  return Math.round((improved / effectivenessData.value.length) * 100)
})

// 获取相关性强度描述
function getCorrelationStrength(score: number): { text: string; color: string } {
  if (score >= 0.7) return { text: legacyT('强相关'), color: 'text-mint-600' }
  if (score >= 0.4) return { text: legacyT('中等相关'), color: 'text-primary-600' }
  if (score >= 0.2) return { text: legacyT('弱相关'), color: 'text-amber-600' }
  return { text: legacyT('无明显相关'), color: 'text-gray-500' }
}
</script>

<template>
  <AppLayout>
    <div class="max-w-7xl mx-auto space-y-6">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl shadow-soft flex items-center justify-center">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-gray-800">{{ lt('Medication', '用药管理') }}</h1>
            <p class="text-gray-500">{{ lt('Track medication use and analyze its relationship to tremor severity', '记录用药情况，分析药效与震颤的关系') }}</p>
          </div>
        </div>
        <!-- 快捷操作 -->
        <div class="flex items-center gap-3">
          <button @click="openAddForm" class="btn btn-primary">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            {{ lt('Add medication', '添加药物') }}
          </button>
        </div>
      </div>

      <!-- 今日服药提醒卡片 -->
      <div v-if="medicationStore.todaySchedule.length > 0" class="card-gradient p-6">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-800">{{ lt("Today's medication plan", '今日服药计划') }}</h3>
              <p class="text-sm text-gray-500">
                {{ lt('Completed', '已完成') }} {{ medicationStore.takenDosages.length }} / {{ medicationStore.todaySchedule.length }} {{ lt('times', '次') }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-300"
                :style="{ width: `${medicationStore.todayCompletionRate}%` }"
              ></div>
            </div>
            <span class="text-lg font-bold text-primary-600">
              {{ medicationStore.todayCompletionRate }}%
            </span>
          </div>
        </div>

        <!-- 待服药列表 -->
        <div v-if="medicationStore.pendingDosages.length > 0" class="space-y-3">
          <div
            v-for="schedule in medicationStore.pendingDosages"
            :key="`${schedule.medication.id}-${schedule.scheduled_time}`"
            class="flex items-center justify-between p-4 bg-white rounded-xl border border-warmGray-100"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                <span class="text-primary-600 font-semibold">{{ schedule.scheduled_time }}</span>
              </div>
              <div>
                <h4 class="font-medium text-gray-800">{{ schedule.medication.name }}</h4>
              <p class="text-sm text-gray-500">{{ schedule.medication.dosage }} · {{ getTimeSlot(schedule.scheduled_time) }}</p>
              </div>
            </div>
            <button
              @click="quickTakeMedication(schedule)"
              class="btn bg-gradient-to-r from-mint-500 to-mint-600 hover:from-mint-600 hover:to-mint-700 text-white"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ lt('Take now', '服药') }}
            </button>
          </div>
        </div>

        <!-- 全部已完成 -->
        <div v-else class="text-center py-4">
          <div class="inline-flex items-center gap-2 px-4 py-2 bg-mint-100 text-mint-700 rounded-full">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ lt('All scheduled doses are completed today', '今日服药计划已全部完成') }}
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
                : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'
            ]"
          >
            <!-- Tab 图标 -->
            <svg v-if="tab.icon === 'pill'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            <svg v-else-if="tab.icon === 'list'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <svg v-else-if="tab.icon === 'chart'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <svg v-else-if="tab.icon === 'bell'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- Tab 内容 -->
      <div class="card-gradient p-6">
        <!-- 加载状态 -->
        <div v-if="medicationStore.loading" class="flex items-center justify-center py-12">
          <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
        </div>

        <!-- 我的药物 Tab -->
        <div v-else-if="activeTab === 'medications'">
          <div v-if="medicationStore.medications.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ lt('No medications yet', '暂无药物记录') }}</h3>
            <p class="text-gray-500 mb-4">{{ lt('Add current medications to begin tracking effectiveness', '添加您正在服用的药物，以便追踪药效') }}</p>
            <button @click="openAddForm" class="btn btn-primary">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ lt('Add your first medication', '添加第一个药物') }}
            </button>
          </div>

          <!-- 药物列表 -->
          <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="medication in medicationStore.medications"
              :key="medication.id"
              class="p-4 bg-white rounded-xl border border-warmGray-100 hover:shadow-soft transition-shadow"
            >
              <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                  <h4 class="font-semibold text-gray-800">{{ medication.name }}</h4>
                  <p v-if="medication.generic_name" class="text-sm text-gray-500">{{ medication.generic_name }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      medication.is_active
                        ? 'bg-mint-100 text-mint-700'
                        : 'bg-gray-100 text-gray-500'
                    ]"
                  >
                    {{ medication.is_active ? legacyT('使用中') : legacyT('已停用') }}
                  </span>
                  <!-- 操作菜单 -->
                  <div class="relative group">
                    <button class="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </button>
                    <div class="absolute right-0 top-full mt-1 w-32 bg-white rounded-lg shadow-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                      <button
                        @click="openEditForm(medication)"
                        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                      >
                        {{ legacyT('编辑') }}
                      </button>
                      <button
                        @click="toggleMedicationStatus(medication)"
                        class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                      >
                        {{ medication.is_active ? legacyT('停用') : legacyT('启用') }}
                      </button>
                      <button
                        @click="deleteMedication(medication)"
                        class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 last:rounded-b-lg"
                      >
                        {{ legacyT('删除') }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-500">{{ legacyT('剂量') }}</span>
                  <span class="text-gray-800">{{ medication.dosage }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">{{ legacyT('频率') }}</span>
                  <span class="text-gray-800">{{ getMedicationFrequencyLabel(medication.frequency) }}</span>
                </div>
                <div v-if="medication.scheduled_times && medication.scheduled_times.length > 0" class="flex justify-between">
                  <span class="text-gray-500">{{ legacyT('服药时间') }}</span>
                  <span class="text-gray-800">{{ medication.scheduled_times.join(', ') }}</span>
                </div>
                <div v-if="medication.purpose" class="flex justify-between">
                  <span class="text-gray-500">{{ legacyT('用途') }}</span>
                  <span class="text-gray-800">{{ medication.purpose }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 服药记录 Tab -->
        <div v-else-if="activeTab === 'records'">
          <div v-if="medicationStore.todayRecords.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('暂无服药记录') }}</h3>
            <p class="text-gray-500">{{ legacyT('服药后记录将显示在这里') }}</p>
          </div>

          <!-- 服药记录列表 -->
          <div v-else class="space-y-4">
            <div
              v-for="record in medicationStore.todayRecords"
              :key="record.id"
              class="flex items-center justify-between p-4 bg-white rounded-xl border border-warmGray-100"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-medium text-gray-800">{{ legacyT('药物') }} #{{ record.medication_id }}</h4>
                  <p class="text-sm text-gray-500">{{ record.dosage_taken }} · {{ formatTime(record.taken_at) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span v-if="record.notes" class="text-sm text-gray-500">{{ record.notes }}</span>
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', getStatusColor(record.status)]">
                  {{ getStatusText(record.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 药效分析 Tab -->
        <div v-else-if="activeTab === 'analysis'">
          <!-- 筛选器 -->
          <div class="flex flex-wrap items-center gap-4 mb-6">
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-600">{{ legacyT('时间范围：') }}</label>
              <div class="flex bg-gray-100 rounded-lg p-1">
                <button
                  v-for="range in [{ value: '7d', label: legacyT('7天') }, { value: '14d', label: legacyT('14天') }, { value: '30d', label: legacyT('30天') }]"
                  :key="range.value"
                  @click="analysisDateRange = range.value as any"
                  :class="[
                    'px-3 py-1.5 text-sm font-medium rounded-md transition-all',
                    analysisDateRange === range.value
                      ? 'bg-white text-primary-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  ]"
                >
                  {{ range.label }}
                </button>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <label class="text-sm text-gray-600">{{ legacyT('药物：') }}</label>
              <select v-model="selectedAnalysisMedication" class="input py-1.5 w-40">
                <option :value="null">{{ legacyT('全部药物') }}</option>
                <option v-for="med in medicationStore.activeMedications" :key="med.id" :value="med.id">
                  {{ med.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="analysisLoading" class="flex items-center justify-center py-12">
            <div class="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          </div>

          <!-- 无数据状态 -->
          <div v-else-if="effectivenessData.length === 0" class="text-center py-12">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-800 mb-2">{{ legacyT('暂无药效数据') }}</h3>
            <p class="text-gray-500 mb-4">{{ legacyT('持续记录服药和震颤数据后，系统将分析药效规律') }}</p>
            <p class="text-sm text-gray-400">{{ legacyT('需要至少7天的服药记录才能生成分析报告') }}</p>
          </div>

          <!-- 有数据展示 -->
          <div v-else class="space-y-6">
            <!-- 统计卡片 -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">{{ legacyT('分析天数') }}</p>
                    <p class="text-xl font-bold text-gray-800">{{ effectivenessData.length }}</p>
                  </div>
                </div>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-mint-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">{{ legacyT('药效评分') }}</p>
                    <p class="text-xl font-bold text-mint-600">{{ avgEffectivenessScore }}%</p>
                  </div>
                </div>
              </div>
              <div class="p-4 bg-white rounded-xl border border-warmGray-100">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-lavender-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">{{ legacyT('改善率') }}</p>
                    <p class="text-xl font-bold text-lavender-600">{{ tremorImprovementRate }}%</p>
                  </div>
                </div>
              </div>
              <div v-if="correlationData" class="p-4 bg-white rounded-xl border border-warmGray-100">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">{{ legacyT('峰值效果') }}</p>
                    <p class="text-xl font-bold text-amber-600">{{ correlationData.peak_effect_hours }}h</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 震颤趋势图 -->
            <div class="p-6 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="font-semibold text-gray-800">{{ legacyT('每日震颤趋势') }}</h3>
                  <p class="text-sm text-gray-500">{{ legacyT('绿色圆点标记服药时间') }}</p>
                </div>
              </div>
              <div class="h-64">
                <Line :data="tremorChartData" :options="tremorChartOptions" />
              </div>
            </div>

            <!-- 药效对比图 -->
            <div class="p-6 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="font-semibold text-gray-800">{{ legacyT('服药前后对比') }}</h3>
                  <p class="text-sm text-gray-500">{{ legacyT('对比服药前1小时与服药后2小时的平均震颤') }}</p>
                </div>
              </div>
              <div class="h-64">
                <Line :data="effectivenessChartData" :options="effectivenessChartOptions" />
              </div>
            </div>

            <!-- 相关性分析 -->
            <div v-if="correlationData" class="p-6 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-gray-800">{{ legacyT('药物关联分析') }}</h3>
                  <p class="text-sm text-gray-500">
                    {{ legacyT('相关性：') }}
                    <span :class="getCorrelationStrength(correlationData.correlation_score).color">
                      {{ getCorrelationStrength(correlationData.correlation_score).text }}
                    </span>
                    ({{ (correlationData.correlation_score * 100).toFixed(0) }}%)
                  </p>
                </div>
              </div>

              <div class="grid md:grid-cols-3 gap-4 mb-4">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-500 mb-1">{{ legacyT('峰值效果时间') }}</p>
                  <p class="text-lg font-semibold text-gray-800">{{ legacyT('服药后') }} {{ correlationData.peak_effect_hours }} {{ legacyT('小时') }}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-500 mb-1">{{ legacyT('有效持续时间') }}</p>
                  <p class="text-lg font-semibold text-gray-800">{{ legacyT('约') }} {{ correlationData.duration_hours }} {{ legacyT('小时') }}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-500 mb-1">{{ legacyT('建议服药时间') }}</p>
                  <p class="text-lg font-semibold text-gray-800">{{ correlationData.optimal_timing.join('、') || legacyT('暂无建议') }}</p>
                </div>
              </div>

              <!-- AI 洞察 -->
              <div v-if="correlationData.insights.length > 0" class="space-y-2">
                <p class="text-sm font-medium text-gray-700">{{ legacyT('分析洞察：') }}</p>
                <ul class="space-y-2">
                  <li
                    v-for="(insight, index) in correlationData.insights"
                    :key="index"
                    class="flex items-start gap-2 text-sm text-gray-600"
                  >
                    <svg class="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ insight }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 提醒设置 Tab -->
        <div v-else-if="activeTab === 'reminders'">
          <div class="space-y-6">
            <div class="flex items-center justify-between p-4 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-medium text-gray-800">{{ legacyT('服药提醒') }}</h4>
                  <p class="text-sm text-gray-500">{{ legacyT('在设定的服药时间推送提醒') }}</p>
                </div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-medium text-gray-800">{{ legacyT('提前提醒') }}</h4>
                  <p class="text-sm text-gray-500">{{ legacyT('提前15分钟发送提醒') }}</p>
                </div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
              </label>
            </div>

            <div class="flex items-center justify-between p-4 bg-white rounded-xl border border-warmGray-100">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-medium text-gray-800">{{ legacyT('漏服提醒') }}</h4>
                  <p class="text-sm text-gray-500">{{ legacyT('超过服药时间30分钟后再次提醒') }}</p>
                </div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑药物模态框 -->
    <Teleport to="body">
      <div v-if="showMedicationForm" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showMedicationForm = false"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
          <div class="p-6 border-b border-gray-100">
            <h3 class="text-xl font-bold text-gray-800">
              {{ editingMedication ? lt('Edit medication', '编辑药物') : lt('Add medication', '添加药物') }}
            </h3>
          </div>
          <form @submit.prevent="submitMedicationForm" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Medication name *', '药物名称 *') }}</label>
              <input
                v-model="medicationForm.name"
                type="text"
                required
                class="input"
                :placeholder="lt('e.g. Madopar', '如：美多芭')"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Generic name', '通用名') }}</label>
              <input
                v-model="medicationForm.generic_name"
                type="text"
                class="input"
                :placeholder="lt('e.g. Levodopa', '如：左旋多巴')"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Dose *', '剂量 *') }}</label>
              <input
                v-model="medicationForm.dosage"
                type="text"
                required
                class="input"
                :placeholder="lt('e.g. 250mg', '如：250mg')"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Frequency *', '服药频率 *') }}</label>
              <select v-model="medicationForm.frequency" class="input">
                <option v-for="opt in frequencyOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div v-if="medicationForm.scheduled_times.length > 0">
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Time', '服药时间') }}</label>
              <div class="flex flex-wrap gap-2">
                <input
                  v-for="(_time, index) in medicationForm.scheduled_times"
                  :key="index"
                  v-model="medicationForm.scheduled_times[index]"
                  type="time"
                  class="input w-auto"
                >
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Start date', '开始日期') }}</label>
              <input
                v-model="medicationForm.start_date"
                type="date"
                class="input"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Purpose', '用途') }}</label>
              <input
                v-model="medicationForm.purpose"
                type="text"
                class="input"
                :placeholder="lt('e.g. tremor control', '如：控制震颤')"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Notes', '备注') }}</label>
              <textarea
                v-model="medicationForm.notes"
                class="input"
                rows="2"
                :placeholder="lt('Other notes...', '其他注意事项...')"
              ></textarea>
            </div>
            <div class="flex gap-3 pt-4">
              <button type="button" @click="showMedicationForm = false" class="btn btn-ghost flex-1">
                {{ lt('Cancel', '取消') }}
              </button>
              <button type="submit" class="btn btn-primary flex-1" :disabled="medicationStore.loading">
                {{ medicationStore.loading ? lt('Saving...', '保存中...') : lt('Save', '保存') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 服药确认模态框 -->
    <Teleport to="body">
      <div v-if="showDosageModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showDosageModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4">
          <div class="p-6 border-b border-gray-100">
            <h3 class="text-xl font-bold text-gray-800">{{ lt('Confirm dose', '确认服药') }}</h3>
          </div>
          <div class="p-6 space-y-4">
            <div v-if="selectedMedication" class="p-4 bg-primary-50 rounded-xl">
              <h4 class="font-semibold text-gray-800">{{ selectedMedication.name }}</h4>
              <p class="text-sm text-gray-600">{{ selectedMedication.dosage }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Notes (optional)', '备注（可选）') }}</label>
              <input
                v-model="dosageForm.notes"
                type="text"
                class="input"
                :placeholder="lt('e.g. taken after a meal', '如：饭后服用')"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ lt('Side effects (optional)', '副作用（可选）') }}</label>
              <input
                v-model="dosageForm.side_effects"
                type="text"
                class="input"
                :placeholder="lt('Record any discomfort if needed', '如有不适请记录')"
              >
            </div>
            <div class="flex gap-3 pt-4">
              <button @click="showDosageModal = false" class="btn btn-ghost flex-1">
                {{ lt('Cancel', '取消') }}
              </button>
              <button @click="confirmTakeMedication" class="btn btn-primary flex-1" :disabled="medicationStore.loading">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ lt('Confirm dose', '确认服药') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>
