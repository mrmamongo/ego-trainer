/** TreeDataProvider for Ego Tasks sidebar.
 *
 * Shows blocks → tasks with status icons. Clicking a task opens it.
 * Offline: reads `.ego/manifest.yaml` + `.ego/progress.json` (8bv.9.7).
 */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta, ProgressRow } from './api';
import { egoDir, readEgoConfig } from './egoWorkspace';

export class TaskItem extends vscode.TreeItem {
    constructor(
        public readonly task: TaskMeta,
        public readonly progress: ProgressRow | undefined,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(task.task_id, collapsibleState);
        const lastRun = progress?.last_run_at
            ? ` · last ${formatRelative(progress.last_run_at)}`
            : '';
        this.tooltip = `${task.title} (v${task.version})${lastRun}`;
        this.description = this._statusLabel();
        this.contextValue = 'task';
        this.iconPath = this._icon();
        this.command = {
            command: 'ego.openTask',
            title: 'Open Task',
            arguments: [task],
        };
    }

    private _statusLabel(): string {
        if (!this.progress) {
            return 'new';
        }
        const icon = this._statusIcon(this.progress.status);
        return `${icon} ${this.progress.passed_tests}/${this.progress.total_tests}`;
    }

    private _statusIcon(status: string): string {
        switch (status) {
            case 'passed':
                return '✓';
            case 'partial':
                return '◐';
            case 'failed':
                return '✗';
            case 'error':
                return '⚠';
            default:
                return '○';
        }
    }

    private _icon(): vscode.ThemeIcon {
        if (!this.progress) {
            return new vscode.ThemeIcon('circle-outline');
        }
        switch (this.progress.status) {
            case 'passed':
                return new vscode.ThemeIcon('check', new vscode.ThemeColor('testing.iconPassed'));
            case 'partial':
                return new vscode.ThemeIcon(
                    'circle-filled',
                    new vscode.ThemeColor('testing.iconQueued')
                );
            case 'failed':
            case 'error':
                return new vscode.ThemeIcon('x', new vscode.ThemeColor('testing.iconFailed'));
            default:
                return new vscode.ThemeIcon('circle-outline');
        }
    }
}

export class BlockItem extends vscode.TreeItem {
    constructor(
        public readonly block: string,
        public readonly taskCount: number,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(`Block ${block}`, collapsibleState);
        this.description = `${taskCount} tasks`;
        this.contextValue = 'block';
        this.iconPath = new vscode.ThemeIcon('folder');
    }
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

export class EgoTaskTreeProvider implements vscode.TreeDataProvider<BlockItem | TaskItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;

    private api: EgoApi;
    private progressMap: Map<string, ProgressRow> = new Map();
    private offlineTasks: TaskMeta[] | undefined;

    constructor(api: EgoApi) {
        this.api = api;
    }

    updateApi(newApi: EgoApi): void {
        this.api = newApi;
        this.progressMap.clear();
        this.offlineTasks = undefined;
        this.refresh();
    }

    refresh(): void {
        this.offlineTasks = undefined;
        this._onDidChange.fire();
    }

    getTreeItem(element: BlockItem | TaskItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: BlockItem | TaskItem): Promise<(BlockItem | TaskItem)[]> {
        if (!element) {
            try {
                const tasks = await this.loadTasks();
                const blocks = new Map<string, TaskMeta[]>();
                for (const t of tasks) {
                    if (!blocks.has(t.block)) blocks.set(t.block, []);
                    blocks.get(t.block)!.push(t);
                }
                return Array.from(blocks.entries())
                    .sort((a, b) => a[0].localeCompare(b[0]))
                    .map(
                        ([block, list]) =>
                            new BlockItem(
                                block,
                                list.length,
                                vscode.TreeItemCollapsibleState.Collapsed
                            )
                    );
            } catch {
                return [new BlockItem('Error', 0, vscode.TreeItemCollapsibleState.None)];
            }
        }

        if (element instanceof BlockItem) {
            try {
                const tasks = (await this.loadTasks()).filter((t) => t.block === element.block);
                return tasks
                    .sort((a, b) => a.task_id.localeCompare(b.task_id))
                    .map(
                        (t) =>
                            new TaskItem(
                                t,
                                this.progressMap.get(t.task_id),
                                vscode.TreeItemCollapsibleState.None
                            )
                    );
            } catch {
                return [];
            }
        }

        return [];
    }

    private async loadTasks(): Promise<TaskMeta[]> {
        const cfg = await readEgoConfig();
        if (cfg?.mode === 'offline') {
            return this.loadOffline();
        }
        try {
            const tasks = await this.api.listTasks();
            try {
                const me = await this.api.me();
                const progress = await this.api.getProgress(me.user_id);
                this.progressMap = new Map(progress.map((p) => [p.task_id, p]));
            } catch {
                // Progress optional.
            }
            return tasks;
        } catch {
            // Server unreachable → offline fallback when .ego/ exists.
            return this.loadOffline();
        }
    }

    private async loadOffline(): Promise<TaskMeta[]> {
        if (this.offlineTasks) return this.offlineTasks;
        const dir = egoDir();
        if (!dir) return [];

        const manifest = await readJsonUri<ManifestFile>(
            vscode.Uri.joinPath(dir, 'manifest.yaml')
        );
        const progress = await readJsonUri<ProgressFile>(
            vscode.Uri.joinPath(dir, 'progress.json')
        );

        this.progressMap = new Map();
        for (const e of progress?.entries || []) {
            this.progressMap.set(e.task_id, {
                student_id: '',
                task_id: e.task_id,
                version: e.version,
                status: e.status,
                attempts: e.attempts,
                passed_tests: e.passed_tests,
                total_tests: e.total_tests,
                last_run_at: e.last_run_at ?? null,
            });
        }

        this.offlineTasks = (manifest?.tasks || []).map((t) => ({
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
        return this.offlineTasks;
    }
}

async function readJsonUri<T>(uri: vscode.Uri): Promise<T | undefined> {
    try {
        const buf = await vscode.workspace.fs.readFile(uri);
        return JSON.parse(Buffer.from(buf).toString('utf-8')) as T;
    } catch {
        return undefined;
    }
}

function formatRelative(iso: string): string {
    const t = Date.parse(iso);
    if (Number.isNaN(t)) return iso;
    const sec = Math.round((Date.now() - t) / 1000);
    if (sec < 60) return `${sec}s ago`;
    if (sec < 3600) return `${Math.round(sec / 60)}m ago`;
    if (sec < 86400) return `${Math.round(sec / 3600)}h ago`;
    return `${Math.round(sec / 86400)}d ago`;
}
