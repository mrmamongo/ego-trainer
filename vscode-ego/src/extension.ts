/** Ego Trainer — VSCode extension entry point.
 *
 * Provides commands for checking tasks, pulling from server, and viewing
 * progress. Uses ego-server (FastAPI) as backend via HTTP.
 *
 * Per ADR-0014: extension = thin UI, all logic on server.
 */

import * as vscode from 'vscode';
import { EgoApi, CheckResponse, LessonMeta, TaskMeta } from './api';
import { EgoTaskTreeProvider, LessonItem, TaskItem } from './treeProvider';
import { createReadState } from './theoryLogic';
import { TestResultsPanel } from './resultsPanel';
import { WelcomeView } from './welcomeView';
import { runOfflineInit, runServerInit } from './initWizard';
import { pullTasksToWorkspace } from './pullTasks';
import { DashboardView } from './dashboardView';
import { TaskViewPanel } from './taskViewPanel';
import { openTaskPy, openTaskWithView } from './openTask';
import { readEgoConfig, writeEgoConfig, readManifest, type EgoMode } from './egoWorkspace';
import { forgejoLogin, registerForgejoUriHandler } from './forgejoLogin';
import { decideSession } from './sessionDecision';
import { classifyAuthStatus, decideAuthStart, type AuthMeResult } from './authStatus';
import { EgoApiError } from './api';
import { EgoStatusBar } from './statusBar';
import { runOfflineCheck } from './offlineCheck';
import { switchMode } from './modeSwitch';
import { AssistantPanel } from './assistantPanel';
import { setupPythonEnv } from './pythonSetup';
import { taskIdFromFilePath } from './taskContext';
import {
    checkForUpdatesManually,
    currentExtensionVersion,
    scheduleUpdateCheck,
    type UpdateCheckDeps,
} from './updateCheck';

const SECRET_KEY = 'ego.token';

let api: EgoApi;
let treeProvider: EgoTaskTreeProvider;
let statusBar: EgoStatusBar;

async function recreateApi(context: vscode.ExtensionContext): Promise<void> {
    AssistantPanel.close();
    const settingsUrl = vscode.workspace
        .getConfiguration('ego')
        .get<string>('serverUrl', 'http://localhost:8000');
    const workspaceConfig = await readEgoConfig();
    const session = decideSession(workspaceConfig, await context.secrets.get(SECRET_KEY));
    api = trackApiToken(new EgoApi(settingsUrl, session.apiToken), session.apiToken);
    treeProvider.updateApi(api);
    void refreshAssistantAccess();
}

