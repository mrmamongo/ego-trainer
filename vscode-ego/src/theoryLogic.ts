/** Pure theory-card logic: catalog grouping, read state, lesson cache.
 *
 * No `vscode` import so it can be unit-tested with node --test and reused
 * from the webview bundle.
 */

import type { LessonFull, LessonMeta, TaskMeta } from './api';

// === Catalog (Project -> Folder -> lessons + tasks) ===

export interface CatalogFolder {
    key: string;
    name: string;
    order: number;
    block: string;
    projectKey: string;
    lessons: LessonMeta[];
    tasks: TaskMeta[];
    /** Every task is a stage (`tasks.challenge_stage`) of a challenge (ADR-0018). */
    challenge: boolean;
}

export interface CatalogProject {
    key: string;
    name: string;
    order: number;
    folders: CatalogFolder[];
}

export interface Catalog {
    /** False when there is a single project: the tree starts at folders. */
    showProjects: boolean;
    projects: CatalogProject[];
}

const NO_PROJECT_KEY = '';
const NO_PROJECT_NAME = 'Без проекта';

function folderKey(folderId: string | null | undefined, block: string): string {
    return folderId ? `id:${folderId}` : `block:${block}`;
}

/** `challenge_stage` of a task, 0 for an ordinary task / an old server. */
function stageNumber(task: TaskMeta): number {
    const value = task.challenge_stage;
    return typeof value === 'number' && value > 0 ? value : 0;
}

function byOrderThenName(
    a: { order: number; name: string },
    b: { order: number; name: string }
): number {
    return a.order - b.order || a.name.localeCompare(b.name);
}

/** Group tasks and lessons into Project -> Folder.
 *
 * Tasks without catalog fields (old server, offline manifest) fall back to a
 * "Блок <block>" folder, exactly like the pre-catalog tree. Lessons carry no
 * names, so a folder/project that has lessons but no tasks borrows the code
 * (`block`) / id as its name.
 */
export function buildCatalog(tasks: TaskMeta[], lessons: LessonMeta[]): Catalog {
    const projects = new Map<string, CatalogProject>();
    const folders = new Map<string, CatalogFolder>();

    const projectFor = (id: string | null | undefined, name: string | null | undefined, order: number | undefined) => {
        const key = id || NO_PROJECT_KEY;
        let project = projects.get(key);
        if (!project) {
            project = { key, name: name || id || NO_PROJECT_NAME, order: order ?? 0, folders: [] };
            projects.set(key, project);
        } else if (name && project.name === (id || NO_PROJECT_NAME)) {
            // A task knows the real name; a lesson-created placeholder does not.
            project.name = name;
            project.order = order ?? project.order;
        }
        return project;
    };

    const folderFor = (
        project: CatalogProject,
        folderId: string | null | undefined,
        name: string | null | undefined,
        order: number | undefined,
        block: string
    ) => {
        const key = `${project.key}/${folderKey(folderId, block)}`;
        let folder = folders.get(key);
        if (!folder) {
            folder = {
                key, name: name || `Блок ${block}`, order: order ?? 0, block,
                projectKey: project.key, lessons: [], tasks: [], challenge: false,
            };
            folders.set(key, folder);
            project.folders.push(folder);
        } else if (name && folder.name === `Блок ${block}`) {
            folder.name = name;
            folder.order = order ?? folder.order;
        }
        return folder;
    };

    for (const task of tasks) {
        const project = projectFor(task.project_id, task.project_name, task.project_order);
        folderFor(project, task.folder_id, task.folder_name, task.folder_order, task.block).tasks.push(task);
    }
    for (const lesson of lessons) {
        const project = projectFor(lesson.project_id, undefined, undefined);
        folderFor(project, lesson.folder_id, undefined, undefined, lesson.block).lessons.push(lesson);
    }

    const sorted = [...projects.values()].sort(byOrderThenName);
    for (const project of sorted) {
        project.folders.sort(byOrderThenName);
        for (const folder of project.folders) {
            folder.lessons.sort((a, b) => a.order - b.order || a.id.localeCompare(b.id));
            // Challenge stages go in stage order, like tasks do by id.
            folder.tasks.sort((a, b) => stageNumber(a) - stageNumber(b) || a.task_id.localeCompare(b.task_id));
            folder.challenge = folder.tasks.length > 0 && folder.tasks.every((task) => stageNumber(task) > 0);
        }
    }
    return { showProjects: sorted.length > 1, projects: sorted };
}

// === Read state ===

/** The slice of vscode.Memento we need (globalState). */
export interface MementoLike {
    get<T>(key: string, defaultValue: T): T;
    update(key: string, value: unknown): PromiseLike<void>;
}

const READ_PREFIX = 'ego.lessonRead:';

/** Read state is per lesson version: a changed content_hash is unread again. */
export function lessonKey(id: string, contentHash: string): string {
    return `${READ_PREFIX}${id}@${contentHash}`;
}

export interface LessonReadState {
    isRead(id: string, contentHash: string): boolean;
    setRead(id: string, contentHash: string, read: boolean): Promise<void>;
    /** Fires after every change; returns an unsubscribe function. */
    onDidChange(listener: () => void): () => void;
}

export function createReadState(store: MementoLike): LessonReadState {
    const listeners = new Set<() => void>();
    return {
        isRead: (id, hash) => store.get<boolean>(lessonKey(id, hash), false) === true,
        async setRead(id, hash, read) {
            await store.update(lessonKey(id, hash), read ? true : undefined);
            for (const listener of [...listeners]) listener();
        },
        onDidChange(listener) {
            listeners.add(listener);
            return () => { listeners.delete(listener); };
        },
    };
}

// === Theory for a task ===

export interface TheoryItem {
    id: string;
    title: string;
    html: string;
    content_hash: string;
}

export interface TheoryDeps {
    listLessons(): Promise<LessonMeta[]>;
    getLesson(id: string): Promise<LessonFull>;
    render(markdown: string): string;
}

/** Resolve a task's linked lessons, in the task's order.
 *
 * Cached by content_hash: the cheap /lessons list tells us the current hash,
 * so the body is fetched only when it is new or changed. Lessons that fail to
 * load (hidden, removed, network) are skipped rather than failing the task.
 */
export async function resolveTheory(
    ids: string[],
    deps: TheoryDeps,
    cache: Map<string, TheoryItem>
): Promise<TheoryItem[]> {
    if (!ids.length) return [];
    let hashes: Map<string, string> | undefined;
    try {
        hashes = new Map((await deps.listLessons()).map((l) => [l.id, l.content_hash]));
    } catch {
        hashes = undefined;
    }
    const items: TheoryItem[] = [];
    for (const id of ids) {
        const cached = cache.get(id);
        if (cached && hashes?.get(id) === cached.content_hash) {
            items.push(cached);
            continue;
        }
        try {
            const lesson = await deps.getLesson(id);
            const item: TheoryItem = {
                id: lesson.id, title: lesson.title,
                html: deps.render(lesson.body_md), content_hash: lesson.content_hash,
            };
            cache.set(id, item);
            items.push(item);
        } catch {
            // Skip an unavailable lesson.
        }
    }
    return items;
}

/** Offer «Повтори теорию» only after a real attempt that did not fully pass. */
export function shouldSuggestTheory(
    result: { status: string } | null | undefined,
    theory: readonly unknown[] | undefined
): boolean {
    if (!result || !theory?.length) return false;
    return result.status !== 'passed' && result.status !== 'no_tests';
}
