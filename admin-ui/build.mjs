#!/usr/bin/env node
/**
 * Bundle Svelte admin UI → ego_server/static/admin/
 *
 * Output (all of it is shipped in the wheel and the Docker image):
 *   theme.css            Tailwind build of src/theme.css (themed admin + IDE)
 *   bundle.css/js        mentor/admin panel (/panel)
 *   ide.css/js           browser IDE (/ide)
 *   workers/             Monaco workers loaded at runtime by URL
 *   assets/              fonts/images emitted by the loaders above
 *   *.LICENSE.txt        vendored licenses (Monaco, shadcn-svelte)
 *
 * The generated files stay in git so that builds from git-only sources (the
 * Docker "web" stage copies tracked files) always have a baseline; every run
 * overwrites them, and CI fails when a committed copy drifts (see
 * `node build.mjs --check`).
 */

import * as esbuild from 'esbuild';
import sveltePlugin from 'esbuild-svelte';
import { existsSync, mkdirSync, copyFileSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { dirname, join, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync, spawn } from 'node:child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, '..', 'ego_server', 'static', 'admin');
// Generated subdirectories: recreated on each build so no stale hashed
// filenames survive (an old asset left behind hides a broken reference).
const generatedDirs = ['assets', 'workers'].map((name) => join(outDir, name));
mkdirSync(outDir, { recursive: true });

const watch = process.argv.includes('--watch');
const check = process.argv.includes('--check');

const shadcnLicense = join(__dirname, 'src', 'lib', 'components', 'ui', 'LICENSE');
if (!existsSync(shadcnLicense)) {
  throw new Error(`missing shadcn license: ${shadcnLicense}`);
}

const themePath = join(__dirname, 'src', 'theme.css');
if (!existsSync(themePath)) {
  throw new Error(`missing theme entry: ${themePath}`);
}
const themeCli = join(__dirname, 'node_modules', '@tailwindcss', 'cli', 'dist', 'index.mjs');
const themeArgsFor = (out) => [themeCli, '-i', themePath, '-o', join(out, 'theme.css'), '--minify'];
if (!check && !watch) compileTheme(outDir);

if (check) {
  // Drift guard: rebuild into a scratch directory and compare the tracked
  // set with what a fresh build emits (integrates the new output directory).
  const actual = listFiles(outDir);
  const scratch = join(__dirname, '.build-check');
  rmSync(scratch, { recursive: true, force: true });
  try {
    await buildAll(scratch);
    const expected = listFiles(scratch);
    const missing = expected.filter((file) => !actual.includes(file));
    const extra = actual.filter((file) => !expected.includes(file));
    const changed = expected.filter((file) => actual.includes(file)
      && !readFileSync(join(scratch, file)).equals(readFileSync(join(outDir, file))));
    const problems = [
      ...missing.map((file) => `missing ${file}`),
      ...extra.map((file) => `unexpected ${file}`),
      ...changed.map((file) => `stale ${file}`),
    ];
    if (problems.length) {
      console.error('[admin-ui] generated static assets are out of date:');
      for (const problem of problems) console.error(`  ${problem}`);
      console.error('[admin-ui] run `npm run build` and commit ego_server/static/admin/');
      process.exitCode = 1;
    } else {
      console.log(`[admin-ui] ${expected.length} generated files match a fresh build`);
    }
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
} else {
  for (const dir of generatedDirs) rmSync(dir, { recursive: true, force: true });
  await buildAll(outDir, watch);
}

function compileTheme(out) {
  execFileSync(process.execPath, themeArgsFor(out), { cwd: __dirname, stdio: 'inherit', windowsHide: true });
}

function listFiles(root, prefix = '') {
  const files = [];
  for (const entry of readdirSync(join(root, prefix), { withFileTypes: true })) {
    const path = prefix ? join(prefix, entry.name) : entry.name;
    if (entry.isDirectory()) files.push(...listFiles(root, path));
    else files.push(path.split(sep).join('/'));
  }
  return files.sort();
}

async function buildAll(out, dev = false) {
  mkdirSync(out, { recursive: true });
  copyFileSync(join(__dirname, 'node_modules', 'monaco-editor', 'LICENSE'), join(out, 'monaco.LICENSE.txt'));
  copyFileSync(shadcnLicense, join(out, 'shadcn.LICENSE.txt'));

  const options = {
    entryPoints: [join(__dirname, 'src', 'main.ts')],
    bundle: true,
    outfile: join(out, 'bundle.js'),
    format: 'iife',
    platform: 'browser',
    target: ['es2022'],
    minify: !dev,
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
    outdir: join(out, 'workers'),
    entryNames: 'editor.worker',
    format: 'esm',
    platform: 'browser',
    target: ['es2022'],
    minify: !dev,
    logLevel: 'info',
  };

  const ideOptions = {
    entryPoints: [join(__dirname, 'src', 'ide', 'main.ts')],
    bundle: true,
    outfile: join(out, 'ide.js'),
    format: 'iife',
    platform: 'browser',
    target: ['es2022'],
    minify: !dev,
    assetNames: 'assets/[name]-[hash]',
    loader: { '.ttf': 'file', '.woff': 'file', '.woff2': 'file' },
    sourcemap: false,
    // Monaco's CSS is imported by src/ide/IdeApp.svelte; esbuild emits it as
    // ide.css next to ide.js, which ide.html loads.
    logLevel: 'info',
    plugins: [
      sveltePlugin({
        compilerOptions: { css: 'injected' },
      }),
    ],
  };

  if (watch) {
    const theme = spawn(process.execPath, [...themeArgsFor(out), '--watch'], { cwd: __dirname, stdio: 'inherit', windowsHide: true });
    process.on('exit', () => theme.kill());
    const ctx = await esbuild.context(options);
    const workerCtx = await esbuild.context(workerOptions);
    const ideCtx = await esbuild.context(ideOptions);
    await ctx.watch();
    await workerCtx.watch();
    await ideCtx.watch();
    console.log('[admin-ui] watching…');
    return;
  }
  compileTheme(out);
  await esbuild.build(options);
  await esbuild.build(workerOptions);
  await esbuild.build(ideOptions);
  if (!check) console.log('[admin-ui] built');
}

if (!watch && !check) {
  // The HTML shells load these files directly; a build that stops emitting
  // one is a broken page, not a smaller bundle.
  const required = ['bundle.js', 'bundle.css', 'theme.css', 'ide.js', 'ide.css', 'workers/editor.worker.js'];
  for (const file of required) {
    if (!existsSync(join(outDir, ...file.split('/')))) throw new Error(`build did not emit admin/${file}`);
  }
}