async function refreshAssistantAccess(): Promise<void> {
    const offline = (await readEgoConfig())?.mode === 'offline';
    const access = offline ? null : await api.getAIAccount().catch(() => null);
    await vscode.commands.executeCommand('setContext', 'ego.aiEnabled', !!access?.enabled);
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
    registerForgejoUriHandler(context);
    // Load config.
    const config = vscode.workspace.getConfiguration('ego');
    const settingsUrl = config.get<string>('serverUrl', 'http://localhost:8000');
    const workspaceConfig = await readEgoConfig();
    const storedToken = await context.secrets.get(SECRET_KEY);
    const session = decideSession(workspaceConfig, storedToken);
    const serverUrl = settingsUrl;

    // Svelte webview bundles live under out/webview/ (ADR-0015).
    TestResultsPanel.configure(context.extensionUri);
    AssistantPanel.configure(context.extensionUri, () => api);
    AssistantPanel.register(context);

    api = trackApiToken(new EgoApi(serverUrl, session.apiToken), session.apiToken);

    // Tree view.
    // Lesson read flags live in globalState; the tree redraws when they change.
    const readState = createReadState(context.globalState);
    treeProvider = new EgoTaskTreeProvider(api, readState);

    DashboardView.configure(context.extensionUri, {
        getApi: () => api,
        refreshTree: () => treeProvider.refresh(),
        openTask: (task) => cmdOpenTask(task),
        checkTask: (taskId) => cmdCheckTask(taskId),
        showHints: (taskId) => cmdHintsForTask(taskId),
        pullAll: () => cmdPullAll(),
        pushProgress: () => cmdPush(),
    });

    TaskViewPanel.configure(context.extensionUri, {
        getApi: () => api,
        checkTask: (taskId) => cmdCheckTask(taskId),
        openPy: (taskId, slug, mdPath) => openTaskPy(taskId, slug, mdPath).then(() => undefined),
        readState,
    });
    TaskViewPanel.register(context);
    const treeView = vscode.window.createTreeView('egoTaskTree', {
        treeDataProvider: treeProvider,
        showCollapseAll: true,
    });
    context.subscriptions.push(treeView);
    let selectionGeneration = 0;
    const followEditor = async (editor: vscode.TextEditor | undefined) => {
        const taskId = editor && taskIdFromFilePath(editor.document.fileName);
        if (!editor || !taskId) return;
        const generation = ++selectionGeneration;
        const doc = editor.document;
        const getCode = async () => doc.isClosed ? await readTaskPy(taskId) || '' : doc.getText();
        void AssistantPanel.follow(taskId, doc.getText(), getCode);
        const manifest = await readManifest();
        if (generation !== selectionGeneration) return;
        const entry = manifest?.tasks.find(task => task.id.toUpperCase() === taskId);
        const mdPath = vscode.workspace.asRelativePath(doc.uri).replace(/\\/g, '/').replace(/\.py$/i, '.md');
        await TaskViewPanel.followTask({ id: taskId, title: taskId, status: 'new',
            slug: entry?.slug || '', version: entry?.version || '0.0.0', md_path: entry?.md_path || mdPath });
        statusBar?.setTask(taskId);
    };
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => { void followEditor(editor); }));

    // Status bar — click opens Dashboard (ADR-0015 / 8bv.9.8).
    statusBar = new EgoStatusBar('ego.dashboard');
    context.subscriptions.push(statusBar.disposable);
    void followEditor(vscode.window.activeTextEditor);

    const welcomeDeps = () => ({
        onApiChanged: async () => {
            await recreateApi(context);
        },
        refreshTree: () => treeProvider.refresh(),
    });

    /** Gate Ego commands that need `.ego/` — otherwise open Welcome (8bv.9.11). */
    async function withReady<T>(fn: () => T | Promise<T>): Promise<T | undefined> {
        const ok = await WelcomeView.ensureInitialized(context, welcomeDeps());
        if (!ok) return undefined;
        return fn();
    }

    // === Commands ===

    context.subscriptions.push(
        vscode.commands.registerCommand('ego.assistant', (arg?: TaskMeta | TaskItem | string) =>
            withReady(() => cmdAssistant(resolveTaskId(arg)))
        ),
        // Setup / auth — no .ego/ required.
        vscode.commands.registerCommand('ego.login', () => cmdLogin(context)),
        vscode.commands.registerCommand('ego.logout', () => cmdLogout(context)),
        vscode.commands.registerCommand('ego.setServer', () => cmdSetServer(context)),
        vscode.commands.registerCommand('ego.setupPython', () => cmdSetupPython()),
        vscode.commands.registerCommand('ego.checkUpdate', () => cmdCheckUpdate(context)),
        vscode.commands.registerCommand('ego.showWelcome', () =>
            WelcomeView.show(context, welcomeDeps())
        ),
        vscode.commands.registerCommand('ego.init', async () => {
            const mode = await vscode.window.showQuickPick(
                [
                    { label: 'Подключиться к серверу', mode: 'server' as const },
                    { label: 'Работать локально (без сервера)', mode: 'offline' as const },
                ],
                { placeHolder: 'Как ты хочешь подключить Cogito?' }
            );
            if (!mode) return;
            const deps = welcomeDeps();
            if (mode.mode === 'server') {
                await runServerInit(context, deps);
                statusBar.setMode('server');
            await refreshAssistantAccess();
            } else {
                await runOfflineInit(context, deps);
                statusBar.setMode('offline');
            }
        }),

        // Need initialized workspace.
        vscode.commands.registerCommand('ego.check', () => withReady(() => cmdCheck())),
        vscode.commands.registerCommand('ego.checkTask', (arg?: TaskMeta | TaskItem | string) =>
            withReady(() => {
                const id = resolveTaskId(arg);
                return id ? cmdCheckTask(id) : cmdCheck();
            })
        ),
        vscode.commands.registerCommand('ego.pull', () => withReady(() => cmdPull())),
        vscode.commands.registerCommand('ego.pullAll', () => withReady(() => cmdPullAll())),
        vscode.commands.registerCommand('ego.pullAllForce', () => withReady(() => cmdPullAllForce())),
        vscode.commands.registerCommand('ego.pullTask', (arg?: TaskMeta | TaskItem) =>
            withReady(async () => {
                const task = resolveTaskMeta(arg);
                if (!task) {
                    await cmdPull();
                    return;
                }
                try {
                    // Single-task pull always fetches, bypassing the incremental planner.
                    await pullTasksToWorkspace(api, [task], { force: true });
                    treeProvider.refresh();
                    if (DashboardView.isOpen()) await DashboardView.refresh();
                } catch (e) {
                    vscode.window.showErrorMessage(`Cogito: не удалось скачать задачи — ${(e as Error).message}`);
                }
            })
        ),
        vscode.commands.registerCommand('ego.list', () => withReady(() => cmdList())),
        vscode.commands.registerCommand('ego.showTask', () => withReady(() => cmdShowTask())),
        vscode.commands.registerCommand('ego.hints', () => withReady(() => cmdHints())),
        vscode.commands.registerCommand('ego.hintsForTask', (arg?: TaskMeta | TaskItem | string) =>
            withReady(() => {
                const id = resolveTaskId(arg);
                return id ? cmdHintsForTask(id) : cmdHints();
            })
        ),
        vscode.commands.registerCommand('ego.myProgress', () => withReady(() => cmdMyProgress())),
        vscode.commands.registerCommand('ego.push', () => withReady(() => cmdPush())),
        vscode.commands.registerCommand('ego.refreshTree', () => treeProvider.refresh()),
        vscode.commands.registerCommand('ego.openTask', (arg?: TaskMeta | TaskItem) =>
            withReady(() => {
                const task = resolveTaskMeta(arg);
                if (!task) {
                    vscode.window.showWarningMessage('Cogito: задача не выбрана.');
                    return;
                }
                return cmdOpenTask(task);
            })
        ),
        vscode.commands.registerCommand('ego.openLesson', (arg?: LessonMeta | LessonItem) =>
            withReady(() => {
                const lesson = arg instanceof LessonItem ? arg.lesson : arg;
                if (!lesson?.id) {
                    vscode.window.showWarningMessage('Cogito: карточка не выбрана.');
                    return;
                }
                return TaskViewPanel.showLesson(lesson);
            })
        ),
        // Targets of `task:<id>` / `lesson:<id>` links in statements and theory cards.
        vscode.commands.registerCommand('ego.openTaskById', (id: string) =>
            withReady(async () => {
                const task = (await api.listTasks()).find((t) => t.id.toLowerCase() === String(id).toLowerCase());
                if (!task) {
                    vscode.window.showWarningMessage(`Cogito: задача ${id} не найдена.`);
                    return;
                }
                return cmdOpenTask(task);
            })
        ),
        vscode.commands.registerCommand('ego.openLessonById', (id: string) =>
            withReady(async () => {
                const lesson = (await api.listLessons()).find((l) => l.id === id);
                if (!lesson) {
                    vscode.window.showWarningMessage(`Cogito: карточка ${id} не найдена.`);
                    return;
                }
                return TaskViewPanel.showLesson(lesson);
            })
        ),
        vscode.commands.registerCommand('ego.switchMode', () =>
            withReady(() => cmdSwitchMode(context))
        ),
        vscode.commands.registerCommand('ego.dashboard', () =>
            withReady(() => DashboardView.show())
        ),
        vscode.commands.registerCommand('ego.openTaskView', () =>
            withReady(async () => {
                const editor = vscode.window.activeTextEditor;
                if (!editor) {
                    vscode.window.showWarningMessage('Cogito: сначала открой .py-файл задачи.');
                    return;
                }
                const fileName = vscode.workspace.asRelativePath(editor.document.fileName);
                const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
                if (!match) {
                    vscode.window.showWarningMessage(`Cogito: ${fileName} — не файл задачи.`);
                    return;
                }
                const taskId = match[1].replace(/_/g, '.').toUpperCase();
                statusBar.setTask(taskId);
                const cfg = await readEgoConfig();
                if (cfg?.mode === 'offline') {
                    const relativeMdPath = fileName.replace(/\.py$/, '.md').replace(/\\/g, '/');
                    const parts = relativeMdPath.split('/');
                    const tasksIndex = parts.indexOf('tasks');
                    const slug = tasksIndex >= 0 ? parts[tasksIndex + 1] || '' : '';
                    await TaskViewPanel.show({
                        id: taskId,
                        title: taskId,
                        slug,
                        version: '0.0.0',
                        status: 'new',
                        md_path: relativeMdPath,
                    });
                    return;
                }
                try {
                    const task = await api.getTask(taskId);
                    await TaskViewPanel.showFromMeta(task);
                } catch {
                    const parts = fileName.replace(/\\/g, '/').split('/');
                    const slug = parts.includes('tasks')
                        ? parts[parts.indexOf('tasks') + 1]
                        : parts.includes('docs')
                          ? parts[parts.indexOf('docs') + 1] || ''
                          : '';
                    await TaskViewPanel.show({
                        id: taskId,
                        title: taskId,
                        slug: slug || '',
                        version: '0.0.0',
                        status: 'new',
                        md_path: fileName.replace(/\.py$/, '.md'),
                    });
                }
            })
        ),
    );

    // Auto-check on save (if enabled) — only when .ego/ is ready.
    context.subscriptions.push(
        vscode.workspace.onWillSaveTextDocument(async (e) => {
            if (!config.get<boolean>('autoCheckOnSave', false)) return;
            if (!e.document.fileName.match(/task_.*\.py$/)) return;
            e.waitUntil(
                new Promise<void>((resolve) => {
                    setTimeout(async () => {
                        await withReady(() => cmdCheck());
                        resolve();
                    }, 100);
                })
            );
        })
    );

    // Config mode is authoritative for auth and readiness.
    await vscode.commands.executeCommand('setContext', 'ego.offline', session.offline);
    await vscode.commands.executeCommand('setContext', 'ego.loggedIn', false);
    await vscode.commands.executeCommand('setContext', 'ego.ready', session.ready);
    if (session.validateToken) {
        try {
            await api.me();
            await vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
        } catch {
            // Invalid tokens are cleared only while operating in server mode.
            await context.secrets.delete(SECRET_KEY);
        }
    }
    statusBar.setMode(session.status);

    // Auto-reload when serverUrl config changes (e.g. via Settings UI).
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(async (e) => {
            if (e.affectsConfiguration('ego.serverUrl')) {
                const newUrl = vscode.workspace.getConfiguration('ego').get<string>('serverUrl', 'http://localhost:8000');
                await recreateApi(context);
                vscode.window.showInformationMessage(`Cogito: адрес сервера изменён на ${newUrl}`);
            }
        })
    );

    // Auto Welcome after window start (onStartupFinished) if .ego/ missing (8bv.9.11).
    if (await WelcomeView.shouldAutoOpen(context)) {
        WelcomeView.show(context, welcomeDeps());
    }

    // Update notification: ~10 s after activation, at most once per 24 h,
    // never in offline mode (see updateCheck.ts). Fires after activation ends.
    context.subscriptions.push(scheduleUpdateCheck(updateDeps(context)));
}

