/** Load DashboardData (student cabinet) from server API or local .ego/ files. */

import * as vscode from 'vscode';
import {
    EgoApi,
    EgoApiError,
    catalogFieldsOf,
    isAuthenticationError,
    type ProgressRow,
    type TaskMetaWithCatalog,
} from './api';
import type { AIAccount } from './aiTypes';
import { readEgoConfig, egoDir, type EgoMode } from './egoWorkspace';
import {
    aiAccessReasonLabel,
    effectiveDefenseRequired,
    groupCatalog,
    naturalCompare,
    newestEvidenceByTask,
    percent,
    pickNextTask,
    taskState,
    understandingStatusLabel,
    type TaskState,
    type UnderstandingEvidence,
} from './dashboardLogic';

/** Mirrors webview DashboardData — keep fields in sync with shared/types.ts */
export interface DashboardRow {
    id: string;
    title: string;
    block: string;
    slug: string;
    version: string;
    status: string;
    stale: boolean;
    passed_tests: number;
    total_tests: number;
    attempts: number;
    last_run_at: string | null;
    md_path?: string;
    project_id?: string | null;
    project_name?: string | null;
    project_order?: number;
    folder_id?: string | null;
    folder_name?: string | null;
    folder_order?: number;
    theory?: string[];
    state?: TaskState;
}

export interface FolderProgress {
    key: string;
    name: string;
    passed: number;
    total: number;
    percent: number;
}

export interface ProjectProgress extends FolderProgress {
    folders: FolderProgress[];
}

export interface UnderstandingEntry {
    task_id: string;
    task_title: string;
    status: string;
    status_label: string;
    at: string | null;
}

export interface AiAccess {
    enabled: boolean;
    available: boolean;
    defense_required: boolean;
    reason: string;
    balance_usd: string;
    spent_usd: string;
}

export interface Cabinet {
    projects: ProjectProgress[];
    next_task_id: string | null;
    next_task_title: string | null;
    understanding: UnderstandingEntry[] | null;
    ai: AiAccess | null;
    defense_required: boolean;
    states: Record<string, TaskState>;
    ai_reason_label: string | null;
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
    cabinet?: Cabinet;
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

const EMPTY_CABINET: Cabinet = {
    projects: [],
    next_task_id: null,
    next_task_title: null,
    understanding: null,
    ai: null,
    defense_required: false,
    states: {},
    ai_reason_label: null,
};

function summarize(rows: DashboardRow[]): DashboardData['summary'] {
    const summary = { passed: 0, partial: 0, new: 0, failed: 0, total: rows.length };
    for (const r of rows) {
        const s = String(r.state ?? r.status ?? 'new').toLowerCase();
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
        cabinet: { ...EMPTY_CABINET },
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

/** Everything the cabinet sections need, assembled once per load. */
export interface CabinetInputs {
    tasks: TaskMetaWithCatalog[];
    progress: ProgressRow[];
    /** null = GET /progress/me/understanding unavailable (old server). */
    evidence: UnderstandingEvidence[] | null;
    /** null = GET /ai/me unavailable (old server / offline). */
    account: AIAccount | null;
    mode: EgoMode;
}

export interface CabinetBuild {
    cabinet: Cabinet;
    /** Task id → state; empty when progress is unavailable. */
    states: Record<string, TaskState>;
}

/**
 * Assemble the cabinet sections from tasks, progress and optional evidence.
 * `evidence` / `account` are null when the server lacks the corresponding
 * endpoint; those sections are then hidden by the webview.
 */
export function buildCabinet(input: CabinetInputs): CabinetBuild {
    const { tasks, progress, evidence, account, mode } = input;
    const progressByTask = new Map(progress.map((p) => [p.task_id, p]));
    const latestEvidence = evidence ? newestEvidenceByTask(evidence) : null;
    // Defense gating needs both the server flag and the evidence list; without
    // them a passed solution stays «passed» instead of «ждёт защиты».
    const defenseRequired = effectiveDefenseRequired(
        mode === 'server' ? account?.defense_required : null,
        evidence !== null
    );
    const stateOf = (task: { id: string; version: string }): TaskState => {
        const p = progressByTask.get(task.id);
        return taskState(task, p ? { ...p } : null, latestEvidence?.get(task.id), defenseRequired);
    };

    const { projects } = groupCatalog(tasks, (project, folder, task) => {
        if (stateOf(task) === 'passed') {
            project.passed++;
            folder.passed++;
        }
    });

    const titles = new Map(tasks.map((t) => [t.id, t.title]));
    const understanding =
        evidence === null
            ? null
            : [...evidence]
                  .filter((row) => row && typeof row.task_id === 'string')
                  .sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''))
                  .map((row) => ({
                      task_id: row.task_id,
                      task_title: titles.get(row.task_id) || row.task_id,
                      status: row.understanding,
                      status_label: understandingStatusLabel(row.understanding),
                      at: row.created_at || null,
                  }));

    const next = pickNextTask(tasks, stateOf);
    const states: Record<string, TaskState> = {};
    if (progress.length > 0) {
        for (const task of tasks) states[task.id] = stateOf(task);
    }
    return {
        states,
        cabinet: {
            projects: projects.map((p) => ({
                key: p.key,
                name: p.name,
                passed: p.passed,
                total: p.total,
                percent: percent(p.passed, p.total),
                folders: p.folders.map((f) => ({
                    key: f.key,
                    name: f.name,
                    passed: f.passed,
                    total: f.total,
                    percent: percent(f.passed, f.total),
                })),
            })),
            next_task_id: next?.id ?? null,
            next_task_title: next?.title ?? null,
            understanding,
            ai: account
                ? {
                      enabled: account.enabled,
                      available: account.available,
                      defense_required: account.defense_required,
                      reason: account.reason,
                      // Russian code translation lives in cabinet.ai_reason_label.
                      balance_usd: account.balance_usd,
                      spent_usd: account.spent_usd,
                  }
                : null,
            defense_required: defenseRequired === true,
            states,
            ai_reason_label: account ? aiAccessReasonLabel(account.reason) : null,
        },
    };
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
        let progress: ProgressRow[] = [];
        let progressAvailable = false;
        try {
            const me = await api.me();
            progress = await api.getProgress(me.user_id);
            progressAvailable = true;
        } catch (e) {
            if (isAuthenticationError(e)) throw e;
            // Progress optional.
        }

        // Cabinet sections: each optional endpoint degrades to "hidden".
        // 401 still means a stale session; 403/404 mean "not supported here".
        let evidence: UnderstandingEvidence[] | null = null;
        try {
            evidence = await api.getMyUnderstanding();
        } catch (e) {
            if (e instanceof EgoApiError && e.status === 401) throw e;
            evidence = null;
        }
        // /ai/me: 401 means the whole session is stale (handled below); 403/404
        // mean the server has no AI section — hide it. Other errors also hide it
        // rather than failing the whole dashboard.
        let account: AIAccount | null = null;
        try {
            account = await api.getAiMe();
        } catch (e) {
            if (e instanceof EgoApiError && e.status === 401) throw e;
            account = null;
        }

        const { cabinet, states } = buildCabinet({ tasks, progress, evidence, account, mode: 'server' });
        const progressMap = new Map(progress.map((p) => [p.task_id, p]));
        const rows: DashboardRow[] = tasks.map((t) => {
            const p = progressMap.get(t.id);
            return {
                id: t.id,
                title: t.title,
                block: t.block,
                slug: t.slug,
                version: t.version,
                stale: p !== undefined && p.version !== t.version,
                status: p?.status || 'new',
                passed_tests: p?.passed_tests ?? 0,
                total_tests: p?.total_tests ?? 0,
                attempts: p?.attempts ?? 0,
                last_run_at: p?.last_run_at ?? null,
                ...catalogFieldsOf(t),
                state: progressAvailable ? states[t.id] : undefined,
            };
        });
        rows.sort((a, b) => naturalCompare(a.id, b.id));
        const blocks = [...new Set(rows.map((r) => r.block))].sort();
        return { mode: 'server', summary: summarize(rows), blocks, rows, cabinet };
    } catch (e) {
        // Fall back to local manifest if server unreachable but .ego/ exists.
        const offline = await loadOffline();
        if (isAuthenticationError(e)) {
            const error = 'Сессия истекла — выполните «Cogito: Войти»';
            if (offline.rows.length > 0) return { ...offline, mode: 'server', error };
            return emptyData('server', error);
        }
        if (offline.rows.length > 0) {
            return {
                ...offline,
                mode: 'server',
                error: `Сервер недоступен — показан локальный список. (${(e as Error).message})`,
            };
        }
        return emptyData('server', (e as Error).message);
    }
}

