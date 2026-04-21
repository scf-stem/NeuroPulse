<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { aiApi, type AnalysisResponse, type InsightsResponse } from '@/api/ai'
import { APP_NAME } from '@/config/branding'
import { demoAiIntro } from '@/demo/data'
import { legacyT, t, tList } from '@/i18n'
import type {
  AIAction,
  DailyAnalysis,
  PersonalizedAdvice,
  DoctorVisitReport,
  SymptomCheckRequest,
  SymptomCheckResponse,
  ChatMessage
} from '@/types'

const router = useRouter()
const AI_REPORT_STORAGE_KEY = 'ai-health-report-current'

// 聊天相关
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const actionLoading = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// 分析相关
const analysisResult = ref<AnalysisResponse | null>(null)
const isAnalyzing = ref(false)
const analysisDays = ref(7)

// 洞察和提示
const insights = ref<InsightsResponse | null>(null)
const healthTips = ref<string[]>([])
const loadingInsights = ref(false)

// 今日解读相关
const dailyAnalysis = ref<DailyAnalysis | null>(null)
const personalizedAdvice = ref<PersonalizedAdvice[]>([])
const loadingDailyAnalysis = ref(false)

// 就诊报告相关
const doctorReport = ref<DoctorVisitReport | null>(null)
const generatingReport = ref(false)
const reportDays = ref(30)

// 症状自查相关
const symptomCheckVisible = ref(false)
const symptomCheckResult = ref<SymptomCheckResponse | null>(null)
const checkingSymptoms = ref(false)
const symptomForm = ref<SymptomCheckRequest>({
  symptoms: [],
  duration: '',
  severity: 3,
  associated_factors: [],
})

// 当前标签页
const activeTab = ref<'chat' | 'daily' | 'report' | 'analysis' | 'insights'>('chat')

// 快捷问题
const quickQuestions = computed(() => tList('ai.quickQuestions'))

// 计算属性
const conversationHistory = computed(() => {
  return messages.value.map(m => ({
    role: m.role,
    content: m.content,
    timestamp: m.timestamp
  }))

})

// 方法
async function sendMessage(text?: string) {
  const messageText = text || inputMessage.value.trim()
  if (!messageText || isLoading.value) return

  inputMessage.value = ''

  // 添加用户消息
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

async function runAnalysis() {
  isAnalyzing.value = true
  analysisResult.value = null

  try {
    analysisResult.value = await aiApi.analyze(analysisDays.value)
  } catch (error: any) {
    console.error('分析失败:', error)
  } finally {
    isAnalyzing.value = false
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

function clearChat() {
  messages.value = [...demoAiIntro]
}

function getRiskColor(risk: string): string {
  switch (risk) {
    case 'low':
    case '低': return 'text-mint-600 bg-mint-100'
    case 'high':
    case '高': return 'text-red-500 bg-red-100'
    default: return 'text-amber-600 bg-amber-100'
  }
}

function getRiskLabel(risk: string): string {
  switch (risk) {
    case 'low':
    case '低':
      return legacyT('低')
    case 'high':
    case '高':
      return legacyT('高')
    case 'medium':
    case '中':
    default:
      return legacyT('中')
  }
}

function getTrendIcon(trend: string): string {
  switch (trend) {
    case 'better':
    case 'improving':
      return '↓'
    case 'worse':
    case 'worsening':
      return '↑'
    default:
      return '→'
  }
}

function getTrendColor(trend: string): string {
  switch (trend) {
    case 'better':
    case 'improving':
      return 'text-mint-600'
    case 'worse':
    case 'worsening':
      return 'text-red-500'
    default:
      return 'text-gray-500'
  }
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-700 border-red-200'
    case 'medium':
      return 'bg-amber-100 text-amber-700 border-amber-200'
    default:
      return 'bg-mint-100 text-mint-700 border-mint-200'
  }
}

function getUrgencyColor(level: string): string {
  switch (level) {
    case 'urgent':
      return 'text-red-600 bg-red-100'
    case 'soon':
      return 'text-amber-600 bg-amber-100'
    default:
      return 'text-mint-600 bg-mint-100'
  }
}

function getUrgencyLabel(level: string): string {
  switch (level) {
    case 'urgent':
      return legacyT('建议尽快就医')
    case 'soon':
      return legacyT('建议近期就医')
    default:
      return legacyT('可继续观察')
  }
}

// 今日解读相关方法
async function loadDailyAnalysis() {
  loadingDailyAnalysis.value = true
  try {
    const [analysis, advice] = await Promise.all([
      aiApi.getDailyAnalysis(),
      aiApi.getPersonalizedAdvice(),
    ])
    dailyAnalysis.value = analysis
    personalizedAdvice.value = advice
  } catch (error) {
    console.error('加载今日解读失败:', error)
  } finally {
    loadingDailyAnalysis.value = false
  }
}

// 就诊报告相关方法
async function generateDoctorReport() {
  generatingReport.value = true
  doctorReport.value = null
  try {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - reportDays.value)
    
    doctorReport.value = await aiApi.generateDoctorReport({
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0]
    })
  } catch (error) {
    console.error('生成就诊报告失败:', error)
  } finally {
    generatingReport.value = false
  }
}

