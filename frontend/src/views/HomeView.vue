<script setup lang="ts">
import LandingNavigation from '@/components/landing/LandingNavigation.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import FeatureShowcase from '@/components/landing/FeatureShowcase.vue'
import InteractiveScale from '@/components/landing/InteractiveScale.vue'
import { APP_NAME } from '@/config/branding'
import { t } from '@/i18n'

// Intersection Observer for scroll reveal animations
import { onMounted } from 'vue'

onMounted(() => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active')
      }
    })
  }, { threshold: 0.1 })

  document.querySelectorAll('.reveal-up, .reveal-scale').forEach(el => observer.observe(el))
})
</script>

<template>
  <div class="min-h-screen bg-warmGray-50 overflow-x-hidden font-sans selection:bg-primary-100 selection:text-primary-900">
    <LandingNavigation />
    
    <main>
      <HeroSection />
      
      <div class="reveal-up relative z-20 -mt-20">
        <FeatureShowcase />
      </div>

      <div class="reveal-up">
        <InteractiveScale />
      </div>

      <!-- How it Works / CTA Section -->
      <section class="py-24 bg-gradient-to-br from-white to-warmGray-50 relative overflow-hidden">
        <!-- Background Glow -->
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary-100 rounded-full blur-[128px] opacity-40 pointer-events-none"></div>
        <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-lavender-100 rounded-full blur-[128px] opacity-40 pointer-events-none"></div>

        <div class="container mx-auto px-4 relative z-10 text-center">
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6 reveal-up">
            {{ t('landing.readyTitle') }}
          </h2>
          <p class="text-xl text-gray-600 mb-12 max-w-2xl mx-auto reveal-up delay-100">
            {{ t('landing.readyBody') }}
          </p>
          
          <div class="flex flex-col sm:flex-row justify-center gap-6 reveal-up delay-200">
            <RouterLink 
              to="/register" 
              class="px-10 py-5 bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white rounded-2xl font-bold text-xl shadow-glow transition-all hover:scale-105"
            >
              {{ t('landing.readyPrimary') }}
            </RouterLink>
            <RouterLink 
              to="/login"
              class="px-10 py-5 bg-white border border-gray-200 hover:border-primary-200 text-gray-700 hover:text-primary-600 rounded-2xl font-bold text-xl transition-all shadow-soft hover:shadow-lg"
            >
              {{ t('landing.readySecondary') }}
            </RouterLink>
          </div>
        </div>
      </section>
    </main>

    <footer class="bg-gray-900 border-t border-gray-800 text-gray-400 py-12">
      <div class="container mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-8">
          <div class="col-span-1 md:col-span-2">
            <div class="flex items-center gap-3 mb-4 text-white">
              <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <span class="text-xl font-bold">{{ APP_NAME }}</span>
            </div>
            <p class="max-w-xs text-sm">
              {{ t('landing.subheadline') }}
            </p>
          </div>
          
          <div>
            <h4 class="text-white font-bold mb-4">{{ t('landing.productHeading') }}</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.featureLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.hardwareLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.appLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.pricingLink') }}</a></li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-white font-bold mb-4">{{ t('landing.supportHeading') }}</h4>
            <ul class="space-y-2 text-sm">
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.helpLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.docsLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.contactLink') }}</a></li>
              <li><a href="#" class="hover:text-primary-400 transition-colors">{{ t('landing.privacyLink') }}</a></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center text-xs">
          <p>{{ t('landing.footerCopyright') }}</p>
          <div class="flex gap-4 mt-4 md:mt-0">
            <a href="#" class="hover:text-white transition-colors">Terms</a>
            <a href="#" class="hover:text-white transition-colors">Privacy</a>
            <a href="#" class="hover:text-white transition-colors">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
