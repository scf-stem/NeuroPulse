/**
 * Tremor Guard - Auth Store
 * 震颤卫士 - 认证状态管理
 */

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { authApi } from '@/api/auth'
import { DEMO_TOKEN, demoUser } from '@/demo'
import { t } from '@/i18n'
import { useSessionStore } from '@/stores/session'

export const useAuthStore = defineStore('auth', () => {
  const sessionStore = useSessionStore()

  sessionStore.ensureBootstrapped()

  const loading = ref(false)
  const error = ref<string | null>(null)

  const user = computed(() => sessionStore.user)
  const token = computed(() => sessionStore.token)
  const isAuthenticated = computed(() => sessionStore.hasAccess)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isDoctor = computed(() => user.value?.role === 'doctor')

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.login(email, password)
      sessionStore.loginSuccess(response.access_token, response.user)
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || t('auth.errors.loginFailed')
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, username: string, password: string, fullName?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.register({ email, username, password, full_name: fullName })
      sessionStore.loginSuccess(response.access_token, response.user)
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || t('auth.errors.registerFailed')
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (sessionStore.isDemo) {
      sessionStore.enterDemo()
      return demoUser
    }

    if (!sessionStore.isRealAuthenticated) {
      return null
    }

    try {
      const nextUser = await authApi.getCurrentUser()
      sessionStore.updateUserSnapshot(nextUser)
      return nextUser
    } catch {
      sessionStore.invalidateRealSession()
      return null
    }
  }

  async function refreshToken() {
    if (sessionStore.isDemo) {
      sessionStore.enterDemo()
      return true
    }

    if (!sessionStore.isRealAuthenticated) {
      return false
    }

    try {
      const response = await authApi.refreshToken()
      sessionStore.loginSuccess(response.access_token, response.user)
      return true
    } catch {
      sessionStore.invalidateRealSession()
      return false
    }
  }

  async function logout() {
    if (sessionStore.isRealAuthenticated) {
      try {
        await authApi.logout()
      } catch {
        // no-op: local session teardown is still authoritative
      }
    }

    sessionStore.logout()
  }

  function clearError() {
    error.value = null
  }

  if (sessionStore.isDemo) {
    sessionStore.enterDemo()
  } else if (sessionStore.isRealAuthenticated && !sessionStore.user) {
    void fetchUser()
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isDoctor,
    login,
    register,
    fetchUser,
    refreshToken,
    logout,
    clearError,
    demoToken: DEMO_TOKEN,
  }
})
