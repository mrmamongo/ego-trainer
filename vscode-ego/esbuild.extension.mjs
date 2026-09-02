#!/usr/bin/env node
/** Bundle the extension host entry → out/extension.cjs (Node18 CommonJS).
 *
 * marked v18 is ESM-only and requires Node ≥ 20, but VS Code ^1.85 runs on
 * Node 18. esbuild transpiles `marked` into the host bundle so the packaged
 * .vsix needs no runtime node_modules. Only `vscode` is external because the
 * extension host provides it at runtime.
 */

import * as esbuild from 'esbuild';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const watch = process.argv.includes('--watch');

const options = {
    entryPoints: [join(__dirname, 'src', 'extension.ts')],
    bundle: true,
    outfile: join(__dirname, 'out', 'extension.cjs'),
    format: 'cjs',
    platform: 'node',
    target: 'node18',
    external: ['vscode'],
    sourcemap: false,
    minify: true,
    logLevel: 'info',
};

if (watch) {
    const ctx = await esbuild.context(options);
    await ctx.watch();
    console.log('[extension] watching…');
} else {
    await esbuild.build(options);
    console.log('[extension] bundled out/extension.cjs');
}
