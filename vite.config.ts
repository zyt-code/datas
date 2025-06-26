import { defineConfig } from 'vite';
import { resolve } from 'path';
import react from '@vitejs/plugin-react';
import electron from 'vite-plugin-electron';
import renderer from 'vite-plugin-electron-renderer';

export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        entry: 'src/main.ts',
        onstart(options) {
          options.startup()
        },
        vite: {
          build: {
            outDir: 'dist-electron',
            rollupOptions: {
              external: ['electron', 'mysql2'],
              input: {
                main: 'src/main.ts',
                ConnectionManager: 'src/backend/ConnectionManager.ts',
                QueryExecutor: 'src/backend/QueryExecutor.ts'
              },
              output: {
                format: 'cjs',
                entryFileNames: '[name].js'
              }
            }
          }
        }
      },
      {
        entry: 'src/preload.ts',
        onstart(options) {
          options.reload()
        },
        vite: {
          build: {
            outDir: 'dist-electron',
            rollupOptions: {
              external: ['electron'],
              output: {
                format: 'cjs'
              }
            }
          }
        }
      }
    ]),
    renderer()
  ],
  root: '.',
  publicDir: 'src/renderer/public',
  build: {
    outDir: 'dist-renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'src/renderer/index.html')
    }
  },
  server: {
    port: 3000
  }
});