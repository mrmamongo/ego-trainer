/** Task view webview host (ADR-0015 / 8bv.9.6). */

import * as vscode from 'vscode';
import { EgoApi, CheckResponse, TaskMeta } from './api';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import {
    extractSection,
    extractSignature,
    renderMarkdownHtml,
    renderStatementHtml,
    stripSolutionDetails,
} from './markdown';
import { readEgoConfig } from './egoWorkspace';
import { parseRunSummary, sortRecentRuns, type TaskRunSummary } from './runHistory';

export interface TaskViewHint {
    level: number;
    title: string;
    /** Pre-rendered HTML (host-side markdown). */
    content: string;
}

export interface TaskViewData {
    id: string;
    title: string;
    status: string;
    version: string;
    statement_html: string;
    hints: TaskViewHint[];
    history: TaskRunSummary[];
    mode: 'server' | 'offline';
    ai_available?: boolean;
    loading?: boolean;
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
    private static panel: vscode.WebviewView | undefined;
    private static extensionUri: vscode.Uri | undefined;
    private static deps: TaskViewDeps | undefined;
    private static ready = false;
    private static current: TaskRef | undefined;
    private static generation = 0;
    private static results = new Map<string, CheckResponse>();

    static configure(extensionUri: vscode.Uri, deps: TaskViewDeps): void {
        this.extensionUri = extensionUri;
        this.deps = deps;
    }

    static register(context: vscode.ExtensionContext): void {
        context.subscriptions.push(vscode.window.registerWebviewViewProvider('egoTaskDetail', {
            resolveWebviewView: view => {
                this.panel = view;
                this.ready = false;
                view.webview.options = { enableScripts: true, localResourceRoots: webviewLocalRoots(context.extensionUri) };
                view.webview.onDidReceiveMessage(msg => this.onMessage(msg), undefined, context.subscriptions);
                view.onDidDispose(() => {
                    if (this.panel === view) { this.panel = undefined; this.ready = false; this.generation++; }
                }, undefined, context.subscriptions);
                view.webview.html = webviewHtml({ webview: view.webview, extensionUri: context.extensionUri,
                    bundleName: 'taskView.js', title: 'Cogito · Задание' });
            },
        }, { webviewOptions: { retainContextWhenHidden: true } }));
    }

    static isOpen(): boolean { return this.current !== undefined; }
    static currentTaskId(): string | undefined { return this.current?.id; }

    /** Follow an editor change without moving focus away from the code. */
    static async followTask(ref: TaskRef): Promise<void> {
        if (this.current?.id === ref.id) return;
        this.current = ref;
        this.generation++;
        await this.pushData();
    }

    static async show(ref: TaskRef): Promise<void> {
        this.current = ref;
        this.generation++;
        if (this.panel) this.panel.show(true);
        else await vscode.commands.executeCommand('egoTaskDetail.focus');
        await this.pushData();
    }

    static showFromMeta(task: TaskMeta, status = 'new'): Promise<void> {
        return this.show({ id: task.id, title: task.title, slug: task.slug,
            version: task.version, status, md_path: task.md_path || undefined });
    }

    /** Keep results attached to their task, even if the editor changed meanwhile. */
    static postResult(result: CheckResponse): boolean {
        this.results.set(result.task_id.toLowerCase(), result);
        if (this.current && result.task_id.toLowerCase() === this.current.id.toLowerCase()) {
            this.current = { ...this.current, status: result.status };
            if (this.ready && this.panel) {
                void this.panel.webview.postMessage({ type: 'taskView.setResult', payload: result });
            }
        }
        return true;
    }

    private static async onMessage(msg: { type?: string; taskId?: string }): Promise<void> {
        const cur = this.current, deps = this.deps;
        if (!deps) return;
        if (msg.type !== 'ready' && msg.type !== 'taskView.refresh' && msg.taskId !== cur?.id) return;
        switch (msg.type) {
            case 'ready': this.ready = true; await this.pushData(); break;
            case 'taskView.check': if (cur) await deps.checkTask(cur.id); break;
            case 'taskView.openPy': if (cur) await deps.openPy(cur.id, cur.slug, cur.md_path); break;
            case 'taskView.refresh': await this.pushData(); break;
            case 'taskView.assistant': if (cur) await vscode.commands.executeCommand('ego.assistant', cur.id); break;
        }
    }

