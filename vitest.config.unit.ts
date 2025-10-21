import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    name: 'unit',
    environment: 'jsdom',
    include: ['tests/unit/**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/public/**'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['assets/js/**/*.ts', 'src/**/*.ts'],
      exclude: ['**/*.test.ts', '**/vendor/**', '**/*.d.ts'],
    },
    setupFiles: ['./tests/setup/unit.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './assets'),
      '@src': path.resolve(__dirname, './src'),
    },
  },
});
