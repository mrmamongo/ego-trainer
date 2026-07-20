/** Load DashboardData from server API or local .ego/ files. */

import * as vscode from 'vscode';
import { EgoApi } from './api';
import { readEgoConfig, egoDir, type EgoMode } from './egoWorkspace';

/** Mirrors webview DashboardData — keep fields in sync with shared/types.ts */
export interface DashboardRow {
    id: string;
    title: string;
    block: string;
    slug: string;
    version: string;
    status: string;
    passed_tests: number;
    total_tests: number;
    attempts: number;
    last_run_at: string | null;
    md_path?: string;
}

export interface DashboardData {
    mode: EgoMode;
    summary: {
        passed: number;
        partial: number;
        new: number;
        failed: number;
        total: number;
    };
    blocks: string[];
    rows: DashboardRow[];
    error?: string;
}

interface ManifestFile {
    tasks: Array<{
        id: string;
        block: string;
        slug: string;
        version: string;
        md_path: string;
    }>;
}

interface ProgressFile {
    entries: Array<{
        task_id: string;
        version: string;
        status: string;
        attempts: number;
        passed_tests: number;
        total_tests: number;
        last_run_at?: string | null;
    }>;
}

function summarize(rows: DashboardRow[]): DashboardData['summary'] {
    const summary = { passed: 0, partial: 0, new: 0, failed: 0, total: rows.length };
    for (const r of rows) {
        const s = (r.status || 'new').toLowerCase();
        if (s === 'passed') summary.passed++;
        else if (s === 'partial') summary.partial++;
        else if (s === 'failed' || s === 'error' || s === 'timeout') summary.failed++;
        else summary.new++;
    }
    return summary;
}

function emptyData(mode: EgoMode, error?: string): DashboardData {
    return {
        mode,
        summary: { passed: 0, partial: 0, new: 0, failed: 0, total: 0 },
        blocks: [],
        rows: [],
        error,
    };
}

async function readJsonUri<T>(uri: vscode.Uri): Promise<T | undefined> {
    try {
        const buf = await vscode.workspace.fs.readFile(uri);
        return JSON.parse(Buffer.from(buf).toString('utf-8')) as T;
    } catch {
        return undefined;
    }
}

async function titleFromMd(mdPath: string): Promise<string | undefined> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) return undefined;
    try {
        const uri = vscode.Uri.joinPath(root, ...mdPath.split('/'));
        const buf = await vscode.workspace.fs.readFile(uri);
        const text = Buffer.from(buf).toString('utf-8');
        const m = text.match(/^#\s+(.+)$/m);
        if (!m) return undefined;
        // "# Задача F1: Найди первый критический баг" → keep full or strip prefix
        return m[1].replace(/^Задача\s+/i, '').trim();
    } catch {
        return undefined;
    }
}

export async function loadDashboardData(api: EgoApi): Promise<DashboardData> {
    const cfg = await readEgoConfig();
    const mode: EgoMode = cfg?.mode === 'offline' ? 'offline' : 'server';

    if (mode === 'offline') {
        return loadOffline();
    }
    return loadServer(api);
}

async function loadServer(api: EgoApi): Promise<DashboardData> {
    try {
        const tasks = await api.listTasks();
        let progressMap = new Map<
            string,
            {
                status: string;
                attempts: number;
                passed_tests: number;
                total_tests: number;
                last_run_at: string | null;
            }
        >();
        try {
            const me = await api.me();
            const progress = await api.getProgress(me.user_id);
            progressMap = new Map(
                progress.map((p) => [
                    p.task_id,
                    {
                        status: p.status,
                        attempts: p.attempts,
                        passed_tests: p.passed_tests,
                        total_tests: p.total_tests,
                        last_run_at: p.last_run_at,
                    },
                ])
            );
        } catch {
            // Progress optional.
        }

        const rows: DashboardRow[] = tasks.map((t) => {
            const p = progressMap.get(t.id);
            return {
                id: t.id,
                title: t.title,
                block: t.block,
                slug: t.slug,
                version: t.version,
                status: p?.status || 'new',
                passed_tests: p?.passed_tests ?? 0,
                total_tests: p?.total_tests ?? 0,
                attempts: p?.attempts ?? 0,
                last_run_at: p?.last_run_at ?? null,
            };
        });
        rows.sort((a, b) => a.id.localeCompare(b.id));
        const blocks = [...new Set(rows.map((r) => r.block))].sort();
        return { mode: 'server', summary: summarize(rows), blocks, rows };
    } catch (e) {
        // Fall back to local manifest if server unreachable but .ego/ exists.
        const offline = await loadOffline();
        if (offline.rows.length > 0) {
            return {
                ...offline,
                mode: 'server',
                error: `Server unavailable — showing local manifest. (${(e as Error).message})`,
            };
        }
        return emptyData('server', (e as Error).message);
    }
}

async function loadOffline(): Promise<DashboardData> {
    const dir = egoDir();
    if (!dir) {
        return emptyData('offline', 'No workspace folder open.');
    }
    const manifest = await readJsonUri<ManifestFile>(
        vscode.Uri.joinPath(dir, 'manifest.yaml')
    );
    const progress = await readJsonUri<ProgressFile>(
        vscode.Uri.joinPath(dir, 'progress.json')
    );
    if (!manifest) {
        return emptyData('offline', 'No .ego/manifest.yaml — run Ego: Init (Offline).');
    }

    const progressMap = new Map(
        (progress?.entries || []).map((e) => [e.task_id, e])
    );

    const rows: DashboardRow[] = [];
    for (const t of manifest.tasks) {
        const p = progressMap.get(t.id);
        const title = (await titleFromMd(t.md_path)) || t.id;
        rows.push({
            id: t.id,
            title,
            block: t.block,
            slug: t.slug,
            version: t.version,
            status: p?.status || 'new',
            passed_tests: p?.passed_tests ?? 0,
            total_tests: p?.total_tests ?? 0,
            attempts: p?.attempts ?? 0,
            last_run_at: p?.last_run_at ?? null,
            md_path: t.md_path,
        });
    }
    rows.sort((a, b) => a.id.localeCompare(b.id));
    const blocks = [...new Set(rows.map((r) => r.block))].sort();
    return { mode: 'offline', summary: summarize(rows), blocks, rows };
}
