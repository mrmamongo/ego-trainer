/** Offline local check via ego CLI / Python (8bv.9.9).
 *
 * Shells out to `python -m ego.cli check <task_id> --json` (writes progress
 * when `.ego/` exists). Falls back across python3 / python / `uv run`.
 *
 * Windows/offline slice (8bv.9.9):
 * - Detection cache is keyed by normalized cwd so switching workspaces can
 *   never reuse a stale executable decision.
 * - Every probe (`canRun`) and the real run (`runCapture`) use that cwd.
 * - On win32, spawn uses `shell:true` so `.cmd` shims (ego/uv) launch.
 * - `taskId` is validated before it can reach a shell.
 * - Child env preserves `process.env` and forces UTF-8.
 * - Promise resolution is guarded against double-settle when both `error`
 *   and `close` fire.
 */

import * as vscode from 'vscode';
import { spawn } from 'child_process';
import { CheckResponse } from './api';
import {
    cwdCacheKey,
    childEnv,
    shouldUseShell,
    validateTaskId,
} from './offlineCheckHelpers';

export interface OfflineCheckOptions {
    taskId: string;
    /** Workspace root (cwd for ego). */
    cwd: string;
    /** Optional student code to write before check (active editor buffer). */
    code?: string;
    /** Absolute path to task .py (if known). */
    pyPath?: string;
}

const pythonCmdCache = new Map<string, string[]>();

async function detectPythonCmd(cwd: string): Promise<string[]> {
    const key = cwdCacheKey(cwd);
    const cached = pythonCmdCache.get(key);
    if (cached) return cached;

    const egoBins: string[][] = [['uv', 'run', 'ego'], ['ego']];
    for (const cmd of egoBins) {
        if (await canRun([...cmd, '--version'], cwd)) {
            pythonCmdCache.set(key, cmd);
            return cmd;
        }
    }

    const pyCandidates: string[][] = [
        ['uv', 'run', 'python'],
        ['python3'],
        ['python'],
    ];
    for (const cmd of pyCandidates) {
        const ok = await canRun([...cmd, '--version'], cwd);
        if (!ok) continue;
        const importOk = await canRun([...cmd, '-c', 'import ego.checker'], cwd);
        if (importOk) {
            const prefix = [...cmd, '-m', 'ego.cli'];
            pythonCmdCache.set(key, prefix);
            return prefix;
        }
    }
    throw new Error(
        'Offline check requires Python 3.11+ with ego-trainer installed (try: uv sync).'
    );
}

function canRun(argv: string[], cwd: string): Promise<boolean> {
    return new Promise((resolve) => {
        const [bin, ...args] = argv;
        const child = spawn(bin, args, {
            cwd,
            env: childEnv(),
            stdio: ['ignore', 'ignore', 'ignore'],
            shell: shouldUseShell(),
        });
        let settled = false;
        const done = (value: boolean) => {
            if (settled) return;
            settled = true;
            resolve(value);
        };
        child.on('error', () => done(false));
        child.on('close', (code) => done(code === 0));
    });
}

function runCapture(
    argv: string[],
    cwd: string
): Promise<{ code: number | null; stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
        const [bin, ...args] = argv;
        const child = spawn(bin, args, {
            cwd,
            env: childEnv(),
            shell: shouldUseShell(),
        });
        let stdout = '';
        let stderr = '';
        let settled = false;
        child.stdout?.on('data', (d: Buffer) => {
            stdout += d.toString('utf-8');
        });
        child.stderr?.on('data', (d: Buffer) => {
            stderr += d.toString('utf-8');
        });
        child.on('error', (err) => {
            if (settled) return;
            settled = true;
            reject(err);
        });
        child.on('close', (code) => {
            if (settled) return;
            settled = true;
            resolve({ code, stdout, stderr });
        });
    });
}

/** Ensure student code is on disk before invoking CLI. */
async function ensureStudentFile(
    opts: OfflineCheckOptions
): Promise<void> {
    if (opts.code === undefined) return;
    const root = vscode.Uri.file(opts.cwd);
    let target: vscode.Uri | undefined;
    if (opts.pyPath) {
        target = vscode.Uri.file(opts.pyPath);
    } else {
        const normalized = opts.taskId.replace(/\./g, '_').toLowerCase();
        const filename = `task_${normalized}.py`;
        const found = await vscode.workspace.findFiles(
            new vscode.RelativePattern(root, `**/${filename}`),
            '**/{node_modules,.ego,out}/**',
            5
        );
        found.sort((a, b) => {
            const ar = vscode.workspace.asRelativePath(a);
            const br = vscode.workspace.asRelativePath(b);
            return (ar.startsWith('tasks/') ? 0 : 1) - (br.startsWith('tasks/') ? 0 : 1);
        });
        target = found[0];
    }
    if (!target) {
        throw new Error(
            `No .py stub for ${opts.taskId}. Create tasks/<block>/task_*.py first.`
        );
    }
    await vscode.workspace.fs.writeFile(target, Buffer.from(opts.code, 'utf-8'));
}

export async function runOfflineCheck(opts: OfflineCheckOptions): Promise<CheckResponse> {
    const idCheck = validateTaskId(opts.taskId);
    if (!idCheck.ok) {
        throw new Error(idCheck.error);
    }

    await ensureStudentFile(opts);
    const base = await detectPythonCmd(opts.cwd);
    const argv = [...base, 'check', opts.taskId, '--json'];
    const { code, stdout, stderr } = await runCapture(argv, opts.cwd);

    const jsonLine = extractJson(stdout);
    if (!jsonLine) {
        const detail = (stderr || stdout || '').trim();
        const exitPart = `exit code ${code}`;
        throw new Error(
            detail
                ? `${detail}\n(${exitPart})`
                : `Offline check produced no JSON output (${exitPart}).`
        );
    }

    let parsed: CheckResponse;
    try {
        parsed = JSON.parse(jsonLine) as CheckResponse;
    } catch {
        throw new Error(`Offline check: invalid JSON — ${jsonLine.slice(0, 200)}`);
    }

    if (!parsed.task_id || !Array.isArray(parsed.results)) {
        throw new Error('Offline check: unexpected JSON shape from ego CLI.');
    }
    return {
        task_id: parsed.task_id,
        version: parsed.version || '0.0.0',
        status: parsed.status,
        passed_tests: parsed.passed_tests ?? 0,
        total_tests: parsed.total_tests ?? 0,
        solution_hash: parsed.solution_hash || '',
        results: parsed.results || [],
        log: parsed.log || '',
    };
}

function extractJson(stdout: string): string | undefined {
    const trimmed = stdout.trim();
    if (!trimmed) return undefined;
    const lines = trimmed.split(/\r?\n/).filter((l) => l.trim().startsWith('{'));
    if (lines.length > 0) return lines[lines.length - 1];
    const start = trimmed.indexOf('{');
    const end = trimmed.lastIndexOf('}');
    if (start >= 0 && end > start) return trimmed.slice(start, end + 1);
    return undefined;
}
