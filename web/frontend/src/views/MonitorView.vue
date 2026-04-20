<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useTremorStore } from '@/stores/tremor'
import { getSeverityLabel, getSeverityColor } from '@/types'
import AppLayout from '@/layouts/AppLayout.vue'

import { dataApi } from '@/api/data'
import { mockService, mockConfig } from '@/services/mock'
import RealTimeWaveCheck from '@/components/charts/RealTimeWaveCheck.vue'
import { localeDateCode, t } from '@/i18n'

const tremorStore = useTremorStore()

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const deviceId = ref('ESP32_DEFAULT')
const useMock = ref(true) // 默认开启模拟模式
const isMocking = ref(false)

// 图表数据
const waveData = ref<number[]>([]) // 用于绘制波形
const maxChartPoints = 100 // 增加点数以获得更平滑的波形

// 自动刷新
const refreshInterval = ref<number | null>(null)
const refreshRate = 2000 // 2秒刷新一次后端状态

// 计算属性
const isMonitoring = computed(() => {
    return useMock.value ? isMocking.value : tremorStore.currentSession?.is_active ?? false
})

const currentSession = computed(() => tremorStore.currentSession)
const recentData = computed(() => tremorStore.recentData)
const latestReading = computed(() => tremorStore.latestReading)

// 模拟状态下的统计数据
const mockStats = ref({
    duration: 0,
    tremorCount: 0,
    totalAnalyses: 0,
    avgSeverity: 0,
    maxSeverity: 0
})

const sessionStats = computed(() => {
  if (useMock.value) {
      return {
        totalAnalyses: mockStats.value.totalAnalyses,
        tremorCount: mockStats.value.tremorCount,
        detectionRate: mockStats.value.totalAnalyses > 0
          ? ((mockStats.value.tremorCount / mockStats.value.totalAnalyses) * 100).toFixed(1)
          : 0,
        avgSeverity: mockStats.value.avgSeverity.toFixed(2),
        maxSeverity: mockStats.value.maxSeverity,
        duration: mockStats.value.duration
      }
  }

  if (!currentSession.value) {
    return {
      totalAnalyses: 0,
      tremorCount: 0,
      detectionRate: 0,
      avgSeverity: 0,
      maxSeverity: 0,
      duration: 0
    }
  }
  const session = currentSession.value
  return {
    totalAnalyses: session.total_analyses,
    tremorCount: session.tremor_count,
    detectionRate: session.total_analyses > 0
      ? ((session.tremor_count / session.total_analyses) * 100).toFixed(1)
      : 0,
    avgSeverity: session.avg_severity?.toFixed(2) || 0,
    maxSeverity: session.max_severity,
    duration: session.duration_seconds || 0
  }
})

const currentSeverity = computed(() => {
  if (useMock.value) {
      // 模拟模式下根据波形振幅判断
      const lastVal = Math.abs(waveData.value[waveData.value.length - 1] || 0)
      if (lastVal > 1.5) return 4
      if (lastVal > 1.0) return 3
      if (lastVal > 0.5) return 2
      if (lastVal > 0.2) return 1
      return 0
  }

  if (!latestReading.value || !latestReading.value.detected) return 0
  return latestReading.value.severity
})

const currentFrequency = computed(() => {
  if (useMock.value) return mockConfig.tremorFrequency
  if (!latestReading.value) return null
  return latestReading.value.frequency
})

const currentAmplitude = computed(() => {
   if (useMock.value) {
       return Math.abs(waveData.value[waveData.value.length - 1] || 0)
   }
  if (!latestReading.value) return null
  return latestReading.value.rms_amplitude
})

// 方法
async function startMonitoring() {
  if (useMock.value) {
      isMocking.value = true
      startMockSimulation()
      return
  }

  loading.value = true
  error.value = null

  try {
    await tremorStore.startSession(deviceId.value)
    tremorStore.clearRecentData()
    waveData.value = []
    startAutoRefresh()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '启动监测失败'
  } finally {
    loading.value = false
  }
}

async function stopMonitoring() {
  if (useMock.value) {
      isMocking.value = false
      stopMockSimulation()
      return
  }

  if (!currentSession.value) return

  loading.value = true
  error.value = null

  try {
    stopAutoRefresh()
    await tremorStore.endSession(currentSession.value.id)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '停止监测失败'
  } finally {
    loading.value = false
  }
}

