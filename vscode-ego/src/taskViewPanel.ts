/** Task view webview host (ADR-0015 / 8bv.9.6). */

import * as vscode from 'vscode';
import { EgoApi, CheckResponse, TaskMeta } from './api';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import {
    extractSection,
    extractSignature,
    renderStatementHtml,
    stripSolutionDetails,
} from './markdown';
import { readEgoConfig } from './egoWorkspace';

export interface TaskViewHint {
    level: number;
    title: string;
    content: string;
}

export interface TaskViewData {
    id: string;
    title: string;
    status: string;
    version: string;
    statement_html: string;
    hints: TaskViewHint[];
    mode: 'server' | 'offline';
}

export interface TaskViewDeps {
    getApi: () => EgoApi;
    checkTask: (taskId: string) => Promise<void>;
    openPy: (taskId: string, slug?: string, mdPath?: string) => Promise<void>;
}

interface TaskRef {
    id: string;
    title: string;
    slug: string;
    version: string;
    status: string;
    md_path?: string;
}

export class TaskViewPanel {
    private static panel: vscode.WebviewPanel | undefined;
    private static extensionUri: vscode.Uri | undefined;
    private static deps: TaskViewDeps | undefined;
    private static ready = false;
    private static current: TaskRef | undefined;
    private static pendingResult: CheckResponse | undefined;

    static configure(extensionUri: vscode.Uri, deps: TaskViewDeps): void {
        TaskViewPanel.extensionUri = extensionUri;
        TaskViewPanel.deps = deps;
    }

    static isOpen(): boolean {
        return TaskViewPanel.panel !== undefined;
    }

    static currentTaskId(): string | undefined {
        return TaskViewPanel.current?.id;
    }

    /** Open (or reuse) Task view for a task in column 2. */
    static async show(ref: TaskRef): Promise<void> {
        const extensionUri = TaskViewPanel.extensionUri;
        const deps = TaskViewPanel.deps;
        if (!extensionUri || !deps) {
            vscode.window.showErrorMessage('Ego: Task view not configured.');
            return;
        }

        TaskViewPanel.current = ref;
        TaskViewPanel.pendingResult = undefined;

        if (TaskViewPanel.panel) {
            TaskViewPanel.panel.title = `Ego: ${ref.id}`;
            TaskViewPanel.panel.reveal(vscode.ViewColumn.Two);
        } else {
            TaskViewPanel.ready = false;
            TaskViewPanel.panel = vscode.window.createWebviewPanel(
                'egoTaskView',
                `Ego: ${ref.id}`,
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true,
                    localResourceRoots: webviewLocalRoots(extensionUri),
                }
            );
            TaskViewPanel.panel.webview.html = webviewHtml({
                webview: TaskViewPanel.panel.webview,
                extensionUri,
                bundleName: 'taskView.js',
                title: `Ego: ${ref.id}`,
            });
            TaskViewPanel.panel.webview.onDidReceiveMessage(async (msg: { type?: string }) => {
                await TaskViewPanel.onMessage(msg);
            });
            TaskViewPanel.panel.onDidDispose(() => {
                TaskViewPanel.panel = undefined;
                TaskViewPanel.ready = false;
                TaskViewPanel.current = undefined;
                TaskViewPanel.pendingResult = undefined;
            });
        }

        if (TaskViewPanel.ready) {
            await TaskViewPanel.pushData();
        }
    }

    static showFromMeta(task: TaskMeta, status = 'new'): Promise<void> {
        return TaskViewPanel.show({
            id: task.id,
            title: task.title,
            slug: task.slug,
            version: task.version,
            status,
            md_path: task.md_path || undefined,
        });
    }

    /** Route check results here when panel is open. */
    static postResult(result: CheckResponse): void {
        if (!TaskViewPanel.panel) return;
        TaskViewPanel.pendingResult = result;
        if (TaskViewPanel.current && result.task_id !== TaskViewPanel.current.id) {
            return; // different task
        }
        if (TaskViewPanel.ready) {
            TaskViewPanel.panel.webview.postMessage({
                type: 'taskView.setResult',
                payload: result,
            });
        }
    }

    private static async onMessage(msg: { type?: string }): Promise<void> {
        const deps = TaskViewPanel.deps;
        const cur = TaskViewPanel.current;
        if (!deps || !msg?.type) return;

        switch (msg.type) {
            case 'ready':
                TaskViewPanel.ready = true;
                await TaskViewPanel.pushData();
                if (TaskViewPanel.pendingResult) {
                    TaskViewPanel.postResult(TaskViewPanel.pendingResult);
                }
                break;
            case 'taskView.check':
                if (cur) await deps.checkTask(cur.id);
                break;
            case 'taskView.openPy':
                if (cur) await deps.openPy(cur.id, cur.slug, cur.md_path);
                break;
            case 'taskView.refresh':
                await TaskViewPanel.pushData();
                break;
            default:
                break;
        }
    }

    private static async pushData(): Promise<void> {
        const deps = TaskViewPanel.deps;
        const cur = TaskViewPanel.current;
        const panel = TaskViewPanel.panel;
        if (!deps || !cur || !panel || !TaskViewPanel.ready) return;

        try {
            const data = await loadTaskViewData(deps.getApi(), cur);
            panel.webview.postMessage({ type: 'taskView.setData', payload: data });
        } catch (e) {
            panel.webview.postMessage({
                type: 'taskView.setData',
                payload: {
                    id: cur.id,
                    title: cur.title,
                    status: cur.status,
                    version: cur.version,
                    statement_html: `<p>Failed to load task: ${escapeHtml((e as Error).message)}</p>`,
                    hints: [],
                    mode: 'offline',
                } satisfies TaskViewData,
            });
        }
    }
}

