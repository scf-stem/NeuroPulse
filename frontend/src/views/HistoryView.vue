<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useTremorStore } from '@/stores/tremor'
import { getSeverityLabel } from '@/types'
import AppLayout from '@/layouts/AppLayout.vue'
import type { TremorSession, TremorData } from '@/types'
import { dataApi } from '@/api/data'
import { formatDate as formatLocaleDate, formatDateTime as formatLocaleDateTime, localeText } from '@/i18n'

const tremorStore = useTremorStore()

const loading = ref(true)
const selectedSession = ref<TremorSession | null>(null)
const sessionData = ref<TremorData[]>([])
const loadingData = ref(false)
const showModal = ref(false)

// 筛选条件
const dateRange = ref({
  start: '',
  end: ''
})

// 分页
const currentPage = ref(1)
const pageSize = 20

const sessions = computed(() => tremorStore.sessions)

const paginatedSessions = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sessions.value.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(sessions.value.length / pageSize))

onMounted(async () => {
  loading.value = true
  try {
    await tremorStore.fetchSessions(100)
  } finally {
    loading.value = false
  }
})

async function viewSession(session: TremorSession) {
  selectedSession.value = session
  loadingData.value = true
  showModal.value = true

  try {
    sessionData.value = await dataApi.getSessionData(session.id, 200)
  } finally {
    loadingData.value = false
  }
}

function closeModal() {
  showModal.value = false
  selectedSession.value = null
  sessionData.value = []
}

