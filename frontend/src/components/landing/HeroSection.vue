<script setup lang="ts">
import { RouterLink } from 'vue-router'

import { t } from '@/i18n'
</script>

<template>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden bg-warmGray-50 pt-20">
    <!-- Animated Warning Stripes Background -->
    <div class="absolute inset-0 opacity-5 pointer-events-none">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImEiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTTAgNDBwNEBMMDQwIDAgMCAwIDAgNDBaIiBmaWxsPSIjMDAwIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2EpIi8+PC9zdmc+')]"></div>
    </div>

    <!-- Dynamic Wave Background (Simulating FFT Analysis) -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute bottom-0 left-0 right-0 h-[50vh] opacity-30">
        <!-- Wave 1 -->
        <svg class="absolute bottom-0 left-0 w-[200%] h-full animate-wave text-primary-200 fill-current" viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path d="M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
        <!-- Wave 2 -->
        <svg class="absolute bottom-0 left-0 w-[200%] h-full animate-wave text-primary-300 fill-current" style="animation-duration: 15s; animation-delay: -5s;" viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path d="M0,96L48,112C96,128,192,160,288,186.7C384,213,480,235,576,213.3C672,192,768,128,864,128C960,128,1056,192,1152,208C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>
    </div>

    <!-- Content -->
    <div class="container mx-auto px-4 z-10 relative">
      <div class="max-w-5xl mx-auto text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur border border-primary-100 rounded-full shadow-soft mb-8 animate-fade-in-up">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-primary-500"></span>
          </span>
          <span class="text-sm font-semibold text-gray-800 tracking-wide">{{ t('landing.badge') }}</span>
        </div>

        <!-- Headline -->
        <h1 class="text-6xl md:text-7xl lg:text-8xl font-bold text-gray-900 mb-8 leading-tight tracking-tight animate-fade-in-up" style="animation-delay: 100ms;">
          {{ t('landing.headlineLead') }}<span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-red-500">{{ t('landing.headlineHighlight') }}</span><br>
          <span class="relative inline-block">
            {{ t('landing.headlineTail') }}
            <svg class="absolute -bottom-2 left-0 w-full h-3 text-primary-400 opacity-50" viewBox="0 0 100 10" preserveAspectRatio="none">
              <path d="M0 5 Q 50 10 100 5" stroke="currentColor" stroke-width="4" fill="none" />
            </svg>
          </span>
        </h1>

        <!-- Subheadline -->
        <p class="text-xl md:text-2xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style="animation-delay: 200ms;">
          {{ t('landing.subheadline') }}
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-6 animate-fade-in-up" style="animation-delay: 300ms;">
          <RouterLink 
            to="/register" 
            class="group relative px-8 py-4 bg-gray-900 text-white rounded-2xl font-bold text-lg hover:shadow-glow-lg transition-all duration-300 overflow-hidden"
          >
            <div class="absolute inset-0 bg-gradient-to-r from-primary-600 to-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <span class="relative flex items-center gap-2">
              {{ t('landing.primaryCta') }}
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </span>
          </RouterLink>

          <button class="group px-8 py-4 bg-white text-gray-800 rounded-2xl font-bold text-lg border border-gray-200 hover:border-primary-200 hover:shadow-soft transition-all duration-300 flex items-center gap-3">
            <span class="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-primary-600 fill-current" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </span>
            {{ t('landing.secondaryCta') }}
          </button>
        </div>

        <!-- Technical Stats -->
        <div class="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto animate-fade-in-up" style="animation-delay: 400ms;">
          <div class="text-center p-4 rounded-2xl bg-white/50 backdrop-blur border border-white shadow-soft">
            <div class="text-3xl font-bold text-gray-900 mb-1">125<span class="text-lg text-primary-500">Hz</span></div>
            <div class="text-xs text-gray-500 font-medium uppercase tracking-wider">{{ t('landing.heroStatsSampling') }}</div>
          </div>
          <div class="text-center p-4 rounded-2xl bg-white/50 backdrop-blur border border-white shadow-soft">
            <div class="text-3xl font-bold text-gray-900 mb-1">0.1<span class="text-lg text-primary-500">g</span></div>
            <div class="text-xs text-gray-500 font-medium uppercase tracking-wider">{{ t('landing.heroStatsSensitivity') }}</div>
          </div>
          <div class="text-center p-4 rounded-2xl bg-white/50 backdrop-blur border border-white shadow-soft">
            <div class="text-3xl font-bold text-gray-900 mb-1">AI<span class="text-lg text-primary-500">+</span></div>
            <div class="text-xs text-gray-500 font-medium uppercase tracking-wider">{{ t('landing.heroStatsAi') }}</div>
          </div>
          <div class="text-center p-4 rounded-2xl bg-white/50 backdrop-blur border border-white shadow-soft">
            <div class="text-3xl font-bold text-gray-900 mb-1">24<span class="text-lg text-primary-500">h</span></div>
            <div class="text-xs text-gray-500 font-medium uppercase tracking-wider">{{ t('landing.heroStatsRealtime') }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