export function deactivate(): void {
    AssistantPanel.close();
    // Cleanup.
}

// === Command implementations ===

/** Mirror of api's current token, so "a token exists" is known without a private getter. */
let apiToken: string | undefined;

/** Mirror an api created during activation. */
function trackApiToken(created: EgoApi, token: string | undefined): EgoApi {
    created.setToken(token);
    apiToken = token;
    return created;
}

/** Apply the signed-in UI state shared by every successful login path. */
async function applyLoggedInState(): Promise<void> {
    await vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
    statusBar.setMode('server');
    await refreshAssistantAccess();
    treeProvider.refresh();
}

/** Store a new token and restore the signed-in state. */
async function startSession(context: vscode.ExtensionContext, token: string): Promise<void> {
    await context.secrets.store(SECRET_KEY, token);
    apiToken = token;
    api.setToken(token);
    await applyLoggedInState();
}

/** Clear the token and reset the signed-in state (shared by logout and expiry). */
async function resetSession(context: vscode.ExtensionContext): Promise<void> {
    await context.secrets.delete(SECRET_KEY);
    apiToken = undefined;
    api.setToken(undefined);
    AssistantPanel.close();
    await vscode.commands.executeCommand('setContext', 'ego.loggedIn', false);
    await vscode.commands.executeCommand('setContext', 'ego.aiEnabled', false);
    const existing = await readEgoConfig();
    if (existing?.token) await writeEgoConfig({ ...existing, token: '' });
    treeProvider.refresh();
}

