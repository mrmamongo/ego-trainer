/** TreeDataProvider for Ego Tasks sidebar.
 *
 * Shows Project → Folder → lessons, then tasks with status icons. Clicking a task opens it.
 * Offline: reads `.ego/manifest.yaml` + `.ego/progress.json` (8bv.9.7).
 */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta, LessonMeta, ProgressRow } from './api';
import { buildCatalog, type Catalog, type CatalogFolder, type CatalogProject, type LessonReadState } from './theoryLogic';
import { egoDir, readEgoConfig } from './egoWorkspace';

export class TaskItem extends vscode.TreeItem {
    constructor(
        public readonly task: TaskMeta,
        public readonly progress: ProgressRow | undefined,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(task.title && task.title !== task.task_id ? `${task.task_id} · ${task.title}` : task.task_id, collapsibleState);
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
            return '';
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

export class ProjectItem extends vscode.TreeItem {
    constructor(public readonly project: CatalogProject, collapsibleState: vscode.TreeItemCollapsibleState) {
        super(project.name, collapsibleState);
        this.id = `project:${project.key}`;
        this.description = `${project.folders.reduce((n, f) => n + f.tasks.length, 0)}`;
        this.contextValue = 'project';
        this.iconPath = new vscode.ThemeIcon('repo');
    }
}

/** A catalog folder (formerly "Блок <block>"): lessons first, then tasks. */
export class BlockItem extends vscode.TreeItem {
    constructor(
        public readonly folder: CatalogFolder,
        collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(folder.name, collapsibleState);
        this.id = `folder:${folder.key}`;
        this.description = `${folder.tasks.length}`;
        if (folder.lessons.length) this.tooltip = `${folder.name}: теория ${folder.lessons.length}, задач ${folder.tasks.length}`;
        this.contextValue = 'block';
        this.iconPath = new vscode.ThemeIcon('folder');
    }
}

export class LessonItem extends vscode.TreeItem {
    constructor(public readonly lesson: LessonMeta, public readonly read: boolean) {
        super(lesson.title || lesson.id, vscode.TreeItemCollapsibleState.None);
        this.description = read ? '✓' : '';
        this.tooltip = `Теория: ${lesson.title || lesson.id}${read ? ' (прочитано)' : ''}`;
        this.contextValue = 'lesson';
        this.iconPath = new vscode.ThemeIcon('book', read ? new vscode.ThemeColor('testing.iconPassed') : undefined);
        this.command = { command: 'ego.openLesson', title: 'Open Lesson', arguments: [lesson] };
    }
}

type TreeNode = ProjectItem | BlockItem | LessonItem | TaskItem;

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

export class EgoTaskTreeProvider implements vscode.TreeDataProvider<TreeNode> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;

    private api: EgoApi;
    private readState: LessonReadState | undefined;
    private progressMap: Map<string, ProgressRow> = new Map();
    private offlineTasks: TaskMeta[] | undefined;
    private catalog: Promise<Catalog> | undefined;

    constructor(api: EgoApi, readState?: LessonReadState) {
        this.api = api;
        this.readState = readState;
        readState?.onDidChange(() => this.refresh());
    }

    updateApi(newApi: EgoApi): void {
        this.api = newApi;
        this.progressMap.clear();
        this.offlineTasks = undefined;
        this.refresh();
    }

    refresh(): void {
        this.offlineTasks = undefined;
        this.catalog = undefined;
        this._onDidChange.fire();
    }

    getTreeItem(element: TreeNode): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TreeNode): Promise<TreeNode[]> {
        if (!element) {
            try {
                const catalog = await this.loadCatalog();
                if (catalog.showProjects) {
                    return catalog.projects.map(
                        (p) => new ProjectItem(p, vscode.TreeItemCollapsibleState.Collapsed)
                    );
                }
                return catalog.projects.flatMap((p) => this.folderItems(p));
            } catch {
                return [new BlockItem(errorFolder(), vscode.TreeItemCollapsibleState.None)];
            }
        }

        if (element instanceof ProjectItem) {
            return this.folderItems(element.project);
        }

        if (element instanceof BlockItem) {
            const { lessons, tasks } = element.folder;
            return [
                ...lessons.map((l) => new LessonItem(l, this.readState?.isRead(l.id, l.content_hash) ?? false)),
                ...tasks.map(
                    (t) =>
                        new TaskItem(
                            t,
                            this.progressMap.get(t.task_id),
                            vscode.TreeItemCollapsibleState.None
                        )
                ),
            ];
        }

        return [];
    }

    private folderItems(project: CatalogProject): BlockItem[] {
        return project.folders.map(
            (f) => new BlockItem(f, vscode.TreeItemCollapsibleState.Collapsed)
        );
    }

    private loadCatalog(): Promise<Catalog> {
        if (!this.catalog) {
            const pending = this.buildCatalogNow();
            this.catalog = pending;
            // Do not cache failures: the next expand retries.
            pending.catch(() => { if (this.catalog === pending) this.catalog = undefined; });
        }
        return this.catalog;
    }

    private async buildCatalogNow(): Promise<Catalog> {
        const { tasks, online } = await this.loadTasks();
        let lessons: LessonMeta[] = [];
        if (online) {
            try {
                lessons = await this.api.listLessons();
            } catch {
                // Lessons are optional: old server or transient error.
            }
        }
        return buildCatalog(tasks, lessons);
    }

    private async loadTasks(): Promise<{ tasks: TaskMeta[]; online: boolean }> {
        const cfg = await readEgoConfig();
        if (cfg?.mode === 'offline') {
            return { tasks: await this.loadOffline(), online: false };
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
            return { tasks, online: true };
        } catch {
            // Server unreachable → offline fallback when .ego/ exists.
            return { tasks: await this.loadOffline(), online: false };
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

function errorFolder(): CatalogFolder {
    return { key: 'error', name: 'Блок Error', order: 0, block: 'Error', projectKey: '', lessons: [], tasks: [] };
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
