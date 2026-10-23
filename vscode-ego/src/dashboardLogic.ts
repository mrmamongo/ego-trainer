/** Pure logic for the student cabinet dashboard (no vscode, no DOM).
 *
 * Project/folder grouping and next-task selection follow catalog order
 * (project_order, folder_order, natural id order). Old servers send none of
 * the catalog fields, so a missing field falls back to `block` and the natural
 * id order. Unit-tested from src/test/dashboardLogic.test.ts.
 */

/** The catalog fields a dashboard row carries (null/[] when the server is old). */
export interface CatalogTask {
    id: string;
    block: string;
    project_id?: string | null;
    project_name?: string | null;
    project_order?: number | string | null;
    folder_id?: string | null;
    folder_name?: string | null;
    folder_order?: number | string | null;
}

/** Minimal progress/evidence shape used for status classification. */
export interface StatusInput {
    status: string;
    passed_tests?: number;
    attempts?: number;
}

export interface UnderstandingEvidence {
    task_id: string;
    version: string;
    solution_hash: string;
    understanding: string;
    created_at?: string;
}

/** Row-level state shown in lists, filters and progress counters. */
export type TaskState = 'passed' | 'defense' | 'started' | 'failed' | 'new';

export interface FolderGroup<T extends CatalogTask> {
    key: string;
    id: string | null;
    name: string;
    order: number;
    tasks: T[];
    passed: number;
    total: number;
}

export interface ProjectGroup<T extends CatalogTask> extends FolderGroup<T> {
    folders: FolderGroup<T>[];
}

export interface CatalogGroups<T extends CatalogTask> {
    projects: ProjectGroup<T>[];
    /** Whether any task carried project_id; false = old server, groups by block. */
    hasProjects: boolean;
}

/** Called for every task with the project/folder buckets it was placed into. */
export type GroupVisitor<T extends CatalogTask> = (
    project: ProjectGroup<T>,
    folder: FolderGroup<T>,
    task: T
) => void;

const FALLBACK_PROJECT_NAME = 'Без проекта';
const FALLBACK_FOLDER_NAME = 'Без папки';

/** Normalize a progress status for comparisons. */
export function normalizeStatus(status: string | null | undefined): string {
    return (status ?? '').trim().toLowerCase();
}

export function isPassedStatus(status: string | null | undefined): boolean {
    return normalizeStatus(status) === 'passed';
}

function isFailedStatus(status: string | null | undefined): boolean {
    const s = normalizeStatus(status);
    return s === 'failed' || s === 'error' || s === 'timeout';
}

function isStartedStatus(status: string | null | undefined): boolean {
    const s = normalizeStatus(status);
    if (s === '' || s === 'new') return false;
    if (isPassedStatus(s) || isFailedStatus(s)) return false;
    return true; // partial, no_tests, unknown
}

/** Whether the evidence belongs to the given progress at its current version. */
function evidenceMatches(
    evidence: UnderstandingEvidence | null | undefined,
    progress: { task_id: string; version: string; solution_hash?: string | null } | null | undefined,
    task: { id: string; version: string }
): boolean {
    if (!evidence || !progress) return false;
    if (evidence.task_id !== task.id) return false;
    if (evidence.version !== progress.version || progress.version !== task.version) return false;
    if (!progress.solution_hash) return true;
    return evidence.solution_hash === progress.solution_hash;
}

/**
 * Classify a task for the cabinet.
 *
 * `defenseRequired` mirrors AIAccount.defense_required: a passed solution waits
 * for the understanding check until its evidence is `confirmed`. Pass `null`
 * when the evidence list is unavailable (old server) — a passed solution then
 * counts as `passed` instead of being blamed for a missing defense.
 */
export function taskState(
    task: { id: string; version: string },
    progress: ({ task_id: string; version: string; solution_hash?: string | null } & StatusInput) | null | undefined,
    evidence: UnderstandingEvidence | null | undefined,
    defenseRequired: boolean | null
): TaskState {
    if (!progress) return 'new';
    if (isPassedStatus(progress.status)) {
        if (!defenseRequired) return 'passed';
        return evidenceMatches(evidence, progress, task) && normalizeStatus(evidence?.understanding) === 'confirmed'
            ? 'passed'
            : 'defense';
    }
    if (isFailedStatus(progress.status)) return 'failed';
    if (isStartedStatus(progress.status)) return 'started';
    return 'new';
}

