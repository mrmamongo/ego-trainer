/** Commands of multi-file challenges (ADR-0018 D18.6).
 *
 * «Начать челлендж» writes `challenges/<folder_id>/` from `starter/` and
 * `.cogito/challenge.json` (existing files are never overwritten);
 * «Проверить этап» collects the project, posts `files` and shows the results
 * grouped by stage; «Запустить» opens a terminal with the entry program.
 * The decisions are pure (`challengeWorkspace.ts`, `challengeRunner.ts`);
 * this module is the VS Code I/O around them.
 */

import * as vscode from 'vscode';
import { ChallengeInfo, CheckResponse, EgoApi } from './api';
import {
    CHALLENGE_DIR, CHALLENGE_FILE, CHALLENGES_DIR, ChallengeLimitError, ChallengeMarker,
    challengeIdFromTaskId, collectChallengeFiles, isValidChallengeId, nextStageNumber,
    orderedStages, parseChallengeMarker, planStarter, serializeChallengeMarker, stageAfter,
    stageByNumber,
} from './challengeWorkspace';
import { challengeCommandLine, challengeRunCommand, PYTHON_PATH_SETTING } from './challengeRunner';
import { workspaceRoot } from './egoWorkspace';
import { TestResultsPanel } from './resultsPanel';
import { TaskViewPanel } from './taskViewPanel';

/** What the challenge commands need from the extension. */
export interface ChallengeCommandDeps {
    api: () => EgoApi;
    /** Server address the workspace is connected to (stored in challenge.json). */
    serverUrl: () => string;
    /** Re-draw the tree after a stage was checked or a project started. */
    refreshTree: () => void;
    /** The stage on screen (the task view panel's current task). */
    currentTaskId: () => string | undefined;
    /** Whether the task view panel shows `taskId` (results go to it instead). */
    panelShows: (taskId: string) => boolean;
    /** Hand a result to the open task view panel. */
    postResult: (result: CheckResponse) => boolean;
    /** Status bar message of a finished check. */
    showResult: (result: CheckResponse, taskId: string) => void;
}

const FAILED_STORE_PREFIX = 'ego.challengeFailed:';
const LAST_STAGE_KEY = 'ego.challengeLastStage';

/** `challenges/<id>/`. */
export function challengeFolder(challengeId: string): vscode.Uri | undefined {
    const root = workspaceRoot();
    return root ? vscode.Uri.joinPath(root, CHALLENGES_DIR, challengeId) : undefined;
}

/** `.cogito/challenge.json` of a project folder. */
export function markerUri(folder: vscode.Uri): vscode.Uri {
    return vscode.Uri.joinPath(folder, CHALLENGE_DIR, CHALLENGE_FILE);
}

/** `challenges/<id>` — the folder as the student sees it. */
export function challengeFolderPath(challengeId: string): string {
    return `${CHALLENGES_DIR}/${challengeId}`;
}

async function readText(uri: vscode.Uri): Promise<string | undefined> {
    try {
        return Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf-8');
    } catch {
        return undefined;
    }
}

export async function readMarker(folder: vscode.Uri): Promise<ChallengeMarker | undefined> {
    const text = await readText(markerUri(folder));
    return text === undefined ? undefined : parseChallengeMarker(text);
}

function showError(action: string, error: unknown): void {
    vscode.window.showErrorMessage(`Cogito: ${action} — ${(error as Error).message}`);
}

/** Relative POSIX paths of every file under `folder` (no glob, no symlinks). */
export async function listRelative(folder: vscode.Uri, prefix = ''): Promise<string[]> {
    const out: string[] = [];
    let entries: [string, vscode.FileType][];
    try {
        entries = await vscode.workspace.fs.readDirectory(folder);
    } catch {
        return out;
    }
    for (const [name, type] of entries) {
        const relative = prefix ? `${prefix}/${name}` : name;
        if ((type & vscode.FileType.SymbolicLink) !== 0) continue;
        if ((type & vscode.FileType.Directory) !== 0) {
            out.push(...await listRelative(vscode.Uri.joinPath(folder, name), relative));
        } else {
            out.push(relative);
        }
    }
    return out;
}

// === Start ===

/**
 * «Cogito: начать челлендж» (`ego.startChallenge`): `target` is a challenge
 * folder id or a stage task id; without one a QuickPick asks.
 */
