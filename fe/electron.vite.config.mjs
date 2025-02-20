import { resolve } from 'path'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        external: ['@electron-toolkit/utils'] // Sesuaikan dengan modul yang Anda gunakan
      }
    }
  },
  preload: {
    plugins: [externalizeDepsPlugin()],
    build: {
      rollupOptions: {
        external: ['@electron-toolkit/preload'] // Sesuaikan dengan modul yang Anda gunakan
      }
    }
  },
  renderer: {
    resolve: {
      alias: {
        '@': resolve('src/renderer/src') // Menggunakan alias '@' untuk kemudahan impor
      }
    },
    plugins: [react()],
    build: {
      rollupOptions: {
        input: {
          index: resolve(__dirname, 'src/renderer/index.html')
        },
        output: {
          assetFileNames: 'assets/[name].[hash][extname]'
        }
      },
      publicDir: resolve('src/renderer/src/assets'),
      assetsInlineLimit: 0
    }
  }
})
