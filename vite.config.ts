import { defineConfig } from 'vite'
import {resolve} from "path";
import tsconfigPaths from 'vite-tsconfig-paths';
import fs from 'fs';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    tsconfigPaths()
  ],
  root: resolve('./static/src'),
  base: '/static/',
  server: {
    host: 'localhost',
    port: 3000,
    open: false,
    watch: {
      usePolling: false,
    },
    https: {
      key: fs.readFileSync('./mkcert/key.pem'),
      cert: fs.readFileSync('./mkcert/cert.pem'),
    },
  },
  build: {
    outDir: resolve('./static/dist'),
    assetsDir: '',
    manifest: true,
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      input: {
        js: resolve('./static/src/js/main.tsx'),
        css: resolve('./static/src/css/main.css'),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  }
})