async function loadOffline(): Promise<DashboardData> {
    const dir = egoDir();
    if (!dir) {
        return emptyData('offline', 'Не открыта папка рабочей области.');
    }
    const manifest = await readJsonUri<ManifestFile>(
        vscode.Uri.joinPath(dir, 'manifest.yaml')
    );
    const progress = await readJsonUri<ProgressFile>(
        vscode.Uri.joinPath(dir, 'progress.json')
    );
    if (!manifest) {
        return emptyData('offline', 'Нет .ego/manifest.yaml — выполните «Cogito: Подключить папку к курсу» для offline-режима.');
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
            stale: p !== undefined && p.version !== t.version,
            status: p?.status || 'new',
            passed_tests: p?.passed_tests ?? 0,
            total_tests: p?.total_tests ?? 0,
            attempts: p?.attempts ?? 0,
            last_run_at: p?.last_run_at ?? null,
            md_path: t.md_path,
        });
    }
    rows.sort((a, b) => naturalCompare(a.id, b.id));
    const blocks = [...new Set(rows.map((r) => r.block))].sort();

    // Offline: no evidence and no AI account — the cabinet groups by block
    // and hides the server-only sections.
    const offlineTasks: TaskMetaWithCatalog[] = manifest.tasks.map((t) => ({
        id: t.id,
        block: t.block,
        slug: t.slug,
        task_id: t.id,
        title: t.id,
        level: '',
        tags: [],
        version: t.version,
        content_hash: '',
        breaking: false,
        md_path: t.md_path,
    }));
    // Prefer the title read from the local .md file.
    const titleById = new Map(rows.map((r) => [r.id, r.title]));
    for (const task of offlineTasks) task.title = titleById.get(task.id) || task.title;
    const offlineProgress: ProgressRow[] = (progress?.entries || []).map((e) => ({
        student_id: '',
        task_id: e.task_id,
        version: e.version,
        status: e.status,
        attempts: e.attempts,
        passed_tests: e.passed_tests,
        total_tests: e.total_tests,
        last_run_at: e.last_run_at ?? null,
    }));
    const { cabinet, states } = buildCabinet({
        tasks: offlineTasks,
        progress: offlineProgress,
        evidence: null,
        account: null,
        mode: 'offline',
    });
    for (const row of rows) row.state = states[row.id];
    return { mode: 'offline', summary: summarize(rows), blocks, rows, cabinet };
}
