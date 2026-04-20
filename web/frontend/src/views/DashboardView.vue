<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import { mockService } from '@/services/mock'
import { getSeverityLabel, getSeverityColor } from '@/types'
import { t, tList } from '@/i18n'

const loading = ref(true)

// Mock Data
const stats = ref({
    todayAnalyses: 12,
    todayTremors: 45,
    avgSeverity: 1.8,
    maxSeverity: 3,
    detectionRate: 25,
    totalSessions: 4
})

const trendData = ref<{ labels: string[], severity: number[], counts: number[] }>({
    labels: [], severity: [], counts: []
})

const recentSessions = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  const sessionMinutes = tList('dashboard.sessionMinutes')
  
  // Simulate API delay
  setTimeout(() => {
      // Load Trend Data
      const history = mockService.generateTrendData(7)
      trendData.value.labels = history.map(d => {
          const date = new Date(d.date)
          return `${date.getMonth()+1}-${date.getDate()}`
      })
      trendData.value.severity = history.map(d => d.avg_severity)
      trendData.value.counts = history.map(d => d.tremor_count)
      
      // Load Recent Sessions
      recentSessions.value = [
          { id: 1, start: '14:30', duration: sessionMinutes[0] || '15 min', tremors: 12, maxSeverity: 2, isActive: false },
          { id: 2, start: '10:15', duration: sessionMinutes[1] || '20 min', tremors: 5, maxSeverity: 1, isActive: false },
          { id: 3, start: '08:45', duration: sessionMinutes[2] || '10 min', tremors: 28, maxSeverity: 3, isActive: false },
      ]
      
      loading.value = false
  }, 600)
})

</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      
      <!-- Welcome Header -->
      <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-800">{{ t('dashboard.greeting') }}</h1>
            <p class="text-gray-500 mt-1">{{ t('dashboard.subtitle') }}</p>
          </div>
          <div class="text-right hidden md:block">
              <p class="text-sm text-gray-500">{{ t('dashboard.lastSync') }}</p>
              <p class="font-medium text-gray-700">{{ t('dashboard.justNow') }}</p>
          </div>
      </div>

      <div v-if="loading" class="flex items-center justify-center h-64">
        <!-- Keep loading state simple -->
        <div class="text-center text-gray-500">{{ t('common.loading') }}</div>
      </div>

      <template v-else>
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <!-- Today's Analyses -->
          <div class="card-gradient group">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-gray-500 text-sm font-medium">{{ t('dashboard.todayAnalyses') }}</p>
                <p class="text-4xl font-bold text-gray-800 mt-2">{{ stats.todayAnalyses }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="badge badge-primary">
                    {{ stats.totalSessions }} {{ t('dashboard.sessions') }}
                  </span>
                </div>
              </div>
              <div class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-500 rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Tremor Count -->
          <div class="card-gradient group">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-gray-500 text-sm font-medium">{{ t('dashboard.tremorCount') }}</p>
                <p class="text-4xl font-bold text-gray-800 mt-2">{{ stats.todayTremors }}</p>
                <div class="flex items-center gap-2 mt-2">
                  <span class="badge badge-warning">
                    {{ t('dashboard.detectionRate') }} {{ stats.detectionRate }}%
                  </span>
                </div>
              </div>
              <div class="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-400 rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Average Severity -->
          <div class="card-gradient group">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-gray-500 text-sm font-medium">{{ t('dashboard.avgSeverity') }}</p>
                <p class="text-4xl font-bold text-gray-800 mt-2">{{ stats.avgSeverity.toFixed(1) }}</p>
                <div class="mt-3">
                  <div class="progress !h-2.5 !bg-warmGray-200">
                    <div
                      class="progress-bar"
                      :style="{ width: `${(stats.avgSeverity / 4) * 100}%` }"
                    ></div>
                  </div>
                </div>
              </div>
              <div class="w-14 h-14 bg-gradient-to-br from-orange-400 to-red-400 rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-glow transition-shadow">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Max Severity -->
          <div class="card-gradient group">
            <div class="flex items-start justify-between">
              <div>
                <p class="text-gray-500 text-sm font-medium">{{ t('dashboard.maxSeverity') }}</p>
                <div class="mt-3">
                  <span
                    class="severity-badge text-lg"
                    :class="`severity-${stats.maxSeverity}`"
                  >
                    {{ getSeverityLabel(stats.maxSeverity) }}
                  </span>
                </div>
              </div>
              <div
                class="w-14 h-14 rounded-2xl flex items-center justify-center shadow-soft"
                :style="{
                  background: `linear-gradient(135deg, ${getSeverityColor(stats.maxSeverity)}80, ${getSeverityColor(stats.maxSeverity)})`
                }"
              >
                <span class="text-2xl font-bold text-white">
                  {{ stats.maxSeverity }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left: Trend Chart -->
            <div class="lg:col-span-2">
                <div class="card h-full">
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="font-bold text-gray-800 text-lg">{{ t('dashboard.weeklyTrend') }}</h3>
                        <select class="px-3 py-1 bg-warmGray-50 border border-warmGray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-100">
                            <option>{{ t('dashboard.sevenDays') }}</option>
                            <option>{{ t('dashboard.thirtyDays') }}</option>
                        </select>
                    </div>
                    <TrendChart 
                        :date-labels="trendData.labels" 
                        :severity-data="trendData.severity"
                        :tremor-count-data="trendData.counts"
                    />
                </div>
            </div>

            <!-- Right: Activity & Tips -->
            <div class="space-y-6">
                 <!-- Recent Sessions List -->
                 <div class="card">
                     <div class="flex items-center justify-between mb-4">
                         <h3 class="font-bold text-gray-800">{{ t('dashboard.recentRecords') }}</h3>
                         <RouterLink to="/history" class="text-sm text-primary-600 hover:text-primary-700 font-medium">{{ t('common.viewAll') }}</RouterLink>
                     </div>
                     <div class="space-y-3">
                         <div v-for="session in recentSessions" :key="session.id" class="flex items-center justify-between p-3 bg-warmGray-50 rounded-xl hover:bg-white hover:shadow-sm transition-all cursor-pointer border border-transparent hover:border-warmGray-100">
                             <div class="flex items-center gap-3">
                                 <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center text-gray-500 shadow-sm text-xs font-bold">
                                     {{ session.start }}
                                 </div>
                                 <div>
                                     <p class="text-sm font-bold text-gray-800">{{ session.duration }}</p>
                                     <p class="text-xs text-gray-500">{{ session.tremors }} {{ t('dashboard.tremorTimesSuffix') }}</p>
                                 </div>
                             </div>
                             <span class="severity-badge scale-90" :class="`severity-${session.maxSeverity}`">
                                {{ getSeverityLabel(session.maxSeverity) }}
                             </span>
                         </div>
                     </div>
                 </div>

                 <!-- AI Assistant Card -->
                 <div class="card-gradient !from-lavender-50 !to-lavender-100/50 border border-lavender-100 relative overflow-hidden">
                      <div class="relative z-10">
                          <h3 class="font-bold text-gray-800 mb-2">{{ t('dashboard.aiCardTitle') }}</h3>
                          <p class="text-sm text-gray-600 mb-4">{{ t('dashboard.aiCardBody') }}</p>
                          <RouterLink to="/ai-assistant" class="btn btn-lavender btn-sm w-full">{{ t('dashboard.aiButton') }}</RouterLink>
                      </div>
                      <div class="absolute -bottom-4 -right-4 w-24 h-24 bg-lavender-200/50 rounded-full blur-xl"></div>
                 </div>
            </div>
        </div>

      </template>
    </div>
  </AppLayout>
</template>
