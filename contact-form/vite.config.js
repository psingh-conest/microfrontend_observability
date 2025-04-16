import { defineConfig } from 'vite'
import preact from '@preact/preset-vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [preact()],
  build: {
    rollupOptions: {
      output: {
        entryFileNames: "index.js",
        assetFileNames: "index.[ext]",
      },
    }
  }
})