async function downloadReportPDF() {
  if (!doctorReport.value) return
  // TODO: 实现 PDF 导出功能
  alert(legacyT('PDF 导出功能即将上线'))
}

// 症状自查相关方法
async function checkSymptoms() {
  if (symptomForm.value.symptoms.length === 0) return
  checkingSymptoms.value = true
  try {
    symptomCheckResult.value = await aiApi.checkSymptoms(symptomForm.value)
  } catch (error) {
    console.error('症状自查失败:', error)
  } finally {
    checkingSymptoms.value = false
  }
}

function resetSymptomCheck() {
  symptomForm.value = {
    symptoms: [],
    duration: '',
    severity: 3,
    associated_factors: [],
  }
  symptomCheckResult.value = null
}

// 常见症状选项
const commonSymptoms = [
  '手部震颤',
  '腿部震颤',
  '行动迟缓',
  '肌肉僵硬',
  '平衡困难',
  '书写困难',
  '说话困难',
  '睡眠问题',
  '情绪变化',
  '疲劳',
].map((item) => legacyT(item))

const durationOptions = [
  { value: 'hours', label: legacyT('几小时内') },
  { value: 'days', label: legacyT('几天') },
  { value: 'weeks', label: legacyT('几周') },
  { value: 'months', label: legacyT('几个月') },
  { value: 'ongoing', label: legacyT('长期存在') },
]