export async function startChallenge(
    deps: ChallengeCommandDeps,
    context: vscode.ExtensionContext,
    target?: string
): Promise<void> {
    const challengeId = typeof target === 'string'
        ? (challengeIdFromTaskId(target) ?? target)
        : await pickChallenge(deps);
    if (!challengeId) return;
    if (!isValidChallengeId(challengeId)) {
        vscode.window.showErrorMessage(`Cogito: «${challengeId}» — недопустимый идентификатор челленджа.`);
        return;
    }
    if (!workspaceRoot()) {
        vscode.window.showErrorMessage('Cogito: папка проекта не открыта.');
        return;
    }
    let challenge: ChallengeInfo | null;
    try {
        challenge = await deps.api().getChallenge(challengeId);
    } catch (error) {
        showError('не удалось загрузить челлендж', error);
        return;
    }
    if (!challenge) {
        vscode.window.showWarningMessage(
            `Cogito: сервер не знает челлендж ${challengeId}. Обнови Cogito или проверь подключение.`
        );
        return;
    }
    const folder = challengeFolder(challenge.id);
    if (!folder) return;
    try {
        await vscode.workspace.fs.createDirectory(folder);

        // Existing files are never overwritten (ADR-0018 D18.6).
        const plan = planStarter(challenge.starter, await listRelative(folder));
        for (const [path, content] of Object.entries(plan.create)) {
            const uri = vscode.Uri.joinPath(folder, ...path.split('/'));
            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(uri, '..'));
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf-8'));
        }
        if (plan.rejected.length) {
            vscode.window.showWarningMessage(
                `Cogito: стартовые файлы с небезопасными путями пропущены: ${plan.rejected.map((item) => item.path).join(', ')}`
            );
        }

        // The stage to open first: where the project was left, else the next unsolved one.
        const previous = await readMarker(folder);
        const stage = previous ? stageByNumber(challenge.stages, previous.stage)?.number ?? nextStageNumber(challenge.stages)
            : nextStageNumber(challenge.stages);
        const marker: ChallengeMarker = { id: challenge.id, server: deps.serverUrl(), stage };
        await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(folder, CHALLENGE_DIR));
        await vscode.workspace.fs.writeFile(markerUri(folder), Buffer.from(serializeChallengeMarker(marker), 'utf-8'));
        deps.refreshTree();

        const created = Object.keys(plan.create).length;
        const kept = plan.skipped.length;
        vscode.window.showInformationMessage(
            `Cogito: «${challenge.name}» — папка ${challengeFolderPath(challenge.id)}/` +
            (created ? `, создано файлов: ${created}` : '') +
            (kept ? `${created ? '' : ', '}существующие файлы не тронуты: ${kept}` : '') +
            `. Открыт этап ${stage}.`
        );
        await openChallengeStage(deps, context, challenge, stage);
    } catch (error) {
        showError('не удалось начать челлендж', error);
    }
}

/** Challenge folders among the server's stages, from the task list. */
async function pickChallenge(deps: ChallengeCommandDeps): Promise<string | undefined> {
    let tasks: Awaited<ReturnType<EgoApi['listTasks']>>;
    try {
        tasks = await deps.api().listTasks();
    } catch (error) {
        showError('не удалось получить список челленджей', error);
        return undefined;
    }
    const ids = new Map<string, string>();
    for (const task of tasks) {
        const id = challengeIdFromTaskId(task.task_id);
        if (id) ids.set(id, task.folder_name || id);
    }
    if (ids.size === 0) {
        vscode.window.showWarningMessage('Cogito: на сервере пока нет челленджей.');
        return undefined;
    }
    const picked = await vscode.window.showQuickPick(
        [...ids].map(([id, name]) => ({ label: name, description: id, id })),
        { placeHolder: 'Какой челлендж начать?' }
    );
    return picked?.id;
}

// === Stage panel ===

/** Open stage `stage` of a challenge: the stage panel + the project entry file. */
export async function openChallengeStage(
    deps: ChallengeCommandDeps,
    context: vscode.ExtensionContext,
    challenge: ChallengeInfo,
    stage: number
): Promise<void> {
    const item = stageByNumber(challenge.stages, stage);
    if (!item) {
        vscode.window.showWarningMessage(`Cogito: у челленджа «${challenge.name}» нет этапа ${stage}.`);
        return;
    }
    const folder = challengeFolder(challenge.id);
    if (!folder) return;
    // Remember the stage in .cogito: the project reopens where it was left.
    const marker = await readMarker(folder);
    if (marker) {
        await vscode.workspace.fs.writeFile(
            markerUri(folder),
            Buffer.from(serializeChallengeMarker({ ...marker, stage: item.number }), 'utf-8')
        );
    }
    await context.workspaceState.update(LAST_STAGE_KEY, { challengeId: challenge.id, taskId: item.id });
    const entry = challenge.workspace.entry || 'main.py';
    const entryUri = vscode.Uri.joinPath(folder, ...entry.split('/'));
    try {
        await vscode.workspace.fs.stat(entryUri);
        const document = await vscode.workspace.openTextDocument(entryUri);
        await vscode.window.showTextDocument(document, vscode.ViewColumn.One);
    } catch {
        vscode.window.showWarningMessage(
            `Cogito: в ${challengeFolderPath(challenge.id)}/ нет ${entry}. Создай его и сохрани.`
        );
    }
    await TaskViewPanel.showStage(challenge.id, item.id, item.number, item.title);
}

