/** TreeDataProvider for the Cogito tasks sidebar.
 *
 * Shows Project → Folder → lessons, then tasks with status icons. Clicking a task opens it.
 * Offline: reads `.ego/manifest.yaml` + `.ego/progress.json` (8bv.9.7).
 */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta, LessonMeta, ProgressRow, ProjectInfo, ChallengeInfo, ChallengeStage } from './api';
import { buildCatalog, type Catalog, type CatalogFolder, type CatalogProject, type LessonReadState } from './theoryLogic';
import { egoDir, readEgoConfig } from './egoWorkspace';
import { indexProjects, readinessLine, recommendationTooltip } from './recommendations';
import { challengeIdFromTaskId, nextStageNumber, orderedStages, stageStatusLabel } from './challengeWorkspace';

export class TaskItem extends vscode.TreeItem {
    /** `challenge_stage` of a challenge stage, undefined for an ordinary task. */
    readonly stage: number | undefined;
    /** The next unsolved stage of its challenge (highlighted, never required). */
    readonly highlighted: boolean;
    /** The challenge folder this stage belongs to (`GET /challenges` id). */
    readonly challengeId: string | undefined;

    constructor(
        public readonly task: TaskMeta,
        public readonly progress: ProgressRow | undefined,
        collapsibleState: vscode.TreeItemCollapsibleState,
        stage?: { number: number; challengeId: string; title: string; status: string; total: number; highlighted: boolean }
    ) {
        super(task.title && task.title !== task.task_id ? `${task.task_id} · ${task.title}` : task.task_id, collapsibleState);
        this.stage = stage?.number;
        this.challengeId = stage?.challengeId ?? challengeIdFromTaskId(task.task_id);
        this.highlighted = stage?.highlighted ?? false;
        const lastRun = progress?.last_run_at
            ? ` · последняя проверка ${formatRelative(progress.last_run_at)}`
            : '';
        this.tooltip = stage
            ? `Этап ${stage.number} из ${stage.total}: ${stage.title} — ${stageStatusLabel(stage.status)}${lastRun}`
            : `${task.title} (v${task.version})${lastRun}`;
        this.description = stage ? stageStatusLabel(stage.status) : this._statusLabel();
        this.contextValue = this.highlighted ? 'challengeStage.current' : 'task';
        this.iconPath = this._icon();
        this.command = stage
            ? { command: 'ego.openStage', title: 'Открыть этап', arguments: [this] }
            : { command: 'ego.openTask', title: 'Открыть задачу', arguments: [task] };
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
    constructor(
        public readonly project: CatalogProject,
        collapsibleState: vscode.TreeItemCollapsibleState,
        private readonly info?: ProjectInfo
    ) {
        super(project.name, collapsibleState);
        this.id = `project:${project.key}`;
        const tasks = `${project.folders.reduce((n, f) => n + f.tasks.length, 0)}`;
        // Unmet recommendation: «рекомендуем после XL-A: 14/21» (never blocks).
        const readiness = readinessLine(info);
        this.description = readiness ? `${tasks} · ${readiness}` : tasks;
        const tooltip = recommendationTooltip(info);
        if (tooltip) this.tooltip = tooltip;
        this.contextValue = 'project';
        this.iconPath = new vscode.ThemeIcon(readiness ? 'lightbulb' : 'repo');
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
        this.contextValue = folder.challenge && folder.tasks[0]?.folder_id ? 'challenge' : 'block';
        this.description = folder.challenge ? `челлендж · ${folder.tasks.length} этапов` : `${folder.tasks.length}`;
        if (folder.challenge) {
            this.tooltip = `${folder.name}: челлендж, этапов ${folder.tasks.length}. Все этапы открыты, следующий подсвечен.`;
        } else if (folder.lessons.length) {
            this.tooltip = `${folder.name}: теория ${folder.lessons.length}, задач ${folder.tasks.length}`;
        }
        this.iconPath = new vscode.ThemeIcon(folder.challenge ? 'rocket' : 'folder');
    }
}

export class LessonItem extends vscode.TreeItem {
    constructor(public readonly lesson: LessonMeta, public readonly read: boolean) {
        super(lesson.title || lesson.id, vscode.TreeItemCollapsibleState.None);
        this.description = read ? '✓' : '';
        this.tooltip = `Теория: ${lesson.title || lesson.id}${read ? ' (прочитано)' : ''}`;
        this.contextValue = 'lesson';
        this.iconPath = new vscode.ThemeIcon('book', read ? new vscode.ThemeColor('testing.iconPassed') : undefined);
        this.command = { command: 'ego.openLesson', title: 'Открыть теорию', arguments: [lesson] };
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
    /** GET /projects rows by id (empty on old servers / offline). */
    private projectInfo: Map<string, ProjectInfo> = new Map();
    /** GET /challenges rows by folder id; `null` cached for "no challenge". */
    private challenges: Map<string, ChallengeInfo | null> = new Map();

    constructor(api: EgoApi, readState?: LessonReadState) {
        this.api = api;
        this.readState = readState;
        readState?.onDidChange(() => this.refresh());
    }

    updateApi(newApi: EgoApi): void {
        this.api = newApi;
        this.progressMap.clear();
        this.offlineTasks = undefined;
        this.projectInfo = new Map();
        this.challenges = new Map();
        this.refresh();
    }

    refresh(): void {
        this.offlineTasks = undefined;
        this.catalog = undefined;
        this.challenges = new Map();
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
                        (p) =>
                            new ProjectItem(
                                p,
                                vscode.TreeItemCollapsibleState.Collapsed,
                                this.projectInfo.get(p.key)
                            )
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
            const challenge = await this.challengeStages(element.folder);
            return [
                ...lessons.map((l) => new LessonItem(l, this.readState?.isRead(l.id, l.content_hash) ?? false)),
                ...tasks.map((t) => this.taskItem(t, challenge)),
            ];
        }

        return [];
    }

