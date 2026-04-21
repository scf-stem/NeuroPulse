<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import SpectrumChart from '@/components/charts/SpectrumChart.vue'
import { mockService } from '@/services/mock'
import { t } from '@/i18n'

const loading = ref(false)
const activeTab = ref('spectrum')

const spectrumData = ref<{ labels: string[], data: number[] }>({ labels: [], data: [] })

const analysisStats = ref({
    dominantFreq: 0,
    energy: 0,
    tremorScore: 0
})

function loadAnalysis() {
    loading.value = true
    setTimeout(() => {
        // Mock FFT Analysis
        const spectrum = mockService.generateSpectrumData(32)
        spectrumData.value = spectrum
        
        // Calculate stats
        const maxEnergyIndex = spectrum.data.indexOf(Math.max(...spectrum.data))
        analysisStats.value.dominantFreq = parseFloat(spectrum.labels[maxEnergyIndex])
        analysisStats.value.energy = spectrum.data.reduce((a, b) => a + b, 0)
        analysisStats.value.tremorScore = Math.min(100, Math.floor(analysisStats.value.energy * 50))
        
        loading.value = false
    }, 800)
}

onMounted(() => {
    loadAnalysis()
})
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">{{ t('analysis.title') }}</h1>
          <p class="text-gray-500 mt-1">{{ t('analysis.subtitle') }}</p>
        </div>
        <button @click="loadAnalysis" class="btn btn-primary btn-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ t('analysis.rerun') }}
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Analysis Stats -->
          <div class="lg:col-span-1 space-y-6">
              <div class="card">
                  <h3 class="text-lg font-bold text-gray-800 mb-4">{{ t('analysis.summary') }}</h3>
                  <div class="space-y-4">
                      <div class="bg-warmGray-50 rounded-xl p-4">
                          <p class="text-sm text-gray-500 mb-1">{{ t('analysis.dominantFreq') }}</p>
                          <p class="text-2xl font-bold text-primary-600">{{ analysisStats.dominantFreq.toFixed(1) }} Hz</p>
                          <p class="text-xs text-gray-400 mt-1">{{ t('analysis.typicalBand') }}</p>
                      </div>
                      <div class="bg-warmGray-50 rounded-xl p-4">
                          <p class="text-sm text-gray-500 mb-1">{{ t('analysis.tremorEnergy') }}</p>
                          <p class="text-2xl font-bold text-gray-800">{{ analysisStats.energy.toFixed(3) }}</p>
                      </div>
                      <div class="bg-warmGray-50 rounded-xl p-4">
                          <p class="text-sm text-gray-500 mb-1">{{ t('analysis.compositeScore') }}</p>
                          <div class="flex items-center gap-3">
                              <div class="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                                  <div class="h-full bg-gradient-to-r from-green-400 to-red-500" :style="{ width: `${analysisStats.tremorScore}%` }"></div>
                              </div>
                              <span class="font-bold text-gray-700">{{ analysisStats.tremorScore }}</span>
                          </div>
                      </div>
                  </div>
              </div>
              
              <div class="card bg-lavender-50 border border-lavender-100">
                  <div class="flex gap-3">
                      <div class="w-10 h-10 bg-lavender-200 rounded-full flex items-center justify-center flex-shrink-0 text-lavender-700">
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                      </div>
                      <div>
                          <h4 class="font-bold text-gray-800 text-sm">{{ t('analysis.aiInsightTitle') }}</h4>
                          <p class="text-sm text-gray-600 mt-1 leading-relaxed">
                              {{ t('analysis.aiInsightBody') }}
                          </p>
                      </div>
                  </div>
              </div>
          </div>

          <!-- Charts -->
          <div class="lg:col-span-2">
              <div class="card h-full">
                  <div class="flex items-center gap-4 mb-6 border-b border-warmGray-100 pb-2">
                      <button 
                        @click="activeTab = 'spectrum'"
                        class="px-4 py-2 font-medium text-sm transition-colors relative"
                        :class="activeTab === 'spectrum' ? 'text-primary-600' : 'text-gray-500 hover:text-gray-700'"
                      >
                          {{ t('analysis.spectrumTab') }}
                          <div v-if="activeTab === 'spectrum'" class="absolute bottom-0 inset-x-0 h-0.5 bg-primary-500 rounded-t-full"></div>
                      </button>
                      <button 
                        @click="activeTab = 'wave'"
                        class="px-4 py-2 font-medium text-sm transition-colors relative"
                        :class="activeTab === 'wave' ? 'text-primary-600' : 'text-gray-500 hover:text-gray-700'"
                      >
                          {{ t('analysis.waveformTab') }}
                          <div v-if="activeTab === 'wave'" class="absolute bottom-0 inset-x-0 h-0.5 bg-primary-500 rounded-t-full"></div>
                      </button>
                  </div>
                  
                  <div class="h-80" v-if="loading">
                      <div class="w-full h-full flex flex-col items-center justify-center text-gray-400">
                          <svg class="w-10 h-10 animate-spin mb-3 text-primary-200" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                          </svg>
                          {{ t('analysis.analyzing') }}
                      </div>
                  </div>

                  <div v-else class="h-full">
                       <SpectrumChart v-if="activeTab === 'spectrum'" :labels="spectrumData.labels" :data="spectrumData.data" />
                       <div v-else class="flex items-center justify-center h-64 text-gray-400 bg-warmGray-50 rounded-xl border border-dashed border-warmGray-200">
                           {{ t('analysis.noWaveform') }}
                       </div>
                  </div>
              </div>
          </div>
      </div>
    </div>
  </AppLayout>
</template>
