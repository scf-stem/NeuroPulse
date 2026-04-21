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
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)

async function handleLogin() {
  isLoading.value = true
  const success = await authStore.login(email.value, password.value)
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
      <div class="floating-decoration w-[600px] h-[600px] bg-primary-200/30 -top-48 -right-48" style="animation-delay: 0s;"></div>
      <div class="floating-decoration w-[400px] h-[400px] bg-primary-100/40 bottom-0 -left-32" style="animation-delay: 3s;"></div>
    </div>

    <!-- Left Panel - Branding -->
    <div class="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-primary-500 via-primary-600 to-primary-700 p-12 items-center justify-center">
      <!-- Decorative circles -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute w-96 h-96 bg-white/10 rounded-full -top-20 -left-20"></div>
        <div class="absolute w-64 h-64 bg-white/5 rounded-full bottom-20 right-10"></div>
        <div class="absolute w-32 h-32 bg-white/10 rounded-full top-1/2 left-1/3"></div>
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
          {{ t('auth.signInTitle') }}
        </h2>
        <p class="text-lg text-white/80 leading-relaxed">
          {{ t('auth.signInSubtitle') }}
        </p>

        <!-- Features list -->
        <div class="mt-12 space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span>{{ t('auth.registerFeatureOne') }}</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span>{{ t('auth.registerFeatureTwo') }}</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span>{{ t('auth.registerFeatureThree') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel - Login Form -->
    <div class="flex-1 flex items-center justify-center p-8 relative z-10">
      <div class="w-full max-w-md">
        <!-- Mobile Logo -->
        <div class="text-center mb-10 lg:hidden">
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

        <!-- Login Card -->
        <div class="card !p-8">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">{{ t('auth.signInFormTitle') }}</h2>
            <p class="text-gray-500">{{ t('auth.signInFormBody') }}</p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('auth.accountLabel') }}
              </label>
              <div class="input-group">
                <svg class="input-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <input
                  id="email"
                  v-model.trim="email"
                  type="text"
                  required
                  class="input"
                  :placeholder="t('auth.accountPlaceholder')"
                />
              </div>
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                {{ t('auth.passwordLabel') }}
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
                    class="input !pr-12"
                    :placeholder="t('auth.passwordPlaceholder')"
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

            <!-- Remember me & Forgot password -->
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" class="w-4 h-4 rounded border-warmGray-300 text-primary-600 focus:ring-primary-500" />
                <span class="text-sm text-gray-600">{{ t('auth.rememberMe') }}</span>
              </label>
              <a href="#" class="text-sm text-primary-600 hover:text-primary-700 font-medium">
                {{ t('auth.forgotPassword') }}
              </a>
            </div>

            <!-- Error Message -->
            <Transition name="fade-up">
              <div v-if="authStore.error" class="alert alert-error !py-3">
                <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm">{{ authStore.error }}</span>
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
              <span v-if="isLoading || authStore.loading">{{ t('auth.signingIn') }}</span>
              <span v-else>{{ t('auth.signInButton') }}</span>
            </button>
          </form>

          <!-- Divider -->
          <div class="relative my-8">
            <div class="divider"></div>
            <span class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-4 text-sm text-gray-400">
              {{ t('common.or') }}
            </span>
          </div>

          <!-- Register Link -->
          <p class="text-center text-gray-600">
            {{ t('auth.noAccount') }}
            <RouterLink to="/register" class="text-primary-600 hover:text-primary-700 font-semibold ml-1">
              {{ t('auth.createAccountLink') }}
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
  </div>
</template>