interface CurrentAuth {
    result: AuthMeResult;
    me?: { user_id: string; username: string; role: string };
    message?: string;
}

/** Check GET /auth/me for the current token: valid, expired or server unreachable. */
async function checkCurrentAuth(): Promise<CurrentAuth> {
    try {
        return { result: 'ok', me: await api.me() };
    } catch (error) {
        if (error instanceof EgoApiError) return { result: classifyAuthStatus(error.status), message: error.message };
        // fetch() rejects with TypeError when the server cannot be reached.
        return { result: 'unreachable', message: (error as Error).message };
    }
}

async function cmdLogin(context: vscode.ExtensionContext): Promise<void> {
    AssistantPanel.close();
    const storedToken = await context.secrets.get(SECRET_KEY);
    const hasToken = !!(storedToken || apiToken);
    if (hasToken) {
        if (storedToken !== apiToken) {
            apiToken = storedToken;
            api.setToken(storedToken);
        }
        const current = await checkCurrentAuth();
        const start = decideAuthStart({ hasToken, meResult: current.result });
        // Offline mode keeps the token out of api; the check above used it only to look.
        if (start !== 'already') api.setToken(undefined);
        if (start === 'unreachable') {
            vscode.window.showErrorMessage(
                `Cogito: сервер недоступен — ${current.message}. Токен сохранён, проверь подключение и повтори «Cogito: Войти».`
            );
            return;
        }
        if (start === 'already' && current.me) {
            const me = current.me;
            if (storedToken) {
                // A valid session switches an offline workspace back to server mode.
                await vscode.commands.executeCommand('setContext', 'ego.offline', false);
                await startSession(context, storedToken);
            }
            await applyLoggedInState();
            const choice = await vscode.window.showInformationMessage(
                `Cogito: ты уже вошёл как ${me.username} (${me.role})`,
                'Войти другим аккаунтом', 'Выйти',
            );
            if (choice === 'Выйти') await resetSession(context);
            else if (choice === 'Войти другим аккаунтом') await startLoginFlow(context);
            return;
        }
        // Expired or invalid token: drop it before the normal flow.
        await resetSession(context);
    }
    await startLoginFlow(context);
}

async function cmdLogout(context: vscode.ExtensionContext): Promise<void> {
    await resetSession(context);
    vscode.window.showInformationMessage('Cogito: ты вышел из аккаунта.');
}

