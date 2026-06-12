<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import {
  aiApi,
  type DailyAnalysisResponse,
  type DoctorReportRequest,
  type DoctorVisitReportResponse,
  type InsightsResponse,
  type SymptomCheckResponse,
} from '@/api/ai'
import { demoAiIntro } from '@/demo/data'
import { legacyT, t, tList } from '@/i18n'
import type {
  AIAction,
  ChatMessage
} from '@/types'

const router = useRouter()
const AI_REPORT_STORAGE_KEY = 'ai-health-report-current'

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const actionLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

const insights = ref<InsightsResponse | null>(null)
const healthTips = ref<string[]>([])
const loadingInsights = ref(false)

const dailyAnalysis = ref<DailyAnalysisResponse | null>(null)
const loadingDailyAnalysis = ref(false)
const dailyAnalysisError = ref<string | null>(null)

const doctorReportRange = ref({
  start: '',
  end: '',
})
const doctorReport = ref<DoctorVisitReportResponse | null>(null)
const doctorReportLoading = ref(false)
const doctorReportError = ref<string | null>(null)

const symptomInput = ref('')
const associatedFactorsInput = ref('')
const symptomDuration = ref('days')
const symptomSeverity = ref(3)
const symptomCheckResult = ref<SymptomCheckResponse | null>(null)
const symptomCheckLoading = ref(false)
const symptomCheckError = ref<string | null>(null)

const quickQuestions = computed(() => tList('ai.quickQuestions'))

const activeTab = ref<'chat' | 'daily' | 'report' | 'insights'>('chat')

const conversationHistory = computed(() => {
  return messages.value.map(m => ({
    role: m.role,
    content: m.content,
    timestamp: m.timestamp
  }))
})

function formatDateInput(date: Date) {
  return date.toISOString().split('T')[0]
}

function initDoctorReportRange() {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  doctorReportRange.value = {
    start: formatDateInput(start),
    end: formatDateInput(end),
  }
}

function parseListInput(value: string) {
  return value
    .split(/[\n,，、；;]+/)
    .map(item => item.trim())
    .filter(Boolean)
}

