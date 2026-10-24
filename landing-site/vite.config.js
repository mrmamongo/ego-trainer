import { defineConfig } from 'vite';

const upstream = 'https://cogito.born-in-july.ru';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    proxy: {
      '/extension': { target: upstream, changeOrigin: true },
      '/student': { target: upstream, changeOrigin: true },
      '/panel': { target: upstream, changeOrigin: true },
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
});
