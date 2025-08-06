import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5001,
    proxy: {
      '/api': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/api-proxy': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api-proxy/, '/api'),
      },
      '/orchestrator': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/agent': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/context': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
      '/test': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
      },
    },
  },
}) 