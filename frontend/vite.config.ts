import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: [
      'vision.dyai.cloud',
      'kanban.vision.dyai.cloud',
      'graph.vision.dyai.cloud',
      'obsidian.vision.dyai.cloud',
      '.dyai.cloud',
      '.railway.app'
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  },
  preview: {
    host: true,
    allowedHosts: true
  }
})