async function sendMessage(text?: string) {
  const messageText = text || inputMessage.value.trim()
  if (!messageText || isLoading.value) return

  inputMessage.value = ''

  messages.value.push({
    role: 'user',
    content: messageText,
    timestamp: new Date().toISOString()
  })

  await scrollToBottom()
  isLoading.value = true

  try {
    const response = await aiApi.chat(messageText, conversationHistory.value.slice(-6))

    messages.value.push({
      role: 'assistant',
      content: response.response,
      timestamp: new Date().toISOString(),
      action_card: response.action_card || undefined,
    })
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 'AI service is temporarily unavailable.'
    messages.value.push({
      role: 'assistant',
      content: `Sorry, ${errorMessage}`,
      timestamp: new Date().toISOString()
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

async function executeAction(action: AIAction) {
  if (actionLoading.value) return

  if (action.route && !action.api_path) {
    await router.push(action.route)
    return
  }

  if (!action.api_path) return

  if (action.type === 'download_rehab_pdf' || action.type === 'download_health_report_pdf') {
    actionLoading.value = true
    try {
      const blob = await aiApi.downloadActionPdf(action.api_path)
      const url = window.URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = action.type === 'download_rehab_pdf' ? 'rehab-plan.pdf' : 'ai-health-report.pdf'
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.URL.revokeObjectURL(url)
    } finally {
      actionLoading.value = false
    }
    return
  }

  actionLoading.value = true
  try {
    const result = await aiApi.executeAction(action.api_path)
    messages.value.push({
      role: 'assistant',
      content: result.message,
      timestamp: new Date().toISOString(),
      action_card: result.action_card || undefined,
    })

    if (result.report_data) {
      sessionStorage.setItem(AI_REPORT_STORAGE_KEY, JSON.stringify(result.report_data))
    }

    if (result.route) {
      await router.push(result.route)
    }
  } catch (error: any) {
    messages.value.push({
      role: 'assistant',
      content: error?.response?.data?.detail || error?.message || legacyT('操作失败，请稍后重试。'),
      timestamp: new Date().toISOString(),
    })
  } finally {
    actionLoading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

async function loadInsights() {
  loadingInsights.value = true

  try {
    const [insightsData, tipsData] = await Promise.all([
      aiApi.getInsights(7),
      aiApi.getHealthTips()
    ])

    insights.value = insightsData
    healthTips.value = tipsData.tips
  } catch (error) {
    console.error('加载洞察失败:', error)
  } finally {
    loadingInsights.value = false
  }
}

async function loadDailyAnalysis(date?: string) {
  loadingDailyAnalysis.value = true
  dailyAnalysisError.value = null

  try {
    dailyAnalysis.value = await aiApi.getDailyAnalysis(date)
  } catch (error: any) {
    dailyAnalysisError.value = error.response?.data?.detail || error.message || '加载每日解读失败'
  } finally {
    loadingDailyAnalysis.value = false
  }
}

async function generateDoctorReport() {
  doctorReportError.value = null
  doctorReport.value = null

  if (!doctorReportRange.value.start || !doctorReportRange.value.end) {
    doctorReportError.value = '请选择完整的报告时间范围'
    return
  }

  if (doctorReportRange.value.start > doctorReportRange.value.end) {
    doctorReportError.value = '开始日期不能晚于结束日期'
    return
  }

  doctorReportLoading.value = true

  try {
    const payload: DoctorReportRequest = {
      start_date: doctorReportRange.value.start,
      end_date: doctorReportRange.value.end,
    }
    doctorReport.value = await aiApi.generateDoctorReport(payload)
  } catch (error: any) {
    doctorReportError.value = error.response?.data?.detail || error.message || '生成就诊报告失败'
  } finally {
    doctorReportLoading.value = false
  }
}

async function runSymptomCheck() {
  symptomCheckError.value = null
  symptomCheckResult.value = null

  const symptoms = parseListInput(symptomInput.value)
  if (!symptoms.length) {
    symptomCheckError.value = '请至少输入一个症状'
    return
  }

  symptomCheckLoading.value = true

  try {
    const associatedFactors = parseListInput(associatedFactorsInput.value)
    symptomCheckResult.value = await aiApi.checkSymptoms({
      symptoms,
      duration: symptomDuration.value,
      severity: symptomSeverity.value,
      associated_factors: associatedFactors.length ? associatedFactors : undefined,
    })
  } catch (error: any) {
    symptomCheckError.value = error.response?.data?.detail || error.message || '症状自查失败'
  } finally {
    symptomCheckLoading.value = false
  }
}

function clearChat() {
  messages.value = [...demoAiIntro]
}

function getTrendTone(trend: string) {
  switch (trend) {
    case 'better':
      return 'bg-mint-100 text-mint-700'
    case 'worse':
      return 'bg-red-100 text-red-600'
    default:
      return 'bg-warmGray-100 text-gray-600'
  }
}

function getTrendLabel(trend: string) {
  switch (trend) {
    case 'better':
      return '较昨日更稳定'
    case 'worse':
      return '较昨日波动更大'
    default:
      return '与昨日接近'
  }
}

function getUrgencyTone(level: string) {
  switch (level) {
    case 'urgent':
      return 'bg-red-100 text-red-600'
    case 'soon':
      return 'bg-amber-100 text-amber-700'
    default:
      return 'bg-mint-100 text-mint-700'
  }
}

function getUrgencyLabel(level: string) {
  switch (level) {
    case 'urgent':
      return '尽快处理'
    case 'soon':
      return '建议近期就医'
    default:
      return '常规观察'
  }
}

onMounted(async () => {
  messages.value = [...demoAiIntro]
  initDoctorReportRange()

  await Promise.all([
    loadInsights(),
    loadDailyAnalysis(),
  ])
})
</script>

<template>
  <AppLayout>
    <!-- 页面标题 -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center shadow-soft">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('ai.title') }}</h1>
          <p class="text-gray-500 text-sm">{{ t('ai.subtitle') }}</p>
        </div>
      </div>
    </div>

    <!-- 标签页切换 -->
    <div class="mb-6">
      <div class="bg-warmGray-100 rounded-2xl p-1.5 inline-flex gap-1 flex-wrap">
        <button
          @click="activeTab = 'chat'"
          :class="[
            'px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
            activeTab === 'chat'
              ? 'bg-white text-lavender-600 shadow-soft'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            {{ t('ai.chat') }}
          </span>
        </button>
        <button
          @click="activeTab = 'daily'"
          :class="[
            'px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
            activeTab === 'daily'
              ? 'bg-white text-lavender-600 shadow-soft'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            今日解读
          </span>
        </button>
        <button
          @click="activeTab = 'report'"
          :class="[
            'px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
            activeTab === 'report'
              ? 'bg-white text-lavender-600 shadow-soft'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            就诊报告
          </span>
        </button>
        <button
          @click="activeTab = 'insights'"
          :class="[
            'px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
            activeTab === 'insights'
              ? 'bg-white text-lavender-600 shadow-soft'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ t('ai.insights') }}
          </span>
        </button>
      </div>
    </div>

    <!-- 智能问答 -->
    <div v-if="activeTab === 'chat'" class="card !p-0 flex flex-col h-[calc(100vh-320px)] overflow-hidden">
      <!-- 聊天历史 -->
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="flex animate-fade-in-up"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
          :style="{ animationDelay: `${index * 50}ms` }"
        >
          <!-- AI 头像 -->
          <div v-if="message.role === 'assistant'" class="flex items-start gap-3 max-w-[85%]">
            <div class="w-9 h-9 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-soft">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="bg-gradient-to-br from-lavender-50 to-warmGray-50 text-gray-800 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm border border-lavender-100">
              <p class="whitespace-pre-wrap leading-relaxed">{{ message.content }}</p>
              <div
                v-if="message.action_card"
                class="mt-4 rounded-2xl border border-lavender-200 bg-white p-4 shadow-sm"
              >
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-lavender-100 flex items-center justify-center flex-shrink-0">
                    <svg
                      v-if="message.action_card.kind === 'rehab_plan'"
                      class="w-5 h-5 text-lavender-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v8m-4-4h8M5 12a7 7 0 1114 0 7 7 0 01-14 0z" />
                    </svg>
                    <svg
                      v-else
                      class="w-5 h-5 text-lavender-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2 flex-wrap">
                      <h4 class="text-sm font-semibold text-gray-800">{{ message.action_card.title }}</h4>
                      <span class="px-2.5 py-1 rounded-full text-xs font-medium bg-warmGray-100 text-gray-600">
                        {{ message.action_card.status === 'preview' ? '待确认' : '已生成' }}
                      </span>
                    </div>
                    <p class="mt-2 text-sm leading-6 text-gray-600">{{ message.action_card.summary }}</p>
                    <div class="mt-4 flex flex-wrap gap-2">
                      <button
                        v-for="action in message.action_card.actions"
                        :key="`${message.timestamp}-${action.type}`"
                        @click="executeAction(action)"
                        :disabled="actionLoading"
                        class="px-3 py-2 rounded-xl text-xs font-medium border border-lavender-200 bg-lavender-50 text-lavender-700 hover:bg-lavender-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        {{ actionLoading ? '处理中...' : action.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 用户消息 -->
          <div v-else class="max-w-[75%]">
            <div class="bg-gradient-to-r from-lavender-500 to-lavender-600 text-white rounded-2xl rounded-tr-md px-4 py-3 shadow-soft">
              <p class="whitespace-pre-wrap">{{ message.content }}</p>
            </div>
          </div>
        </div>

        <!-- 加载动画 -->
        <div v-if="isLoading" class="flex justify-start">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-soft">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="bg-lavender-50 rounded-2xl rounded-tl-md px-4 py-3 flex items-center gap-2 border border-lavender-100">
              <div class="flex gap-1">
                <span class="w-2 h-2 bg-lavender-400 rounded-full animate-bounce" style="animation-delay: 0ms;"></span>
                <span class="w-2 h-2 bg-lavender-400 rounded-full animate-bounce" style="animation-delay: 150ms;"></span>
                <span class="w-2 h-2 bg-lavender-400 rounded-full animate-bounce" style="animation-delay: 300ms;"></span>
              </div>
              <span class="text-lavender-600 text-sm">{{ t('ai.loading') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div v-if="messages.length <= 1" class="px-6 pb-4">
        <p class="text-sm text-gray-500 mb-3">{{ t('ai.subtitle') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="q in quickQuestions"
            :key="q"
            @click="sendMessage(q)"
            class="px-4 py-2 bg-gradient-to-r from-lavender-50 to-warmGray-50 hover:from-lavender-100 hover:to-warmGray-100 rounded-xl text-sm text-lavender-700 border border-lavender-200 transition-all duration-200 hover:shadow-sm"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="p-4 border-t border-warmGray-200 bg-warmGray-50">
        <div class="flex gap-3">
          <div class="flex-1 relative">
            <input
              v-model="inputMessage"
              type="text"
              class="input !rounded-xl !py-3 !pr-12"
              :placeholder="t('ai.inputPlaceholder')"
              @keyup.enter="sendMessage()"
              :disabled="isLoading"
            />
            <button
              @click="sendMessage()"
              :disabled="isLoading || !inputMessage.trim()"
              class="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 flex items-center justify-center rounded-lg bg-gradient-to-r from-lavender-500 to-lavender-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-soft transition-all"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <button
            v-if="messages.length > 1"
            @click="clearChat"
            class="btn btn-ghost !px-3"
            :title="t('ai.clear')"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 今日解读 -->
    <div v-else-if="activeTab === 'daily'" class="space-y-6">
      <div class="card">
        <div class="flex items-center justify-between gap-4 flex-wrap mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">今日 AI 解读</h3>
              <p class="text-sm text-gray-500">基于最近监测数据生成每日总结、提醒和建议</p>
            </div>
          </div>
          <button
            @click="loadDailyAnalysis()"
            :disabled="loadingDailyAnalysis"
            class="btn btn-ghost text-sm"
          >
            {{ loadingDailyAnalysis ? '刷新中...' : '刷新解读' }}
          </button>
        </div>

        <div v-if="dailyAnalysisError" class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {{ dailyAnalysisError }}
        </div>

        <div v-if="dailyAnalysis" class="space-y-5">
          <div class="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <p class="text-sm text-gray-500">{{ dailyAnalysis.date }}</p>
              <p class="text-base text-gray-700 leading-7 mt-1">{{ dailyAnalysis.summary }}</p>
            </div>
            <span
              class="px-3 py-1.5 rounded-full text-sm font-medium"
              :class="getTrendTone(dailyAnalysis.tremor_summary.trend)"
            >
              {{ getTrendLabel(dailyAnalysis.tremor_summary.trend) }}
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="rounded-2xl bg-warmGray-50 px-4 py-4 border border-warmGray-200">
              <p class="text-sm text-gray-500">检测次数</p>
              <p class="mt-2 text-2xl font-semibold text-gray-800">{{ dailyAnalysis.tremor_summary.total_detections }}</p>
            </div>
            <div class="rounded-2xl bg-warmGray-50 px-4 py-4 border border-warmGray-200">
              <p class="text-sm text-gray-500">平均严重度</p>
              <p class="mt-2 text-2xl font-semibold text-gray-800">{{ dailyAnalysis.tremor_summary.avg_severity }}</p>
            </div>
            <div class="rounded-2xl bg-warmGray-50 px-4 py-4 border border-warmGray-200">
              <p class="text-sm text-gray-500">最高严重度</p>
              <p class="mt-2 text-2xl font-semibold text-gray-800">{{ dailyAnalysis.tremor_summary.max_severity }}</p>
            </div>
          </div>

          <div class="rounded-2xl border border-lavender-200 bg-lavender-50 px-4 py-4">
            <p class="text-sm font-medium text-lavender-700">趋势对比</p>
            <p class="mt-2 text-sm leading-6 text-gray-700">{{ dailyAnalysis.tremor_summary.comparison_text }}</p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="rounded-2xl border border-primary-100 bg-primary-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">关键观察</h4>
              <ul class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in dailyAnalysis.key_observations" :key="`observation-${index}`">• {{ item }}</li>
              </ul>
            </div>
            <div class="rounded-2xl border border-mint-100 bg-mint-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">建议</h4>
              <ul class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in dailyAnalysis.recommendations" :key="`recommendation-${index}`">• {{ item }}</li>
              </ul>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="rounded-2xl border border-amber-100 bg-amber-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">关注点</h4>
              <ul v-if="dailyAnalysis.concerns.length" class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in dailyAnalysis.concerns" :key="`concern-${index}`">• {{ item }}</li>
              </ul>
              <p v-else class="text-sm text-gray-500">今日暂无额外风险提示。</p>
            </div>
            <div class="rounded-2xl border border-mint-100 bg-mint-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">积极变化</h4>
              <ul v-if="dailyAnalysis.positive_notes.length" class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in dailyAnalysis.positive_notes" :key="`positive-${index}`">• {{ item }}</li>
              </ul>
              <p v-else class="text-sm text-gray-500">继续保持当前监测习惯。</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4" v-if="dailyAnalysis.medication_notes || dailyAnalysis.exercise_notes">
            <div v-if="dailyAnalysis.medication_notes" class="rounded-2xl border border-warmGray-200 bg-white p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-2">用药提示</h4>
              <p class="text-sm leading-6 text-gray-700">{{ dailyAnalysis.medication_notes }}</p>
            </div>
            <div v-if="dailyAnalysis.exercise_notes" class="rounded-2xl border border-warmGray-200 bg-white p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-2">运动提示</h4>
              <p class="text-sm leading-6 text-gray-700">{{ dailyAnalysis.exercise_notes }}</p>
            </div>
          </div>
        </div>

        <div v-else-if="!loadingDailyAnalysis" class="text-center py-12 text-gray-500">
          暂无每日解读数据。
        </div>
      </div>
    </div>

    <!-- 就诊报告 -->
    <div v-else-if="activeTab === 'report'" class="space-y-6">
      <div class="card">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">就诊报告</h3>
            <p class="text-sm text-gray-500">按时间范围生成给医生查看的 AI 汇总报告</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <label class="block">
            <span class="text-sm text-gray-600">开始日期</span>
            <input v-model="doctorReportRange.start" type="date" class="input mt-2" />
          </label>
          <label class="block">
            <span class="text-sm text-gray-600">结束日期</span>
            <input v-model="doctorReportRange.end" type="date" class="input mt-2" />
          </label>
          <button
            @click="generateDoctorReport"
            :disabled="doctorReportLoading"
            class="btn bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white"
          >
            {{ doctorReportLoading ? '生成中...' : '生成就诊报告' }}
          </button>
        </div>

        <div v-if="doctorReportError" class="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          {{ doctorReportError }}
        </div>

        <div v-if="doctorReport" class="mt-6 space-y-5">
          <div class="rounded-2xl bg-warmGray-50 border border-warmGray-200 p-4">
            <div class="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <p class="text-sm text-gray-500">报告周期</p>
                <p class="text-base font-medium text-gray-800 mt-1">
                  {{ doctorReport.period.start }} 至 {{ doctorReport.period.end }}
                </p>
              </div>
              <span class="text-xs text-gray-500">
                生成时间：{{ doctorReport.generated_at }}
              </span>
            </div>
            <p class="mt-3 text-sm leading-6 text-gray-700">{{ doctorReport.summary.executive_summary }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="metric in doctorReport.summary.key_metrics"
              :key="metric.metric"
              class="rounded-2xl border border-primary-100 bg-primary-50 p-4"
            >
              <p class="text-sm text-gray-500">{{ metric.metric }}</p>
              <p class="mt-2 text-lg font-semibold text-gray-800">{{ metric.value }}</p>
              <p class="mt-1 text-xs text-gray-500">{{ metric.trend }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="rounded-2xl border border-lavender-100 bg-lavender-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">震颤分析</h4>
              <p class="text-sm leading-6 text-gray-700">{{ doctorReport.tremor_analysis.frequency_analysis }}</p>
              <div class="mt-4 flex flex-wrap gap-2">
                <span
                  v-for="(count, level) in doctorReport.tremor_analysis.severity_distribution"
                  :key="`severity-${level}`"
                  class="px-3 py-1.5 rounded-full bg-white border border-lavender-200 text-xs text-gray-700"
                >
                  严重度 {{ level }}: {{ count }}
                </span>
              </div>
            </div>
            <div class="rounded-2xl border border-mint-100 bg-mint-50 p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">AI 观察</h4>
              <ul class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in doctorReport.ai_observations" :key="`observation-${index}`">• {{ item }}</li>
              </ul>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="rounded-2xl border border-warmGray-200 bg-white p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">高发时段与模式</h4>
              <div class="flex flex-wrap gap-2 mb-3">
                <span
                  v-for="time in doctorReport.tremor_analysis.peak_times"
                  :key="time"
                  class="px-3 py-1.5 rounded-full bg-warmGray-100 text-xs text-gray-700"
                >
                  {{ time }}
                </span>
              </div>
              <ul class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in doctorReport.tremor_analysis.notable_patterns" :key="`pattern-${index}`">• {{ item }}</li>
              </ul>
            </div>
            <div class="rounded-2xl border border-warmGray-200 bg-white p-4">
              <h4 class="text-sm font-semibold text-gray-800 mb-3">建议和问诊问题</h4>
              <ul class="space-y-2 text-sm text-gray-700">
                <li v-for="(item, index) in doctorReport.questions_for_doctor" :key="`question-${index}`">• {{ item }}</li>
              </ul>
            </div>
          </div>

          <div v-if="doctorReport.medication_analysis" class="rounded-2xl border border-amber-100 bg-amber-50 p-4">
            <h4 class="text-sm font-semibold text-gray-800 mb-3">用药分析</h4>
            <p class="text-sm text-gray-700 mb-3">{{ doctorReport.medication_analysis.effectiveness_summary }}</p>
            <div class="flex flex-wrap gap-2 mb-3">
              <span
                v-for="medication in doctorReport.medication_analysis.current_medications"
                :key="medication"
                class="px-3 py-1.5 rounded-full bg-white border border-amber-200 text-xs text-gray-700"
              >
                {{ medication }}
              </span>
            </div>
            <ul class="space-y-2 text-sm text-gray-700">
              <li v-for="(item, index) in doctorReport.medication_analysis.concerns" :key="`med-concern-${index}`">• {{ item }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 洞察与建议 -->
    <div v-else-if="activeTab === 'insights'" class="space-y-6">
      <!-- 加载状态 -->
      <div v-if="loadingInsights" class="flex flex-col items-center justify-center h-64">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-lavender-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-lavender-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
        </div>
        <p class="text-gray-500 mt-4">加载洞察中...</p>
      </div>

      <template v-else>
        <!-- 数据洞察 -->
        <div class="card">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-lavender-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-800">数据洞察</h3>
            </div>
            <button @click="loadInsights" class="btn btn-ghost text-sm">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              刷新
            </button>
          </div>

          <div v-if="insights?.insights.length" class="space-y-3">
            <div
              v-for="(insight, index) in insights.insights"
              :key="index"
              class="flex items-start gap-3 p-4 bg-gradient-to-r from-lavender-50 to-warmGray-50 rounded-xl border border-lavender-100 animate-fade-in-up"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="w-8 h-8 bg-lavender-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-gray-700 leading-relaxed">{{ insight }}</span>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <div class="w-12 h-12 bg-warmGray-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg class="w-6 h-6 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p class="text-gray-500">暂无数据洞察</p>
          </div>
        </div>

        <!-- 健康提示 -->
        <div class="card">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-mint-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-800">健康提示</h3>
          </div>
          <div class="space-y-3">
            <div
              v-for="(tip, index) in healthTips"
              :key="index"
              class="flex items-start gap-3 p-4 bg-gradient-to-r from-mint-50 to-warmGray-50 rounded-xl border border-mint-100 animate-fade-in-up"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="w-8 h-8 bg-mint-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-gray-700 leading-relaxed">{{ tip }}</span>
            </div>
          </div>
        </div>

        <!-- 症状自查 -->
        <div class="card">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-mint-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">症状自查</h3>
              <p class="text-sm text-gray-500">输入当前症状和诱因，获取 AI 参考建议</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <label class="block lg:col-span-2">
              <span class="text-sm text-gray-600">症状</span>
              <textarea
                v-model="symptomInput"
                rows="3"
                class="input mt-2 min-h-[96px]"
                placeholder="例如：手部震颤、行动迟缓、僵硬"
              />
            </label>
            <label class="block">
              <span class="text-sm text-gray-600">持续时间</span>
              <select v-model="symptomDuration" class="input mt-2">
                <option value="hours">几小时内</option>
                <option value="days">几天</option>
                <option value="weeks">几周</option>
                <option value="months">几个月</option>
                <option value="ongoing">长期存在</option>
              </select>
            </label>
            <label class="block">
              <span class="text-sm text-gray-600">主观严重程度：{{ symptomSeverity }}/5</span>
              <input v-model.number="symptomSeverity" type="range" min="1" max="5" step="1" class="mt-4 w-full" />
            </label>
            <label class="block lg:col-span-2">
              <span class="text-sm text-gray-600">相关因素</span>
              <input
                v-model="associatedFactorsInput"
                type="text"
                class="input mt-2"
                placeholder="例如：疲劳、睡眠不足、压力大"
              />
            </label>
          </div>

          <div class="mt-4 flex justify-end">
            <button
              @click="runSymptomCheck"
              :disabled="symptomCheckLoading"
              class="btn bg-gradient-to-r from-mint-500 to-mint-600 hover:from-mint-600 hover:to-mint-700 text-white"
            >
              {{ symptomCheckLoading ? '分析中...' : '开始自查' }}
            </button>
          </div>

          <div v-if="symptomCheckError" class="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
            {{ symptomCheckError }}
          </div>

          <div v-if="symptomCheckResult" class="mt-6 space-y-4">
            <div class="flex items-start justify-between gap-4 flex-wrap">
              <p class="text-sm leading-6 text-gray-700 max-w-3xl">{{ symptomCheckResult.assessment }}</p>
              <span
                class="px-3 py-1.5 rounded-full text-sm font-medium"
                :class="getUrgencyTone(symptomCheckResult.urgency_level)"
              >
                {{ getUrgencyLabel(symptomCheckResult.urgency_level) }}
              </span>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div class="rounded-2xl border border-warmGray-200 bg-white p-4">
                <h4 class="text-sm font-semibold text-gray-800 mb-3">可能原因</h4>
                <ul class="space-y-2 text-sm text-gray-700">
                  <li v-for="(item, index) in symptomCheckResult.possible_causes" :key="`cause-${index}`">• {{ item }}</li>
                </ul>
              </div>
              <div class="rounded-2xl border border-warmGray-200 bg-white p-4">
                <h4 class="text-sm font-semibold text-gray-800 mb-3">建议</h4>
                <ul class="space-y-2 text-sm text-gray-700">
                  <li v-for="(item, index) in symptomCheckResult.recommendations" :key="`symptom-rec-${index}`">• {{ item }}</li>
                </ul>
              </div>
            </div>

            <div class="flex flex-wrap gap-3">
              <span class="px-3 py-1.5 rounded-full bg-lavender-100 text-lavender-700 text-sm">
                帕金森相关性：{{ symptomCheckResult.related_to_parkinsons_likelihood }}
              </span>
              <span
                class="px-3 py-1.5 rounded-full text-sm"
                :class="symptomCheckResult.should_see_doctor ? 'bg-amber-100 text-amber-700' : 'bg-mint-100 text-mint-700'"
              >
                {{ symptomCheckResult.should_see_doctor ? '建议就医沟通' : '可继续观察记录' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 免责声明 -->
        <div class="bg-gradient-to-r from-amber-50 to-warmGray-50 border border-amber-200 rounded-2xl p-5">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-amber-800 mb-1">重要提示</p>
              <p class="text-sm text-amber-700 leading-relaxed">
                AI 助手提供的分析和建议仅供参考，不能替代专业医生的诊断和治疗意见。
                如有任何健康问题，请及时咨询医疗专业人员。
              </p>
            </div>
          </div>
        </div>
      </template>
    </div>
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
