import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    outDir: '../web',  // Build 输出到上级 web/ 目录
    emptyOutDir: true, // Build 前清空目标目录
    chunkSizeWarningLimit: 1000, // 提高 chunk 大小警告阈值（1MB）
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router'],
          'element-plus': ['element-plus'],
          'fullcalendar': ['@fullcalendar/core', '@fullcalendar/vue3', '@fullcalendar/daygrid'],
        },
      },
    },
  },
})
