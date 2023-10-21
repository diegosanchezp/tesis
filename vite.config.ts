import { defineConfig, UserConfig } from 'vite'
import {resolve} from "path";
import tsconfigPaths from 'vite-tsconfig-paths';
import fs from 'fs';
import {getInputFiles} from './vite/vite_utils'

// https://vitejs.dev/config/
const baseconfig: UserConfig = {
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
  },
  build: {
    outDir: resolve('./static/dist'),
    assetsDir: '',
    manifest: true,
    emptyOutDir: true,
    // es2017 is required by alpine
    // https://github.com/alpinejs/alpine/discussions/2487
    target: 'es2017',
    rollupOptions: {
      input: [
        ...getInputFiles(resolve("./static/src/js")),
        ...getInputFiles(resolve("./static/src/css"))
      ],
      output: {
        chunkFileNames: undefined,
      },
    },
  }
}

// https://vitejs.dev/config/#conditional-config
export default defineConfig(({ command, mode, ssrBuild })=>{

  // dev specific config
  console.log(command);
  if (command === 'serve') {
    return {
      ...baseconfig,
      server: {
        ...baseconfig.server,
        // Add https configuration
        https: {
          key: fs.readFileSync('./mkcert/key.pem'),
          cert: fs.readFileSync('./mkcert/cert.pem'),
        },
      }
    };
  } else {
    // command === 'build'
    // build specific config
    return baseconfig;
  }
})