    private static async pushData(): Promise<void> {
        const deps = this.deps, cur = this.current, panel = this.panel, generation = this.generation;
        if (!deps || !cur || !panel || !this.ready) return;
        void panel.webview.postMessage({ type: 'taskView.setData', payload: {
            id: cur.id, title: cur.title, status: cur.status, version: cur.version,
            statement_html: '', hints: [], history: [], mode: 'offline', loading: true,
        } satisfies TaskViewData });
        const isCurrent = () => this.generation === generation && this.panel === panel;
        try {
            const data = await loadTaskViewData(deps.getApi(), cur);
            if (!isCurrent()) return;
            const result = this.results.get(cur.id.toLowerCase());
            if (result) data.status = result.status;
            void panel.webview.postMessage({ type: 'taskView.setData', payload: data });
            if (result) void panel.webview.postMessage({ type: 'taskView.setResult', payload: result });
        } catch (error) {
            if (!isCurrent()) return;
            void panel.webview.postMessage({ type: 'taskView.setData', payload: {
                id: cur.id, title: cur.title, status: cur.status, version: cur.version,
                statement_html: '<p>' + escapeHtml((error as Error).message) + '</p>',
                hints: [], history: [], mode: 'offline',
            } satisfies TaskViewData });
        }
    }
}

async function loadTaskViewData(api: EgoApi, ref: TaskRef): Promise<TaskViewData> {
    const cfg = await readEgoConfig();
    const mode = cfg?.mode === 'offline' ? 'offline' : 'server';
    const history = await readLocalRunHistory(ref.id);

    if (mode === 'server') {
        try {
            const full = await api.getTask(ref.id);
            const access = await api.getAIAccount().catch(() => null);
            let hints: TaskViewHint[] = [];
            try {
                const resp = await api.getHints(ref.id, 3);
                hints = resp.hints.map((h) => ({
                    level: h.level,
                    title: h.title,
                    content: renderMarkdownHtml(h.content),
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
                history,
                mode: 'server',
                ai_available: access?.available || false,
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
        history,
        mode: 'offline',
    };
}

async function readLocalRunHistory(taskId: string): Promise<TaskRunSummary[]> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) return [];
    const runsDir = vscode.Uri.joinPath(root, '.ego', 'runs');
    const safeId = taskId.replace(/\./g, '_').toLowerCase();
    try {
        const entries = await vscode.workspace.fs.readDirectory(runsDir);
        const files = entries.filter(([name, type]) =>
            type === vscode.FileType.File &&
            name.toLowerCase().startsWith(`${safeId}-`) &&
            name.toLowerCase().endsWith('.json')
        );
        const runs: TaskRunSummary[] = [];
        for (const [name] of files) {
            try {
                const raw = JSON.parse(Buffer.from(await vscode.workspace.fs.readFile(
                    vscode.Uri.joinPath(runsDir, name)
                )).toString('utf-8')) as unknown;
                const summary = parseRunSummary(raw);
                if (summary) runs.push(summary);
            } catch {
                // Ignore inaccessible and malformed run files.
            }
        }
        return sortRecentRuns(runs);
    } catch {
        return [];
    }
}

function hintsFromMarkdown(statementMd: string, stubPy: string): TaskViewHint[] {
    const hints: TaskViewHint[] = [];
    const rules = extractSection(statementMd, 'Правила');
    if (rules) hints.push({ level: 1, title: 'Правила', content: renderMarkdownHtml(rules) });
    const example = extractSection(statementMd, 'Пример');
    if (example) hints.push({ level: 2, title: 'Пример', content: renderMarkdownHtml(example) });
    const sig = extractSignature(stubPy);
    if (sig) {
        hints.push({
            level: 3,
            title: 'Сигнатура функции',
            content: renderMarkdownHtml('```python\n' + sig + '\n```'),
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
