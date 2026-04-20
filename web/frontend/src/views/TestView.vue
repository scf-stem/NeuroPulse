<template>
  <div class="min-h-screen bg-warmGray-900 text-white p-6">
    <div class="max-w-7xl mx-auto">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between mb-8 animate-fade-in-up">
        <div class="flex items-center gap-4">
          <div class="w-14 h-14 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/30">
            <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h1 class="text-3xl font-bold text-primary-400">ESP32 数据测试</h1>
            <p class="text-warmGray-400 mt-1">实时接收和显示设备发送的数据包</p>
          </div>
        </div>
        <div class="flex gap-3">
          <button
            @click="refreshData"
            :disabled="loading"
            class="px-5 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 rounded-xl flex items-center gap-2 disabled:opacity-50 shadow-lg shadow-primary-500/30 transition-all duration-200"
          >
            <svg class="w-5 h-5" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            刷新
          </button>
          <button
            @click="toggleAutoRefresh"
            :class="autoRefresh ? 'bg-gradient-to-r from-mint-500 to-mint-600 shadow-mint-500/30' : 'bg-warmGray-700 hover:bg-warmGray-600'"
            class="px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all duration-200 shadow-lg"
          >
            <span class="relative flex h-2.5 w-2.5">
              <span v-if="autoRefresh" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span :class="autoRefresh ? 'bg-white' : 'bg-warmGray-400'" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
            </span>
            {{ autoRefresh ? '自动刷新中' : '自动刷新' }}
          </button>
          <button
            @click="clearPackets"
            class="px-4 py-2.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-xl transition-all duration-200"
          >
            清空数据
          </button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-5 mb-6">
        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 50ms;">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <span class="text-warmGray-400 text-sm">总数据包</span>
          </div>
          <div class="text-3xl font-bold text-primary-400">{{ stats.total_packets || 0 }}</div>
        </div>

        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 100ms;">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
            <span class="text-warmGray-400 text-sm">最大容量</span>
          </div>
          <div class="text-3xl font-bold text-yellow-400">{{ stats.max_packets || 500 }}</div>
        </div>

        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 150ms;">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
            </div>
            <span class="text-warmGray-400 text-sm">设备 IP</span>
          </div>
          <div class="text-lg font-mono text-mint-400 truncate">
            {{ (stats.recent_client_ips || []).join(', ') || '-' }}
          </div>
        </div>

        <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 200ms;">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span class="text-warmGray-400 text-sm">最新数据时间</span>
          </div>
          <div class="text-lg font-mono text-lavender-400">
            {{ formatTime(stats.newest_packet) }}
          </div>
        </div>
      </div>

      <!-- API 端点说明 -->
      <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl p-5 mb-6 border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 250ms;">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
          <h2 class="text-lg font-semibold text-primary-400">ESP32 API 端点</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm font-mono">
          <div class="bg-warmGray-700/50 rounded-xl p-4 border border-warmGray-600/30 hover:border-mint-500/30 transition-colors">
            <div class="text-mint-400 font-semibold mb-1">POST</div>
            <div class="text-white">/api/test/receive</div>
            <div class="text-warmGray-400 text-xs mt-2">接收任意 JSON 数据</div>
          </div>
          <div class="bg-warmGray-700/50 rounded-xl p-4 border border-warmGray-600/30 hover:border-mint-500/30 transition-colors">
            <div class="text-mint-400 font-semibold mb-1">POST</div>
            <div class="text-white">/api/test/heartbeat</div>
            <div class="text-warmGray-400 text-xs mt-2">设备心跳</div>
          </div>
          <div class="bg-warmGray-700/50 rounded-xl p-4 border border-warmGray-600/30 hover:border-mint-500/30 transition-colors">
            <div class="text-mint-400 font-semibold mb-1">POST</div>
            <div class="text-white">/api/test/batch</div>
            <div class="text-warmGray-400 text-xs mt-2">批量数据上传</div>
          </div>
        </div>
      </div>

      <!-- 数据包列表 -->
      <div class="bg-warmGray-800/80 backdrop-blur rounded-2xl overflow-hidden border border-warmGray-700/50 animate-fade-in-up" style="animation-delay: 300ms;">
        <div class="p-5 border-b border-warmGray-700/50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold">数据包列表</h2>
          </div>
          <div class="text-sm text-warmGray-400 bg-warmGray-700/50 px-3 py-1.5 rounded-lg">
            显示 {{ packets.length }} / {{ stats.total_packets || 0 }} 条
          </div>
        </div>

        <!-- 数据包表格 -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-warmGray-700/50 text-left text-sm">
              <tr>
                <th class="p-4 w-16 font-medium text-warmGray-300">ID</th>
                <th class="p-4 w-24 font-medium text-warmGray-300">类型</th>
                <th class="p-4 w-32 font-medium text-warmGray-300">来源 IP</th>
                <th class="p-4 w-40 font-medium text-warmGray-300">时间</th>
                <th class="p-4 font-medium text-warmGray-300">数据预览</th>
                <th class="p-4 w-20 font-medium text-warmGray-300">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(packet, index) in packets"
                :key="packet.id"
                class="border-t border-warmGray-700/50 hover:bg-warmGray-700/30 transition-colors animate-fade-in-up"
                :style="{ animationDelay: `${index * 30}ms` }"
              >
                <td class="p-4 font-mono text-primary-400">#{{ packet.id }}</td>
                <td class="p-4">
                  <span
                    :class="getTypeClass(packet.type)"
                    class="px-2.5 py-1 rounded-lg text-xs font-medium"
                  >
                    {{ packet.type || 'data' }}
                  </span>
                </td>
                <td class="p-4 font-mono text-sm">{{ packet.client_ip }}</td>
                <td class="p-4 font-mono text-sm text-warmGray-400">
                  {{ formatTime(packet.received_at) }}
                </td>
                <td class="p-4">
                  <pre class="text-xs text-warmGray-300 max-w-xl overflow-hidden text-ellipsis bg-warmGray-700/50 px-2 py-1 rounded">{{ getDataPreview(packet.data) }}</pre>
                </td>
                <td class="p-4">
                  <button
                    @click="showDetail(packet)"
                    class="text-primary-400 hover:text-primary-300 text-sm font-medium hover:underline transition-colors"
                  >
                    详情
                  </button>
                </td>
              </tr>
              <tr v-if="packets.length === 0">
                <td colspan="6" class="p-12 text-center text-warmGray-500">
                  <div class="flex flex-col items-center">
                    <div class="w-20 h-20 bg-warmGray-700/50 rounded-2xl flex items-center justify-center mb-4">
                      <svg class="w-10 h-10 text-warmGray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                    </div>
                    <p class="text-lg font-medium mb-1">暂无数据包</p>
                    <p class="text-sm">等待 ESP32 设备发送数据...</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 详情弹窗 -->
      <Transition name="modal">
        <div
          v-if="selectedPacket"
          class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          @click.self="selectedPacket = null"
        >
          <div class="bg-warmGray-800 rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden border border-warmGray-700/50 shadow-2xl animate-scale-in">
            <div class="p-5 border-b border-warmGray-700/50 flex items-center justify-between bg-gradient-to-r from-warmGray-800 to-warmGray-700">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold">
                  数据包详情 <span class="text-primary-400">#{{ selectedPacket.id }}</span>
                </h3>
              </div>
              <button
                @click="selectedPacket = null"
                class="w-10 h-10 bg-warmGray-700/50 hover:bg-warmGray-600 rounded-xl flex items-center justify-center transition-colors"
              >
                <svg class="w-5 h-5 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="p-5 overflow-y-auto max-h-[calc(80vh-80px)]">
              <!-- 基本信息 -->
              <div class="grid grid-cols-2 gap-4 mb-5">
                <div class="bg-warmGray-700/50 rounded-xl p-4 border border-warmGray-600/30">
                  <div class="text-warmGray-400 text-sm mb-1">接收时间</div>
                  <div class="font-mono text-white">{{ selectedPacket.received_at }}</div>
                </div>
                <div class="bg-warmGray-700/50 rounded-xl p-4 border border-warmGray-600/30">
                  <div class="text-warmGray-400 text-sm mb-1">客户端 IP</div>
                  <div class="font-mono text-mint-400">{{ selectedPacket.client_ip }}</div>
                </div>
              </div>

              <!-- Headers -->
              <div class="mb-5">
                <h4 class="text-sm text-warmGray-400 mb-3 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                  HTTP Headers
                </h4>
                <pre class="bg-warmGray-900 rounded-xl p-4 text-xs overflow-x-auto border border-warmGray-700/50 text-warmGray-300">{{ JSON.stringify(selectedPacket.headers, null, 2) }}</pre>
              </div>

              <!-- Data -->
              <div>
                <h4 class="text-sm text-warmGray-400 mb-3 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                  数据内容
                </h4>
                <pre class="bg-warmGray-900 rounded-xl p-4 text-sm overflow-x-auto border border-warmGray-700/50 text-mint-400">{{ JSON.stringify(selectedPacket.data, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { formatDateTime, legacyT } from '@/i18n'

interface Packet {
  id: number
  received_at: string
  type?: string
  client_ip: string
  headers?: Record<string, string>
  data: unknown
}

interface Stats {
  total_packets: number
  max_packets: number
  type_counts: Record<string, number>
  recent_client_ips: string[]
  oldest_packet: string | null
  newest_packet: string | null
}

const packets = ref<Packet[]>([])
const stats = ref<Partial<Stats>>({})
const loading = ref(false)
const autoRefresh = ref(false)
const selectedPacket = ref<Packet | null>(null)

let refreshInterval: number | null = null

const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'

async function fetchStats() {
  try {
    const response = await axios.get(`${apiBase}/test/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

async function fetchPackets() {
  try {
    const response = await axios.get(`${apiBase}/test/packets`, {
      params: { limit: 50 }
    })
    packets.value = response.data.packets
  } catch (error) {
    console.error('获取数据包失败:', error)
  }
}

async function refreshData() {
  loading.value = true
  try {
    await Promise.all([fetchStats(), fetchPackets()])
  } finally {
    loading.value = false
  }
}

async function clearPackets() {
  if (!confirm(legacyT('确定要清空所有数据包吗？'))) return

  try {
    await axios.delete(`${apiBase}/test/packets`)
    await refreshData()
  } catch (error) {
    console.error('清空失败:', error)
  }
}

function toggleAutoRefresh() {
  autoRefresh.value = !autoRefresh.value

  if (autoRefresh.value) {
    refreshInterval = window.setInterval(refreshData, 2000)
  } else if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

function showDetail(packet: Packet) {
  selectedPacket.value = packet
}

function formatTime(isoString: string | null | undefined): string {
  if (!isoString) return '-'
  try {
    return formatDateTime(isoString, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return isoString
  }
}

function getDataPreview(data: unknown): string {
  const str = JSON.stringify(data)
  if (str.length > 100) {
    return str.substring(0, 100) + '...'
  }
  return str
}

function getTypeClass(type: string | undefined): string {
  switch (type) {
    case 'heartbeat':
      return 'bg-mint-500/20 text-mint-400 border border-mint-500/30'
    case 'batch':
      return 'bg-lavender-500/20 text-lavender-400 border border-lavender-500/30'
    default:
      return 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
  }
}

onMounted(() => {
  refreshData()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .animate-scale-in,
.modal-leave-to .animate-scale-in {
  transform: scale(0.95);
}

/* Scale in animation */
.animate-scale-in {
  animation: scale-in 0.3s ease-out;
}

@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
