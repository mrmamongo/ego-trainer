import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

interface CommandResult {
    stdout: string;
    stderr: string;
}

function runUv(workspacePath: string, args: string[]): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
        let settled = false;
        let stdout = '';
        let stderr = '';
        const command = `uv ${args.join(' ')}`;
        const child = spawn('uv', args, {
            cwd: workspacePath,
            shell: false,
            env: {
                ...process.env,
                PYTHONUTF8: '1',
                PYTHONIOENCODING: 'utf-8',
            },
            stdio: ['ignore', 'pipe', 'pipe'],
        });

        child.stdout.on('data', (chunk: Buffer | string) => {
            stdout += chunk.toString();
        });
        child.stderr.on('data', (chunk: Buffer | string) => {
            stderr += chunk.toString();
        });
        child.once('error', (error) => {
            if (settled) return;
            settled = true;
            reject(new Error(`${command} could not start: ${error.message}`));
        });
        child.once('close', (code, signal) => {
            if (settled) return;
            settled = true;
            if (code === 0) {
                resolve({ stdout, stderr });
                return;
            }
            const details = [stderr.trim(), stdout.trim()].filter(Boolean).join('\n');
            reject(new Error(`${command} failed${signal ? ` (${signal})` : ` (exit code ${code ?? 'unknown'})`}${details ? `: ${details}` : '.'}`));
        });
    });
}

async function hasPyproject(workspacePath: string): Promise<boolean> {
    try {
        await fs.stat(path.join(workspacePath, 'pyproject.toml'));
        return true;
    } catch {
        return false;
    }
}

export async function isPythonEnvReady(workspacePath: string): Promise<boolean> {
    try {
        await runUv(workspacePath, ['run', 'python', '-c', 'import ego.checker']);
        return true;
    } catch {
        return false;
    }
}

export async function setupPythonEnv(workspacePath: string): Promise<void> {
    const packageSpec = vscode.workspace
        .getConfiguration('ego', vscode.Uri.file(workspacePath))
        .get<string>('pythonPackageSpec', 'ego-trainer')
        .trim() || 'ego-trainer';

    try {
        await runUv(workspacePath, ['--version']);
    } catch (error) {
        throw new Error(`Ego: uv is required to set up Python in this workspace. ${(error as Error).message}`);
    }

    if (!(await hasPyproject(workspacePath))) {
        try {
            await runUv(workspacePath, ['init', '--bare']);
        } catch (error) {
            const message = (error as Error).message;
            if (!/unknown option|unexpected argument|unrecognized option|invalid.*option|no such option|does not support/i.test(message)) {
                throw new Error(`Ego: Could not initialize Python in this workspace: ${message}`);
            }
            try {
                await runUv(workspacePath, ['init', '--no-readme']);
            } catch (fallbackError) {
                throw new Error(`Ego: Could not initialize Python in this workspace with uv init --bare or uv init --no-readme: ${(fallbackError as Error).message}`);
            }
        }
    }

    try {
        await runUv(workspacePath, ['add', packageSpec]);
    } catch (error) {
        throw new Error(`Ego: Could not install configured Python package "${packageSpec}": ${(error as Error).message}`);
    }

    try {
        await runUv(workspacePath, ['run', 'python', '-c', 'import ego.checker']);
    } catch (error) {
        throw new Error(`Ego: Python setup completed for "${packageSpec}", but uv run python -c "import ego.checker" failed: ${(error as Error).message}`);
    }
}