function formatDate(dateStr: string) {
  return formatLocaleDate(dateStr, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

function formatTime(dateStr: string) {
  return formatLocaleDateTime(dateStr, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function formatDuration(seconds: number | undefined | null) {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return localeText(`${mins}m ${secs}s`, `${mins}分${secs}秒`)
}

async function applyFilter() {
  loading.value = true
  try {
    await dataApi.getHistory({
      startDate: dateRange.value.start || undefined,
      endDate: dateRange.value.end || undefined,
      limit: 100
    }).then(data => {
      tremorStore.sessions = data
    })
  } finally {
    loading.value = false
  }
}

function clearFilter() {
  dateRange.value = { start: '', end: '' }
  tremorStore.fetchSessions(100)
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 计算检出率
function getDetectionRate(session: TremorSession) {
  if (session.total_analyses === 0) return 0
  return ((session.tremor_count / session.total_analyses) * 100).toFixed(1)
}
</script>

<template>
  <AppLayout>
    <!-- 页面标题 -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">历史记录</h1>
          <p class="text-gray-500 text-sm">查看所有检测会话记录</p>
        </div>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="card mb-6">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        <span class="font-medium text-gray-700">筛选条件</span>
      </div>
      <div class="flex flex-wrap gap-4 items-end">
        <div>
          <label class="block text-sm text-gray-600 mb-1.5">开始日期</label>
          <input
            v-model="dateRange.start"
            type="date"
            class="input"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1.5">结束日期</label>
          <input
            v-model="dateRange.end"
            type="date"
            class="input"
          />
        </div>
        <button @click="applyFilter" class="btn btn-primary">
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          筛选
        </button>
        <button @click="clearFilter" class="btn btn-ghost">
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          重置
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center h-64">
      <div class="relative">
        <div class="w-16 h-16 border-4 border-primary-200 rounded-full"></div>
        <div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
      </div>
      <p class="text-gray-500 mt-4">加载记录中...</p>
    </div>

    <!-- 会话列表 -->
    <template v-else>
      <!-- 空状态 -->
      <div v-if="sessions.length === 0" class="card text-center py-16">
        <div class="w-20 h-20 bg-gradient-to-br from-warmGray-100 to-warmGray-200 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">暂无检测记录</h3>
        <p class="text-gray-500">开始监测后，数据将显示在这里</p>
        <RouterLink to="/monitor" class="btn btn-primary mt-6 inline-flex">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          开始监测
        </RouterLink>
      </div>

      <!-- 数据表格 -->
      <div v-else class="card !p-0 overflow-hidden">
        <!-- 表格头部统计 -->
        <div class="bg-gradient-to-r from-primary-50 to-warmGray-50 px-6 py-4 border-b border-warmGray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 bg-primary-500 rounded-full"></div>
              <span class="text-gray-700 font-medium">共 {{ sessions.length }} 条记录</span>
            </div>
            <div class="text-sm text-gray-500">
              显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, sessions.length) }} 条
            </div>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="table">
            <thead>
              <tr>
                <th>日期</th>
                <th>开始时间</th>
                <th>时长</th>
                <th>检测次数</th>
                <th>震颤次数</th>
                <th>检出率</th>
                <th>最高严重度</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(session, index) in paginatedSessions"
                :key="session.id"
                class="animate-fade-in-up"
                :style="{ animationDelay: `${index * 30}ms` }"
              >
                <td>
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span class="font-medium">{{ formatDate(session.start_time) }}</span>
                  </div>
                </td>
                <td class="text-gray-600">{{ formatTime(session.start_time) }}</td>
                <td class="text-gray-600">{{ formatDuration(session.duration_seconds) }}</td>
                <td>
                  <span class="font-medium text-gray-800">{{ session.total_analyses }}</span>
                </td>
                <td>
                  <span class="font-medium" :class="session.tremor_count > 0 ? 'text-amber-600' : 'text-gray-600'">
                    {{ session.tremor_count }}
                  </span>
                </td>
                <td>
                  <div class="flex items-center gap-2">
                    <div class="w-16 h-2 bg-warmGray-200 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all duration-500"
                        :class="Number(getDetectionRate(session)) > 50 ? 'bg-amber-500' : 'bg-primary-500'"
                        :style="{ width: `${getDetectionRate(session)}%` }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium text-gray-700">{{ getDetectionRate(session) }}%</span>
                  </div>
                </td>
                <td>
                  <span class="severity-badge" :class="`severity-${session.max_severity}`">
                    {{ getSeverityLabel(session.max_severity) }}
                  </span>
                </td>
                <td>
                  <span
                    :class="[
                      'badge',
                      session.is_active ? 'badge-success' : 'badge-secondary'
                    ]"
                  >
                    <span v-if="session.is_active" class="w-1.5 h-1.5 bg-current rounded-full mr-1.5 animate-pulse"></span>
                    {{ session.is_active ? '进行中' : '已完成' }}
                  </span>
                </td>
                <td>
                  <button
                    @click="viewSession(session)"
                    class="btn btn-ghost !py-1.5 !px-3 text-sm"
                  >
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    查看
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="flex items-center justify-between px-6 py-4 border-t border-warmGray-200 bg-warmGray-50">
          <p class="text-sm text-gray-500">
            共 {{ sessions.length }} 条记录，{{ totalPages }} 页
          </p>
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="pagination-btn"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <template v-for="page in totalPages" :key="page">
              <button
                v-if="page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)"
                @click="goToPage(page)"
                :class="['pagination-btn', page === currentPage && 'active']"
              >
                {{ page }}
              </button>
              <span
                v-else-if="page === currentPage - 2 || page === currentPage + 2"
                class="text-gray-400"
              >
                ...
              </span>
            </template>

            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="pagination-btn"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- 会话详情模态框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showModal"
          class="modal-overlay"
          @click.self="closeModal"
        >
          <div class="modal max-w-4xl">
            <!-- 模态框头部 -->
            <div class="modal-header">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-800">会话详情</h3>
                  <p class="text-sm text-gray-500" v-if="selectedSession">
                    {{ formatDate(selectedSession.start_time) }} {{ formatTime(selectedSession.start_time) }}
                  </p>
                </div>
              </div>
              <button @click="closeModal" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- 会话统计 -->
            <div v-if="selectedSession" class="px-6 py-4 bg-gradient-to-r from-primary-50 to-warmGray-50 border-b">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-3 bg-white/60 rounded-xl">
                  <p class="text-xs text-gray-500 mb-1">开始时间</p>
                  <p class="font-semibold text-gray-800">{{ formatTime(selectedSession.start_time) }}</p>
                </div>
                <div class="text-center p-3 bg-white/60 rounded-xl">
                  <p class="text-xs text-gray-500 mb-1">时长</p>
                  <p class="font-semibold text-gray-800">{{ formatDuration(selectedSession.duration_seconds) }}</p>
                </div>
                <div class="text-center p-3 bg-white/60 rounded-xl">
                  <p class="text-xs text-gray-500 mb-1">震颤检出率</p>
                  <p class="font-semibold text-primary-600">{{ getDetectionRate(selectedSession) }}%</p>
                </div>
                <div class="text-center p-3 bg-white/60 rounded-xl">
                  <p class="text-xs text-gray-500 mb-1">平均严重度</p>
                  <p class="font-semibold text-gray-800">{{ selectedSession.avg_severity?.toFixed(2) || '-' }}</p>
                </div>
              </div>
            </div>

            <!-- 数据列表 -->
            <div class="modal-body max-h-[50vh] overflow-auto">
              <div v-if="loadingData" class="flex flex-col items-center justify-center py-12">
                <div class="relative">
                  <div class="w-12 h-12 border-4 border-primary-200 rounded-full"></div>
                  <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
                </div>
                <p class="text-gray-500 mt-3 text-sm">加载数据中...</p>
              </div>

              <div v-else-if="sessionData.length === 0" class="text-center py-12">
                <div class="w-16 h-16 bg-warmGray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <p class="text-gray-500">暂无详细数据</p>
              </div>

              <table v-else class="table text-sm">
                <thead class="sticky top-0 bg-white z-10">
                  <tr>
                    <th>时间</th>
                    <th>检测结果</th>
                    <th>频率 (Hz)</th>
                    <th>RMS (g)</th>
                    <th>严重度</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(data, index) in sessionData"
                    :key="data.id"
                    class="animate-fade-in-up"
                    :style="{ animationDelay: `${index * 20}ms` }"
                  >
                    <td class="text-gray-600">{{ formatTime(data.timestamp) }}</td>
                    <td>
                      <span
                        :class="[
                          'badge',
                          data.detected ? 'badge-warning' : 'badge-success'
                        ]"
                      >
                        {{ data.detected ? '检测到震颤' : '正常' }}
                      </span>
                    </td>
                    <td class="font-mono text-gray-700">{{ data.frequency?.toFixed(2) || '-' }}</td>
                    <td class="font-mono text-gray-700">{{ data.rms_amplitude?.toFixed(3) || '-' }}</td>
                    <td>
                      <span class="severity-badge text-xs" :class="`severity-${data.severity}`">
                        {{ getSeverityLabel(data.severity) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 模态框底部 -->
            <div class="modal-footer">
              <button @click="closeModal" class="btn btn-secondary">
                关闭
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AppLayout>
</template>

<style scoped>
.pagination-btn {
  @apply w-9 h-9 flex items-center justify-center rounded-xl text-sm font-medium
         text-gray-600 bg-white border border-warmGray-200
         hover:bg-primary-50 hover:border-primary-200 hover:text-primary-600
         disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-warmGray-200 disabled:hover:text-gray-600
         transition-all duration-200;
}

.pagination-btn.active {
  @apply bg-gradient-to-r from-primary-500 to-primary-600 text-white border-transparent shadow-soft;
}

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
