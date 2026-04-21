<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { reportApi, type ReportData, type QuickStats, type DoctorSummary, type ReportType } from '@/api/report'
import { getSeverityLabel, getSeverityColor } from '@/types'
import { formatDate as formatLocaleDate, formatDateTime as formatLocaleDateTime, t } from '@/i18n'

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const quickStats = ref<QuickStats | null>(null)
const doctorSummary = ref<DoctorSummary | null>(null)
const currentReport = ref<ReportData | null>(null)
const AI_REPORT_STORAGE_KEY = 'ai-health-report-current'

// 报告生成参数
const reportType = ref<ReportType>('weekly')
const customDateRange = ref({
  start: '',
  end: ''
})

// 导出参数
const exportDateRange = ref({
  start: '',
  end: ''
})
const showExportModal = ref(false)
const exporting = ref(false)

// Tab 切换
const activeTab = ref<'overview' | 'generate' | 'doctor'>('overview')

// 初始化日期
function initDates() {
  const now = new Date()
  const end = now.toISOString().split('T')[0]
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  const start = weekAgo.toISOString().split('T')[0]

  customDateRange.value = { start, end }
  exportDateRange.value = { start, end }
}

// 加载快速统计
async function loadQuickStats() {
  try {
    quickStats.value = await reportApi.getQuickStats()
  } catch (e: any) {
    console.error('加载快速统计失败:', e)
  }
}

// 加载医生摘要
async function loadDoctorSummary(days = 7) {
  loading.value = true
  error.value = null
  try {
    doctorSummary.value = await reportApi.getDoctorSummary(days)
  } catch (e: any) {
    error.value = e.message || '加载医生摘要失败'
  } finally {
    loading.value = false
  }
}

// 生成报告
async function generateReport() {
  loading.value = true
  error.value = null

  try {
    const request: any = {
      report_type: reportType.value,
      format: 'json'
    }

    if (reportType.value === 'custom') {
      if (!customDateRange.value.start || !customDateRange.value.end) {
        error.value = t('reports.errors.dateRequired')
        loading.value = false
        return
      }
      request.start_date = new Date(customDateRange.value.start).toISOString()
      request.end_date = new Date(customDateRange.value.end).toISOString()
    }

    currentReport.value = await reportApi.generate(request)
  } catch (e: any) {
    error.value = e.message || t('reports.errors.generate')
  } finally {
    loading.value = false
  }
}

