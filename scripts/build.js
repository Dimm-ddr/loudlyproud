import * as esbuild from 'esbuild';
import { copy } from 'fs-extra';
import path from 'path';

// Copy Alpine.js to static directory
async function copyAlpineJs() {
  const source = path.resolve('node_modules/alpinejs/dist/cdn.js');
  const destination = path.resolve('static/js/alpine.js');
  await copy(source, destination);
  console.log('Alpine.js copied to static/js/');
}

const buildOptions = {
  entryPoints: [
    'src/js/accessibility-enhancements.ts',
    'src/js/filter-search.ts',
    'src/js/tag-helpers.ts'
  ],
  bundle: true,
  outdir: 'static/js',
  format: 'esm',
  sourcemap: true,
  target: ['es2020'],
  minify: process.env.NODE_ENV === 'production'
};

try {
  if (process.argv.includes('--watch')) {
    await copyAlpineJs();
    const ctx = await esbuild.context(buildOptions);
    await ctx.watch();
    console.log('Watching for changes...');
  } else {
    await copyAlpineJs();
    await esbuild.build(buildOptions);
    console.log('Build complete');
  }
} catch (err) {
  console.error('Build failed:', err);
  process.exit(1);
}
