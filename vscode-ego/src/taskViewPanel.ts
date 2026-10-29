/** Task view webview host (ADR-0015 / 8bv.9.6). */

import * as vscode from 'vscode';
import { EgoApi, CheckResponse, LessonMeta, TaskMeta } from './api';
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
import { resolveTheory, type LessonReadState, type TheoryItem } from './theoryLogic';
import { handleTrainerMessage, isTrainerMessage, trainerKindFromTags, type TrainerContext } from './trainerHost';
import {
    challengeIdFromTaskId, challengeViewInfo, parseStageNav, stageByNumber, type ChallengeViewInfo,
} from './challengeWorkspace';

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
    /** 'lesson' renders a theory card (no check, read toggle). Default 'task'. */
    kind?: 'task' | 'lesson';
    /** Linked theory lessons of a task, in order (server mode only). */
    theory?: TheoryViewItem[];
    lesson?: { id: string; content_hash: string; read: boolean };
    /** Interactive trainer for tasks tagged `trace` / `parsons`. */
    trainer?: 'trace' | 'parsons';
    /** Multi-file challenge: the stage panel layout (ADR-0018 D18.6). */
    challenge?: ChallengeViewInfo;
}

export type TheoryViewItem = Pick<TheoryItem, 'id' | 'title' | 'html'>;

export interface TaskViewDeps {
    getApi: () => EgoApi;
    checkTask: (taskId: string) => Promise<void>;
    openPy: (taskId: string, slug?: string, mdPath?: string) => Promise<void>;
    readState: LessonReadState;
    /** Challenge project folder and navigation (optional: older wiring). */
    challenge?: ChallengeViewDeps;
}

export interface ChallengeViewDeps {
    /** `challenges/<id>/` of the project, for the given challenge folder id. */
    projectFolder: (challengeId: string) => string;
    /** Show stage `stage` (opens its statement in this panel). */
    openStage: (challengeId: string, stage: number) => Promise<void>;
    run: (challengeId: string) => Promise<void>;
}

interface TaskRef {
    id: string;
    title: string;
    slug: string;
    version: string;
    status: string;
    md_path?: string;
    kind?: 'task' | 'lesson';
    /** Lesson version the read flag belongs to (known after the body loads). */
    content_hash?: string;
    /** Challenge folder id and the stage shown (stage panel mode). */
    challenge_id?: string;
    stage?: number;
    /** `id` is a stage task id (`stage_02_…`), so its own statement loads normally. */
    challenge_task?: boolean;
}

export class TaskViewPanel {
    private static panel: vscode.WebviewView | undefined;
    private static extensionUri: vscode.Uri | undefined;
    private static deps: TaskViewDeps | undefined;
    private static ready = false;
    private static current: TaskRef | undefined;
    private static generation = 0;
    private static results = new Map<string, CheckResponse>();
    private static theoryCache = new Map<string, TheoryItem>();

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

    static showLesson(lesson: LessonMeta): Promise<void> {
        return this.show({ id: lesson.id, title: lesson.title, slug: '', version: lesson.version,
            status: 'new', kind: 'lesson', content_hash: lesson.content_hash });
    }