/** Forgejo browser login, then the local username/password fallback. */
async function startLoginFlow(context: vscode.ExtensionContext): Promise<void> {
    try {
        const response = await forgejoLogin(api);
        if (response !== null) {
            if (!response) return;
            await context.secrets.store(SECRET_KEY, response.access_token);
            apiToken = response.access_token;
            api.setToken(response.access_token);
            const existing = await readEgoConfig();
            if (existing) await writeEgoConfig({ ...existing, token: '', student_id: response.user_id, student_username: response.username, role: response.role });
            await applyLoggedInState();
            vscode.window.showInformationMessage(`Cogito: ты вошёл как ${response.username} (${response.role})`);
            return;
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Cogito: не удалось войти — ${(error as Error).message}`);
        return;
    }
    const username = await vscode.window.showInputBox({
        prompt: 'Логин',
        placeHolder: 'Введи свой логин',
    });
    if (!username) return;

    const password = await vscode.window.showInputBox({
        prompt: 'Пароль',
        password: true,
        placeHolder: 'Введи свой пароль',
    });
    if (!password) return;

    // Registration always creates a student — the server ignores any client-
    // supplied role and self-registration must never escalate to mentor/admin.
    // Existing users fall back to login below.
    try {
        const resp = await api.register(username, password, 'student');
        await startSession(context, resp.access_token);
        await vscode.commands.executeCommand('setContext', 'ego.offline', false);
        vscode.window.showInformationMessage(`Cogito: ты вошёл как ${username} (студент)`);
    } catch (e) {
        // Maybe already registered — try login.
        try {
            const resp = await api.login(username, password);
            await startSession(context, resp.access_token);
            await vscode.commands.executeCommand('setContext', 'ego.offline', false);
            vscode.window.showInformationMessage(`Cogito: ты вошёл как ${username}`);
        } catch (e2) {
            vscode.window.showErrorMessage(`Cogito: не удалось войти — ${(e2 as Error).message}`);
        }
    }
}

async function cmdSetupPython(): Promise<void> {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspacePath) {
        vscode.window.showErrorMessage('Cogito: сначала открой папку проекта, потом настраивай Python.');
        return;
    }

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Cogito: настраиваю Python…',
            cancellable: false,
        },
        async (progress) => {
            try {
                const packageSpec = vscode.workspace
                    .getConfiguration('ego', vscode.Uri.file(workspacePath))
                    .get<string>('pythonPackageSpec', 'ego-trainer');
                progress.report({ message: `Устанавливаю ${packageSpec}…` });
                await setupPythonEnv(workspacePath);
                vscode.window.showInformationMessage(
                    `Cogito: окружение Python готово (${packageSpec}).`
                );
            } catch (error) {
                vscode.window.showErrorMessage(
                    `Cogito: не удалось настроить Python — ${(error as Error).message}`
                );
            }
        }
    );
}

/** Dependencies of the update check: server URL, version and workspace mode. */
function updateDeps(context: vscode.ExtensionContext): UpdateCheckDeps {
    return {
        context,
        currentVersion: currentExtensionVersion(context),
        serverUrl: vscode.workspace
            .getConfiguration('ego')
            .get<string>('serverUrl', 'http://localhost:8000'),
        mode: async () => (await readEgoConfig())?.mode,
    };
}

/** «Cogito: Проверить обновления» — reachable from the Command Palette. */
async function cmdCheckUpdate(context: vscode.ExtensionContext): Promise<void> {
    await checkForUpdatesManually(updateDeps(context));
}

async function cmdSetServer(context: vscode.ExtensionContext): Promise<void> {    AssistantPanel.close();
    const url = await vscode.window.showInputBox({
        prompt: 'Адрес сервера',
        value: vscode.workspace.getConfiguration('ego').get('serverUrl', 'http://localhost:8000'),
        placeHolder: 'http://localhost:8000',
    });
    if (!url) return;

    await vscode.workspace.getConfiguration('ego').update('serverUrl', url, vscode.ConfigurationTarget.Global);
    await recreateApi(context);
    vscode.window.showInformationMessage(`Cogito: сервер — ${url}`);
}

async function cmdCheck(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Cogito: нет открытого файла. Сначала открой .py-файл задачи.');
        return;
    }

    const fileName = vscode.workspace.asRelativePath(editor.document.fileName);
    // Extract task_id from filename: tasks/block_f_simple/task_f1.py -> F1
    const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
    if (!match) {
        vscode.window.showWarningMessage(`Cogito: ${fileName} — не файл задачи.`);
        return;
    }
    const taskId = match[1].replace(/_/g, '.').toUpperCase();
    await runCheckOnCode(taskId, editor.document.getText(), editor.document.uri.fsPath);
}

/** Check a task by id — used by Dashboard / TreeView / Task view. */
async function cmdCheckTask(taskId: string): Promise<void> {
    const code = await readTaskPy(taskId);
    if (code === undefined) {
        vscode.window.showWarningMessage(
            `Cogito: для задачи ${taskId} нет .py-файла. Сначала открой задачу или скачай все задачи.`
        );
        return;
    }
    await runCheckOnCode(taskId, code);
}

async function runCheckOnCode(
    taskId: string,
    code: string,
    pyPath?: string
): Promise<void> {
    statusBar.setChecking();
    try {
        const cfg = await readEgoConfig();
        const offline = cfg?.mode === 'offline';
        let result: CheckResponse;
        if (offline) {
            const root = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (!root) throw new Error('Папка проекта не открыта.');
            result = await runOfflineCheck({ taskId, cwd: root, code, pyPath });
        } else {
            result = await api.check(taskId, code);
        }
        showCheckResult(result, taskId);
        if (!offline && result.understanding && result.understanding.status !== 'confirmed') {
            await AssistantPanel.show(taskId, code, result.understanding.submission_id,
                async () => await readTaskPy(taskId) ?? code);
        }
        statusBar.setCheckResult(
            taskId,
            result.status,
            result.passed_tests,
            result.total_tests
        );
        treeProvider.refresh();
        if (DashboardView.isOpen()) {
            await DashboardView.refresh();
        }
    } catch (e) {
        statusBar.setError((e as Error).message);
        vscode.window.showErrorMessage(`Cogito: проверка не удалась — ${(e as Error).message}`);
    }
}

/** Open the tutor for the selected task and keep its code context current. */
async function cmdAssistant(taskId?: string): Promise<void> {
    try {
        if ((await readEgoConfig())?.mode === 'offline') {
            throw new Error('Ассистент доступен при подключении к серверу.');
        }
        const editor = vscode.window.activeTextEditor;
        if (!taskId) {
            const match = editor?.document.fileName.match(/task_([a-z0-9_]+)\.py$/i);
            taskId = match?.[1].replace(/_/g, '.').toUpperCase();
        }
        if (!taskId) throw new Error('Открой файл задания или выбери задание в дереве.');
        const expected = `task_${taskId.replace(/\./g, '_').toLowerCase()}.py`;
        const id = taskId;
        const original = editor?.document.uri.path.split('/').pop()?.toLowerCase() === expected ? editor.document : undefined;
        const getCode = async () => {
            const current = vscode.window.activeTextEditor;
            return current?.document.uri.path.split('/').pop()?.toLowerCase() === expected
                ? current.document.getText() : original && !original.isClosed ? original.getText()
                    : vscode.workspace.textDocuments.find(doc => doc.uri.path.split('/').pop()?.toLowerCase() === expected)?.getText()
                        ?? await readTaskPy(id) ?? '';
        };
        await AssistantPanel.show(taskId, await getCode(), undefined, getCode);
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: ${(e as Error).message}`);
    }
}

