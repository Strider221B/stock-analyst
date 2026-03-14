import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
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
    }
  }
})
