<script setup lang="ts">
import { ref, computed } from 'vue'

import { t, tList } from '@/i18n'

const severity = ref(0)


const handleInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  severity.value = parseInt(target.value)
}

const severityLabels = computed(() => tList('landing.scaleLabels'))
const severityDescriptions = computed(() => tList('landing.scaleDescriptions'))

// Jitter Animation Classes based on severity
const jitterClass = computed(() => {
  if (severity.value === 0) return ''
  if (severity.value === 1) return 'animate-jitter-low'
  if (severity.value === 2) return 'animate-jitter-medium'
  if (severity.value === 3) return 'animate-jitter-high blur-sm-simulated' // Add ghosting
  return 'animate-jitter-chaos blur-md-simulated'
})

// Ring Colors (Reactive to severity)
const getRingStyle = (level: number) => {
  // If current severity >= ring level, the ring lights up
  const isActive = severity.value >= level
  
  if (!isActive) return 'border-gray-700/30' // Inactive state

  switch (level) {
    case 1: return 'border-green-500/50 shadow-[0_0_10px_rgba(34,197,94,0.3)]'
    case 2: return 'border-yellow-500/60 shadow-[0_0_15px_rgba(234,179,8,0.4)] animate-pulse-fast'
    case 3: return 'border-orange-500/70 shadow-[0_0_20px_rgba(249,115,22,0.5)] animate-pulse-fast'
    case 4: return 'border-red-500/80 shadow-[0_0_25px_rgba(239,68,68,0.6)] animate-flash'
    default: return 'border-gray-700'
  }
}

const colorClass = computed(() => {
  if (severity.value === 0) return 'text-green-500 bg-green-50 border-green-200'
  if (severity.value === 1) return 'text-lime-500 bg-lime-50 border-lime-200'
  if (severity.value === 2) return 'text-yellow-500 bg-yellow-50 border-yellow-200'
  if (severity.value === 3) return 'text-orange-500 bg-orange-50 border-orange-200'
  return 'text-red-500 bg-red-50 border-red-200'
})
</script>

<template>
  <section id="scale" class="py-24 bg-white relative overflow-hidden">
    <div class="container mx-auto px-4">
      <div class="text-center mb-16">
        <h2 class="text-4xl font-bold text-gray-900 mb-4">{{ t('landing.scaleTitle') }}</h2>
        <p class="text-gray-600 max-w-lg mx-auto">
          {{ t('landing.scaleBody') }}
        </p>
      </div>

      <div class="max-w-4xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        <!-- Control Panel -->
        <div class="space-y-8">
          <div class="bg-gray-50 rounded-3xl p-8 border border-gray-100 shadow-sm">
            <div class="flex justify-between items-end mb-6">
              <span class="text-lg font-bold text-gray-700">{{ t('landing.scaleIntensity') }}</span>
              <span class="text-3xl font-bold transition-colors" :class="colorClass.split(' ')[0]">{{ severity }}</span>
            </div>
            
            <input 
              type="range" 
              min="0" 
              max="4" 
              step="1" 
              v-model="severity"
              @input="handleInput"
              class="w-full h-4 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-800 hover:accent-black transition-all"
            >
            
            <div class="flex justify-between mt-3 text-xs text-gray-400 font-medium">
              <span>{{ t('landing.scaleStill') }}</span>
              <span>{{ t('landing.scaleMild') }}</span>
              <span>{{ t('landing.scaleModerate') }}</span>
              <span>{{ t('landing.scaleSevere') }}</span>
              <span>{{ t('landing.scaleExtreme') }}</span>
            </div>
          </div>

          <!-- Description Box -->
          <div 
            class="p-6 rounded-2xl border-2 transition-all duration-300 transform"
            :class="[colorClass, severity > 2 ? 'scale-105 shadow-md' : '']"
          >
            <h3 class="text-xl font-bold mb-2">{{ severityLabels[severity] }}</h3>
            <p class="opacity-90">{{ severityDescriptions[severity] }}</p>
          </div>
        </div>

        <!-- Visual Simulation (Target) -->
        <div class="relative h-96 bg-gray-900 rounded-[2.5rem] p-8 shadow-2xl overflow-hidden flex items-center justify-center border-4 border-gray-800">
           <!-- Grid Background -->
           <div class="absolute inset-0 opacity-10" style="background-image: linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px); background-size: 40px 40px;"></div>
           
           <div 
                class="relative w-80 h-80 flex items-center justify-center"
                :class="jitterClass"
           >
                <!-- Stability Rings (Static Targets -> Now Vibrating) -->
                <!-- Level 4 Zone (Red) Outline -->
                <div 
                    class="absolute w-72 h-72 rounded-full border-2 transition-all duration-300"
                    :class="getRingStyle(4)"
                ></div>
                <!-- Level 3 Zone (Orange) Outline -->
                <div 
                    class="absolute w-56 h-56 rounded-full border-2 transition-all duration-300"
                    :class="getRingStyle(3)"
                ></div>
                <!-- Level 2 Zone (Yellow) Outline -->
                <div 
                    class="absolute w-40 h-40 rounded-full border-2 transition-all duration-300"
                    :class="getRingStyle(2)"
                ></div>
                <!-- Level 1 Zone (Green) Outline -->
                <div 
                    class="absolute w-24 h-24 rounded-full border-2 transition-all duration-300"
                    :class="getRingStyle(1)"
                ></div>

                <!-- Crosshair -->
                <div class="absolute w-full h-[1px] bg-gray-700/50"></div>
                <div class="absolute h-full w-[1px] bg-gray-700/50"></div>

                <!-- The HAND (Dynamic Actor) -->
                <div 
                    class="relative z-10 w-24 h-24 text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]"
                    :class="jitterClass"
                >
                    <!-- Motion Blur Ghosts (Visible at high severity) -->
                    <div v-if="severity >= 3" class="absolute inset-0 text-white/30 animate-ghost-lag pointer-events-none">
                         <svg viewBox="0 0 24 24" fill="currentColor" class="w-full h-full"><path d="M12.75 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" /><path d="M16.25 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" /><path d="M9.25 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" /><path fill-rule="evenodd" d="M18.5 13.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .638-.088 1.254-.254 1.838a2.5 2.5 0 0 1-4.746 0 2.25 2.25 0 0 0-2.25-2.25H9.5a2.25 2.25 0 0 0-2.25 2.25 4 4 0 1 0 8 0c0 .414.336.75.75.75s.75-.336.75-.75a5.5 5.5 0 1 1-11 0 3.75 3.75 0 0 1 3.75-3.75h.25a.75.75 0 0 0 0-1.5h-.25a5.25 5.25 0 0 0-5.25 5.25c0 3.866 3.134 7 7 7s7-3.134 7-7ZM5.75 8a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 5.75 8Z" clip-rule="evenodd" /></svg>
                    </div>

                    <!-- Main Hand -->
                    <svg viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
                         <path d="M12.75 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" />
                         <path d="M16.25 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" />
                         <path d="M9.25 6.75a.75.75 0 0 0-1.5 0v5.5a.75.75 0 0 0 1.5 0v-5.5Z" />
                         <path fill-rule="evenodd" d="M18.5 13.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .638-.088 1.254-.254 1.838a2.5 2.5 0 0 1-4.746 0 2.25 2.25 0 0 0-2.25-2.25H9.5a2.25 2.25 0 0 0-2.25 2.25 4 4 0 1 0 8 0c0 .414.336.75.75.75s.75-.336.75-.75a5.5 5.5 0 1 1-11 0 3.75 3.75 0 0 1 3.75-3.75h.25a.75.75 0 0 0 0-1.5h-.25a5.25 5.25 0 0 0-5.25 5.25c0 3.866 3.134 7 7 7s7-3.134 7-7ZM5.75 8a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 5.75 8Z" clip-rule="evenodd" />
                    </svg>
                </div>
           </div>

           <!-- Warning Label -->
           <div v-if="severity > 0" class="absolute bottom-6 font-mono text-sm tracking-widest text-white/80 animate-pulse">
                {{ t('landing.scaleStatus') }}: <span :class="{'text-green-400': severity < 2, 'text-yellow-400': severity === 2, 'text-red-500': severity >= 3}">{{ severityLabels[severity] }}</span>
           </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Custom Chaotic Jitter Animations */