/** Find task_*.py on disk (tasks/ preferred). */
async function readTaskPy(taskId: string): Promise<string | undefined> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) return undefined;
    const normalized = taskId.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}.py`;

    // Sidebar focus hides activeTextEditor; open documents still hold unsaved code.
    const active = vscode.window.activeTextEditor?.document;
    const documents = active ? [active, ...vscode.workspace.textDocuments] : vscode.workspace.textDocuments;
    const open = documents.find(doc => !doc.isClosed && doc.uri.path.split('/').pop()?.toLowerCase() === filename);
    if (open) return open.getText();

    const matches = await vscode.workspace.findFiles(
        new vscode.RelativePattern(root, `**/${filename}`),
        '**/{node_modules,.ego,out}/**',
        5
    );
    // Prefer tasks/ over docs/
    matches.sort((a, b) => {
        const ar = vscode.workspace.asRelativePath(a);
        const br = vscode.workspace.asRelativePath(b);
        const ascore = ar.startsWith('tasks/') ? 0 : 1;
        const bscore = br.startsWith('tasks/') ? 0 : 1;
        return ascore - bscore;
    });
    if (matches.length === 0) return undefined;
    const buf = await vscode.workspace.fs.readFile(matches[0]);
    return Buffer.from(buf).toString('utf-8');
}

async function cmdPull(): Promise<void> {
    const block = await vscode.window.showInputBox({
        prompt: 'Буква блока (например, F) или номер задачи (например, F1)',
        placeHolder: 'F или F1',
    });
    if (!block) return;

    const isBlock = block.length === 1;
    try {
        const tasks = await api.listTasks(isBlock ? block : undefined);
        const filtered = isBlock
            ? tasks
            : tasks.filter(t => t.id === block.toUpperCase());

        if (filtered.length === 0) {
            vscode.window.showWarningMessage(`Cogito: по запросу «${block}» задач не найдено.`);
            return;
        }

        await pullTasksToWorkspace(api, filtered);
        treeProvider.refresh();
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось скачать задачи — ${(e as Error).message}`);
    }
}

async function cmdPullAll(): Promise<void> {
    try {
        const tasks = await api.listTasks();
        await pullTasksToWorkspace(api, tasks);
        treeProvider.refresh();
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось скачать задачи — ${(e as Error).message}`);
    }
}

/** Re-download every task regardless of manifest freshness (ego.pullAllForce). */
async function cmdPullAllForce(): Promise<void> {
    const confirm = await vscode.window.showWarningMessage(
        'Cogito: Перескачать все задачи заново? Актуальные задачи тоже будут загружены; изменённые локально файлы сохранятся как .server.py или резервные копии.',
        { modal: true },
        'Перескачать'
    );
    if (confirm !== 'Перескачать') return;
    try {
        const tasks = await api.listTasks();
        await pullTasksToWorkspace(api, tasks, { force: true });
        treeProvider.refresh();
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось скачать задачи — ${(e as Error).message}`);
    }
}

async function cmdList(): Promise<void> {
    try {
        const tasks = await api.listTasks();
        const items = tasks.map(t => ({
            label: `${t.id}: ${t.title}`,
            description: `Блок ${t.block}, v${t.version}`,
            task: t,
        }));
        const picked = await vscode.window.showQuickPick(items, {
            placeHolder: 'Выбери задачу, чтобы открыть',
        });
        if (picked) {
            await cmdOpenTask(picked.task);
        }
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось получить список задач — ${(e as Error).message}`);
    }
}

async function cmdShowTask(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const fileName = vscode.workspace.asRelativePath(editor.document.fileName).replace(/\\/g, '/');
    const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
    if (!match) return;
    const taskId = match[1].replace(/_/g, '.').toUpperCase();
    const cfg = await readEgoConfig();

    if (cfg?.mode === 'offline') {
        const root = vscode.workspace.workspaceFolders?.[0]?.uri;
        if (!root) {
            vscode.window.showWarningMessage('Cogito: открой папку проекта, чтобы увидеть условие задачи.');
            return;
        }
        const filename = `task_${match[1]}.md`;
        const candidates = [
            ...(await vscode.workspace.findFiles(new vscode.RelativePattern(root, `tasks/**/${filename}`), '**/{node_modules,.ego,out}/**', 20)),
            ...(await vscode.workspace.findFiles(new vscode.RelativePattern(root, `docs/tasks/**/${filename}`), '**/{node_modules,.ego,out}/**', 20)),
        ];
        const mdUri = candidates[0];
        if (!mdUri) {
            vscode.window.showWarningMessage(`Cogito: локальное условие задачи ${taskId} не найдено. Ожидается файл ${filename} в tasks/ или docs/tasks/.`);
            return;
        }
        const doc = await vscode.workspace.openTextDocument(mdUri);
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
        return;
    }

    try {
        const task = await api.getTask(taskId);
        const doc = await vscode.workspace.openTextDocument({
            content: task.statement_md,
            language: 'markdown',
        });
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось показать условие — ${(e as Error).message}`);
    }
}

