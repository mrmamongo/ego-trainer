#!/usr/bin/env node
/** Bundle Svelte admin UI → ego_server/static/admin/ */

import * as esbuild from 'esbuild';
import sveltePlugin from 'esbuild-svelte';
import { mkdirSync, copyFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, '..', 'ego_server', 'static', 'admin');
mkdirSync(outDir, { recursive: true });
copyFileSync(join(__dirname, 'node_modules', 'monaco-editor', 'LICENSE'), join(outDir, 'monaco.LICENSE.txt'));

const watch = process.argv.includes('--watch');

const options = {
  entryPoints: [join(__dirname, 'src', 'main.ts')],
  bundle: true,
  outfile: join(outDir, 'bundle.js'),
  format: 'iife',
  platform: 'browser',
  target: ['es2022'],
  minify: !watch,
  assetNames: 'assets/[name]-[hash]',
  loader: { '.ttf': 'file', '.woff': 'file', '.woff2': 'file' },
  sourcemap: false,
  logLevel: 'info',
  plugins: [
    sveltePlugin({
      compilerOptions: { css: 'injected' },
    }),
  ],
};

const workerOptions = {
  entryPoints: [join(__dirname, 'node_modules', 'monaco-editor', 'esm', 'vs', 'editor', 'editor.worker.js')],
  bundle: true,
  outdir: join(outDir, 'workers'),
  entryNames: 'editor.worker',
  format: 'esm',
  platform: 'browser',
  target: ['es2022'],
  minify: !watch,
  logLevel: 'info',
};

if (watch) {
  const ctx = await esbuild.context(options);
  const workerCtx = await esbuild.context(workerOptions);
  await ctx.watch();
  await workerCtx.watch();
  console.log('[admin-ui] watching…');
} else {
  await esbuild.build(options);
  await esbuild.build(workerOptions);
  console.log('[admin-ui] built');
}