// 导出数据
async function exportData(format: 'csv' | 'json') {
  if (!exportDateRange.value.start || !exportDateRange.value.end) {
    error.value = t('reports.errors.dateRequired')
    return
  }

  exporting.value = true
  error.value = null

  try {
    const startDate = new Date(exportDateRange.value.start).toISOString()
    const endDate = new Date(exportDateRange.value.end).toISOString()

    let blob: Blob
    let filename: string

    if (format === 'csv') {
      blob = await reportApi.exportCsv(startDate, endDate)
      filename = `tremor_data_${exportDateRange.value.start}_${exportDateRange.value.end}.csv`
    } else {
      blob = await reportApi.exportJson(startDate, endDate)
      filename = `tremor_data_${exportDateRange.value.start}_${exportDateRange.value.end}.json`
    }

    // 下载文件
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    showExportModal.value = false
  } catch (e: any) {
    error.value = e.message || t('reports.errors.export')
  } finally {
    exporting.value = false
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  return formatLocaleDate(dateStr)
}

// 格式化时间
function formatDateTime(dateStr: string) {
  return formatLocaleDateTime(dateStr)
}

// 获取趋势图标和颜色
function getTrendInfo(trend: string) {
  switch (trend) {
    case 'improving':
    case 'decreasing':
      return { icon: '↓', color: 'text-mint-600', bgColor: 'bg-mint-100', label: t('reports.trend.down') }
    case 'worsening':
    case 'increasing':
      return { icon: '↑', color: 'text-red-500', bgColor: 'bg-red-100', label: t('reports.trend.up') }
    default:
      return { icon: '→', color: 'text-gray-600', bgColor: 'bg-warmGray-100', label: t('reports.trend.stable') }
  }
}

// 计算属性
const reportTypeLabels = computed(() => ({
  daily: t('reports.reportTypes.daily'),
  weekly: t('reports.reportTypes.weekly'),
  monthly: t('reports.reportTypes.monthly'),
  custom: t('reports.reportTypes.custom')
}))

const reportTypeIcons = {
  daily: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  weekly: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
  monthly: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  custom: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4'
}

onMounted(() => {
  initDates()
  loadQuickStats()
  const stored = sessionStorage.getItem(AI_REPORT_STORAGE_KEY)
  if (stored) {
    try {
      currentReport.value = JSON.parse(stored) as ReportData
      activeTab.value = 'generate'
    } catch {
      // ignore malformed cached report
    }
  }
})
</script>

<template>
  <AppLayout>
    <!-- 页面标题 -->
    <div class="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('reports.title') }}</h1>
          <p class="text-gray-500 text-sm">{{ t('reports.subtitle') }}</p>
        </div>
      </div>

      <button @click="showExportModal = true" class="btn btn-secondary">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        {{ t('reports.export') }}
      </button>
    </div>

    <!-- 错误提示 -->
    <Transition name="fade-up">
      <div v-if="error" class="alert alert-error mb-6">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
        <button @click="error = null" class="ml-auto text-red-600 hover:text-red-700 font-medium">{{ t('reports.close') }}</button>
      </div>
    </Transition>

    <!-- 快速统计卡片 -->
    <div v-if="quickStats" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('reports.quickToday') }}</p>
            <p class="text-3xl font-bold text-gray-800">{{ quickStats.today.tremor_count }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ t('reports.tremorSuffix', { count: quickStats.today.total_analyses }) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('reports.quickWeek') }}</p>
            <p class="text-3xl font-bold text-mint-600">{{ quickStats.this_week.tremor_count }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ t('reports.tremorSuffix', { count: quickStats.this_week.total_analyses }) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('reports.quickMonth') }}</p>
            <p class="text-3xl font-bold text-lavender-600">{{ quickStats.this_month.tremor_count }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ t('reports.tremorSuffix', { count: quickStats.this_month.total_analyses }) }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 导航 -->
    <div class="card !p-0 overflow-hidden">
      <div class="bg-warmGray-50 border-b border-warmGray-200 px-6 py-3">
        <div class="flex gap-1">
          <button
            @click="activeTab = 'overview'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
              activeTab === 'overview'
                ? 'bg-white text-primary-600 shadow-soft'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              生成报告
            </span>
          </button>
          <button
            @click="activeTab = 'doctor'; loadDoctorSummary()"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
              activeTab === 'doctor'
                ? 'bg-white text-primary-600 shadow-soft'
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            <span class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              医生摘要
            </span>
          </button>
        </div>
      </div>

      <!-- 生成报告 Tab -->
      <div v-if="activeTab === 'overview'" class="p-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 左侧：报告类型选择 -->
          <div class="space-y-6">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 class="font-semibold text-gray-800">选择报告类型</h3>
            </div>

            <div class="space-y-3">
              <label
                v-for="type in (['daily', 'weekly', 'monthly', 'custom'] as ReportType[])"
                :key="type"
                class="flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all duration-200"
                :class="reportType === type
                  ? 'border-primary-400 bg-gradient-to-r from-primary-50 to-warmGray-50 shadow-soft'
                  : 'border-warmGray-200 hover:bg-warmGray-50'"
              >
                <input
                  type="radio"
                  :value="type"
                  v-model="reportType"
                  class="sr-only"
                />
                <div
                  class="w-10 h-10 rounded-xl flex items-center justify-center mr-3"
                  :class="reportType === type ? 'bg-primary-500' : 'bg-warmGray-100'"
                >
                  <svg
                    class="w-5 h-5"
                    :class="reportType === type ? 'text-white' : 'text-warmGray-500'"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="reportTypeIcons[type]" />
                  </svg>
                </div>
                <div>
                  <span class="font-medium" :class="reportType === type ? 'text-primary-700' : 'text-gray-700'">
                    {{ reportTypeLabels[type] }}
                  </span>
                  <p class="text-xs text-gray-400">
                    {{ type === 'daily' ? '今日数据汇总' : type === 'weekly' ? '最近7天数据' : type === 'monthly' ? '最近30天数据' : '自定义日期范围' }}
                  </p>
                </div>
                <div v-if="reportType === type" class="ml-auto">
                  <svg class="w-5 h-5 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </label>
            </div>

            <!-- 自定义日期范围 -->
            <Transition name="fade-up">
              <div v-if="reportType === 'custom'" class="space-y-3 p-4 bg-warmGray-50 rounded-xl">
                <div>
                  <label class="block text-sm text-gray-600 mb-1.5">开始日期</label>
                  <input
                    v-model="customDateRange.start"
                    type="date"
                    class="input"
                  />
                </div>
                <div>
                  <label class="block text-sm text-gray-600 mb-1.5">结束日期</label>
                  <input
                    v-model="customDateRange.end"
                    type="date"
                    class="input"
                  />
                </div>
              </div>
            </Transition>

            <button
              @click="generateReport"
              :disabled="loading"
              class="btn btn-primary w-full"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ loading ? '生成中...' : '生成报告' }}
            </button>
          </div>

          <!-- 右侧：报告预览 -->
          <div class="lg:col-span-2">
            <div v-if="!currentReport" class="text-center py-16">
              <div class="w-20 h-20 bg-gradient-to-br from-warmGray-100 to-warmGray-200 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-700 mb-2">生成您的报告</h3>
              <p class="text-gray-500">选择报告类型并点击"生成报告"按钮</p>
            </div>

            <div v-else class="space-y-6">
              <!-- 报告头部 -->
              <div class="flex items-center justify-between p-4 bg-gradient-to-r from-primary-50 to-warmGray-50 rounded-xl border border-primary-100">
                <div>
                  <h3 class="font-semibold text-lg text-gray-800">{{ reportTypeLabels[currentReport.report_type] }}</h3>
                  <p class="text-sm text-gray-500">
                    {{ formatDate(currentReport.summary.period_start) }} - {{ formatDate(currentReport.summary.period_end) }}
                  </p>
                </div>
                <span class="text-xs text-gray-400 bg-white px-3 py-1 rounded-full">
                  生成于 {{ formatDateTime(currentReport.generated_at) }}
                </span>
              </div>

              <!-- 报告摘要 -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-gradient-to-br from-warmGray-50 to-primary-50/30 rounded-xl">
                  <p class="text-gray-500 text-sm mb-1">总检测</p>
                  <p class="text-2xl font-bold text-gray-800">{{ currentReport.summary.total_analyses }}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-warmGray-50 to-amber-50/30 rounded-xl">
                  <p class="text-gray-500 text-sm mb-1">震颤次数</p>
                  <p class="text-2xl font-bold text-amber-600">{{ currentReport.summary.tremor_detections }}</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-warmGray-50 to-mint-50/30 rounded-xl">
                  <p class="text-gray-500 text-sm mb-1">检出率</p>
                  <p class="text-2xl font-bold text-gray-800">{{ currentReport.summary.detection_rate }}%</p>
                </div>
                <div class="text-center p-4 bg-gradient-to-br from-warmGray-50 to-lavender-50/30 rounded-xl">
                  <p class="text-gray-500 text-sm mb-1">平均严重度</p>
                  <p class="text-2xl font-bold text-gray-800">{{ currentReport.summary.avg_severity }}</p>
                </div>
              </div>

              <!-- 严重度分布 -->
              <div class="bg-warmGray-50 rounded-xl p-5">
                <h4 class="font-medium mb-4 text-gray-800">严重度分布</h4>
                <div class="flex items-end h-32 gap-3">
                  <div
                    v-for="(count, severity) in currentReport.severity_distribution"
                    :key="severity"
                    class="flex-1 flex flex-col items-center"
                  >
                    <div
                      class="w-full rounded-t-lg transition-all duration-500"
                      :style="{
                        height: `${Math.max(8, (count / Math.max(...Object.values(currentReport.severity_distribution), 1)) * 100)}%`,
                        backgroundColor: getSeverityColor(Number(severity))
                      }"
                    ></div>
                    <span class="text-xs text-gray-500 mt-2">{{ getSeverityLabel(Number(severity)) }}</span>
                    <span class="text-xs font-medium text-gray-700">{{ count }}</span>
                  </div>
                </div>
              </div>

              <!-- 每日统计 -->
              <div v-if="currentReport.daily_breakdown.length > 0">
                <h4 class="font-medium mb-4 text-gray-800">每日统计</h4>
                <div class="overflow-x-auto">
                  <table class="table text-sm">
                    <thead>
                      <tr>
                        <th>日期</th>
                        <th>检测次数</th>
                        <th>震颤次数</th>
                        <th>平均严重度</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(day, index) in currentReport.daily_breakdown" :key="day.date" class="animate-fade-in-up" :style="{ animationDelay: `${index * 30}ms` }">
                        <td class="font-medium">{{ day.date }}</td>
                        <td>{{ day.total }}</td>
                        <td>
                          <span :class="day.tremors > 0 ? 'text-amber-600 font-medium' : 'text-gray-600'">
                            {{ day.tremors }}
                          </span>
                        </td>
                        <td>{{ day.avg_severity.toFixed(2) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 医生摘要 Tab -->
      <div v-if="activeTab === 'doctor'" class="p-6">
        <div v-if="loading" class="flex flex-col items-center justify-center py-16">
          <div class="relative">
            <div class="w-16 h-16 border-4 border-primary-200 rounded-full"></div>
            <div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
          </div>
          <p class="text-gray-500 mt-4">加载医生摘要...</p>
        </div>

        <div v-else-if="!doctorSummary" class="text-center py-16">
          <div class="w-20 h-20 bg-gradient-to-br from-warmGray-100 to-warmGray-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-10 h-10 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-gray-500">无法加载医生摘要</p>
        </div>

        <div v-else class="space-y-6">
          <!-- 头部信息 -->
          <div class="flex flex-wrap items-center justify-between gap-4 p-5 bg-gradient-to-r from-lavender-50 to-warmGray-50 rounded-xl border border-lavender-100">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-gray-800">医生查阅摘要</h3>
                <p class="text-sm text-gray-500">
                  {{ doctorSummary.patient_info.full_name || doctorSummary.patient_info.username }} |
                  {{ formatDate(doctorSummary.period.start) }} - {{ formatDate(doctorSummary.period.end) }}
                </p>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                v-for="days in [7, 14, 30]"
                :key="days"
                @click="loadDoctorSummary(days)"
                :class="[
                  'px-4 py-2 text-sm rounded-lg font-medium transition-all',
                  doctorSummary.period.days === days
                    ? 'bg-lavender-500 text-white shadow-soft'
                    : 'bg-white text-lavender-600 hover:bg-lavender-50'
                ]"
              >
                {{ days }}天
              </button>
            </div>
          </div>

          <!-- 关键指标 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="card card-gradient text-center">
              <p class="text-gray-500 text-sm mb-1">震颤发作</p>
              <p class="text-2xl font-bold text-gray-800">{{ doctorSummary.summary.tremor_episodes }}</p>
              <p class="text-xs mt-1 px-2 py-0.5 rounded-full inline-flex items-center" :class="getTrendInfo(doctorSummary.summary.frequency_trend).bgColor">
                <span :class="getTrendInfo(doctorSummary.summary.frequency_trend).color">
                  {{ getTrendInfo(doctorSummary.summary.frequency_trend).icon }}
                  {{ doctorSummary.comparison.tremor_change_percent }}%
                </span>
              </p>
            </div>
            <div class="card card-gradient text-center">
              <p class="text-gray-500 text-sm mb-1">平均严重度</p>
              <p class="text-2xl font-bold text-gray-800">{{ doctorSummary.summary.avg_severity }}</p>
              <p class="text-xs mt-1 px-2 py-0.5 rounded-full inline-flex items-center" :class="getTrendInfo(doctorSummary.summary.severity_trend).bgColor">
                <span :class="getTrendInfo(doctorSummary.summary.severity_trend).color">
                  {{ getTrendInfo(doctorSummary.summary.severity_trend).icon }}
                  {{ doctorSummary.comparison.severity_change_percent }}%
                </span>
              </p>
            </div>
            <div class="card card-gradient text-center">
              <p class="text-gray-500 text-sm mb-1">严重发作 (3-4级)</p>
              <p class="text-2xl font-bold text-red-500">{{ doctorSummary.summary.severe_episodes }}</p>
            </div>
            <div class="card card-gradient text-center">
              <p class="text-gray-500 text-sm mb-1">监测记录数</p>
              <p class="text-2xl font-bold text-gray-800">{{ doctorSummary.summary.total_monitoring_records }}</p>
            </div>
          </div>

          <!-- 趋势状态 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="card">
              <p class="text-sm text-gray-500 mb-3">严重度趋势</p>
              <div class="flex items-center gap-3">
                <div
                  class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                  :class="getTrendInfo(doctorSummary.summary.severity_trend).bgColor"
                >
                  <span :class="getTrendInfo(doctorSummary.summary.severity_trend).color">
                    {{ getTrendInfo(doctorSummary.summary.severity_trend).icon }}
                  </span>
                </div>
                <span class="font-semibold" :class="getTrendInfo(doctorSummary.summary.severity_trend).color">
                  {{
                    doctorSummary.summary.severity_trend === 'improving' ? '好转中' :
                    doctorSummary.summary.severity_trend === 'worsening' ? '恶化中' : '稳定'
                  }}
                </span>
              </div>
            </div>
            <div class="card">
              <p class="text-sm text-gray-500 mb-3">发作频率趋势</p>
              <div class="flex items-center gap-3">
                <div
                  class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                  :class="getTrendInfo(doctorSummary.summary.frequency_trend).bgColor"
                >
                  <span :class="getTrendInfo(doctorSummary.summary.frequency_trend).color">
                    {{ getTrendInfo(doctorSummary.summary.frequency_trend).icon }}
                  </span>
                </div>
                <span class="font-semibold" :class="getTrendInfo(doctorSummary.summary.frequency_trend).color">
                  {{
                    doctorSummary.summary.frequency_trend === 'decreasing' ? '减少中' :
                    doctorSummary.summary.frequency_trend === 'increasing' ? '增加中' : '稳定'
                  }}
                </span>
              </div>
            </div>
          </div>

          <!-- 观察结论 -->
          <div v-if="doctorSummary.key_observations.length > 0" class="card">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 class="font-medium text-gray-800">关键观察</h4>
            </div>
            <ul class="space-y-3">
              <li
                v-for="(obs, index) in doctorSummary.key_observations"
                :key="index"
                class="flex items-start gap-3 p-3 bg-primary-50 rounded-xl animate-fade-in-up"
                :style="{ animationDelay: `${index * 100}ms` }"
              >
                <div class="w-6 h-6 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" />
                  </svg>
                </div>
                <span class="text-gray-700">{{ obs }}</span>
              </li>
            </ul>
          </div>

          <!-- 建议 -->
          <div v-if="doctorSummary.recommendations.length > 0" class="bg-gradient-to-r from-amber-50 to-warmGray-50 border border-amber-200 rounded-2xl p-5">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h4 class="font-medium text-amber-800">建议</h4>
            </div>
            <ul class="space-y-3">
              <li
                v-for="(rec, index) in doctorSummary.recommendations"
                :key="index"
                class="flex items-start gap-3 p-3 bg-white/60 rounded-xl animate-fade-in-up"
                :style="{ animationDelay: `${index * 100}ms` }"
              >
                <div class="w-6 h-6 bg-amber-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-amber-800">{{ rec }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出模态框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showExportModal"
          class="modal-overlay"
          @click.self="showExportModal = false"
        >
          <div class="modal max-w-md">
            <div class="modal-header">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-800">导出数据</h3>
              </div>
              <button @click="showExportModal = false" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">开始日期</label>
                <input
                  v-model="exportDateRange.start"
                  type="date"
                  class="input"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">结束日期</label>
                <input
                  v-model="exportDateRange.end"
                  type="date"
                  class="input"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button
                @click="exportData('csv')"
                :disabled="exporting"
                class="btn btn-secondary"
              >
                <svg v-if="exporting" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                导出 CSV
              </button>
              <button
                @click="exportData('json')"
                :disabled="exporting"
                class="btn btn-primary"
              >
                <svg v-if="exporting" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                导出 JSON
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AppLayout>
</template>

<style scoped>
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.3s ease-out forwards;
  opacity: 0;
}
</style>
