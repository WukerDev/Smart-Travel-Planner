import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueRouter from 'unplugin-vue-router/vite'
import vuetify from 'vite-plugin-vuetify'

export default defineConfig({
  plugins: [
    VueRouter({
      /* Opcje routera - trasy będą automatycznie czytane z folderu src/pages */
    }),
    vue(),
    vuetify({ autoImport: true }), // Automatyczne importowanie komponentów Vuetify
  ],
    server: {
    fs: {
      allow: [
        '.',
        '..',
      ],
    },
  },
})