async function cmdOpenTask(task: TaskMeta): Promise<void> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) return;

    const normalized = task.id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}`;
    const pyUri = vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug, `${filename}.py`);
    const mdUri = vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug, `${filename}.md`);

    // Ensure files exist (pull from server if missing).
    try {
        await vscode.workspace.fs.stat(pyUri);
    } catch {
        try {
            const full = await api.getTask(task.id);
            await vscode.workspace.fs.createDirectory(
                vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug)
            );
            await vscode.workspace.fs.writeFile(mdUri, Buffer.from(full.statement_md, 'utf-8'));
            await vscode.workspace.fs.writeFile(pyUri, Buffer.from(full.stub_py, 'utf-8'));
            task = { ...task, title: full.title, version: full.version, md_path: vscode.workspace.asRelativePath(mdUri) };
        } catch (e) {
            vscode.window.showErrorMessage(`Cogito: не удалось открыть задачу — ${(e as Error).message}`);
            return;
        }
    }

    statusBar.setTask(task.id);
    await openTaskWithView(task);
}

async function cmdSwitchMode(context: vscode.ExtensionContext): Promise<void> {
    await switchMode({
        getApi: () => api,
        setApi: (a) => {
            api = a;
            apiToken = undefined;
            treeProvider.updateApi(api);
            void refreshAssistantAccess();
        },
        getToken: async () => context.secrets.get(SECRET_KEY),
        refreshTree: () => treeProvider.refresh(),
        refreshDashboard: async () => {
            if (DashboardView.isOpen()) await DashboardView.refresh();
        },
        setModeUi: (mode: EgoMode) => statusBar.setMode(mode),
        runServerInit: async () => {
            await runServerInit(context, {
                onApiChanged: async () => {
                    await recreateApi(context);
                },
                refreshTree: () => treeProvider.refresh(),
            });
            statusBar.setMode('server');
            await refreshAssistantAccess();
        },
    });
}

// === Helpers ===

function resolveTaskId(arg?: TaskMeta | TaskItem | string): string | undefined {
    if (!arg) return undefined;
    if (typeof arg === 'string') return arg;
    if (arg instanceof TaskItem) return arg.task.id || arg.task.task_id;
    return arg.id || arg.task_id;
}

function resolveTaskMeta(arg?: TaskMeta | TaskItem): TaskMeta | undefined {
    if (!arg) return undefined;
    if (arg instanceof TaskItem) return arg.task;
    return arg;
}

function showCheckResult(result: CheckResponse, taskId: string): void {
    const statusIcons: Record<string, string> = {
        passed: '✓',
        partial: '◐',
        failed: '✗',
        error: '⚠',
        timeout: '⏱',
        no_tests: '○',
    };
    const icon = statusIcons[result.status] || '?';

    if (result.status === 'passed') {
        vscode.window.showInformationMessage(
            `Cogito: ${icon} ${taskId} — пройдена (${result.passed_tests}/${result.total_tests})`
        );
    } else if (result.status === 'no_tests') {
        vscode.window.showWarningMessage(
            `Cogito: ${icon} ${taskId} — у задачи нет тестов`
        );
    } else {
        const failedCount = result.total_tests - result.passed_tests;
        vscode.window.showWarningMessage(
            `Cogito: ${icon} ${taskId} — ${STATUS_LABELS_RU[result.status] ?? result.status} (${result.passed_tests}/${result.total_tests}, не прошло: ${failedCount})`
        );
    }

    // Prefer the matching Task view; otherwise keep results visible in a standalone panel.
    if (TaskViewPanel.isOpen() && TaskViewPanel.postResult(result)) return;
    if (TaskViewPanel.isOpen()) {
        vscode.window.showInformationMessage(
            `Cogito: проверка ${result.task_id} завершена, результаты показаны в отдельной панели.`
        );
    }
    TestResultsPanel.show(result);
}

const STATUS_LABELS_RU: Record<string, string> = {
    partial: 'частично',
    failed: 'не пройдена',
    error: 'ошибка',
    timeout: 'превышено время',
};

async function cmdHints(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    let taskId: string | undefined;

    if (editor) {
        const fileName = vscode.workspace.asRelativePath(editor.document.fileName);
        const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
        if (match) {
            taskId = match[1].replace(/_/g, '.').toUpperCase();
        }
    }

    if (!taskId) {
        // Ask user to pick a task.
        try {
            const cfg = await readEgoConfig();
            const tasks = cfg?.mode === 'offline'
                ? (await readManifest())?.tasks || []
                : await api.listTasks();
            const picked = await vscode.window.showQuickPick(
                tasks.map(t => ({ label: `${t.id}: ${'title' in t ? t.title : t.slug}`, taskId: t.id })),
                { placeHolder: 'Выбери задачу, чтобы посмотреть подсказки' }
            );
            if (!picked) return;
            taskId = picked.taskId;
        } catch (e) {
            vscode.window.showErrorMessage(`Cogito: не удалось получить список задач — ${(e as Error).message}`);
            return;
        }
    }

    await cmdHintsForTask(taskId);
}

async function cmdHintsForTask(taskId: string): Promise<void> {
    const cfg = await readEgoConfig();
    if (cfg?.mode === 'offline') {
        // Offline: hints live in Task view (parsed from local .md).
        statusBar.setTask(taskId);
        await TaskViewPanel.show({
            id: taskId,
            title: taskId,
            slug: '',
            version: '0.0.0',
            status: 'new',
        });
        vscode.window.showInformationMessage(
            `Cogito: открыта панель задания ${taskId} — подсказки 1/2/3 в кнопках на панели.`
        );
        return;
    }

    const level = await vscode.window.showQuickPick(
        [
            { label: 'Уровень 1: правила', value: 1 },
            { label: 'Уровень 2: правила и пример', value: 2 },
            { label: 'Уровень 3: правила, пример и сигнатура', value: 3 },
        ],
        { placeHolder: `Выбери уровень подсказки для ${taskId}` }
    );
    if (!level) return;

    try {
        const resp = await api.getHints(taskId, level.value);
        if (resp.hints.length === 0) {
            vscode.window.showInformationMessage(`Cogito: для задачи ${taskId} подсказок нет.`);
            return;
        }
        const mdContent = resp.hints.map(h => `## ${h.title}\n\n${h.content}`).join('\n\n---\n\n');
        const doc = await vscode.workspace.openTextDocument({
            content: `# Подсказки к задаче ${taskId}\n\n${mdContent}`,
            language: 'markdown',
        });
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    } catch (e) {
        vscode.window.showErrorMessage(`Cogito: не удалось получить подсказки — ${(e as Error).message}`);
    }
}

