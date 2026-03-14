import { createApp } from 'vue'
import App from './App.vue'

// --- Vuetify ---
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
const vuetify = createVuetify()

// --- Pinia ---
import { createPinia } from 'pinia'
const pinia = createPinia()

// --- i18n ---
import { createI18n } from 'vue-i18n'
import pl from './locales/pl.json'
import en from './locales/en.json'

const i18n = createI18n({
  legacy: false, // Używamy Composition API we Vue 3
  locale: 'pl',  // Domyślny język
  fallbackLocale: 'en',
  messages: {
    pl,
    en
  }
})

// --- File-based Router ---
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from 'vue-router/auto-routes'
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// --- Inicjalizacja App ---
const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(i18n)
app.use(vuetify)

app.mount('#app')