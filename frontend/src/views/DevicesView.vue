<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { deviceApi, type Device } from '@/api/device'
import { formatDate, t } from '@/i18n'

// State
const loading = ref(true)
const devices = ref<Device[]>([])
const error = ref<string | null>(null)

// Add device dialog
const showAddModal = ref(false)
const addingDevice = ref(false)
const newDevice = ref({
  device_id: '',
  name: ''
})

// Edit device dialog
const showEditModal = ref(false)
const editingDevice = ref(false)
const selectedDevice = ref<Device | null>(null)
const editDeviceName = ref('')

// Delete confirmation dialog
const showDeleteModal = ref(false)
const deletingDevice = ref(false)
const deviceToDelete = ref<Device | null>(null)

// Computed properties
const onlineDevices = computed(() => devices.value.filter(d => d.is_online).length)
const offlineDevices = computed(() => devices.value.filter(d => !d.is_online).length)

// Methods
async function fetchDevices() {
  loading.value = true
  error.value = null
  try {
    devices.value = await deviceApi.list()
  } catch (e: any) {
    error.value = e.message || t('devices.errors.fetch')
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  newDevice.value = { device_id: '', name: '' }
  showAddModal.value = true
}

async function addDevice() {
  if (!newDevice.value.device_id.trim()) {
    error.value = t('devices.addDeviceIdError')
    return
  }

  addingDevice.value = true
  error.value = null

  try {
    await deviceApi.register({
      device_id: newDevice.value.device_id.trim(),
      name: newDevice.value.name.trim() || undefined
    })
    showAddModal.value = false
    await fetchDevices()
  } catch (e: any) {
    error.value = e.message || t('devices.errors.add')
  } finally {
    addingDevice.value = false
  }
}

function openEditModal(device: Device) {
  selectedDevice.value = device
  editDeviceName.value = device.name || ''
  showEditModal.value = true
}

async function saveDeviceName() {
  if (!selectedDevice.value) return

  editingDevice.value = true
  error.value = null

  try {
    await deviceApi.update(selectedDevice.value.device_id, {
      name: editDeviceName.value.trim() || undefined
    })
    showEditModal.value = false
    await fetchDevices()
  } catch (e: any) {
    error.value = e.message || t('devices.errors.update')
  } finally {
    editingDevice.value = false
  }
}

function openDeleteModal(device: Device) {
  deviceToDelete.value = device
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!deviceToDelete.value) return

  deletingDevice.value = true
  error.value = null

  try {
    await deviceApi.unbind(deviceToDelete.value.device_id)
    showDeleteModal.value = false
    await fetchDevices()
  } catch (e: any) {
    error.value = e.message || t('devices.errors.remove')
  } finally {
    deletingDevice.value = false
  }
}

function formatLastSeen(dateStr: string | null) {
  if (!dateStr) return t('devices.lastSeenNever')
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return t('devices.lastSeenJustNow')
  if (diff < 3600000) return t('devices.lastSeenMinutes', { count: Math.floor(diff / 60000) })
  if (diff < 86400000) return t('devices.lastSeenHours', { count: Math.floor(diff / 3600000) })
  return formatDate(date)
}

function getBatteryColor(level: number | null) {
  if (level === null) return 'text-gray-400'
  if (level >= 80) return 'text-mint-500'
  if (level >= 50) return 'text-mint-400'
  if (level >= 20) return 'text-amber-500'
  return 'text-red-500'
}

onMounted(() => {
  fetchDevices()
})
</script>

