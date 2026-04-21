/**
 * Tremor Guard - Vue Router
 * 震颤卫士 - 路由配置
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { LocationQuery, RouteRecordRaw } from 'vue-router'

import { getDemoIntent } from '@/demo'
import { pinia } from '@/stores'
import { useSessionStore } from '@/stores/session'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { titleKey: 'routes.home' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { titleKey: 'routes.login', guest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { titleKey: 'routes.register', guest: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { titleKey: 'routes.dashboard', requiresAuth: true }
  },
  {
    path: '/monitor',
    name: 'monitor',
    component: () => import('@/views/MonitorView.vue'),
    meta: { titleKey: 'routes.monitor', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/HistoryView.vue'),
    meta: { titleKey: 'routes.history', requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: () => import('@/views/AnalysisView.vue'),
    meta: { titleKey: 'routes.analysis', requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'ai-assistant',
    component: () => import('@/views/AIAssistantView.vue'),
    meta: { titleKey: 'routes.aiAssistant', requiresAuth: true }
  },
  {
    path: '/devices',
    name: 'devices',
    component: () => import('@/views/DevicesView.vue'),
    meta: { titleKey: 'routes.devices', requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'reports',
    component: () => import('@/views/ReportsView.vue'),
    meta: { titleKey: 'routes.reports', requiresAuth: true }
  },
  {
    path: '/medication',
    name: 'medication',
    component: () => import('@/views/MedicationView.vue'),
    meta: { titleKey: 'routes.medication', requiresAuth: true }
  },
  {
    path: '/health-profile',
    name: 'health-profile',
    component: () => import('@/views/HealthProfileView.vue'),
    meta: { titleKey: 'routes.healthProfile', requiresAuth: true }
  },
  {
    path: '/rehabilitation',
    name: 'rehabilitation',
    component: () => import('@/views/RehabilitationView.vue'),
    meta: { titleKey: 'routes.rehabilitation', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { titleKey: 'routes.settings', requiresAuth: true }
  },
  {
    path: '/test',
    name: 'test',
    component: () => import('@/views/TestView.vue'),
    meta: { titleKey: 'routes.test' }
  },
  {
    path: '/config',
    name: 'config',
    component: () => import('@/views/ConfigView.vue'),
    meta: { titleKey: 'routes.config' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { titleKey: 'routes.notFound' }
  }
]

function sanitizeRedirect(value: unknown) {
  if (typeof value !== 'string' || !value.startsWith('/')) {
    return null
  }

  return value
}

function withoutDemoQuery(query: LocationQuery) {
  const nextQuery = { ...query }
  delete nextQuery.demo
  return nextQuery
}

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach((to, _from, next) => {
  const sessionStore = useSessionStore(pinia)
  sessionStore.bootstrap()

  const demoIntent = getDemoIntent(to.query.demo)
  const cleanedQuery = withoutDemoQuery(to.query)
  const redirectTarget = sanitizeRedirect(to.query.redirect)

  if (demoIntent === false) {
    sessionStore.exitDemo()
    return next({ name: 'login', query: cleanedQuery })
  }

  if (demoIntent === true) {
    sessionStore.enterDemo()

    if (to.meta.guest) {
      return next(redirectTarget || { name: 'dashboard' })
    }

    return next({ path: to.path, query: cleanedQuery, hash: to.hash })
  }

  if (to.meta.requiresAuth && !sessionStore.hasAccess) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.guest && sessionStore.hasAccess) {
    return next(redirectTarget || { name: 'dashboard' })
  }

  return next()
})

export default router