/** «Cogito: открыть этап» (`ego.openStage`): a tree stage row or a task id. */
export async function openStageCommand(
    deps: ChallengeCommandDeps,
    context: vscode.ExtensionContext,
    taskId: string,
    challengeId?: string
): Promise<void> {
    const id = challengeId ?? challengeIdFromTaskId(taskId);
    if (!id) {
        vscode.window.showWarningMessage(`Cogito: ${taskId} — не этап челленджа.`);
        return;
    }
    let challenge: ChallengeInfo | null;
    try {
        challenge = await deps.api().getChallenge(id);
    } catch (error) {
        showError('не удалось загрузить челлендж', error);
        return;
    }
    if (!challenge) {
        vscode.window.showWarningMessage(`Cogito: сервер не знает челлендж ${id}.`);
        return;
    }
    const item = orderedStages(challenge.stages).find((stage) => stage.id.toLowerCase() === taskId.toLowerCase());
    await openChallengeStage(deps, context, challenge, item?.number ?? nextStageNumber(challenge.stages));
}

// === Check ===

/**
 * «Cogito: проверить этап» (`ego.checkStage`): collect the project folder,
 * `POST /check` with `files`, show the results grouped by stage.
 */
export async function checkStage(
    deps: ChallengeCommandDeps,
    context: vscode.ExtensionContext,
    taskId?: string
): Promise<{ challengeId: string; stage: number } | undefined> {
    const api = deps.api();
    const onScreen = taskId ?? deps.currentTaskId();
    let challengeId = onScreen ? challengeIdFromTaskId(onScreen) : undefined;
    let challenge: ChallengeInfo | null = null;
    try {
        if (challengeId) challenge = await api.getChallenge(challengeId);
    } catch (error) {
        showError('не удалось загрузить челлендж', error);
        return undefined;
    }
    // Without a stage on screen: the project folder the student last opened.
    if (!challengeId) {
        const last = await lastChallenge(context);
        if (!last) {
            vscode.window.showWarningMessage(
                'Cogito: этап не выбран. Открой челлендж в списке задач или выполни «Cogito: начать челлендж».'
            );
            return undefined;
        }
        challengeId = last.challengeId;
        challenge = await api.getChallenge(challengeId);
    }
    if (!challenge) {
        vscode.window.showWarningMessage(`Cogito: сервер не знает челлендж ${challengeId}.`);
        return undefined;
    }
    const folder = challengeFolder(challenge.id);
    if (!folder) {
        vscode.window.showErrorMessage('Cogito: папка проекта не открыта.');
        return undefined;
    }
    const marker = await readMarker(folder);
    // The stage on screen, else the one the project was left on, else the next unsolved one.
    const stored = marker?.id === challenge.id ? marker.stage : undefined;
    const stageItem = orderedStages(challenge.stages)
        .find((stage) => stage.id.toLowerCase() === (onScreen ?? '').toLowerCase())
        ?? stageByNumber(challenge.stages, stored ?? nextStageNumber(challenge.stages));
    if (!stageItem) {
        vscode.window.showWarningMessage(`Cogito: в челлендже «${challenge.name}» не нашёлся этап.`);
        return undefined;
    }

    let files: Record<string, string>;
    try {
        files = (await collectProjectFiles(folder, challenge)).files;
    } catch (error) {
        if (error instanceof ChallengeLimitError) {
            vscode.window.showErrorMessage(`Cogito: проект не отправлен. ${error.message}`);
            return undefined;
        }
        showError('не удалось собрать файлы проекта', error);
        return undefined;
    }
    if (Object.keys(files).length === 0) {
        vscode.window.showWarningMessage(
            `Cogito: в ${challengeFolderPath(challenge.id)}/ нет файлов по include ` +
            `(${challenge.workspace.include.join(', ')}). Выполни «Cogito: начать челлендж».`
        );
        return undefined;
    }

    const before = failedStages(context, challenge.id);
    let result: CheckResponse;
    try {
        result = await api.checkFiles(stageItem.id, files);
    } catch (error) {
        showError('проверка не удалась', error);
        return undefined;
    }

    // A passed stage needs every earlier stage to pass too (ADR-0018 D18.2).
    const broken = new Set<number>();
    for (const row of result.results) {
        if (!row.passed && typeof row.stage === 'number' && row.stage < stageItem.number) broken.add(row.stage);
    }
    await saveFailedStages(context, challenge.id, broken);
    const healed = before.filter((stage) => !broken.has(stage));

    if (deps.panelShows(stageItem.id) && deps.postResult(result)) {
        deps.showResult(result, stageItem.id);
    } else {
        TestResultsPanel.show(result);
    }
    deps.refreshTree();
    await context.workspaceState.update(LAST_STAGE_KEY, { challengeId: challenge.id, taskId: stageItem.id });

    if (broken.size) {
        vscode.window.showWarningMessage(
            `Cogito: этап ${stageItem.number} не пройден — сломанные прошлые этапы: ` +
            `${[...broken].sort((a, b) => a - b).join(', ')}. Тесты этапов 1..${stageItem.number} должны проходить.`
        );
    } else if (healed.length) {
        vscode.window.showInformationMessage(
            `Cogito: прошлые этапы снова проходят: ${healed.sort((a, b) => a - b).join(', ')}.`
        );
    }

    if (result.status === 'passed') {
        const next = stageAfter(challenge.stages, stageItem.number);
        if (next) {
            const choice = await vscode.window.showInformationMessage(
                `Cogito: этап ${stageItem.number} «${stageItem.title}» пройден. Открыть следующий этап?`,
                'Открыть следующий этап'
            );
            if (choice) await openChallengeStage(deps, context, challenge, next.number);
        }
    }
    return { challengeId: challenge.id, stage: stageItem.number };
}

