<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { localeText } from '@/i18n'

const router = useRouter()
const authStore = useAuthStore()
const lt = (en: string, zh: string) => localeText(en, zh)

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

// Tab
const activeTab = ref<'profile' | 'password' | 'notifications' | 'danger'>('profile')

// 个人信息
const profileForm = ref({
  full_name: '',
  email: ''
})

// 密码修改
const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// 通知设置
const notificationSettings = ref({
  tremor_alerts: true,
  daily_summary: true,
  weekly_report: false,
  device_offline: true,
  email_notifications: false
})

// 删除账户确认
const showDeleteModal = ref(false)
const deleteConfirmText = ref('')
const deleting = ref(false)

// 计算属性
const user = computed(() => authStore.user)

const canDeleteAccount = computed(() => {
  return deleteConfirmText.value === user.value?.username
})

// Tab 配置
const tabs = [
  { id: 'profile', label: lt('Profile', '个人信息'), icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { id: 'password', label: lt('Password', '修改密码'), icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
  { id: 'notifications', label: lt('Notifications', '通知设置'), icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { id: 'danger', label: lt('Danger zone', '危险区域'), icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z', danger: true }
]

// 初始化
onMounted(() => {
  if (user.value) {
    profileForm.value = {
      full_name: user.value.full_name || '',
      email: user.value.email || ''
    }
  }
})

// 保存个人信息
async function saveProfile() {
  loading.value = true
  error.value = null
  success.value = null

  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    success.value = lt('Profile updated', '个人信息已更新')

    if (authStore.user) {
      authStore.user.full_name = profileForm.value.full_name
      authStore.user.email = profileForm.value.email
    }
  } catch (e: any) {
    error.value = e.message || lt('Update failed', '更新失败')
  } finally {
    loading.value = false
  }
}

// 修改密码
async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    error.value = lt('The passwords do not match', '两次输入的密码不一致')
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    error.value = lt('Password must be at least 6 characters', '密码长度至少为 6 位')
    return
  }

  loading.value = true
  error.value = null
  success.value = null

  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    success.value = lt('Password updated', '密码已更新')

    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (e: any) {
    error.value = e.message || lt('Unable to update password', '修改密码失败')
  } finally {
    loading.value = false
  }
}

// 保存通知设置
async function saveNotifications() {
  loading.value = true
  error.value = null
  success.value = null

  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    success.value = lt('Notification settings saved', '通知设置已保存')
  } catch (e: any) {
    error.value = e.message || lt('Save failed', '保存失败')
  } finally {
    loading.value = false
  }
}

// 登出
async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

// 删除账户
async function deleteAccount() {
  if (!canDeleteAccount.value) return

  deleting.value = true
  error.value = null

  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    await authStore.logout()
    router.push('/')
  } catch (e: any) {
    error.value = e.message || lt('Unable to delete account', '删除账户失败')
  } finally {
    deleting.value = false
  }
}

// 清除消息
function clearMessages() {
  error.value = null
  success.value = null
}
</script>

