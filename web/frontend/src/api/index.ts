/**
 * Tremor Guard - API Client
 * 震颤卫士 - API 客户端
 */

import axios from 'axios'
import type { AxiosInstance } from 'axios'

import {
  demoDailyAnalysis,
  demoDevices,
  demoDoctorReport,
  demoDoctorSummary,
  demoGeneratedReport,
  demoPersonalizedAdvice,
  demoQuickStats,
  demoRehabExercises,
  demoRehabPlan,
  demoRehabStats,
  demoSymptomCheck,
  demoTodayExercises,
} from '@/demo/data'
import { DEMO_TOKEN, demoUser } from '@/demo'
import { currentLocale } from '@/i18n'
import { pinia } from '@/stores'
import { useSessionStore } from '@/stores/session'

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function demoResponse(config: any, data: unknown, status = 200) {
  return Promise.resolve({
    data,
    status,
    statusText: 'OK',
    headers: {},
    config,
    request: {},
  })
}

function maybeAttachDemoAdapter(config: any, demoMode: boolean) {
  if (!demoMode) {
    return config
  }

  const method = (config.method || 'get').toLowerCase()
  const url = String(config.url || '')

  // 这些 AI 接口在 demo 模式下也走真实后端，以便访问真实千问。
  const realAiEndpoints = new Set([
    '/ai/chat',
    '/ai/analyze',
    '/ai/insights',
    '/ai/health-tips',
  ])

  if (realAiEndpoints.has(url)) {
    return config
  }

  if (url === '/auth/login' || url === '/auth/register' || url === '/auth/refresh') {
    config.adapter = () =>
      demoResponse(config, {
        access_token: DEMO_TOKEN,
        token_type: 'bearer',
        expires_in: 3600,
        user: demoUser,
      })
    return config
  }

  if (url === '/auth/me') {
    config.adapter = () => demoResponse(config, demoUser)
    return config
  }

  if (url === '/auth/logout') {
    config.adapter = () => demoResponse(config, { message: 'Logged out' })
    return config
  }

  if (url === '/device/list') {
    config.adapter = () => demoResponse(config, demoDevices)
    return config
  }

  if (url === '/device/register' && method === 'post') {
    config.adapter = async () => {
      const payload = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      const created = {
        ...demoDevices[0],
        id: 99,
        device_id: payload.device_id,
        name: payload.name || 'New Demo Device',
      }
      return demoResponse(config, created, 201)
    }
    return config
  }

  if (url.startsWith('/device/') && method === 'put') {
    config.adapter = async () => {
      const payload = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      return demoResponse(config, { ...demoDevices[0], name: payload.name || demoDevices[0].name })
    }
    return config
  }

  if (url.startsWith('/device/') && method === 'delete') {
    config.adapter = () => demoResponse(config, null, 204)
    return config
  }

  if (url === '/report/quick-stats') {
    config.adapter = () => demoResponse(config, demoQuickStats)
    return config
  }

  if (url === '/report/summary/doctor') {
    config.adapter = () => demoResponse(config, demoDoctorSummary)
    return config
  }

  if (url === '/report/generate') {
    config.adapter = () => demoResponse(config, demoGeneratedReport)
    return config
  }

  if (url === '/ai/actions/rehab-plan/confirm') {
    config.adapter = () =>
      demoResponse(config, {
        message: '康复训练计划已生成并同步到康复训练页面。',
        route: '/rehabilitation',
        action_card: {
          kind: 'rehab_plan',
          title: 'AI康复训练计划',
          summary: '已生成演示训练计划，总目标时长 30 分钟。',
          status: 'generated',
          actions: [
            { type: 'view_rehab_page', label: '查看康复计划', route: '/rehabilitation' },
            { type: 'download_rehab_pdf', label: '下载 PDF', api_path: '/api/ai/actions/rehab-plan/1/pdf' },
          ],
        },
      })
    return config
  }

  if (url === '/ai/actions/health-report/confirm') {
    config.adapter = () =>
      demoResponse(config, {
        message: 'AI 健康报告已生成并同步到报告页面。',
        route: '/reports',
        report_data: demoGeneratedReport,
        action_card: {
          kind: 'health_report',
          title: 'AI健康报告',
          summary: '已生成演示健康报告，可在线查看或下载 PDF。',
          status: 'generated',
          actions: [
            { type: 'view_health_report', label: '查看报告页面', route: '/reports' },
            { type: 'download_health_report_pdf', label: '下载 PDF', api_path: '/api/ai/actions/health-report/demo/pdf' },
          ],
        },
      })
    return config
  }

  if (url.startsWith('/ai/actions/rehab-plan/') && url.endsWith('/pdf')) {
    config.adapter = () => demoResponse(config, new Blob(['demo pdf'], { type: 'application/pdf' }))
    return config
  }

  if (url.startsWith('/ai/actions/health-report/') && url.endsWith('/pdf')) {
    config.adapter = () => demoResponse(config, new Blob(['demo pdf'], { type: 'application/pdf' }))
    return config
  }

  if (url === '/ai/daily-analysis' || url === '/ai/daily-analysis/refresh') {
    config.adapter = () => demoResponse(config, demoDailyAnalysis)
    return config
  }

  if (url === '/ai/personalized-advice' || url === '/ai/personalized-advice/refresh') {
    config.adapter = () => demoResponse(config, demoPersonalizedAdvice)
    return config
  }

  if (url.startsWith('/ai/personalized-advice/') && url.endsWith('/action')) {
    config.adapter = () => demoResponse(config, null, 204)
    return config
  }

  if (url === '/ai/doctor-report') {
    config.adapter = () => demoResponse(config, demoDoctorReport)
    return config
  }

  if (url === '/ai/doctor-reports') {
    config.adapter = () =>
      demoResponse(config, [
        {
          report_id: demoDoctorReport.report_id,
          generated_at: demoDoctorReport.generated_at,
          period_start: demoDoctorReport.period.start,
          period_end: demoDoctorReport.period.end,
        },
      ])
    return config
  }

  if (url.startsWith('/ai/doctor-reports/')) {
    config.adapter = () => demoResponse(config, demoDoctorReport)
    return config
  }

  if (url === '/ai/symptom-check') {
    config.adapter = () => demoResponse(config, demoSymptomCheck)
    return config
  }

  if (url === '/rehabilitation/exercises') {
    config.adapter = () => demoResponse(config, demoRehabExercises)
    return config
  }

  if (url === '/rehabilitation/exercises/recommended') {
    config.adapter = () => demoResponse(config, demoRehabExercises.slice(0, 2))
    return config
  }

  if (url === '/rehabilitation/plans') {
    config.adapter = () => demoResponse(config, [demoRehabPlan])
    return config
  }

  if (url === '/rehabilitation/plans/active') {
    config.adapter = () => demoResponse(config, demoRehabPlan)
    return config
  }

  if (url === '/rehabilitation/plans/today') {
    config.adapter = () => demoResponse(config, demoTodayExercises)
    return config
  }

  if (url === '/rehabilitation/stats') {
    config.adapter = () => demoResponse(config, demoRehabStats)
    return config
  }

  if (url === '/rehabilitation/check-ins/today') {
    config.adapter = () => demoResponse(config, null, 404)
    return config
  }

  if (url === '/rehabilitation/check-ins') {
    config.adapter = () => demoResponse(config, [])
    return config
  }

  if (url === '/rehabilitation/plans' && method === 'post') {
    config.adapter = async () => {
      const payload = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      return demoResponse(
        config,
        {
          ...demoRehabPlan,
          ...payload,
          id: 2,
          user_id: demoUser.id,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        201
      )
    }
    return config
  }

  if (url.includes('/rehabilitation/plans/') && method === 'put') {
    config.adapter = async () => {
      const payload = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      return demoResponse(config, { ...demoRehabPlan, ...payload })
    }
    return config
  }

  if (url.includes('/rehabilitation/plans/') && method === 'delete') {
    config.adapter = () => demoResponse(config, null, 204)
    return config
  }

  if (url.includes('/rehabilitation/plans/') && url.endsWith('/activate')) {
    config.adapter = () => demoResponse(config, demoRehabPlan)
    return config
  }

  if (url === '/rehabilitation/check-ins' && method === 'post') {
    config.adapter = async () => {
      const payload = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      return demoResponse(config, { id: 1, user_id: demoUser.id, created_at: new Date().toISOString(), ...payload }, 201)
    }
    return config
  }

  if (url === '/data/stats/today') {
    config.adapter = () =>
      demoResponse(config, {
        date: '2026-04-18',
        total_sessions: 4,
        total_analyses: 42,
        tremor_detections: 11,
        detection_rate: 26.1,
        avg_severity: 1.6,
        max_severity: 3,
      })
    return config
  }

  return config
}

// 请求拦截器 - 添加认证 token
apiClient.interceptors.request.use(
  (config) => {
    const sessionStore = useSessionStore(pinia)
    sessionStore.bootstrap()

    config.headers = config.headers ?? {}

    if (sessionStore.token) {
      config.headers.Authorization = `Bearer ${sessionStore.token}`
    } else if ('Authorization' in config.headers) {
      delete config.headers.Authorization
    }

    config.headers['Accept-Language'] = currentLocale.value
    return maybeAttachDemoAdapter(config, sessionStore.isDemo)
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      if (error.config.url?.includes('/auth/login')) {
        return Promise.reject(error)
      }

      const sessionStore = useSessionStore(pinia)
      const { redirectToLogin, redirectPath } = sessionStore.invalidateRealSession()

      if (redirectToLogin) {
        const router = (await import('@/router')).default
        await router.push({
          name: 'login',
          query: redirectPath ? { redirect: redirectPath } : undefined,
        })
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