    /** The stage panel: the stage statement + every stage with its status. */
    static showStage(challengeId: string, taskId: string, stage: number, title = ''): Promise<void> {
        const current = this.current;
        // Same challenge, stage already on screen: keep an unsaved state.
        if (current?.challenge_id === challengeId && current.id === taskId && current.stage === stage) return Promise.resolve();
        return this.show({ id: taskId, title, slug: '', version: '', status: 'new', challenge_id: challengeId, stage,
            // The challenge folder id of a stage id (`stage_02_set_get` → `set_get`).
            challenge_task: challengeIdFromTaskId(taskId) === challengeId });
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

    private static async onMessage(msg: { type?: string; taskId?: string; read?: boolean }): Promise<void> {
        const cur = this.current, deps = this.deps;
        if (!deps) return;
        if (msg.type === 'taskView.openLink' && typeof (msg as { target?: unknown }).target === 'string') {
            await openTaskLink((msg as { target: string }).target);
            return;
        }
        if (isTrainerMessage(msg)) {
            const trainer = await this.trainer();
            if (trainer && await handleTrainerMessage(msg as Parameters<typeof handleTrainerMessage>[0], trainer)) return;
        }
        // Challenge stage panel: stage clicks and «Запустить» carry the challenge id.
        const challengeNav = parseStageNav(msg);
        if (challengeNav) {
            if (challengeNav.challengeId === cur?.challenge_id) await deps.challenge?.openStage(challengeNav.challengeId, challengeNav.stage);
            return;
        }
        const challengeMsg = msg as { type?: string; challengeId?: unknown; stage?: unknown };
        if (challengeMsg.type === 'challenge.run' && typeof challengeMsg.challengeId === 'string') {
            await deps.challenge?.run(challengeMsg.challengeId);
            return;
        }
        if (challengeMsg.type === 'challenge.openNext' && typeof challengeMsg.challengeId === 'string'
            && typeof challengeMsg.stage === 'number' && challengeMsg.challengeId === cur?.challenge_id) {
            await deps.challenge?.openStage(challengeMsg.challengeId, challengeMsg.stage + 1);
            return;
        }
        if (msg.type !== 'ready' && msg.type !== 'taskView.refresh' && msg.taskId !== cur?.id) return;
        switch (msg.type) {
            case 'ready': this.ready = true; await this.pushData(); break;
            case 'taskView.check': if (cur) await deps.checkTask(cur.id); break;
            case 'taskView.openPy': if (cur) await deps.openPy(cur.id, cur.slug, cur.md_path); break;
            case 'taskView.refresh': await this.pushData(); break;
            case 'taskView.toggleRead': await this.toggleRead(msg.read === true); break;
            case 'taskView.assistant': if (cur) await vscode.commands.executeCommand('ego.assistant', cur.id); break;
        }
    }

    /** Context for the trace/Parsons trainers: the student's local .py file of the current task. */
    private static async trainer(): Promise<TrainerContext | undefined> {
        const cur = this.current, panel = this.panel, deps = this.deps;
        if (!cur || !panel || !deps || cur.kind === 'lesson') return undefined;
        let pyUri = await findLocalPy(cur);
        if (!pyUri) {
            // Server mode before the first open: let the normal flow pull the starter.
            await deps.openPy(cur.id, cur.slug, cur.md_path);
            pyUri = await findLocalPy(cur);
        }
        if (!pyUri) return undefined;
        const uri = pyUri;
        return {
            pyUri: uri,
            // Read through the open document so unsaved edits are kept.
            readFile: async () => vscode.workspace.textDocuments.find((d) => d.uri.toString() === uri.toString())?.getText()
                ?? Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf-8'),
            writeFile: async (text: string) => {
                const doc = await vscode.workspace.openTextDocument(uri);
                const edit = new vscode.WorkspaceEdit();
                edit.replace(doc.uri, new vscode.Range(doc.positionAt(0), doc.positionAt(doc.getText().length)), text);
                await vscode.workspace.applyEdit(edit);
                await doc.save();
            },
            runCheck: () => deps.checkTask(cur.id),
            post: (message: unknown) => void panel.webview.postMessage(message),
        } as TrainerContext;
    }

    private static async toggleRead(read: boolean): Promise<void> {
        const cur = this.current, deps = this.deps;
        if (!cur || cur.kind !== 'lesson' || !cur.content_hash || !deps) return;
        await deps.readState.setRead(cur.id, cur.content_hash, read);
        if (this.ready && this.panel && this.current?.id === cur.id) {
            void this.panel.webview.postMessage({ type: 'taskView.setLessonRead', taskId: cur.id, read });
        }
    }

    private static async pushData(): Promise<void> {
        const deps = this.deps, cur = this.current, panel = this.panel, generation = this.generation;
        if (!deps || !cur || !panel || !this.ready) return;
        void panel.webview.postMessage({ type: 'taskView.setData', payload: {
            id: cur.id, title: cur.title, status: cur.status, version: cur.version,
            statement_html: '', hints: [], history: [], mode: 'offline', loading: true, kind: cur.kind,
        } satisfies TaskViewData });
        const isCurrent = () => this.generation === generation && this.panel === panel;
        try {
            let data: TaskViewData;
            const stageRef = cur.challenge_task ? { ...cur, kind: undefined as undefined, challenge_id: undefined } : cur;
            if (cur.challenge_id !== undefined && cur.stage !== undefined) {
                // A stage still loads its task normally; the stage list is added on top.
                const base = await loadTaskViewData(deps.getApi(), stageRef, this.theoryCache);
                data = { ...base, title: cur.title || base.title, kind: undefined,
                    challenge: await challengeBlock(deps, cur.challenge_id, cur.stage) };
            } else if (cur.kind === 'lesson') {
                data = await loadLessonViewData(deps.getApi(), cur, deps.readState);
            } else {
                data = await loadTaskViewData(deps.getApi(), cur, this.theoryCache);
            }
            if (!isCurrent()) return;
            if (data.lesson) this.current = { ...cur, content_hash: data.lesson.content_hash };
            // The panel moved to another stage while loading: switch it without a reload.
            const onScreen = this.current;
            if (data.challenge && onScreen?.challenge_id === data.challenge.challenge_id
                && onScreen.stage !== undefined && onScreen.stage !== data.challenge.stage) {
                void panel.webview.postMessage({ type: 'challenge.stageData',
                    payload: { challenge_id: data.challenge.challenge_id, stage: data.challenge.stage } });
                return;
            }
            const result = (cur.challenge_id !== undefined && !cur.challenge_task) || cur.kind === 'lesson'
                ? undefined
                : this.results.get(cur.id.toLowerCase());
            if (result) data.status = result.status;
            void panel.webview.postMessage({ type: 'taskView.setData', payload: data });
            if (result) void panel.webview.postMessage({ type: 'taskView.setResult', payload: result });
        } catch (error) {
            if (!isCurrent()) return;
            void panel.webview.postMessage({ type: 'taskView.setData', payload: {
                id: cur.id, title: cur.title, status: cur.status, version: cur.version,
                statement_html: '<p>' + escapeHtml((error as Error).message) + '</p>',
                hints: [], history: [], mode: 'offline', kind: cur.kind,
            } satisfies TaskViewData });
        }
    }
}

/** `task:<id>` / `lesson:<id>` links inside statements and theory cards. */
async function openTaskLink(target: string): Promise<void> {
    const match = /^(task|lesson):(.+)$/.exec(target.trim());
    if (!match) return;
    const id = decodeURIComponent(match[2]);
    await vscode.commands.executeCommand(match[1] === 'task' ? 'ego.openTaskById' : 'ego.openLessonById', id);
}

/**
 * Stage list of the stage panel. An old server (no /challenges route) or a
 * broken statement still shows the stage: the block is simply left out.
 */
async function challengeBlock(
    deps: TaskViewDeps,
    challengeId: string | undefined,
    stage: number
): Promise<ChallengeViewInfo | undefined> {
    if (!challengeId) return undefined;
    try {
        const challenge = await deps.getApi().getChallenge(challengeId);
        if (!challenge) return undefined;
        const item = stageByNumber(challenge.stages, stage);
        if (!item) return undefined;
        const folder = deps.challenge?.projectFolder(challengeId) ?? `challenges/${challengeId}`;
        return challengeViewInfo(challenge, item.number, folder);
    } catch {
        return undefined;
    }
}

/** Lesson mode: the card body rendered like a statement, plus its read flag. */
async function loadLessonViewData(api: EgoApi, ref: TaskRef, readState: LessonReadState): Promise<TaskViewData> {
    const lesson = await api.getLesson(ref.id);
    return {
        id: lesson.id,
        title: lesson.title,
        status: 'new',
        version: lesson.version,
        statement_html: renderMarkdownHtml(lesson.body_md),
        hints: [],
        history: [],
        mode: 'server',
        kind: 'lesson',
        lesson: { id: lesson.id, content_hash: lesson.content_hash, read: readState.isRead(lesson.id, lesson.content_hash) },
    };
}

async function loadTaskViewData(api: EgoApi, ref: TaskRef, theoryCache: Map<string, TheoryItem>): Promise<TaskViewData> {
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
            const theory = await resolveTheory(full.theory ?? [], {
                listLessons: () => api.listLessons(),
                getLesson: (id) => api.getLesson(id),
                render: renderMarkdownHtml,
            }, theoryCache);
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
                theory: theory.map(({ id, title, html }) => ({ id, title, html })),
                trainer: trainerKindFromTags(full.tags),
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
    if (!root) throw new Error('Папка проекта не открыта.');

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
    throw new Error(`Файл условия задачи ${ref.id} не найден.`);
}

async function readLocalStub(ref: TaskRef): Promise<string> {
    const uri = await findLocalPy(ref, false);
    if (!uri) return '';
    try {
        return Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf-8');
    } catch {
        return '';
    }
}

/** The student's task .py: tasks/<slug>/, next to md_path, then (optionally) a workspace search. */
async function findLocalPy(ref: TaskRef, search = true): Promise<vscode.Uri | undefined> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) return undefined;
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
            await vscode.workspace.fs.stat(uri);
            return uri;
        } catch {
            // next
        }
    }
    if (!search) return undefined;
    const found = await vscode.workspace.findFiles(
        new vscode.RelativePattern(root, `**/${filename}`),
        '**/node_modules/**',
        1
    );
    return found[0];
}

function escapeHtml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