async function cmdMyProgress(): Promise<void> {
    // Dashboard replaces the old markdown progress table (8bv.9.5).
    await DashboardView.show();
}

async function cmdPush(): Promise<void> {
    const cfg = await readEgoConfig();
    if (cfg?.mode === 'offline') {
        vscode.window.showWarningMessage(
            'Cogito: отправка прогресса недоступна в локальном режиме. Выбери «Cogito: Переключить режим» → сервер.'
        );
        return;
    }

    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) {
        vscode.window.showErrorMessage('Cogito: папка проекта не открыта.');
        return;
    }

    // Read .ego/progress.json from workspace.
    const progressUri = vscode.Uri.joinPath(wsFolder.uri, '.ego', 'progress.json');
    let progressData: { entries?: Array<{ task_id: string; version: string; status: string; attempts: number; passed_tests: number; total_tests: number; solution_hash?: string }> };
    try {
        const buf = await vscode.workspace.fs.readFile(progressUri);
        progressData = JSON.parse(Buffer.from(buf).toString('utf-8'));
    } catch {
        vscode.window.showWarningMessage('Cogito: файл .ego/progress.json не найден. Сначала запусти «Cogito: Проверить задачу».');
        return;
    }

    const entries = progressData.entries || [];
    if (entries.length === 0) {
        vscode.window.showInformationMessage('Cogito: нет прогресса для отправки.');
        return;
    }

    // Also read run logs from .ego/runs/ to attach to push.
    const runsDir = vscode.Uri.joinPath(wsFolder.uri, '.ego', 'runs');

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Cogito: отправляю прогресс (записей: ${entries.length})…`,
            cancellable: false,
        },
        async (progress) => {
            let pushed = 0;
            let errors = 0;
            for (const [index, entry] of entries.entries()) {
                progress.report({ message: `${entry.task_id}: ${entry.status}` });
                try {
                    // Find the latest run log for this task.
                    let log = '';
                    try {
                        const runFiles = await vscode.workspace.fs.readDirectory(runsDir);
                        const taskRuns = runFiles
                            .filter(([name]) => name.startsWith(entry.task_id.replace(/\./g, '_') + '-'))
                            .sort()
                            .reverse();
                        if (taskRuns.length > 0) {
                            const logBuf = await vscode.workspace.fs.readFile(
                                vscode.Uri.joinPath(runsDir, taskRuns[0][0])
                            );
                            const runData = JSON.parse(Buffer.from(logBuf).toString('utf-8'));
                            log = runData.log || '';
                        }
                    } catch {
                        // No run log — empty log is fine.
                    }

                    await api.pushProgress({
                        task_id: entry.task_id,
                        version: entry.version,
                        solution_hash: entry.solution_hash || '',
                        status: entry.status,
                        log,
                        passed_tests: entry.passed_tests,
                        total_tests: entry.total_tests,
                    });
                    pushed++;
                } catch (e) {
                    errors++;
                    console.error(`Push ${entry.task_id} failed:`, e);
                } finally {
                    progress.report({ increment: ((index + 1) / entries.length) * 100 - (index / entries.length) * 100 });
                }
            }
            if (errors === 0) {
                vscode.window.showInformationMessage(`Cogito: прогресс отправлен на сервер (записей: ${pushed}).`);
            } else {
                vscode.window.showWarningMessage(`Cogito: отправлено записей: ${pushed}, с ошибками: ${errors}.`);
            }
            treeProvider.refresh();
        }
    );
}