async function loadTaskViewData(api: EgoApi, ref: TaskRef): Promise<TaskViewData> {
    const cfg = await readEgoConfig();
    const mode = cfg?.mode === 'offline' ? 'offline' : 'server';

    if (mode === 'server') {
        try {
            const full = await api.getTask(ref.id);
            let hints: TaskViewHint[] = [];
            try {
                const resp = await api.getHints(ref.id, 3);
                hints = resp.hints.map((h) => ({
                    level: h.level,
                    title: h.title,
                    content: h.content,
                }));
            } catch {
                hints = hintsFromMarkdown(full.statement_md, full.stub_py);
            }
            return {
                id: full.id,
                title: full.title,
                status: ref.status,
                version: full.version,
                statement_html: renderStatementHtml(full.statement_md),
                hints,
                mode: 'server',
            };
        } catch {
            // fall through to local files
        }
    }

    const md = await readLocalMarkdown(ref);
    const stub = await readLocalStub(ref);
    const title =
        md.match(/^#\s+(.+)$/m)?.[1]?.replace(/^Задача\s+/i, '').trim() || ref.title || ref.id;

    return {
        id: ref.id,
        title,
        status: ref.status,
        version: ref.version,
        statement_html: renderStatementHtml(md),
        hints: hintsFromMarkdown(stripSolutionDetails(md), stub),
        mode: 'offline',
    };
}

function hintsFromMarkdown(statementMd: string, stubPy: string): TaskViewHint[] {
    const hints: TaskViewHint[] = [];
    const rules = extractSection(statementMd, 'Правила');
    if (rules) hints.push({ level: 1, title: 'Правила', content: rules });
    const example = extractSection(statementMd, 'Пример');
    if (example) hints.push({ level: 2, title: 'Пример', content: example });
    const sig = extractSignature(stubPy);
    if (sig) {
        hints.push({
            level: 3,
            title: 'Сигнатура функции',
            content: `\`\`\`python\n${sig}\n\`\`\``,
        });
    }
    return hints;
}

async function readLocalMarkdown(ref: TaskRef): Promise<string> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) throw new Error('No workspace folder.');

    const candidates: vscode.Uri[] = [];
    if (ref.md_path) {
        candidates.push(vscode.Uri.joinPath(root, ...ref.md_path.split('/')));
    }
    const normalized = ref.id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}.md`;
    if (ref.slug) {
        candidates.push(vscode.Uri.joinPath(root, 'tasks', ref.slug, filename));
        candidates.push(vscode.Uri.joinPath(root, 'docs', 'tasks', ref.slug, filename));
    }
    // Last resort: search
    for (const uri of candidates) {
        try {
            const buf = await vscode.workspace.fs.readFile(uri);
            return Buffer.from(buf).toString('utf-8');
        } catch {
            // next
        }
    }
    const found = await vscode.workspace.findFiles(
        new vscode.RelativePattern(root, `**/${filename}`),
        '**/node_modules/**',
        3
    );
    if (found[0]) {
        const buf = await vscode.workspace.fs.readFile(found[0]);
        return Buffer.from(buf).toString('utf-8');
    }
    throw new Error(`Markdown for ${ref.id} not found.`);
}

async function readLocalStub(ref: TaskRef): Promise<string> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) return '';
    const normalized = ref.id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}.py`;
    const candidates: vscode.Uri[] = [];
    if (ref.slug) {
        candidates.push(vscode.Uri.joinPath(root, 'tasks', ref.slug, filename));
    }
    if (ref.md_path) {
        candidates.push(vscode.Uri.joinPath(root, ...ref.md_path.split('/').slice(0, -1), filename));
    }
    for (const uri of candidates) {
        try {
            const buf = await vscode.workspace.fs.readFile(uri);
            return Buffer.from(buf).toString('utf-8');
        } catch {
            // next
        }
    }
    return '';
}

function escapeHtml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