// 生命周期
onMounted(async () => {
  messages.value = [...demoAiIntro]

  // 加载洞察和提示
  await loadInsights()
  // 预加载今日解读
  await loadDailyAnalysis()
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            {{ t('ai.daily') }}
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
            {{ t('ai.report') }}
          </span>
        </button>
        <button
          @click="activeTab = 'analysis'"
          :class="[
            'px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
            activeTab === 'analysis'
              ? 'bg-white text-lavender-600 shadow-soft'
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          <span class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {{ t('ai.analysis') }}
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
      <!-- 加载状态 -->
      <div v-if="loadingDailyAnalysis" class="flex flex-col items-center justify-center h-64">
        <div class="relative">
          <div class="w-16 h-16 border-4 border-lavender-200 rounded-full"></div>
          <div class="w-16 h-16 border-4 border-lavender-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
        </div>
        <p class="text-gray-500 mt-4">加载今日解读中...</p>
      </div>

      <template v-else>
        <!-- 今日数据摘要 -->
        <div v-if="dailyAnalysis" class="card">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-800">{{ dailyAnalysis.date }} 数据解读</h3>
                <p class="text-sm text-gray-500">{{ dailyAnalysis.summary }}</p>
              </div>
            </div>
            <button @click="loadDailyAnalysis" class="btn btn-ghost text-sm">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              刷新
            </button>
          </div>

          <!-- 震颤数据统计 -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-gradient-to-br from-lavender-50 to-warmGray-50 rounded-xl p-4 border border-lavender-100">
              <p class="text-sm text-gray-500 mb-1">检测次数</p>
              <p class="text-2xl font-bold text-gray-800">{{ dailyAnalysis.tremor_summary.total_detections }}</p>
            </div>
            <div class="bg-gradient-to-br from-lavender-50 to-warmGray-50 rounded-xl p-4 border border-lavender-100">
              <p class="text-sm text-gray-500 mb-1">平均严重度</p>
              <p class="text-2xl font-bold text-gray-800">{{ dailyAnalysis.tremor_summary.avg_severity.toFixed(1) }}</p>
            </div>
            <div class="bg-gradient-to-br from-lavender-50 to-warmGray-50 rounded-xl p-4 border border-lavender-100">
              <p class="text-sm text-gray-500 mb-1">最高严重度</p>
              <p class="text-2xl font-bold text-gray-800">{{ dailyAnalysis.tremor_summary.max_severity }}</p>
            </div>
            <div class="bg-gradient-to-br from-lavender-50 to-warmGray-50 rounded-xl p-4 border border-lavender-100">
              <p class="text-sm text-gray-500 mb-1">趋势</p>
              <p class="text-2xl font-bold" :class="getTrendColor(dailyAnalysis.tremor_summary.trend)">
                {{ getTrendIcon(dailyAnalysis.tremor_summary.trend) }} {{ legacyT(dailyAnalysis.tremor_summary.comparison_text) }}
              </p>
            </div>
          </div>

          <!-- 关键观察 -->
          <div v-if="dailyAnalysis.key_observations.length" class="mb-6">
            <h4 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-lavender-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              关键观察
            </h4>
            <div class="space-y-2">
              <div
                v-for="(obs, index) in dailyAnalysis.key_observations"
                :key="index"
                class="flex items-start gap-3 p-3 bg-warmGray-50 rounded-xl"
              >
                <div class="w-6 h-6 bg-lavender-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span class="text-lavender-600 text-sm font-medium">{{ index + 1 }}</span>
                </div>
                <span class="text-gray-700">{{ obs }}</span>
              </div>
            </div>
          </div>

          <!-- 注意事项 -->
          <div v-if="dailyAnalysis.concerns.length" class="mb-6">
            <h4 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              需要关注
            </h4>
            <div class="space-y-2">
              <div
                v-for="(concern, index) in dailyAnalysis.concerns"
                :key="index"
                class="flex items-start gap-3 p-3 bg-amber-50 rounded-xl border border-amber-100"
              >
                <svg class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01" />
                </svg>
                <span class="text-amber-800">{{ concern }}</span>
              </div>
            </div>
          </div>

          <!-- 积极方面 -->
          <div v-if="dailyAnalysis.positive_notes.length" class="mb-6">
            <h4 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-mint-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              积极方面
            </h4>
            <div class="space-y-2">
              <div
                v-for="(note, index) in dailyAnalysis.positive_notes"
                :key="index"
                class="flex items-start gap-3 p-3 bg-mint-50 rounded-xl border border-mint-100"
              >
                <svg class="w-5 h-5 text-mint-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="text-mint-800">{{ note }}</span>
              </div>
            </div>
          </div>

          <!-- 建议 -->
          <div v-if="dailyAnalysis.recommendations.length">
            <h4 class="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              AI 建议
            </h4>
            <div class="space-y-2">
              <div
                v-for="(rec, index) in dailyAnalysis.recommendations"
                :key="index"
                class="flex items-start gap-3 p-3 bg-primary-50 rounded-xl border border-primary-100"
              >
                <div class="w-6 h-6 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
                <span class="text-gray-700">{{ rec }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 个性化建议 -->
        <div v-if="personalizedAdvice.length" class="card">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">个性化健康建议</h3>
              <p class="text-sm text-gray-500">基于您的健康数据生成的专属建议</p>
            </div>
          </div>

          <div class="space-y-4">
            <div
              v-for="advice in personalizedAdvice"
              :key="advice.advice_id"
              class="p-4 rounded-xl border"
              :class="getPriorityColor(advice.priority)"
            >
              <div class="flex items-start justify-between mb-2">
                <h4 class="font-semibold">{{ advice.title }}</h4>
                <span class="text-xs px-2 py-1 rounded-full" :class="getPriorityColor(advice.priority)">
                  {{ advice.priority === 'high' ? '重要' : advice.priority === 'medium' ? '建议' : '参考' }}
                </span>
              </div>
              <p class="text-sm mb-3 opacity-90">{{ advice.content }}</p>
              <div v-if="advice.action_items.length" class="space-y-1">
                <p class="text-xs font-medium opacity-75">行动建议：</p>
                <ul class="text-sm space-y-1">
                  <li v-for="(item, idx) in advice.action_items" :key="idx" class="flex items-start gap-2">
                    <span class="opacity-60">•</span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 症状自查入口 -->
        <div class="card">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-800">症状自查</h3>
                <p class="text-sm text-gray-500">记录症状，获取 AI 初步评估</p>
              </div>
            </div>
            <button
              @click="symptomCheckVisible = !symptomCheckVisible"
              class="btn bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white"
            >
              {{ symptomCheckVisible ? '收起' : '开始自查' }}
            </button>
          </div>

          <!-- 症状自查表单 -->
          <div v-if="symptomCheckVisible" class="mt-6 pt-6 border-t border-warmGray-200">
            <div class="space-y-4">
              <!-- 症状选择 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">选择您的症状（可多选）</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="symptom in commonSymptoms"
                    :key="symptom"
                    @click="symptomForm.symptoms.includes(symptom)
                      ? symptomForm.symptoms = symptomForm.symptoms.filter(s => s !== symptom)
                      : symptomForm.symptoms.push(symptom)"
                    :class="[
                      'px-3 py-2 rounded-lg text-sm border transition-all',
                      symptomForm.symptoms.includes(symptom)
                        ? 'bg-amber-100 border-amber-300 text-amber-800'
                        : 'bg-warmGray-50 border-warmGray-200 text-gray-600 hover:bg-warmGray-100'
                    ]"
                  >
                    {{ symptom }}
                  </button>
                </div>
              </div>

              <!-- 持续时间 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">症状持续时间</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="option in durationOptions"
                    :key="option.value"
                    @click="symptomForm.duration = option.value"
                    :class="[
                      'px-4 py-2 rounded-lg text-sm border transition-all',
                      symptomForm.duration === option.value
                        ? 'bg-amber-100 border-amber-300 text-amber-800'
                        : 'bg-warmGray-50 border-warmGray-200 text-gray-600 hover:bg-warmGray-100'
                    ]"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <!-- 严重程度 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  严重程度：{{ symptomForm.severity }} / 5
                </label>
                <input
                  type="range"
                  v-model="symptomForm.severity"
                  min="1"
                  max="5"
                  class="w-full h-2 bg-warmGray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                  <span>轻微</span>
                  <span>严重</span>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="flex gap-3">
                <button
                  @click="checkSymptoms"
                  :disabled="checkingSymptoms || symptomForm.symptoms.length === 0"
                  class="btn bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white flex-1"
                >
                  <svg v-if="checkingSymptoms" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  {{ checkingSymptoms ? '分析中...' : '获取评估' }}
                </button>
                <button @click="resetSymptomCheck" class="btn btn-ghost">
                  重置
                </button>
              </div>
            </div>

            <!-- 症状自查结果 -->
            <div v-if="symptomCheckResult" class="mt-6 p-4 bg-warmGray-50 rounded-xl space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="font-semibold text-gray-800">评估结果</h4>
                <span
                  class="px-3 py-1 rounded-full text-sm font-medium"
                  :class="getUrgencyColor(symptomCheckResult.urgency_level)"
                >
                  {{ getUrgencyLabel(symptomCheckResult.urgency_level) }}
                </span>
              </div>
              <p class="text-gray-700">{{ symptomCheckResult.assessment }}</p>

              <div v-if="symptomCheckResult.possible_causes.length">
                <p class="text-sm font-medium text-gray-600 mb-2">可能原因：</p>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li v-for="(cause, idx) in symptomCheckResult.possible_causes" :key="idx">• {{ cause }}</li>
                </ul>
              </div>

              <div v-if="symptomCheckResult.recommendations.length">
                <p class="text-sm font-medium text-gray-600 mb-2">建议措施：</p>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li v-for="(rec, idx) in symptomCheckResult.recommendations" :key="idx">• {{ rec }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 无数据状态 -->
        <div v-if="!dailyAnalysis && !loadingDailyAnalysis" class="card text-center py-16">
          <div class="w-20 h-20 bg-gradient-to-br from-lavender-100 to-lavender-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-10 h-10 text-lavender-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">暂无今日数据</h3>
          <p class="text-gray-500 mb-4">使用设备监测后将自动生成今日解读</p>
          <button @click="loadDailyAnalysis" class="btn btn-primary">
            刷新数据
          </button>
        </div>
      </template>
    </div>

    <!-- 就诊报告 -->
    <div v-else-if="activeTab === 'report'" class="space-y-6">
      <!-- 报告生成控制 -->
      <div class="card">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">就诊报告生成器</h3>
            <p class="text-sm text-gray-500">生成专业的数据摘要，方便与医生沟通</p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center gap-3 bg-warmGray-50 rounded-xl px-4 py-2">
            <span class="text-sm text-gray-600">报告周期:</span>
            <select v-model="reportDays" class="bg-transparent border-none text-sm font-medium text-gray-700 focus:outline-none cursor-pointer">
              <option :value="7">最近7天</option>
              <option :value="14">最近14天</option>
              <option :value="30">最近30天</option>
              <option :value="90">最近3个月</option>
            </select>
          </div>
          <button
            @click="generateDoctorReport"
            :disabled="generatingReport"
            class="btn bg-gradient-to-r from-lavender-500 to-lavender-600 hover:from-lavender-600 hover:to-lavender-700 text-white"
          >
            <svg v-if="generatingReport" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ generatingReport ? '生成中...' : '生成报告' }}
          </button>
        </div>
      </div>

      <!-- 报告内容 -->
      <div v-if="doctorReport" class="space-y-6">
        <!-- 报告头部 -->
        <div class="card">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-xl font-bold text-gray-800">{{ APP_NAME }} - Clinical report</h3>
              <p class="text-sm text-gray-500">
                报告周期：{{ doctorReport.period.start }} 至 {{ doctorReport.period.end }}（共 {{ doctorReport.period.days }} 天）
              </p>
            </div>
            <button
              @click="downloadReportPDF"
              class="btn bg-gradient-to-r from-mint-500 to-mint-600 hover:from-mint-600 hover:to-mint-700 text-white"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              导出 PDF
            </button>
          </div>

          <!-- 患者信息 -->
          <div class="bg-warmGray-50 rounded-xl p-4 mb-6">
            <h4 class="font-medium text-gray-700 mb-3">患者信息</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500">姓名：</span>
                <span class="font-medium">{{ doctorReport.patient_info.name }}</span>
              </div>
              <div v-if="doctorReport.patient_info.age">
                <span class="text-gray-500">年龄：</span>
                <span class="font-medium">{{ doctorReport.patient_info.age }} 岁</span>
              </div>
              <div v-if="doctorReport.patient_info.diagnosis_years">
                <span class="text-gray-500">确诊时长：</span>
                <span class="font-medium">{{ doctorReport.patient_info.diagnosis_years }} 年</span>
              </div>
              <div v-if="doctorReport.patient_info.hoehn_yahr_stage">
                <span class="text-gray-500">H-Y分期：</span>
                <span class="font-medium">{{ doctorReport.patient_info.hoehn_yahr_stage }} 期</span>
              </div>
            </div>
          </div>

          <!-- 执行摘要 -->
          <div>
            <h4 class="font-medium text-gray-700 mb-3">摘要</h4>
            <p class="text-gray-600 leading-relaxed">{{ doctorReport.summary.executive_summary }}</p>
          </div>
        </div>

        <!-- 关键指标 -->
        <div class="card">
          <h4 class="font-semibold text-gray-800 mb-4">关键指标</h4>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div
              v-for="metric in doctorReport.summary.key_metrics"
              :key="metric.metric"
              class="bg-gradient-to-br from-lavender-50 to-warmGray-50 rounded-xl p-4 border border-lavender-100"
            >
              <p class="text-sm text-gray-500 mb-1">{{ metric.metric }}</p>
              <p class="text-xl font-bold text-gray-800">{{ metric.value }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ metric.trend }}</p>
            </div>
          </div>
        </div>

        <!-- 震颤分析 -->
        <div class="card">
          <h4 class="font-semibold text-gray-800 mb-4">震颤数据分析</h4>
          <p class="text-gray-600 mb-4">{{ doctorReport.tremor_analysis.frequency_analysis }}</p>

          <div v-if="doctorReport.tremor_analysis.peak_times.length" class="mb-4">
            <p class="text-sm font-medium text-gray-600 mb-2">高发时段：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="time in doctorReport.tremor_analysis.peak_times"
                :key="time"
                class="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm"
              >
                {{ time }}
              </span>
            </div>
          </div>

          <div v-if="doctorReport.tremor_analysis.notable_patterns.length">
            <p class="text-sm font-medium text-gray-600 mb-2">显著模式：</p>
            <ul class="text-sm text-gray-600 space-y-1">
              <li v-for="(pattern, idx) in doctorReport.tremor_analysis.notable_patterns" :key="idx">
                • {{ pattern }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 用药分析 -->
        <div v-if="doctorReport.medication_analysis" class="card">
          <h4 class="font-semibold text-gray-800 mb-4">用药情况</h4>
          <div v-if="doctorReport.medication_analysis.current_medications.length" class="mb-4">
            <p class="text-sm font-medium text-gray-600 mb-2">当前用药：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="med in doctorReport.medication_analysis.current_medications"
                :key="med"
                class="px-3 py-1 bg-lavender-100 text-lavender-700 rounded-full text-sm"
              >
                {{ med }}
              </span>
            </div>
          </div>
          <p class="text-gray-600 mb-4">{{ doctorReport.medication_analysis.effectiveness_summary }}</p>
          <div v-if="doctorReport.medication_analysis.concerns.length">
            <p class="text-sm font-medium text-amber-600 mb-2">注意事项：</p>
            <ul class="text-sm text-amber-700 space-y-1">
              <li v-for="(concern, idx) in doctorReport.medication_analysis.concerns" :key="idx">
                • {{ concern }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 运动康复分析 -->
        <div v-if="doctorReport.exercise_analysis" class="card">
          <h4 class="font-semibold text-gray-800 mb-4">运动康复情况</h4>
          <div class="grid grid-cols-3 gap-4 mb-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-mint-600">{{ doctorReport.exercise_analysis.compliance_rate }}%</p>
              <p class="text-sm text-gray-500">训练完成率</p>
            </div>
          </div>
          <div v-if="doctorReport.exercise_analysis.observed_benefits.length">
            <p class="text-sm font-medium text-gray-600 mb-2">观察到的改善：</p>
            <ul class="text-sm text-gray-600 space-y-1">
              <li v-for="(benefit, idx) in doctorReport.exercise_analysis.observed_benefits" :key="idx">
                • {{ benefit }}
              </li>
            </ul>
          </div>
        </div>

        <!-- AI 观察 -->
        <div class="card">
          <h4 class="font-semibold text-gray-800 mb-4">AI 观察与建议</h4>
          <ul class="space-y-2">
            <li
              v-for="(obs, idx) in doctorReport.ai_observations"
              :key="idx"
              class="flex items-start gap-3 p-3 bg-lavender-50 rounded-xl"
            >
              <div class="w-6 h-6 bg-lavender-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <span class="text-gray-700">{{ obs }}</span>
            </li>
          </ul>
        </div>

        <!-- 就诊问题建议 -->
        <div v-if="doctorReport.questions_for_doctor.length" class="card">
          <h4 class="font-semibold text-gray-800 mb-4">建议与医生讨论的问题</h4>
          <ul class="space-y-2">
            <li
              v-for="(question, idx) in doctorReport.questions_for_doctor"
              :key="idx"
              class="flex items-start gap-3 p-3 bg-primary-50 rounded-xl"
            >
              <div class="w-6 h-6 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <span class="text-primary-600 text-sm font-medium">{{ idx + 1 }}</span>
              </div>
              <span class="text-gray-700">{{ question }}</span>
            </li>
          </ul>
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
              <p class="font-semibold text-amber-800 mb-1">免责声明</p>
              <p class="text-sm text-amber-700 leading-relaxed">
                本报告由 AI 根据用户数据自动生成，仅供参考，不能作为医学诊断依据。
                所有分析和建议需由专业医生审核确认。请在就诊时将此报告作为参考资料与医生沟通。
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!generatingReport" class="card text-center py-16">
        <div class="w-20 h-20 bg-gradient-to-br from-lavender-100 to-lavender-200 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-lavender-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">生成就诊报告</h3>
        <p class="text-gray-500 mb-4">选择报告周期，生成专业的数据摘要报告</p>
        <p class="text-sm text-gray-400">报告将包含震颤数据分析、用药情况、运动康复情况等信息</p>
      </div>
    </div>

    <!-- 数据分析 -->
    <div v-else-if="activeTab === 'analysis'" class="space-y-6">
      <!-- 分析控制 -->
      <div class="card">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-800">AI 智能分析</h3>
            <p class="text-sm text-gray-500">使用 AI 对您的震颤数据进行深度分析</p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <div class="flex items-center gap-3 bg-warmGray-50 rounded-xl px-4 py-2">
            <span class="text-sm text-gray-600">分析范围:</span>
            <select v-model="analysisDays" class="bg-transparent border-none text-sm font-medium text-gray-700 focus:outline-none cursor-pointer">
              <option :value="7">最近7天</option>
              <option :value="14">最近14天</option>
              <option :value="30">最近30天</option>
            </select>
          </div>
          <button
            @click="runAnalysis"
            :disabled="isAnalyzing"
            class="btn bg-gradient-to-r from-lavender-500 to-lavender-600 hover:from-lavender-600 hover:to-lavender-700 text-white"
          >
            <svg v-if="isAnalyzing" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {{ isAnalyzing ? '分析中...' : '开始分析' }}
          </button>
        </div>
      </div>

      <!-- 分析结果 -->
      <div v-if="analysisResult" class="space-y-6">
        <!-- 风险等级 -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 bg-lavender-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-lavender-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-800">分析结果</h3>
            </div>
            <span
              class="px-4 py-1.5 rounded-full text-sm font-medium"
              :class="getRiskColor(analysisResult.risk_level)"
            >
              风险等级: {{ getRiskLabel(analysisResult.risk_level) }}
            </span>
          </div>
          <p class="text-gray-700 leading-relaxed">{{ analysisResult.summary }}</p>
        </div>

        <!-- 关键发现 -->
        <div class="card">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-800">关键发现</h3>
          </div>
          <ul class="space-y-3">
            <li
              v-for="(finding, index) in analysisResult.key_findings"
              :key="index"
              class="flex items-start gap-3 p-3 bg-primary-50 rounded-xl animate-fade-in-up"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="w-6 h-6 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4" />
                </svg>
              </div>
              <span class="text-gray-700">{{ finding }}</span>
            </li>
          </ul>
        </div>

        <!-- 建议 -->
        <div class="card">
          <div class="flex items-center gap-2 mb-4">
            <div class="w-8 h-8 bg-mint-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-800">建议</h3>
          </div>
          <ul class="space-y-3">
            <li
              v-for="(rec, index) in analysisResult.recommendations"
              :key="index"
              class="flex items-start gap-3 p-3 bg-mint-50 rounded-xl animate-fade-in-up"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="w-6 h-6 bg-mint-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg class="w-4 h-4 text-mint-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span class="text-gray-700">{{ rec }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!isAnalyzing" class="card text-center py-16">
        <div class="w-20 h-20 bg-gradient-to-br from-lavender-100 to-lavender-200 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-lavender-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">开始智能分析</h3>
        <p class="text-gray-500">点击"开始分析"获取 AI 智能分析报告</p>
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
