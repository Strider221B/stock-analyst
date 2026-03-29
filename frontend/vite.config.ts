import path from "path"
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: [
      { find: "@", replacement: path.resolve(__dirname, "src") },
    ],
  },
  // ---------------------------------------------------------
  // MANUALLY ADDED: Docker Network & HMR Configuration
  // ---------------------------------------------------------
  server: {
    host: true, // Listen on all network interfaces (0.0.0.0)
    port: 5173,
    strictPort: true,
    watch: {
      usePolling: true, // Forces Vite to actively check for file changes over the Docker volume
      interval: 1000,   // Check every 1 second
    },
    hmr: {
      clientPort: 5173, // Ensures the browser's websocket connects to the mapped host port
    },
    // ---------------------------------------------------------
    // THE FIX: Proxy API requests to the FastAPI backend
    // ---------------------------------------------------------
    proxy: {
      '/api': {
        // 'backend' is the service name from docker-compose.yml
        // '8000' is the internal port FastAPI is listening on
        target: process.env.PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    }
  }
})