function toggleMonitoring() {
  if (isMonitoring.value) {
    stopMonitoring()
  } else {
    startMonitoring()
  }
}

// 模拟相关逻辑
let mockTimer: number | null = null
function startMockSimulation() {
    waveData.value = new Array(maxChartPoints).fill(0)
    mockStats.value = { duration: 0, tremorCount: 0, totalAnalyses: 0, avgSeverity: 0, maxSeverity: 0 }
    
    // 启动 service 模拟
    mockService.startSimulation((data) => {
        // 更新波形数据
        waveData.value.push(data.amplitude || 0)
        if (waveData.value.length > maxChartPoints) {
            waveData.value.shift()
        }

        // 更新统计 (低频更新，避免刷新过快)
        mockStats.value.totalAnalyses++
        if (data.detected) mockStats.value.tremorCount++
        
        // 移动平均严重度
        const n = mockStats.value.totalAnalyses
        const prevAvg = mockStats.value.avgSeverity
        mockStats.value.avgSeverity = prevAvg + (data.severity - prevAvg) / n
        
        mockStats.value.maxSeverity = Math.max(mockStats.value.maxSeverity, data.severity)
        
        // 模拟最近记录 (每20次数据点存一次，即每秒1条)
        if (mockStats.value.totalAnalyses % 20 === 0) {
            const record = { ...data, id: Date.now() } // ensure unique key
            tremorStore.recentData.unshift(record)
            if (tremorStore.recentData.length > 50) tremorStore.recentData.pop()
        }
    })

    // 计时器
    mockTimer = window.setInterval(() => {
        mockStats.value.duration++
    }, 1000)
}

function stopMockSimulation() {
    mockService.stopSimulation()
    if (mockTimer) clearInterval(mockTimer)
}

// 模拟配置控制
function setMockTremor(level: number) {
    if (level === 0) {
        mockConfig.tremorIntensity = 0
    } else {
        // 简单映射：1级=0.2, 2级=0.4, 3级=0.6, 4级=0.8
        mockConfig.tremorIntensity = level * 0.2
    }
}

async function refreshData() {
  if (!currentSession.value) return

  try {
    const session = await dataApi.getSession(currentSession.value.id)
    tremorStore.setCurrentSession(session)

    const data = await dataApi.getSessionData(currentSession.value.id, 50)
    tremorStore.recentData = data
    
    // 更新真实数据的图表
    const points = data.slice().reverse().map(d => d.rms_amplitude || 0)
    while (points.length < maxChartPoints) points.unshift(0)
    waveData.value = points.slice(-maxChartPoints)

  } catch (e) {
    console.error('刷新数据失败:', e)
  }
}

function startAutoRefresh() {
  if (refreshInterval.value) return
  refreshInterval.value = window.setInterval(refreshData, refreshRate)
}

