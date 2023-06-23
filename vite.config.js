import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const fs = require('fs')
const packageJson = fs.readFileSync('./package.json')
const version = JSON.parse(packageJson).version || 0

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
  },
  define: {
    "__APP_VERSION__": JSON.stringify(version)
  }
});