/** Newest evidence per task id (input order does not matter). */
export function newestEvidenceByTask(
    rows: readonly UnderstandingEvidence[]
): Map<string, UnderstandingEvidence> {
    const byTask = new Map<string, UnderstandingEvidence>();
    for (const row of rows) {
        if (!row || typeof row.task_id !== 'string') continue;
        const seen = byTask.get(row.task_id);
        if (!seen || (row.created_at || '') > (seen.created_at || '')) byTask.set(row.task_id, row);
    }
    return byTask;
}

/**
 * Effective defense requirement: only when the server says so AND the evidence
 * list is actually available; otherwise null (no «ждёт защиты» claims).
 */
export function effectiveDefenseRequired(accountDefenseRequired: boolean | null | undefined, evidenceAvailable: boolean): boolean | null {
    return evidenceAvailable && accountDefenseRequired === true ? true : null;
}

/** True when the task still needs work (everything except 'passed'). */
export function isOpenState(state: TaskState): boolean {
    return state !== 'passed';
}

export function taskStateLabel(state: TaskState): string {
    switch (state) {
        case 'passed':
            return 'Решена';
        case 'defense':
            return 'Ждёт защиты понимания';
        case 'started':
            return 'В работе';
        case 'failed':
            return 'Есть ошибки';
        default:
            return 'Не начата';
    }
}

/** Russian label for one evidence row from GET /progress/me/understanding. */
export function understandingStatusLabel(status: string | null | undefined): string {
    switch (normalizeStatus(status)) {
        case 'confirmed':
            return 'Понимание подтверждено';
        case 'pending':
        case 'active':
            return 'Защита идёт';
        case 'needs_review':
            return 'Нужна проверка наставника';
        default:
            // Unknown or empty status: a submission exists but is not confirmed yet.
            return 'Ждёт защиты понимания';
    }
}

/** Russian label for the AIAccount.reason code (or a ready-made sentence). */
export function aiAccessReasonLabel(reason: string | null | undefined): string {
    const text = (reason ?? '').trim();
    switch (text.toLowerCase()) {
        case '':
        case 'available':
            return 'доступен';
        case 'disabled':
        case 'not_granted':
            return 'доступ не выдан — обратись к наставнику';
        case 'low_balance':
        case 'insufficient_funds':
        case 'no_funds':
        case 'budget_exhausted':
            return 'бюджет исчерпан';
        case 'not_configured':
            return 'не настроен на сервере';
        default:
            return text;
    }
}

/** Natural compare: "V2" < "V10", "F1.2" < "F1.10"; digit runs before letters. */
export function naturalCompare(a: string, b: string): number {
    const ax = a.match(/(\d+|\D+)/g) ?? [];
    const bx = b.match(/(\d+|\D+)/g) ?? [];
    const n = Math.min(ax.length, bx.length);
    for (let i = 0; i < n; i++) {
        const pa = ax[i];
        const pb = bx[i];
        const numA = /^\d/.test(pa);
        const numB = /^\d/.test(pb);
        if (numA && numB) {
            const diff = Number(pa) - Number(pb);
            if (diff !== 0) return diff;
            if (pa.length !== pb.length) return pa.length - pb.length;
            continue;
        }
        if (numA !== numB) return numA ? -1 : 1;
        const cmp = pa.toLowerCase().localeCompare(pb.toLowerCase());
        if (cmp !== 0) return cmp;
        if (pa !== pb) return pa < pb ? -1 : 1;
    }
    if (ax.length !== bx.length) return ax.length - bx.length;
    return a === b ? 0 : a < b ? -1 : 1;
}

function orderOf(value: number | string | null | undefined): number {
    const n = typeof value === 'string' && value.trim() !== '' ? Number(value) : value;
    return typeof n === 'number' && Number.isFinite(n) ? n : 0;
}

/**
 * Catalog order within one project: folder_order, then natural id order.
 * The project level is compared by `compareProjectOrder` first.
 */
export function compareCatalogOrder(a: CatalogTask, b: CatalogTask): number {
    const byFolder = orderOf(a.folder_order) - orderOf(b.folder_order);
    if (byFolder !== 0) return byFolder;
    return naturalCompare(a.id, b.id);
}

