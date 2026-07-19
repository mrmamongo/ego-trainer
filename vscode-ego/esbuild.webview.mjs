#!/usr/bin/env node
/** Bundle Svelte webviews → out/webview/*.js (ADR-0015). */

import * as esbuild from 'esbuild';
import sveltePlugin from 'esbuild-svelte';
import { readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const watch = process.argv.includes('--watch');
const webviewDir = join(__dirname, 'src', 'webview');

/** Entry points: src/webview/*.ts (not *.d.ts, not shared/). */
const entryPoints = readdirSync(webviewDir)
  .filter((f) => f.endsWith('.ts') && !f.endsWith('.d.ts'))
  .map((f) => join(webviewDir, f));

if (entryPoints.length === 0) {
  console.error('No webview entry points found in src/webview/*.ts');
  process.exit(1);
}

const options = {
  entryPoints,
  bundle: true,
  outdir: join(__dirname, 'out', 'webview'),
  format: 'iife',
  platform: 'browser',
  target: ['es2022'],
  sourcemap: true,
  logLevel: 'info',
  plugins: [
    sveltePlugin({
      compilerOptions: {
        css: 'injected',
      },
    }),
  ],
};

if (watch) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
  console.log('[webview] watching…');
} else {
  await esbuild.build(options);
  console.log(`[webview] built ${entryPoints.length} bundle(s)`);
}