<template>
  <AppLayout>
    <!-- 页面标题 -->
    <div class="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('devices.title') }}</h1>
          <p class="text-gray-500 text-sm">{{ t('devices.subtitle') }}</p>
        </div>
      </div>

      <button @click="openAddModal" class="btn btn-primary">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        {{ t('devices.addDevice') }}
      </button>
    </div>

    <!-- 错误提示 -->
    <Transition name="fade-up">
      <div v-if="error" class="alert alert-error mb-6">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
        <button @click="error = null" class="ml-auto text-red-600 hover:text-red-700 font-medium">{{ t('common.close') }}</button>
      </div>
    </Transition>

    <!-- 设备统计 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('devices.totalDevices') }}</p>
            <p class="text-3xl font-bold text-gray-800">{{ devices.length }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('devices.onlineDevices') }}</p>
            <p class="text-3xl font-bold text-mint-600">{{ onlineDevices }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-mint-400 to-mint-600 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="card card-gradient group">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm mb-1">{{ t('devices.offlineDevices') }}</p>
            <p class="text-3xl font-bold text-gray-500">{{ offlineDevices }}</p>
          </div>
          <div class="w-12 h-12 bg-gradient-to-br from-warmGray-300 to-warmGray-400 rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex flex-col items-center justify-center h-64">
      <div class="relative">
        <div class="w-16 h-16 border-4 border-primary-200 rounded-full"></div>
        <div class="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin absolute inset-0"></div>
      </div>
      <p class="text-gray-500 mt-4">{{ t('devices.loading') }}</p>
    </div>

    <!-- 设备列表 -->
    <template v-else>
      <!-- 空状态 -->
      <div v-if="devices.length === 0" class="card text-center py-16">
        <div class="w-20 h-20 bg-gradient-to-br from-warmGray-100 to-warmGray-200 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ t('devices.emptyTitle') }}</h3>
        <p class="text-gray-500 mb-6">{{ t('devices.emptyBody') }}</p>
        <button @click="openAddModal" class="btn btn-primary inline-flex">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          {{ t('devices.addDevice') }}
        </button>
      </div>

      <!-- 设备卡片列表 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="(device, index) in devices"
          :key="device.id"
          class="card hover:shadow-lg transition-all duration-300 animate-fade-in-up"
          :style="{ animationDelay: `${index * 50}ms` }"
        >
          <!-- 设备头部 -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3">
              <div
                class="w-12 h-12 rounded-xl flex items-center justify-center relative"
                :class="device.is_online ? 'bg-gradient-to-br from-mint-400 to-mint-600' : 'bg-warmGray-200'"
              >
                <svg
                  class="w-6 h-6"
                  :class="device.is_online ? 'text-white' : 'text-warmGray-400'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <!-- 在线指示灯 -->
                <span
                  v-if="device.is_online"
                  class="absolute -top-1 -right-1 w-3 h-3 bg-mint-400 border-2 border-white rounded-full animate-pulse"
                ></span>
              </div>
              <div>
                <h3 class="font-semibold text-gray-800">{{ device.name || 'Unnamed Device' }}</h3>
                <p class="text-xs text-gray-400 font-mono">{{ device.device_id }}</p>
              </div>
            </div>
            <span
              :class="[
                'badge',
                device.is_online ? 'badge-success' : 'badge-secondary'
              ]"
            >
              <span v-if="device.is_online" class="w-1.5 h-1.5 bg-current rounded-full mr-1.5"></span>
              {{ device.is_online ? 'Online' : 'Offline' }}
            </span>
          </div>

          <!-- Device Information -->
          <div class="space-y-3 text-sm">
            <!-- Battery -->
            <div class="flex items-center justify-between">
              <span class="text-gray-500">Battery</span>
              <div class="flex items-center gap-2">
                <div class="w-20 h-2.5 bg-warmGray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="device.battery_level !== null && device.battery_level >= 50 ? 'bg-gradient-to-r from-mint-400 to-mint-500' : device.battery_level !== null && device.battery_level >= 20 ? 'bg-gradient-to-r from-amber-400 to-amber-500' : 'bg-gradient-to-r from-red-400 to-red-500'"
                    :style="{ width: `${device.battery_level || 0}%` }"
                  ></div>
                </div>
                <span :class="getBatteryColor(device.battery_level)" class="font-medium w-10 text-right">
                  {{ device.battery_level !== null ? `${device.battery_level}%` : '-' }}
                </span>
              </div>
            </div>

            <!-- Firmware Version -->
            <div class="flex items-center justify-between">
              <span class="text-gray-500">Firmware Version</span>
              <span class="font-medium text-gray-700">{{ device.firmware_version || '-' }}</span>
            </div>

            <!-- Hardware Version -->
            <div class="flex items-center justify-between">
              <span class="text-gray-500">Hardware Version</span>
              <span class="font-medium text-gray-700">{{ device.hardware_version || '-' }}</span>
            </div>

            <!-- MAC Address -->
            <div class="flex items-center justify-between">
              <span class="text-gray-500">MAC Address</span>
              <span class="font-mono text-xs text-gray-600 bg-warmGray-100 px-2 py-0.5 rounded">
                {{ device.mac_address || '-' }}
              </span>
            </div>

            <!-- Last Seen -->
            <div class="flex items-center justify-between">
              <span class="text-gray-500">Last Seen</span>
              <span class="font-medium text-gray-700">{{ formatLastSeen(device.last_seen) }}</span>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex items-center justify-end mt-5 pt-4 border-t border-warmGray-200 gap-2">
            <button
              @click="openEditModal(device)"
              class="btn btn-ghost text-sm !py-1.5"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
            <button
              @click="openDeleteModal(device)"
              class="text-sm px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Unbind
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Add Device Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showAddModal"
          class="modal-overlay"
          @click.self="showAddModal = false"
        >
          <div class="modal max-w-md">
            <div class="modal-header">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-800">Add Device</h3>
              </div>
              <button @click="showAddModal = false" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  Device ID <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="newDevice.device_id"
                  type="text"
                  class="input"
                  placeholder="e.g., ESP32_XXXXXX"
                />
                <p class="text-xs text-gray-500 mt-1.5">
                  Device ID can be found on the back of the device or in the settings page
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  Device Name
                </label>
                <input
                  v-model="newDevice.name"
                  type="text"
                  class="input"
                  placeholder="Enter a name for the device (optional)"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button @click="showAddModal = false" class="btn btn-secondary">
                Cancel
              </button>
              <button
                @click="addDevice"
                :disabled="addingDevice"
                class="btn btn-primary"
              >
                <svg v-if="addingDevice" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ addingDevice ? 'Adding...' : 'Add Device' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Edit Device Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showEditModal"
          class="modal-overlay"
          @click.self="showEditModal = false"
        >
          <div class="modal max-w-md">
            <div class="modal-header">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-800">Edit Device</h3>
              </div>
              <button @click="showEditModal = false" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  Device Name
                </label>
                <input
                  v-model="editDeviceName"
                  type="text"
                  class="input"
                  placeholder="Enter a new device name"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button @click="showEditModal = false" class="btn btn-secondary">
                Cancel
              </button>
              <button
                @click="saveDeviceName"
                :disabled="editingDevice"
                class="btn btn-primary"
              >
                <svg v-if="editingDevice" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ editingDevice ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Confirmation Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showDeleteModal"
          class="modal-overlay"
          @click.self="showDeleteModal = false"
        >
          <div class="modal max-w-md">
            <div class="modal-header">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-red-400 to-red-600 rounded-xl flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-red-600">Unbind Device</h3>
              </div>
              <button @click="showDeleteModal = false" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <p class="text-gray-600">
                Are you sure you want to unbind device <span class="font-semibold text-gray-800">{{ deviceToDelete?.name || deviceToDelete?.device_id }}</span>?
              </p>
              <p class="text-sm text-gray-500 mt-3 p-3 bg-warmGray-50 rounded-xl">
                After unbinding, this device will no longer be associated with your account, but device data will not be deleted.
              </p>
            </div>

            <div class="modal-footer">
              <button @click="showDeleteModal = false" class="btn btn-secondary">
                Cancel
              </button>
              <button
                @click="confirmDelete"
                :disabled="deletingDevice"
                class="btn bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white"
              >
                <svg v-if="deletingDevice" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ deletingDevice ? 'Unbinding...' : 'Confirm Unbind' }}
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
