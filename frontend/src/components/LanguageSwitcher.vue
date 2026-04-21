<script setup lang="ts">
import { computed } from 'vue'

import { useI18n } from '@/i18n'

const { locale, localeLabels, setLocale, t } = useI18n()

const locales = computed(() => Object.entries(localeLabels) as Array<['en' | 'zh-CN', string]>)
</script>

<template>
  <div
    class="inline-flex items-center gap-1 rounded-full border border-warmGray-200 bg-white/90 px-1 py-1 shadow-soft"
    :aria-label="t('common.language')"
  >
    <button
      v-for="[value, label] in locales"
      :key="value"
      type="button"
      class="rounded-full px-3 py-1.5 text-xs font-semibold transition-all"
      :class="
        locale === value
          ? 'bg-gray-900 text-white shadow-sm'
          : 'text-gray-500 hover:text-gray-800'
      "
      @click="setLocale(value)"
    >
      {{ label }}
    </button>
  </div>
</template>
