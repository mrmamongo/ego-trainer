#!/usr/bin/env node
/** Bundle Svelte admin UI → ego_server/static/admin/ */

import * as esbuild from 'esbuild';
import sveltePlugin from 'esbuild-svelte';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, '..', 'ego_server', 'static', 'admin');
mkdirSync(outDir, { recursive: true });

const watch = process.argv.includes('--watch');

const options = {
  entryPoints: [join(__dirname, 'src', 'main.ts')],
  bundle: true,
  outfile: join(outDir, 'bundle.js'),
  format: 'iife',
  platform: 'browser',
  target: ['es2022'],
  sourcemap: false,
  logLevel: 'info',
  plugins: [
    sveltePlugin({
      compilerOptions: { css: 'injected' },
    }),
  ],
};

if (watch) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
  console.log('[admin-ui] watching…');
} else {
  await esbuild.build(options);
  console.log('[admin-ui] built');
}