function stopAutoRefresh() {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleTimeString(localeDateCode(), {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function formatDuration(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 生命周期
onMounted(async () => {
  // 默认开启模拟
  if (useMock.value) {
      // Do nothing
  } else {
      try {
        const sessions = await dataApi.getHistory({ limit: 1 })
        const activeSession = sessions.find(s => s.is_active)
        if (activeSession) {
          tremorStore.setCurrentSession(activeSession)
          await refreshData()
          startAutoRefresh()
        }
      } catch (e) {
        console.error('获取会话失败:', e)
      }
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  stopMockSimulation()
})

watch(isMonitoring, (newVal) => {
  if (!useMock.value) {
      if (newVal) {
        startAutoRefresh()
      } else {
        stopAutoRefresh()
      }
  }
})
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('monitor.title') }}</h1>
          <p class="text-gray-500 mt-1">{{ t('monitor.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-4">
             <!-- 模式切换 -->
             <div class="flex items-center gap-2 bg-white rounded-lg p-1 border border-warmGray-200 shadow-sm">
                <button 
                    @click="useMock = true"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                    :class="useMock ? 'bg-primary-100 text-primary-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                    {{ t('common.demoMode') }}
                </button>
                <div class="w-px h-4 bg-warmGray-200"></div>
                <button 
                    @click="useMock = false"
                    class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                    :class="!useMock ? 'bg-primary-100 text-primary-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                >
                    Real device
                </button>
            </div>

          <span class="badge" :class="isMonitoring ? 'badge-success' : 'bg-warmGray-200 text-gray-600'">
            <span v-if="isMonitoring" class="w-2 h-2 bg-mint-500 rounded-full animate-pulse mr-1.5"></span>
            {{ isMonitoring ? 'Live' : 'Idle' }}
          </span>
        </div>
      </div>

      <!-- 错误提示 -->
      <Transition name="fade-up">
        <div v-if="error" class="alert alert-error">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="flex-1">{{ error }}</span>
          <button @click="error = null" class="btn btn-ghost btn-sm !p-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </Transition>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：控制面板 + 当前状态 -->
        <div class="space-y-6">
          <!-- 控制面板 -->
          <div class="card text-center !p-8">
            <!-- 监测状态圆环 -->
            <div class="relative w-40 h-40 mx-auto mb-6">
              <!-- 外层光环 -->
              <div
                v-if="isMonitoring"
                class="absolute inset-0 rounded-full border-4 border-mint-400 animate-pulse-ring"
              ></div>
              <div
                v-if="isMonitoring"
                class="absolute inset-0 rounded-full border-4 border-mint-400 animate-pulse-ring"
                style="animation-delay: 1s;"
              ></div>

              <!-- 主圆环 -->
              <div
                class="absolute inset-4 rounded-full flex items-center justify-center transition-all duration-500"
                :class="isMonitoring
                  ? 'bg-gradient-to-br from-mint-400 to-mint-500 shadow-glow'
                  : 'bg-warmGray-100'"
              >
                <svg
                  class="w-16 h-16 transition-colors"
                  :class="isMonitoring ? 'text-white' : 'text-warmGray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>

            <h2 class="text-2xl font-bold text-gray-800 mb-2">
              {{ isMonitoring ? 'Live session active' : 'Ready to monitor' }}
            </h2>
            <p class="text-gray-500 mb-8">
              {{ isMonitoring ? (useMock ? 'Generating stable demo data…' : 'Receiving live device data…') : 'Start a session to view real-time signal tracking.' }}
            </p>

            <button
              @click="toggleMonitoring"
              :disabled="loading"
              class="btn btn-lg w-full"
              :class="isMonitoring ? 'btn-danger' : 'btn-primary'"
            >
              <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <span v-if="loading">Working...</span>
              <template v-else>
                <svg v-if="!isMonitoring" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
                <span>{{ isMonitoring ? t('monitor.stop') : t('monitor.start') }}</span>
              </template>
            </button>
            
            <!-- 模拟控制 -->
            <transition name="fade-up">
                <div v-if="useMock && isMonitoring" class="mt-6 pt-6 border-t border-warmGray-100">
                    <p class="text-sm font-medium text-gray-500 mb-3">{{ t('monitor.mockPreset') }}</p>
                    <div class="flex justify-center gap-2">
                        <button v-for="level in 5" :key="level-1"
                            @click="setMockTremor(level-1)" 
                            class="w-9 h-9 rounded-full font-bold transition-transform active:scale-95 border-2"
                            :class="{
                                'bg-green-100 text-green-700 border-green-200 hover:bg-green-200': level-1 === 0,
                                'bg-lime-100 text-lime-700 border-lime-200 hover:bg-lime-200': level-1 === 1,
                                'bg-yellow-100 text-yellow-700 border-yellow-200 hover:bg-yellow-200': level-1 === 2,
                                'bg-orange-100 text-orange-700 border-orange-200 hover:bg-orange-200': level-1 === 3,
                                'bg-red-100 text-red-700 border-red-200 hover:bg-red-200': level-1 === 4
                            }"
                        >
                            {{ level-1 }}
                        </button>
                    </div>
                </div>
            </transition>

            <p class="text-sm text-gray-400 mt-4 flex items-center justify-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              {{ t('monitor.deviceId') }}: {{ deviceId }}
            </p>
          </div>

          <!-- 当前严重度 -->
          <div class="card">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Current signal</h3>

            <div class="text-center mb-6">
              <div
                class="w-28 h-28 rounded-full mx-auto flex items-center justify-center text-4xl font-bold text-white shadow-soft transition-all duration-300"
                :style="{ backgroundColor: getSeverityColor(currentSeverity) }"
              >
                {{ currentSeverity }}
              </div>
              <p class="mt-4 text-lg font-semibold" :style="{ color: getSeverityColor(currentSeverity) }">
                {{ getSeverityLabel(currentSeverity) }}
              </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="card-flat !p-4 text-center">
                <p class="text-sm text-gray-500 mb-1">{{ t('monitor.currentFrequency') }}</p>
                <p class="text-xl font-bold text-gray-800">
                  {{ currentFrequency ? `${currentFrequency.toFixed(2)}` : '-' }}
                  <span class="text-sm font-normal text-gray-500">Hz</span>
                </p>
              </div>
              <div class="card-flat !p-4 text-center">
                <p class="text-sm text-gray-500 mb-1">{{ t('monitor.currentAmplitude') }}</p>
                <p class="text-xl font-bold text-gray-800">
                  {{ currentAmplitude ? `${currentAmplitude.toFixed(3)}` : '-' }}
                  <span class="text-sm font-normal text-gray-500">g</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：图表 + 数据列表 -->
        <div class="lg:col-span-2 space-y-6">
          <!-- 会话统计 -->
          <Transition name="fade-up">
            <div v-if="isMonitoring" class="card-gradient">
              <h3 class="text-lg font-bold text-gray-800 mb-4">{{ t('monitor.sessionStats') }}</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-white/50 rounded-xl">
                  <p class="text-sm text-gray-500 mb-1">{{ t('monitor.duration') }}</p>
                  <p class="text-2xl font-bold text-gray-800">{{ formatDuration(sessionStats.duration) }}</p>
                </div>
                <div class="text-center p-4 bg-white/50 rounded-xl">
                  <p class="text-sm text-gray-500 mb-1">{{ t('monitor.analyses') }}</p>
                  <p class="text-2xl font-bold text-primary-600">{{ sessionStats.totalAnalyses }}</p>
                </div>
                <div class="text-center p-4 bg-white/50 rounded-xl">
                  <p class="text-sm text-gray-500 mb-1">{{ t('monitor.tremorEvents') }}</p>
                  <p class="text-2xl font-bold text-orange-500">{{ sessionStats.tremorCount }}</p>
                </div>
                <div class="text-center p-4 bg-white/50 rounded-xl">
                  <p class="text-sm text-gray-500 mb-1">{{ t('monitor.detectionRate') }}</p>
                  <p class="text-2xl font-bold text-gray-800">{{ sessionStats.detectionRate }}%</p>
                </div>
              </div>
            </div>
          </Transition>

          <!-- 波形图 -->
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold text-gray-800">Real-time acceleration</h3>
              <span class="badge badge-primary">Live</span>
            </div>
            
            <RealTimeWaveCheck 
                :data-points="waveData" 
                :color="isMonitoring ? getSeverityColor(currentSeverity) : '#9CA3AF'"
                :height="300"
            />
          </div>

          <!-- 最近数据列表 -->
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold text-gray-800">{{ t('monitor.recentReadings') }}</h3>
              <span class="text-sm text-gray-500">{{ recentData.length }} entries</span>
            </div>

            <div class="table-container !shadow-none">
              <table class="table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Frequency</th>
                    <th>Amplitude</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(data, index) in recentData.slice(0, 10)"
                    :key="data.id"
                    class="animate-fade-in-up"
                    :style="{ animationDelay: `${index * 30}ms` }"
                  >
                    <td class="font-medium">{{ formatTime(data.timestamp) }}</td>
                    <td>
                      <span
                        :class="[
                          'badge',
                          data.detected ? 'badge-warning' : 'badge-success'
                        ]"
                      >
                        {{ data.detected ? 'Tremor' : 'Stable' }}
                      </span>
                    </td>
                    <td>{{ data.frequency?.toFixed(2) || '-' }} Hz</td>
                    <td>{{ data.rms_amplitude?.toFixed(3) || '-' }} g</td>
                    <td>
                      <span class="severity-badge" :class="`severity-${data.severity}`">
                        {{ getSeverityLabel(data.severity) }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="recentData.length === 0">
                    <td colspan="5" class="!py-12 text-center">
                      <div class="text-gray-400">
                        <svg class="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                        <p>{{ t('monitor.noReadings') }}</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.animate-pulse-ring {
  animation: pulseRing 2s ease-out infinite;
}

@keyframes pulseRing {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}
</style>
