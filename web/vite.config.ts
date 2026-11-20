import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

// No host address is hard-coded. Set VITE_API_PROXY_TARGET when the API runs on
// a reachable loopback (for example via an SSH tunnel to the dev VM).
const proxyTarget = process.env.VITE_API_PROXY_TARGET
const mediaProxyTarget = process.env.VITE_MEDIA_PROXY_TARGET

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '127.0.0.1',
    port: 55173,
    strictPort: true,
    proxy: proxyTarget || mediaProxyTarget
      ? {
          ...(proxyTarget
            ? { '/api': { target: proxyTarget, changeOrigin: false } }
            : {}),
          ...(mediaProxyTarget
            ? { '/audio': { target: mediaProxyTarget, changeOrigin: false } }
            : {}),
        }
      : undefined,
  },
  preview: { host: '127.0.0.1', port: 55173, strictPort: true },
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.spec.ts'],
    globals: false,
    restoreMocks: true,
  },
})
