import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

import { DEMO_MODE_STORAGE_KEY } from '@/config/branding'
import { DEMO_TOKEN, demoUser } from '@/demo'
import type { User } from '@/types'

export type SessionLane = 'anonymous' | 'demo' | 'authenticated'

const AUTH_TOKEN_STORAGE_KEY = 'token'
const AUTH_USER_STORAGE_KEY = 'neuro-pulse-user'
const SESSION_LANE_STORAGE_KEY = 'neuro-pulse-session-lane'
const DEMO_SESSION_STORAGE_KEY = 'neuro-pulse-demo-session'

function hasWindow() {
  return typeof window !== 'undefined'
}

function cloneDemoUser(): User {
  return { ...demoUser }
}

function readStoredUser(): User | null {
  if (!hasWindow()) {
    return null
  }

  const stored = window.localStorage.getItem(AUTH_USER_STORAGE_KEY)
  if (!stored) {
    return null
  }

  try {
    return JSON.parse(stored) as User
  } catch {
    window.localStorage.removeItem(AUTH_USER_STORAGE_KEY)
    return null
  }
}

function getCurrentPath() {
  if (!hasWindow()) {
    return '/login'
  }

  const { pathname, search, hash } = window.location
  return `${pathname}${search}${hash}`
}

export const useSessionStore = defineStore('session', () => {
  const lane = ref<SessionLane>('anonymous')
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const bootstrapped = ref(false)

  const isDemo = computed(() => lane.value === 'demo')
  const isRealAuthenticated = computed(() => lane.value === 'authenticated' && !!token.value)
  const hasAccess = computed(() => lane.value === 'demo' || isRealAuthenticated.value)

  function persistState() {
    if (!hasWindow()) {
      return
    }

    const storage = window.localStorage
    storage.setItem(SESSION_LANE_STORAGE_KEY, lane.value)

    if (lane.value === 'demo') {
      storage.setItem(DEMO_MODE_STORAGE_KEY, '1')
      storage.setItem(DEMO_SESSION_STORAGE_KEY, '1')
      storage.removeItem(AUTH_TOKEN_STORAGE_KEY)
      storage.removeItem(AUTH_USER_STORAGE_KEY)
      return
    }

    storage.removeItem(DEMO_MODE_STORAGE_KEY)
    storage.removeItem(DEMO_SESSION_STORAGE_KEY)

    if (lane.value === 'authenticated' && token.value) {
      storage.setItem(AUTH_TOKEN_STORAGE_KEY, token.value)
      if (user.value) {
        storage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user.value))
      } else {
        storage.removeItem(AUTH_USER_STORAGE_KEY)
      }
      return
    }

    storage.removeItem(AUTH_TOKEN_STORAGE_KEY)
    storage.removeItem(AUTH_USER_STORAGE_KEY)
  }

  function applyState(nextLane: SessionLane, nextUser: User | null, nextToken: string | null) {
    lane.value = nextLane
    user.value = nextUser
    token.value = nextToken
    persistState()
  }

  function bootstrap() {
    if (bootstrapped.value) {
      return
    }

    if (!hasWindow()) {
      bootstrapped.value = true
      return
    }

    const storage = window.localStorage
    const storedLane = storage.getItem(SESSION_LANE_STORAGE_KEY)
    const demoEnabled = storage.getItem(DEMO_MODE_STORAGE_KEY) === '1'
    const demoSession = storage.getItem(DEMO_SESSION_STORAGE_KEY) === '1'
    const storedToken = storage.getItem(AUTH_TOKEN_STORAGE_KEY)
    const storedUser = readStoredUser()

    if (demoEnabled || demoSession || storedLane === 'demo') {
      applyState('demo', cloneDemoUser(), DEMO_TOKEN)
    } else if (storedToken || storedLane === 'authenticated') {
      applyState('authenticated', storedUser, storedToken)
    } else {
      applyState('anonymous', null, null)
    }

    bootstrapped.value = true
  }

  function ensureBootstrapped() {
    if (!bootstrapped.value) {
      bootstrap()
    }
  }

  function enterDemo() {
    ensureBootstrapped()
    applyState('demo', cloneDemoUser(), DEMO_TOKEN)
  }

  function exitDemo() {
    ensureBootstrapped()
    applyState('anonymous', null, null)
  }

  function loginSuccess(nextToken: string, nextUser: User) {
    ensureBootstrapped()
    applyState('authenticated', nextUser, nextToken)
  }

  function logout() {
    ensureBootstrapped()
    applyState('anonymous', null, null)
  }

  function invalidateRealSession() {
    ensureBootstrapped()

    if (lane.value === 'demo') {
      return {
        redirectToLogin: false,
        redirectPath: null as string | null,
      }
    }

    const redirectToLogin = lane.value === 'authenticated'
    const redirectPath = redirectToLogin ? getCurrentPath() : null
    applyState('anonymous', null, null)

    return {
      redirectToLogin,
      redirectPath,
    }
  }

  function updateUserSnapshot(nextUser: User | null) {
    user.value = nextUser
    if (lane.value === 'authenticated') {
      persistState()
    }
  }

  watch(user, () => {
    if (lane.value === 'authenticated') {
      persistState()
    }
  }, { deep: true })

  return {
    lane,
    user,
    token,
    bootstrapped,
    isDemo,
    isRealAuthenticated,
    hasAccess,
    bootstrap,
    ensureBootstrapped,
    enterDemo,
    exitDemo,
    loginSuccess,
    logout,
    invalidateRealSession,
    updateUserSnapshot,
  }
})