/** Orders projects (or blocks on an old server) by project_order, then name. */
export function compareProjectOrder(
    a: { project_id?: string | null; project_order?: number | string | null; block?: string },
    b: { project_id?: string | null; project_order?: number | string | null; block?: string }
): number {
    const byOrder = orderOf(a.project_order) - orderOf(b.project_order);
    if (byOrder !== 0) return byOrder;
    const byId = naturalCompare(a.project_id || a.block || '', b.project_id || b.block || '');
    if (byId !== 0) return byId;
    return compareCatalogOrder(a as CatalogTask, b as CatalogTask);
}

/**
 * The first not-passed task in catalog order, or undefined when all are done.
 * Order: project_order → folder_order → natural id order (V2 before V10).
 */
export function pickNextTask<T extends CatalogTask>(
    tasks: T[],
    stateOf: (task: T) => TaskState
): T | undefined {
    const ordered = [...tasks].sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b));
    return ordered.find((task) => isOpenState(stateOf(task)));
}

function catalogValue(value: string | null | undefined): string {
    return typeof value === 'string' && value !== '' ? value : '';
}

/**
 * Group tasks into projects → folders, sorted by catalog order.
 *
 * Tasks without project/folder fields fall back to one project per `block`, so
 * an old server still gets the familiar breakdown. Folder-less tasks go to one
 * «Без папки» bucket; project-less tasks (on a server that does send projects)
 * to «Без проекта».
 *
 * Counting is left to the caller: `visit` receives every task together with its
 * buckets, so it can compute `taskState` and increment `passed` counters.
 */
export function groupCatalog<T extends CatalogTask>(
    tasks: T[],
    visit?: GroupVisitor<T>
): CatalogGroups<T> {
    const hasProjects = tasks.some((t) => catalogValue(t.project_id) !== '');
    const projects: ProjectGroup<T>[] = [];
    const projectByKey = new Map<string, ProjectGroup<T>>();
    const folderByKey = new Map<string, FolderGroup<T>>();

    for (const task of tasks) {
        const projectId = catalogValue(task.project_id);
        const projectKey = projectId ? `p:${projectId}` : hasProjects ? 'p:' : `b:${catalogValue(task.block)}`;
        let project = projectByKey.get(projectKey);
        if (!project) {
            const name = projectId
                ? catalogValue(task.project_name) || projectId
                : catalogValue(task.block)
                  ? `Блок ${task.block}`
                  : FALLBACK_PROJECT_NAME;
            project = {
                key: projectKey,
                id: projectId || null,
                name,
                order: orderOf(task.project_order),
                tasks: [],
                folders: [],
                passed: 0,
                total: 0,
            };
            projectByKey.set(projectKey, project);
            projects.push(project);
        }

        const folderId = catalogValue(task.folder_id);
        const folderKey = `${projectKey}|${folderId ? `f:${folderId}` : `b:${catalogValue(task.block)}`}`;
        let folder = folderByKey.get(folderKey);
        if (!folder) {
            const name = folderId
                ? catalogValue(task.folder_name) || folderId
                : catalogValue(task.block)
                  ? `Блок ${task.block}`
                  : FALLBACK_FOLDER_NAME;
            folder = {
                key: folderKey,
                id: folderId || null,
                name,
                order: orderOf(task.folder_order),
                tasks: [],
                passed: 0,
                total: 0,
            };
            folderByKey.set(folderKey, folder);
            project.folders.push(folder);
        }

        folder.tasks.push(task);
        folder.total++;
        project.tasks.push(task);
        project.total++;
    }

    for (const project of projects) {
        project.folders.sort(compareGroups);
        for (const folder of project.folders) {
            folder.tasks.sort(compareCatalogOrder);
            if (visit) for (const task of folder.tasks) visit(project, folder, task);
        }
        project.tasks.sort(compareCatalogOrder);
    }
    projects.sort(compareGroups);
    return { projects, hasProjects };
}

function compareGroups(
    a: { order: number; name: string },
    b: { order: number; name: string }
): number {
    if (a.order !== b.order) return a.order - b.order;
    return naturalCompare(a.name, b.name);
}

/** Percent 0–100 for a passed/total pair; 0 when there is nothing to count. */
export function percent(passed: number, total: number): number {
    if (!Number.isFinite(total) || total <= 0) return 0;
    return Math.round((Math.min(passed, total) / total) * 100);
}
