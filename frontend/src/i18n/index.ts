import { computed, ref } from 'vue'

import { LOCALE_STORAGE_KEY } from '@/config/branding'
import { translateLegacyText } from './legacy'
import { defaultLocale, localeLabels, messages, type Locale } from './messages'

function normalizeLocale(locale?: string | null): Locale {
  if (locale === 'zh-CN' || locale === 'zh' || locale === 'zh_CN') {
    return 'zh-CN'
  }
  return 'en'
}

function loadStoredLocale(): Locale {
  if (typeof window === 'undefined') {
    return defaultLocale
  }
  return normalizeLocale(window.localStorage.getItem(LOCALE_STORAGE_KEY))
}

function deepGet(source: Record<string, unknown>, key: string): unknown {
  return key.split('.').reduce<unknown>((current, part) => {
    if (!current || typeof current !== 'object') {
      return undefined
    }
    return (current as Record<string, unknown>)[part]
  }, source)
}

function interpolate(template: string, params?: Record<string, string | number>): string {
  if (!params) {
    return template
  }

  return Object.entries(params).reduce((value, [paramKey, paramValue]) => {
    return value.split(`{${paramKey}}`).join(String(paramValue))
  }, template)
}

export const currentLocale = ref<Locale>(loadStoredLocale())

export function setLocale(locale: Locale) {
  currentLocale.value = normalizeLocale(locale)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, currentLocale.value)
    document.documentElement.lang = currentLocale.value === 'zh-CN' ? 'zh-CN' : 'en'
  }
}

export function initializeLocale() {
  setLocale(loadStoredLocale())
}

export function t(key: string, params?: Record<string, string | number>): string {
  const dictionary = messages[currentLocale.value] as Record<string, unknown>
  const fallbackDictionary = messages[defaultLocale] as Record<string, unknown>
  const value = deepGet(dictionary, key) ?? deepGet(fallbackDictionary, key)

  if (typeof value === 'string') {
    return interpolate(value, params)
  }

  return key
}

export function tList(key: string): string[] {
  const dictionary = messages[currentLocale.value] as Record<string, unknown>
  const fallbackDictionary = messages[defaultLocale] as Record<string, unknown>
  const value = deepGet(dictionary, key) ?? deepGet(fallbackDictionary, key)
  return Array.isArray(value) ? (value as string[]) : []
}

export function tm<T = unknown>(key: string): T | undefined {
  const dictionary = messages[currentLocale.value] as Record<string, unknown>
  const fallbackDictionary = messages[defaultLocale] as Record<string, unknown>
  return (deepGet(dictionary, key) ?? deepGet(fallbackDictionary, key)) as T | undefined
}

export function localeDateCode() {
  return currentLocale.value === 'zh-CN' ? 'zh-CN' : 'en-US'
}

export function formatDate(value: string | Date, options?: Intl.DateTimeFormatOptions) {
  const date = value instanceof Date ? value : new Date(value)
  return date.toLocaleDateString(localeDateCode(), options)
}

export function formatDateTime(value: string | Date, options?: Intl.DateTimeFormatOptions) {
  const date = value instanceof Date ? value : new Date(value)
  return date.toLocaleString(localeDateCode(), options)
}

export function formatRelativeMinutes(count: number) {
  return currentLocale.value === 'zh-CN'
    ? t('devices.lastSeenMinutes', { count })
    : t('devices.lastSeenMinutes', { count })
}

export function severityLabel(level: number) {
  return t(`severity.${level}`) || t('severity.unknown')
}

export function localeText(en: string, zh: string) {
  return currentLocale.value === 'zh-CN' ? zh : en
}

export function legacyT(input: string) {
  return translateLegacyText(input, currentLocale.value)
}

export function useI18n() {
  return {
    locale: computed(() => currentLocale.value),
    localeLabels,
    setLocale,
    t,
    tList,
    tm,
    localeText,
    legacyT,
  }
}