<template>
  <AppLayout>
    <!-- 页面标题 -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-2">
        <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center shadow-soft">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ lt('Settings', '设置') }}</h1>
          <p class="text-gray-500 text-sm">{{ lt('Manage your account and preferences', '管理您的账户和偏好设置') }}</p>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <Transition name="fade-up">
      <div v-if="error" class="alert alert-error mb-6">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
        <button @click="clearMessages" class="ml-auto text-red-600 hover:text-red-700 font-medium">{{ lt('Close', '关闭') }}</button>
      </div>
    </Transition>
    <Transition name="fade-up">
      <div v-if="success" class="alert alert-success mb-6">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ success }}</span>
        <button @click="clearMessages" class="ml-auto text-mint-600 hover:text-mint-700 font-medium">{{ lt('Close', '关闭') }}</button>
      </div>
    </Transition>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 左侧：导航 -->
      <div class="lg:col-span-1">
        <div class="card !p-2">
          <nav class="flex flex-col gap-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id as any; clearMessages()"
              :class="[
                'flex items-center px-4 py-3 rounded-xl text-left transition-all duration-200',
                activeTab === tab.id
                  ? tab.danger
                    ? 'bg-gradient-to-r from-red-50 to-warmGray-50 text-red-600'
                    : 'bg-gradient-to-r from-primary-50 to-warmGray-50 text-primary-600'
                  : 'text-gray-600 hover:bg-warmGray-50'
              ]"
            >
              <div
                :class="[
                  'w-9 h-9 rounded-lg flex items-center justify-center mr-3',
                  activeTab === tab.id
                    ? tab.danger ? 'bg-red-100' : 'bg-primary-100'
                    : 'bg-warmGray-100'
                ]"
              >
                <svg
                  class="w-5 h-5"
                  :class="activeTab === tab.id ? (tab.danger ? 'text-red-600' : 'text-primary-600') : 'text-gray-500'"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" />
                </svg>
              </div>
              <span class="font-medium">{{ tab.label }}</span>
            </button>
          </nav>
        </div>

        <!-- 登出按钮 -->
        <button
          @click="handleLogout"
          class="w-full mt-4 btn btn-secondary flex items-center justify-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          {{ lt('Log out', '退出登录') }}
        </button>
      </div>

      <!-- 右侧：内容 -->
      <div class="lg:col-span-3">
        <!-- 个人信息 -->
        <div v-if="activeTab === 'profile'" class="card">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-800">{{ lt('Profile', '个人信息') }}</h2>
          </div>

          <div class="space-y-6">
            <!-- 头像 -->
            <div class="flex items-center gap-5">
              <div class="w-20 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-soft">
                {{ user?.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <div>
                <p class="font-semibold text-lg text-gray-800">{{ user?.username }}</p>
                <p class="text-sm text-gray-500">{{ lt('User ID:', '用户 ID:') }} {{ user?.id }}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('Username', '用户名') }}</label>
                <input
                  type="text"
                  :value="user?.username"
                  disabled
                  class="input !bg-warmGray-100 cursor-not-allowed"
                />
                <p class="text-xs text-gray-500 mt-1.5">{{ lt('Username cannot be changed', '用户名不可修改') }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('Name', '姓名') }}</label>
                <input
                  v-model="profileForm.full_name"
                  type="text"
                  class="input"
                  :placeholder="lt('Enter your name', '输入您的姓名')"
                />
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('Email', '邮箱') }}</label>
                <input
                  v-model="profileForm.email"
                  type="email"
                  class="input"
                  :placeholder="lt('Enter your email', '输入您的邮箱')"
                />
              </div>
            </div>

            <div class="flex justify-end pt-4">
              <button
                @click="saveProfile"
                :disabled="loading"
                class="btn btn-primary"
              >
                <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ loading ? lt('Saving...', '保存中...') : lt('Save changes', '保存更改') }}
              </button>
            </div>
          </div>
        </div>

        <!-- 修改密码 -->
        <div v-if="activeTab === 'password'" class="card">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-800">{{ lt('Password', '修改密码') }}</h2>
          </div>

          <div class="space-y-4 max-w-md">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('Current password', '当前密码') }}</label>
              <input
                v-model="passwordForm.current_password"
                type="password"
                class="input"
                :placeholder="lt('Enter current password', '输入当前密码')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('New password', '新密码') }}</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                class="input"
                :placeholder="lt('Enter a new password (min 6 characters)', '输入新密码（至少 6 位）')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">{{ lt('Confirm new password', '确认新密码') }}</label>
              <input
                v-model="passwordForm.confirm_password"
                type="password"
                class="input"
                :placeholder="lt('Re-enter the new password', '再次输入新密码')"
              />
            </div>

            <div class="flex justify-end pt-4">
              <button
                @click="changePassword"
                :disabled="loading"
                class="btn btn-primary"
              >
                <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ loading ? lt('Updating...', '更新中...') : lt('Update password', '更新密码') }}
              </button>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div v-if="activeTab === 'notifications'" class="card">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-gray-800">{{ lt('Notifications', '通知设置') }}</h2>
          </div>

          <div class="space-y-8">
            <!-- 震颤提醒 -->
            <div class="space-y-4">
              <h3 class="font-medium text-gray-800 flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                {{ lt('Tremor alerts', '震颤提醒') }}
              </h3>

              <label class="flex items-center justify-between p-4 bg-gradient-to-r from-warmGray-50 to-primary-50/30 rounded-xl cursor-pointer hover:shadow-soft transition-all">
                <div>
                  <p class="font-medium text-gray-700">{{ lt('Tremor warning', '震颤预警') }}</p>
                  <p class="text-sm text-gray-500">{{ lt('Notify when severe tremor is detected', '检测到严重震颤时发送通知') }}</p>
                </div>
                <div class="switch" :class="{ active: notificationSettings.tremor_alerts }">
                  <input v-model="notificationSettings.tremor_alerts" type="checkbox" class="sr-only" />
                  <span class="switch-slider"></span>
                </div>
              </label>

              <label class="flex items-center justify-between p-4 bg-gradient-to-r from-warmGray-50 to-primary-50/30 rounded-xl cursor-pointer hover:shadow-soft transition-all">
                <div>
                  <p class="font-medium text-gray-700">{{ lt('Device offline alert', '设备离线提醒') }}</p>
                  <p class="text-sm text-gray-500">{{ lt('Notify if a device is offline for over 30 minutes', '设备断开连接超过 30 分钟时提醒') }}</p>
                </div>
                <div class="switch" :class="{ active: notificationSettings.device_offline }">
                  <input v-model="notificationSettings.device_offline" type="checkbox" class="sr-only" />
                  <span class="switch-slider"></span>
                </div>
              </label>
            </div>

            <!-- 报告通知 -->
            <div class="space-y-4">
              <h3 class="font-medium text-gray-800 flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-mint-500 rounded-full"></span>
                {{ lt('Report notifications', '报告通知') }}
              </h3>

              <label class="flex items-center justify-between p-4 bg-gradient-to-r from-warmGray-50 to-mint-50/30 rounded-xl cursor-pointer hover:shadow-soft transition-all">
                <div>
                  <p class="font-medium text-gray-700">{{ lt('Daily summary', '每日摘要') }}</p>
                  <p class="text-sm text-gray-500">{{ lt('Send a monitoring summary every day', '每天发送今日监测摘要') }}</p>
                </div>
                <div class="switch" :class="{ active: notificationSettings.daily_summary }">
                  <input v-model="notificationSettings.daily_summary" type="checkbox" class="sr-only" />
                  <span class="switch-slider"></span>
                </div>
              </label>

              <label class="flex items-center justify-between p-4 bg-gradient-to-r from-warmGray-50 to-mint-50/30 rounded-xl cursor-pointer hover:shadow-soft transition-all">
                <div>
                  <p class="font-medium text-gray-700">{{ lt('Weekly report', '周报') }}</p>
                  <p class="text-sm text-gray-500">{{ lt('Send last week’s report every Monday', '每周一发送上周分析报告') }}</p>
                </div>
                <div class="switch" :class="{ active: notificationSettings.weekly_report }">
                  <input v-model="notificationSettings.weekly_report" type="checkbox" class="sr-only" />
                  <span class="switch-slider"></span>
                </div>
              </label>
            </div>

            <!-- 通知方式 -->
            <div class="space-y-4">
              <h3 class="font-medium text-gray-800 flex items-center gap-2">
                <span class="w-1.5 h-1.5 bg-lavender-500 rounded-full"></span>
                {{ lt('Delivery channel', '通知方式') }}
              </h3>

              <label class="flex items-center justify-between p-4 bg-gradient-to-r from-warmGray-50 to-lavender-50/30 rounded-xl cursor-pointer hover:shadow-soft transition-all">
                <div>
                  <p class="font-medium text-gray-700">{{ lt('Email notifications', '邮件通知') }}</p>
                  <p class="text-sm text-gray-500">{{ lt('Receive notifications by email (requires verified email)', '通过邮件接收通知（需要验证邮箱）') }}</p>
                </div>
                <div class="switch" :class="{ active: notificationSettings.email_notifications }">
                  <input v-model="notificationSettings.email_notifications" type="checkbox" class="sr-only" />
                  <span class="switch-slider"></span>
                </div>
              </label>
            </div>

            <div class="flex justify-end pt-4">
              <button
                @click="saveNotifications"
                :disabled="loading"
                class="btn btn-primary"
              >
                <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ loading ? lt('Saving...', '保存中...') : lt('Save settings', '保存设置') }}
              </button>
            </div>
          </div>
        </div>

        <!-- 危险区域 -->
        <div v-if="activeTab === 'danger'" class="card border-red-200">
          <div class="flex items-center gap-2 mb-6">
            <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold text-red-600">{{ lt('Danger zone', '危险区域') }}</h2>
          </div>

          <div class="space-y-6">
            <!-- 导出数据 -->
            <div class="p-5 bg-gradient-to-r from-warmGray-50 to-primary-50/30 rounded-xl border border-warmGray-200">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 class="font-medium text-gray-800">{{ lt('Export all data', '导出所有数据') }}</h3>
                  <p class="text-sm text-gray-500 mt-1">
                    {{ lt('Download all monitoring data and account details', '下载您的所有震颤监测数据和账户信息') }}
                  </p>
                </div>
                <RouterLink to="/reports" class="btn btn-secondary">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  {{ lt('Go to reports', '前往报告中心') }}
                </RouterLink>
              </div>
            </div>

            <!-- 删除账户 -->
            <div class="p-5 bg-gradient-to-r from-red-50 to-warmGray-50 rounded-xl border border-red-200">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 class="font-medium text-red-700">{{ lt('Delete account', '删除账户') }}</h3>
                  <p class="text-sm text-red-600 mt-1">
                    {{ lt('Permanently delete your account and all related data. This action cannot be undone.', '永久删除您的账户和所有相关数据。此操作不可撤销。') }}
                  </p>
                </div>
                <button
                  @click="showDeleteModal = true"
                  class="btn bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  {{ lt('Delete account', '删除账户') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除账户确认模态框 -->
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
                <h3 class="text-lg font-semibold text-red-600">{{ lt('Delete account', '删除账户') }}</h3>
              </div>
              <button @click="showDeleteModal = false" class="p-2 hover:bg-warmGray-100 rounded-xl transition-colors">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <div class="bg-gradient-to-r from-red-50 to-warmGray-50 border border-red-200 rounded-xl p-4 mb-4">
                <p class="text-red-700 font-medium">{{ lt('Warning: this cannot be undone!', '警告：此操作无法撤销！') }}</p>
                <p class="text-red-600 text-sm mt-1">
                  {{ lt('Deleting the account permanently removes:', '删除账户将永久移除所有数据，包括：') }}
                </p>
                <ul class="text-red-600 text-sm mt-2 list-disc list-inside space-y-1">
                  <li>{{ lt('All monitoring records', '所有震颤监测记录') }}</li>
                  <li>{{ lt('Device links', '设备绑定信息') }}</li>
                  <li>{{ lt('Reports and historical data', '分析报告和历史数据') }}</li>
                  <li>{{ lt('Account settings and profile data', '账户设置和个人信息') }}</li>
                </ul>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">
                  {{ lt('Enter your username', '请输入您的用户名') }} <span class="font-bold text-gray-800">{{ user?.username }}</span> {{ lt('to confirm deletion:', '以确认删除：') }}
                </label>
                <input
                  v-model="deleteConfirmText"
                  type="text"
                  class="input"
                  :placeholder="user?.username"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button @click="showDeleteModal = false" class="btn btn-secondary">
                {{ lt('Cancel', '取消') }}
              </button>
              <button
                @click="deleteAccount"
                :disabled="!canDeleteAccount || deleting"
                class="btn bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="deleting" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ deleting ? lt('Deleting...', '删除中...') : lt('Confirm deletion', '确认删除') }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AppLayout>
</template>

<style scoped>
.switch {
  @apply relative inline-flex h-6 w-11 items-center rounded-full bg-warmGray-300 transition-colors duration-200;
}

.switch.active {
  @apply bg-primary-500;
}

.switch-slider {
  @apply inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 translate-x-1;
}

.switch.active .switch-slider {
  @apply translate-x-6;
}
</style>
