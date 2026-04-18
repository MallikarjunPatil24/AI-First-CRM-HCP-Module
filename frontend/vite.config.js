import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Optional: proxy API calls during dev to avoid CORS issues
      // '/api': { target: 'http://localhost:8000', rewrite: (path) => path.replace(/^\/api/, '') }
    }
  }
})
