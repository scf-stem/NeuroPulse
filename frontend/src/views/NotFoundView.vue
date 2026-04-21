<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-warmGray-50 via-primary-50/30 to-warmGray-100 flex items-center justify-center p-6 overflow-hidden relative">
    <!-- Decorative Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="floating-decoration w-[500px] h-[500px] bg-primary-200/40 -top-32 -right-32" style="animation-delay: 0s;"></div>
      <div class="floating-decoration w-[400px] h-[400px] bg-primary-100/50 bottom-0 -left-24" style="animation-delay: 2s;"></div>
      <div class="floating-decoration w-[300px] h-[300px] bg-lavender-200/30 top-1/3 left-1/4" style="animation-delay: 4s;"></div>
    </div>

    <div class="text-center relative z-10 animate-fade-in-up">
      <!-- Animated 404 Illustration -->
      <div class="mb-8 relative">
        <!-- Main 404 Number -->
        <div class="relative inline-block">
          <h1 class="text-[180px] md:text-[220px] font-black text-transparent bg-clip-text bg-gradient-to-br from-primary-400 via-primary-500 to-primary-600 leading-none select-none">
            404
          </h1>
          <!-- Floating decorative elements around 404 -->
          <div class="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/30 animate-bounce" style="animation-duration: 2s;">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="absolute -bottom-2 -right-2 w-10 h-10 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-xl flex items-center justify-center shadow-lg shadow-lavender-500/30 animate-pulse">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Friendly Illustration -->
      <div class="mb-8">
        <div class="w-32 h-32 mx-auto bg-gradient-to-br from-warmGray-100 to-warmGray-200 rounded-3xl flex items-center justify-center shadow-soft">
          <svg class="w-16 h-16 text-warmGray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
      </div>

      <!-- Message -->
      <div class="mb-10">
        <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
          迷路了？
        </h2>
        <p class="text-lg text-gray-500 max-w-md mx-auto leading-relaxed">
          抱歉，您访问的页面似乎已经搬家了。<br>
          别担心，让我们帮您找到回家的路。
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <RouterLink
          to="/"
          class="btn btn-primary px-8 py-3.5 text-lg shadow-lg shadow-primary-500/30 hover:shadow-xl hover:shadow-primary-500/40 transition-all duration-300"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          返回首页
        </RouterLink>
        <button
          @click="$router.back()"
          class="btn btn-secondary px-8 py-3.5 text-lg"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回上页
        </button>
      </div>

      <!-- Quick Links -->
      <div class="mt-12 pt-8 border-t border-warmGray-200/50">
        <p class="text-sm text-gray-400 mb-4">或者访问以下页面</p>
        <div class="flex flex-wrap justify-center gap-3">
          <RouterLink
            to="/dashboard"
            class="px-4 py-2 bg-white/80 hover:bg-white rounded-xl text-sm text-gray-600 hover:text-primary-600 shadow-sm hover:shadow transition-all duration-200"
          >
            仪表盘
          </RouterLink>
          <RouterLink
            to="/monitor"
            class="px-4 py-2 bg-white/80 hover:bg-white rounded-xl text-sm text-gray-600 hover:text-primary-600 shadow-sm hover:shadow transition-all duration-200"
          >
            实时监测
          </RouterLink>
          <RouterLink
            to="/history"
            class="px-4 py-2 bg-white/80 hover:bg-white rounded-xl text-sm text-gray-600 hover:text-primary-600 shadow-sm hover:shadow transition-all duration-200"
          >
            历史记录
          </RouterLink>
          <RouterLink
            to="/settings"
            class="px-4 py-2 bg-white/80 hover:bg-white rounded-xl text-sm text-gray-600 hover:text-primary-600 shadow-sm hover:shadow transition-all duration-200"
          >
            设置
          </RouterLink>
        </div>
      </div>

      <!-- Footer Branding -->
      <div class="mt-16 flex items-center justify-center gap-3 text-gray-400">
        <div class="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
        </div>
        <span class="text-sm">Neuro Pulse</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.floating-decoration {
  @apply absolute rounded-full blur-3xl;
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(5deg);
  }
}
</style>
