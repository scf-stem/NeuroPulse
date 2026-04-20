<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { APP_NAME } from '@/config/branding'
import { t } from '@/i18n'

const isScrolled = ref(false)
const mobileMenuOpen = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const scrollToSection = (id: string) => {
  mobileMenuOpen.value = false
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<template>
  <nav
    :class="[
      'fixed top-0 left-0 right-0 z-50 transition-all duration-300 ease-in-out px-4 md:px-8 py-4',
      isScrolled ? 'bg-white/80 backdrop-blur-md shadow-soft' : 'bg-transparent'
    ]"
  >
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-3 group">
        <div class="relative">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <div class="absolute inset-0 bg-primary-400 rounded-xl animate-ping opacity-20"></div>
        </div>
        <div class="flex flex-col">
          <span class="text-xl font-bold text-gray-900 tracking-tight">{{ APP_NAME }}</span>
          <span class="text-[10px] text-gray-500 font-medium tracking-wider uppercase">{{ t('app.tagline') }}</span>
        </div>
      </RouterLink>

      <!-- Desktop Links -->
      <div class="hidden md:flex items-center gap-8">
        <button @click="scrollToSection('features')" class="text-gray-600 hover:text-primary-600 font-medium transition-colors">{{ t('nav.features') }}</button>
        <button @click="scrollToSection('technology')" class="text-gray-600 hover:text-primary-600 font-medium transition-colors">{{ t('nav.technology') }}</button>
        <button @click="scrollToSection('scale')" class="text-gray-600 hover:text-primary-600 font-medium transition-colors">{{ t('nav.severityScale') }}</button>
        
        <RouterLink to="/dashboard" class="text-gray-600 hover:text-primary-600 font-medium transition-colors">
          {{ t('nav.dashboardDemo') }}
        </RouterLink>
        <div class="h-6 w-px bg-gray-200"></div>
        <LanguageSwitcher />

        <RouterLink to="/login" class="text-gray-700 hover:text-primary-600 font-semibold transition-colors">
          {{ t('nav.signIn') }}
        </RouterLink>
        <RouterLink 
          to="/register" 
          class="bg-gray-900 hover:bg-primary-600 text-white px-5 py-2.5 rounded-full font-semibold transition-all duration-300 shadow-md hover:shadow-glow flex items-center gap-2"
        >
          {{ t('nav.getStarted') }}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </RouterLink>
      </div>

      <!-- Mobile Menu Button -->
      <button class="md:hidden p-2 text-gray-600" @click="mobileMenuOpen = !mobileMenuOpen">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    <div 
      v-show="mobileMenuOpen"
      class="md:hidden absolute top-full left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-gray-100 shadow-xl p-4 flex flex-col gap-4"
    >
      <button @click="scrollToSection('features')" class="text-left text-gray-600 font-medium p-2">{{ t('nav.features') }}</button>
      <button @click="scrollToSection('technology')" class="text-left text-gray-600 font-medium p-2">{{ t('nav.technology') }}</button>
      <button @click="scrollToSection('scale')" class="text-left text-gray-600 font-medium p-2">{{ t('nav.severityScale') }}</button>
      <div class="h-px bg-gray-100"></div>
      <div class="px-2 py-1">
        <LanguageSwitcher />
      </div>
      <RouterLink to="/login" class="text-center text-gray-700 font-semibold p-2">{{ t('nav.signIn') }}</RouterLink>
      <RouterLink to="/register" class="bg-primary-600 text-white text-center py-3 rounded-xl font-bold shadow-lg">
        {{ t('nav.getStarted') }}
      </RouterLink>
    </div>
  </nav>
</template>
