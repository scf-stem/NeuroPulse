<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { APP_NAME } from '@/config/branding'
import { t } from '@/i18n'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarOpen = ref(true)
const userMenuOpen = ref(false)

const menuItems = computed(() => [
  { name: t('layout.menu.dashboard'), path: '/dashboard', icon: 'dashboard' },
  { name: t('layout.menu.monitor'), path: '/monitor', icon: 'monitor' },
  { name: t('layout.menu.history'), path: '/history', icon: 'history' },
  { name: t('layout.menu.analysis'), path: '/analysis', icon: 'analysis' },
  { name: t('layout.menu.aiAssistant'), path: '/ai-assistant', icon: 'ai' },
  { name: t('layout.menu.medication'), path: '/medication', icon: 'medication' },
  { name: t('layout.menu.healthProfile'), path: '/health-profile', icon: 'health' },
  { name: t('layout.menu.rehabilitation'), path: '/rehabilitation', icon: 'rehabilitation' },
  { name: t('layout.menu.devices'), path: '/devices', icon: 'devices' },
  { name: t('layout.menu.reports'), path: '/reports', icon: 'reports' },
  { name: t('layout.menu.config'), path: '/config', icon: 'config' },
  { name: t('layout.menu.settings'), path: '/settings', icon: 'settings' },
])

const currentPath = computed(() => route.path)

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

// 获取当前时间的问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return t('layout.welcome')
  if (hour < 12) return t('layout.welcome')
  if (hour < 14) return t('layout.welcome')
  if (hour < 18) return t('layout.welcome')
  return t('layout.welcome')
})
</script>