    private taskItem(task: TaskMeta, challenge: ChallengeInfo | undefined): TaskItem {
        const progress = this.progressMap.get(task.task_id);
        if (!challenge || !challenge.stages.length) {
            return new TaskItem(task, progress, vscode.TreeItemCollapsibleState.None);
        }
        // Stages in stage order; the first not-passed one is highlighted (soft).
        const ordered = orderedStages(challenge.stages);
        const item = ordered.find((stage) => stage.id.toLowerCase() === task.task_id.toLowerCase());
        const next = nextStageNumber(ordered);
        const status = item?.status ?? progress?.status ?? 'new';
        return new TaskItem(task, progress, vscode.TreeItemCollapsibleState.None, {
            number: item?.number ?? 0,
            challengeId: challenge.id,
            // A stage tile shows its own title, not the task's `stage_02_…` one.
            title: item?.title || task.title,
            status,
            total: ordered.length,
            highlighted: (item?.number ?? 0) === next && status !== 'passed',
        });
    }

    /**
     * `GET /challenges/<id>` of a challenge folder — stage order and the callers'
     * statuses; `undefined` offline, on an old server or after a failure (the
     * stages then show their progress alone).
     */
    private async challengeStages(folder: CatalogFolder): Promise<ChallengeInfo | undefined> {
        const folderId = folder.tasks[0]?.folder_id;
        if (!folder.challenge || !folderId || !folder.key.startsWith(`${folder.projectKey}/id:`)) return undefined;
        const cached = this.challenges.get(folderId);
        if (cached !== undefined) return cached ?? undefined;
        try {
            const info = await this.api.getChallenge(folderId);
            this.challenges.set(folderId, info);
            return info ?? undefined;
        } catch {
            return undefined;
        }
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
            try {
                // Soft recommendations (404 on an old server → empty map).
                this.projectInfo = indexProjects(await this.api.listProjects());
            } catch {
                this.projectInfo = new Map();
            }
        } else {
            this.projectInfo = new Map();
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
    return { key: 'error', name: 'Блок с ошибкой', order: 0, block: 'Error', projectKey: '', lessons: [], tasks: [], challenge: false };
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
    if (sec < 60) return `${sec} с назад`;
    if (sec < 3600) return `${Math.round(sec / 60)} мин назад`;
    if (sec < 86400) return `${Math.round(sec / 3600)} ч назад`;
    return `${Math.round(sec / 86400)} дн. назад`;
}
