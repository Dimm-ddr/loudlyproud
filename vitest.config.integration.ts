import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    name: 'integration',
    environment: 'jsdom',
    include: ['tests/integration/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**'],
    globals: true,
    testTimeout: 10000,
    setupFiles: ['./tests/setup/integration.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './assets'),
      '@src': path.resolve(__dirname, './src'),
    },
  },
});