<template>
  <div class="min-h-screen bg-warmGray-50 flex">
    <!-- Decorative background elements -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="floating-decoration w-96 h-96 bg-primary-200 -top-48 -right-48" style="animation-delay: 0s;"></div>
      <div class="floating-decoration w-64 h-64 bg-primary-100 top-1/3 -left-32" style="animation-delay: 2s;"></div>
      <div class="floating-decoration w-80 h-80 bg-primary-50 bottom-0 right-1/4" style="animation-delay: 4s;"></div>
    </div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-72 transform transition-all duration-300 ease-out lg:relative lg:translate-x-0',
        'bg-white/80 backdrop-blur-xl shadow-soft-lg',
        'rounded-r-3xl',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo Area -->
      <div class="h-20 flex items-center justify-center px-6">
        <RouterLink to="/dashboard" class="flex items-center space-x-3 group">
          <!-- Animated Logo Icon -->
          <div class="relative">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl shadow-soft flex items-center justify-center transform transition-transform group-hover:scale-105 group-hover:rotate-3">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <!-- Pulse effect -->
            <div class="absolute inset-0 bg-primary-400 rounded-2xl animate-ping opacity-20"></div>
          </div>
          <div>
            <span class="text-xl font-bold text-gradient">{{ APP_NAME }}</span>
            <p class="text-xs text-gray-400">{{ t('app.tagline') }}</p>
          </div>
        </RouterLink>
      </div>

      <!-- Divider -->
      <div class="mx-6 divider"></div>

      <!-- Navigation -->
      <nav class="mt-6 px-4 space-y-1.5 flex-1 overflow-y-auto scrollbar-hide">
        <RouterLink
          v-for="(item, index) in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'nav-item group',
            currentPath === item.path ? 'active' : ''
          ]"
          :style="{ animationDelay: `${index * 50}ms` }"
        >
          <!-- Icons based on type -->
          <div class="nav-icon">
            <svg v-if="item.icon === 'dashboard'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <svg v-else-if="item.icon === 'monitor'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <svg v-else-if="item.icon === 'history'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="item.icon === 'analysis'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <svg v-else-if="item.icon === 'ai'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <svg v-else-if="item.icon === 'devices'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <svg v-else-if="item.icon === 'reports'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <!-- 用药管理图标 -->
            <svg v-else-if="item.icon === 'medication'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
            <!-- 健康档案图标 -->
            <svg v-else-if="item.icon === 'health'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <!-- 运动康复图标 -->
            <svg v-else-if="item.icon === 'rehabilitation'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="item.icon === 'config'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <svg v-else-if="item.icon === 'settings'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span class="font-medium">{{ item.name }}</span>
          <!-- Active indicator -->
          <div
            v-if="currentPath === item.path"
            class="absolute right-3 w-1.5 h-1.5 bg-white rounded-full"
          ></div>
        </RouterLink>
      </nav>

      <!-- User Info Card -->
      <div class="p-4 mt-auto">
        <div class="card-gradient !p-4 relative">
          <div class="flex items-center">
            <!-- Avatar with gradient border -->
            <div class="relative">
              <div class="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 p-0.5">
                <div class="w-full h-full bg-white rounded-full flex items-center justify-center">
                  <span class="text-lg font-bold text-gradient">
                    {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
                  </span>
                </div>
              </div>
              <!-- Online indicator -->
              <div class="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-mint-500 rounded-full border-2 border-white"></div>
            </div>

            <div class="ml-3 flex-1 min-w-0">
              <p class="font-semibold text-gray-800 truncate">
                {{ authStore.user?.username || 'demo' }}
              </p>
              <p class="text-xs text-gray-500 truncate">{{ authStore.user?.email }}</p>
            </div>

            <!-- User menu button -->
            <button
              @click="toggleUserMenu"
              class="btn btn-ghost btn-icon !p-2"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
          </div>

          <!-- User dropdown menu -->
          <Transition name="scale">
            <div
              v-if="userMenuOpen"
              class="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-xl shadow-soft-lg border border-warmGray-100 py-2 overflow-hidden"
            >
              <RouterLink
                to="/settings"
                class="dropdown-item"
                @click="userMenuOpen = false"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>{{ t('common.profile') }}</span>
              </RouterLink>
              <div class="divider mx-2 my-1"></div>
              <button
                @click="handleLogout"
                class="dropdown-item w-full text-red-600 hover:bg-red-50 hover:text-red-700"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>{{ t('common.logout') }}</span>
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </aside>

    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-40 lg:hidden"
        @click="sidebarOpen = false"
      ></div>
    </Transition>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 relative">
      <!-- Top Header -->
      <header class="h-20 glass rounded-b-2xl mx-4 mt-0 flex items-center justify-between px-6 shadow-soft sticky top-0 z-30">
        <!-- Left side -->
        <div class="flex items-center gap-4">
          <!-- Mobile menu button -->
          <button
            @click="toggleSidebar"
            class="btn btn-ghost btn-icon lg:hidden"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Greeting -->
          <div class="hidden sm:block">
            <p class="text-lg font-semibold text-gray-800">
              {{ greeting }}, {{ authStore.user?.username || 'demo' }}
            </p>
            <p class="text-sm text-gray-500">{{ t('layout.welcomeSubtext') }}</p>
          </div>
        </div>

        <!-- Right side items -->
        <div class="flex items-center gap-3">
          <LanguageSwitcher />
          <!-- Search button -->
          <button class="btn btn-ghost btn-icon hidden sm:flex" :title="t('layout.search')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>

          <!-- Notifications -->
          <button class="btn btn-ghost btn-icon relative" :title="t('layout.notifications')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <!-- Notification badge -->
            <span class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
              3
            </span>
          </button>

          <!-- Quick actions -->
          <RouterLink to="/monitor" class="btn btn-primary btn-sm hidden md:flex">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{{ t('layout.monitoringShortcut') }}</span>
          </RouterLink>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-auto p-4 lg:p-6">
        <slot></slot>
      </main>

    </div>

    <!-- Click outside to close user menu -->
    <div
      v-if="userMenuOpen"
      class="fixed inset-0 z-30"
      @click="userMenuOpen = false"
    ></div>
  </div>
</template>

<style scoped>
/* Sidebar animation on load */
.nav-item {
  opacity: 0;
  animation: fadeInUp 0.4s ease-out forwards;
}

/* User card hover effect */
.card-gradient::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(249, 115, 22, 0.05) 100%);
  border-radius: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-gradient:hover::before {
  opacity: 1;
}
</style>
