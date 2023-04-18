import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8080,
    strictPort: true,
    host: true
  },
  build: {
    rollupOptions: {
      output:
      {
        format: 'es',
        strict: false,
        entryFileNames: "[name].js",
        dir: 'dist/'
      }
    }
  }
});