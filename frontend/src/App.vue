<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, watch, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'

import { APP_NAME } from '@/config/branding'
import { currentLocale, t } from '@/i18n'
import { applyLegacyEnglish } from '@/i18n/legacy'

// 页面过渡动画名称
const transitionName = 'fade-up'
const route = useRoute()
let observer: MutationObserver | null = null
let sanitizing = false

async function sanitizeLegacyContent() {
  if (currentLocale.value !== 'en' || sanitizing) {
    return
  }

  sanitizing = true
  await nextTick()
  const appRoot = document.getElementById('app')
  if (appRoot) {
    applyLegacyEnglish(appRoot, currentLocale.value)
  }
  sanitizing = false
}

watchEffect(() => {
  const titleKey = (route.meta.titleKey as string | undefined) || 'routes.home'
  document.title = `${t(titleKey)} | ${APP_NAME}`
  document.documentElement.lang = currentLocale.value === 'zh-CN' ? 'zh-CN' : 'en'
})

watch(() => [route.fullPath, currentLocale.value], () => {
  sanitizeLegacyContent()
})

onMounted(() => {
  sanitizeLegacyContent()
  const appRoot = document.getElementById('app')
  if (!appRoot) return

  observer = new MutationObserver(() => {
    if (currentLocale.value === 'en' && !sanitizing) {
      sanitizeLegacyContent()
    }
  })

  observer.observe(appRoot, {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['placeholder', 'title', 'aria-label', 'value'],
  })
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <RouterView v-slot="{ Component, route: currentRoute }">
    <Transition :name="transitionName" mode="out-in">
      <component :is="Component" :key="`${currentRoute.path}-${currentLocale}`" />
    </Transition>
  </RouterView>
</template>

<style>
/* 全局页面过渡样式已在 main.css 中定义 */
</style>
