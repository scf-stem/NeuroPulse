/**
 * Tremor Guard - Frontend Entry
 * 震颤卫士 - 前端入口
 */

import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { syncDemoModeFromLocation } from './demo'
import { initializeLocale } from './i18n'
import { pinia } from './stores'
import { useSessionStore } from './stores/session'

import './styles/main.css'
import './assets/animations.css'

initializeLocale()

const sessionStore = useSessionStore(pinia)
sessionStore.bootstrap()
syncDemoModeFromLocation(sessionStore)

const app = createApp(App)

app.use(pinia)
app.use(router)

app.mount('#app')