/** Every local file of the project folder, decided for the submission. */
async function collectProjectFiles(folder: vscode.Uri, challenge: ChallengeInfo) {
    return collectChallengeFiles({
        paths: await listRelative(folder),
        workspace: challenge.workspace,
        read: async (path) => {
            const uri = vscode.Uri.joinPath(folder, ...path.split('/'));
            const open = vscode.workspace.textDocuments.find((doc) => doc.uri.toString() === uri.toString());
            // Unsaved edits of the open editor are what the student sees.
            if (open) return open.getText();
            return new Uint8Array(await vscode.workspace.fs.readFile(uri));
        },
    });
}

interface LastChallenge {
    challengeId: string;
    taskId: string;
}

async function lastChallenge(context: vscode.ExtensionContext): Promise<LastChallenge | undefined> {
    const stored = context.workspaceState.get<LastChallenge>(LAST_STAGE_KEY);
    if (stored && typeof stored.challengeId === 'string' && isValidChallengeId(stored.challengeId)) return stored;
    return undefined;
}

function failedStages(context: vscode.ExtensionContext, challengeId: string): number[] {
    const stored = context.workspaceState.get<number[]>(FAILED_STORE_PREFIX + challengeId, []);
    return Array.isArray(stored) ? stored.filter((value) => typeof value === 'number') : [];
}

async function saveFailedStages(
    context: vscode.ExtensionContext,
    challengeId: string,
    broken: Set<number>
): Promise<void> {
    const merged = [...new Set([...failedStages(context, challengeId), ...broken])].sort((a, b) => a - b);
    await context.workspaceState.update(FAILED_STORE_PREFIX + challengeId, merged);
}

// === Run ===

/**
 * «Cogito: запустить программу» (`ego.runChallenge`): a terminal in
 * `challenges/<id>/` running the entry program.
 */
export async function runChallenge(
    deps: ChallengeCommandDeps,
    challengeId: string,
    entry = 'main.py'
): Promise<void> {
    const folder = challengeFolder(challengeId);
    if (!folder) {
        vscode.window.showErrorMessage('Cogito: папка проекта не открыта.');
        return;
    }
    const relative = await listRelative(folder);
    if (!relative.length) {
        vscode.window.showWarningMessage(
            `Cogito: папка ${challengeFolderPath(challengeId)}/ пуста. Выполни «Cogito: начать челлендж».`
        );
        return;
    }
    if (!relative.includes(entry)) {
        vscode.window.showWarningMessage(`Cogito: в ${challengeFolderPath(challengeId)}/ нет ${entry}.`);
        return;
    }
    const pythonPath = vscode.workspace.getConfiguration('ego').get<string>(PYTHON_PATH_SETTING, '')
        || vscode.workspace.getConfiguration('python').get<string>('defaultInterpreterPath', '');
    const command = challengeRunCommand({
        workspaceFolders: (vscode.workspace.workspaceFolders ?? []).map((item) => item.uri.fsPath),
        entry,
        pythonPath,
        hasPyproject: relative.includes('pyproject.toml'),
        hasVenv: relative.some((path) => path === '.venv' || path.startsWith('.venv/')),
    });
    const terminal = vscode.window.createTerminal({ name: `Cogito: ${challengeId}`, cwd: folder.fsPath });
    terminal.show();
    // The command semantics stay in the pure `challengeRunner`; the line only
    // brings back not-found / permission problems of the interpreter.
    terminal.sendText(challengeCommandLine(command, entry, process.platform));
    await deps.refreshTree();
}