@keyframes jitter-low {
  0% { transform: translate(0,0); }
  25% { transform: translate(1px, 1px); }
  50% { transform: translate(-1px, 0); }
  75% { transform: translate(0, -1px); }
  100% { transform: translate(0,0); }
}

@keyframes jitter-medium {
  0% { transform: translate(0,0); }
  20% { transform: translate(2px, -2px); }
  40% { transform: translate(-2px, 2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(-2px, -2px); }
  100% { transform: translate(0,0); }
}

@keyframes jitter-high {
  0% { transform: translate(0,0); }
  10% { transform: translate(4px, -3px) rotate(1deg); }
  20% { transform: translate(-4px, 3px) rotate(-1deg); }
  30% { transform: translate(3px, 4px) rotate(1deg); }
  40% { transform: translate(-3px, -4px) rotate(-1deg); }
  50% { transform: translate(4px, 2px); }
  60% { transform: translate(-4px, -2px); }
  70% { transform: translate(2px, 4px); }
  80% { transform: translate(-2px, -4px); }
  90% { transform: translate(4px, -2px); }
  100% { transform: translate(0,0); }
}

@keyframes jitter-chaos {
  0% { transform: translate(0,0) rotate(0); }
  10% { transform: translate(-5px, 2px) rotate(-5deg); }
  20% { transform: translate(5px, -2px) rotate(5deg); }
  30% { transform: translate(-8px, 6px) rotate(-8deg); }
  40% { transform: translate(8px, -6px) rotate(8deg); }
  50% { transform: translate(-3px, 10px) rotate(-3deg); }
  60% { transform: translate(3px, -10px) rotate(3deg); }
  70% { transform: translate(7px, 5px) rotate(5deg); }
  80% { transform: translate(-7px, -5px) rotate(-5deg); }
  90% { transform: translate(2px, 8px) rotate(2deg); }
  100% { transform: translate(0,0) rotate(0); }
}

@keyframes ghost-lag {
    0% { transform: translate(0,0); opacity: 0.3; }
    50% { transform: translate(-10px, -5px); opacity: 0.1; }
    100% { transform: translate(0,0); opacity: 0.3; }
}

@keyframes flash-red {
    0%, 100% { border-color: rgba(239,68,68, 0.8); }
    50% { border-color: rgba(239,68,68, 1); box-shadow: 0 0 40px rgba(239,68,68, 0.8); }
}

.animate-jitter-low { 
    animation: jitter-low 0.5s linear infinite; 
    will-change: transform;
    transform: translateZ(0); 
    backface-visibility: hidden;
}
.animate-jitter-medium { 
    animation: jitter-medium 0.4s linear infinite;
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
}
.animate-jitter-high { 
    animation: jitter-high 0.2s linear infinite;
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
}
.animate-jitter-chaos { 
    animation: jitter-chaos 0.15s linear infinite;
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
}

.animate-ghost-lag {
    animation: ghost-lag 0.2s ease-in-out infinite;
}

.animate-flash {
    animation: flash-red 0.5s ease-in-out infinite;
}

.animate-pulse-fast {
    animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
/* Ensure tailwind pulse is available or redefine */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}
</style>
