<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { APP_NAME } from '@/config/branding'
import { t } from '@/i18n'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const username = ref('')
const fullName = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const localError = ref('')
const isLoading = ref(false)
const agreeTerms = ref(false)

async function handleRegister() {
  localError.value = ''

  if (!agreeTerms.value) {
    localError.value = t('auth.errors.agreeTerms')
    return
  }

  if (password.value !== confirmPassword.value) {
    localError.value = t('auth.errors.passwordMismatch')
    return
  }

  if (password.value.length < 6) {
    localError.value = t('auth.errors.passwordLength')
    return
  }

  isLoading.value = true
  const success = await authStore.register(
    email.value,
    username.value,
    password.value,
    fullName.value || undefined
  )
  isLoading.value = false

  if (success) {
    const redirect = typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
      ? route.query.redirect
      : '/dashboard'
    router.push(redirect)
  }
}
</script>

<template>
  <div class="min-h-screen bg-warmGray-50 flex overflow-hidden">
    <!-- Decorative Background -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="floating-decoration w-[600px] h-[600px] bg-primary-200/30 -top-48 -left-48" style="animation-delay: 0s;"></div>
      <div class="floating-decoration w-[400px] h-[400px] bg-primary-100/40 bottom-0 -right-32" style="animation-delay: 3s;"></div>
    </div>

    <!-- Left Panel - Register Form -->
    <div class="flex-1 flex items-center justify-center p-8 relative z-10">
      <div class="w-full max-w-md">
        <!-- Mobile Logo -->
        <div class="text-center mb-8 lg:hidden">
          <RouterLink to="/" class="inline-flex items-center gap-3">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl shadow-soft flex items-center justify-center">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div class="text-left">
              <span class="text-2xl font-bold text-gradient">{{ APP_NAME }}</span>
              <p class="text-xs text-gray-400">{{ t('app.tagline') }}</p>
            </div>
          </RouterLink>
        </div>

        <!-- Register Card -->
        <div class="card !p-8">
          <div class="text-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">{{ t('auth.createTitle') }}</h2>
            <p class="text-gray-500">{{ t('auth.createSubtitle') }}</p>
          </div>

          <form @submit.prevent="handleRegister" class="space-y-4">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('auth.email') }} <span class="text-red-500">*</span>
              </label>
              <div class="input-group">
                <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  required
                  class="input"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            <!-- Username -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('auth.username') }} <span class="text-red-500">*</span>
              </label>
              <div class="input-group">
                <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  required
                  class="input"
                  :placeholder="t('auth.usernamePlaceholder')"
                />
              </div>
            </div>

            <!-- Full Name -->
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('auth.fullName') }} <span class="text-gray-400 text-xs">{{ t('auth.fullNameOptional') }}</span>
              </label>
              <div class="input-group">
                <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                </svg>
                <input
                  id="fullName"
                  v-model="fullName"
                  type="text"
                  class="input"
                  :placeholder="t('auth.fullNamePlaceholder')"
                />
              </div>
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('auth.passwordLabel') }} <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <div class="input-group">
                  <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <input
                    id="password"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    minlength="6"
                    class="input !pr-12"
                    :placeholder="t('auth.passwordMin')"
                  />
                </div>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Confirm Password -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1.5">
                {{ t('auth.confirmPassword') }} <span class="text-red-500">*</span>
              </label>
              <div class="input-group">
                <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  type="password"
                  required
                  class="input"
                  :placeholder="t('auth.confirmPasswordPlaceholder')"
                />
              </div>
            </div>

            <!-- Terms Agreement -->
            <div class="flex items-start gap-3 py-2">
              <input
                id="terms"
                v-model="agreeTerms"
                type="checkbox"
                class="mt-0.5 w-4 h-4 rounded border-warmGray-300 text-primary-600 focus:ring-primary-500"
              />
              <label for="terms" class="text-sm text-gray-600 leading-relaxed">
                {{ t('auth.agreePrefix') }}
                <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">服务条款</a>
                和
                <a href="#" class="text-primary-600 hover:text-primary-700 font-medium">隐私政策</a>
              </label>
            </div>

            <!-- Error Message -->
            <Transition name="fade-up">
              <div v-if="localError || authStore.error" class="alert alert-error !py-3">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm">{{ localError || authStore.error }}</span>
              </div>
            </Transition>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="isLoading || authStore.loading"
              class="btn btn-primary w-full py-3.5"
            >
              <svg v-if="isLoading || authStore.loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span v-if="isLoading || authStore.loading">{{ t('auth.creating') }}</span>
              <span v-else>{{ t('auth.createButton') }}</span>
            </button>
          </form>

          <!-- Divider -->
          <div class="relative my-6">
            <div class="divider"></div>
            <span class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-sm text-gray-400">
              {{ t('common.or') }}
            </span>
          </div>

          <!-- Login Link -->
          <p class="text-center text-gray-600">
            {{ t('auth.alreadyHaveAccount') }}
            <RouterLink to="/login" class="text-primary-600 hover:text-primary-700 font-semibold ml-1">
              {{ t('auth.signInLink') }}
            </RouterLink>
          </p>
        </div>

        <!-- Back to home -->
        <div class="text-center mt-6">
          <RouterLink to="/" class="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>{{ t('auth.backHome') }}</span>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Right Panel - Branding -->
    <div class="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 p-12 items-center justify-center">
      <!-- Decorative circles -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute w-96 h-96 bg-white/10 rounded-full -bottom-20 -right-20"></div>
        <div class="absolute w-64 h-64 bg-white/5 rounded-full top-20 left-10"></div>
        <div class="absolute w-32 h-32 bg-white/10 rounded-full bottom-1/2 right-1/3"></div>
      </div>

      <div class="relative z-10 max-w-md text-white">
        <!-- Logo -->
        <div class="flex items-center gap-4 mb-12">
          <div class="w-16 h-16 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <div>
            <h1 class="text-3xl font-bold">{{ APP_NAME }}</h1>
            <p class="text-white/70">{{ t('app.tagline') }}</p>
          </div>
        </div>

        <!-- Tagline -->
        <h2 class="text-4xl font-bold mb-6 leading-tight">
          {{ t('auth.createTitle') }}<br>
          {{ t('auth.createSubtitle') }}
        </h2>
        <p class="text-lg text-white/80 leading-relaxed mb-12">
          {{ t('auth.registerTrust') }}
        </p>

        <!-- Stats -->
        <div class="grid grid-cols-3 gap-6">
          <div class="text-center p-4 bg-white/10 rounded-2xl backdrop-blur">
            <div class="text-3xl font-bold">24/7</div>
            <div class="text-sm text-white/70 mt-1">Always-on</div>
          </div>
          <div class="text-center p-4 bg-white/10 rounded-2xl backdrop-blur">
            <div class="text-3xl font-bold">AI</div>
            <div class="text-sm text-white/70 mt-1">AI insight</div>
          </div>
          <div class="text-center p-4 bg-white/10 rounded-2xl backdrop-blur">
            <div class="text-3xl font-bold">100%</div>
            <div class="text-sm text-white/70 mt-1">Privacy-first</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
