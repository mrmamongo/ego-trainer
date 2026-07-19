/** Ego Trainer — VSCode extension entry point.
 *
 * Provides commands for checking tasks, pulling from server, and viewing
 * progress. Uses ego-server (FastAPI) as backend via HTTP.
 *
 * Per ADR-0014: extension = thin UI, all logic on server.
 */

import * as vscode from 'vscode';
import { EgoApi, CheckResponse, TaskMeta, Hint } from './api';
import { EgoTaskTreeProvider } from './treeProvider';
import { TestResultsPanel } from './resultsPanel';
import { WelcomeView } from './welcomeView';
import { runOfflineInit, runServerInit } from './initWizard';
import { pullTasksToWorkspace } from './pullTasks';
import { showDashboard } from './dashboardView';
import { hasEgoDir, readEgoConfig } from './egoWorkspace';

const SECRET_KEY = 'ego.token';
const STATUS_BAR_CMD = 'ego.dashboard';

let api: EgoApi;
let treeProvider: EgoTaskTreeProvider;
let statusBar: vscode.StatusBarItem;

function initDeps() {
    return {
        onApiChanged: () => {
            // Reload API from current config + secret is done by wizard callers
            // via recreateApi; tree still needs the latest instance.
            treeProvider.updateApi(api);
        },
        refreshTree: () => treeProvider.refresh(),
    };
}

async function recreateApi(context: vscode.ExtensionContext): Promise<void> {
    const serverUrl = vscode.workspace
        .getConfiguration('ego')
        .get<string>('serverUrl', 'http://localhost:8000');
    const token = await context.secrets.get(SECRET_KEY);
    api = new EgoApi(serverUrl, token);
    treeProvider.updateApi(api);
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
    // Load config.
    const config = vscode.workspace.getConfiguration('ego');
    const serverUrl = config.get<string>('serverUrl', 'http://localhost:8000');

    // Svelte webview bundles live under out/webview/ (ADR-0015).
    TestResultsPanel.configure(context.extensionUri);

    // Load token from SecretStorage.
    const token = await context.secrets.get(SECRET_KEY);
    api = new EgoApi(serverUrl, token);

    // Tree view.
    treeProvider = new EgoTaskTreeProvider(api);
    const treeView = vscode.window.createTreeView('egoTaskTree', {
        treeDataProvider: treeProvider,
        showCollapseAll: true,
    });
    context.subscriptions.push(treeView);

    // Status bar — click opens Dashboard (ADR-0015).
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.command = STATUS_BAR_CMD;
    statusBar.text = '$(circle-outline) Ego';
    statusBar.tooltip = 'Ego: Dashboard';
    statusBar.show();
    context.subscriptions.push(statusBar);

    // === Commands ===

    context.subscriptions.push(
        vscode.commands.registerCommand('ego.login', () => cmdLogin(context)),
        vscode.commands.registerCommand('ego.setServer', () => cmdSetServer(context)),
        vscode.commands.registerCommand('ego.check', () => cmdCheck()),
        vscode.commands.registerCommand('ego.pull', () => cmdPull()),
        vscode.commands.registerCommand('ego.pullAll', () => cmdPullAll()),
        vscode.commands.registerCommand('ego.list', () => cmdList()),
        vscode.commands.registerCommand('ego.showTask', () => cmdShowTask()),
        vscode.commands.registerCommand('ego.hints', () => cmdHints()),
        vscode.commands.registerCommand('ego.myProgress', () => cmdMyProgress()),
        vscode.commands.registerCommand('ego.push', () => cmdPush()),
        vscode.commands.registerCommand('ego.refreshTree', () => treeProvider.refresh()),
        vscode.commands.registerCommand('ego.openTask', (task: TaskMeta) => cmdOpenTask(task)),
        vscode.commands.registerCommand('ego.showWelcome', () =>
            WelcomeView.show(context, {
                ...initDeps(),
                onApiChanged: async () => {
                    await recreateApi(context);
                },
            })
        ),
        vscode.commands.registerCommand('ego.init', async () => {
            const mode = await vscode.window.showQuickPick(
                [
                    { label: 'Connect to Server', mode: 'server' as const },
                    { label: 'Offline (local only)', mode: 'offline' as const },
                ],
                { placeHolder: 'How do you want to initialize Ego?' }
            );
            if (!mode) return;
            const deps = {
                onApiChanged: async () => {
                    await recreateApi(context);
                },
                refreshTree: () => treeProvider.refresh(),
            };
            if (mode.mode === 'server') {
                await runServerInit(context, deps);
            } else {
                await runOfflineInit(context, deps);
            }
        }),
        vscode.commands.registerCommand('ego.dashboard', () => showDashboard()),
    );

    // Auto-check on save (if enabled).
    context.subscriptions.push(
        vscode.workspace.onWillSaveTextDocument(async (e) => {
            if (!config.get<boolean>('autoCheckOnSave', false)) return;
            if (!e.document.fileName.match(/task_.*\.py$/)) return;
            // Run check after save.
            e.waitUntil(
                new Promise<void>((resolve) => {
                    setTimeout(async () => {
                        await cmdCheck();
                        resolve();
                    }, 100);
                })
            );
        })
    );

    // Check if logged in / offline ready.
    if (token) {
        try {
            await api.me();
            await vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
            await vscode.commands.executeCommand('setContext', 'ego.ready', true);
        } catch {
            // Token invalid — clear it.
            await context.secrets.delete(SECRET_KEY);
        }
    } else if (await hasEgoDir()) {
        const egoCfg = await readEgoConfig();
        if (egoCfg?.mode === 'offline') {
            await vscode.commands.executeCommand('setContext', 'ego.offline', true);
            await vscode.commands.executeCommand('setContext', 'ego.ready', true);
            statusBar.text = '$(circle-outline) Ego: Offline';
        } else if (egoCfg) {
            await vscode.commands.executeCommand('setContext', 'ego.ready', true);
        }
    }

    // Auto-reload when serverUrl config changes (e.g. via Settings UI).
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(async (e) => {
            if (e.affectsConfiguration('ego.serverUrl')) {
                const newUrl = vscode.workspace.getConfiguration('ego').get<string>('serverUrl', 'http://localhost:8000');
                const tok = await context.secrets.get(SECRET_KEY);
                api = new EgoApi(newUrl, tok);
                treeProvider.updateApi(api);
                vscode.window.showInformationMessage(`Ego: Server URL changed to ${newUrl}`);
            }
        })
    );

    // First-launch welcome (no token OR no .ego/).
    if (await WelcomeView.shouldAutoOpen(context)) {
        WelcomeView.show(context, {
            onApiChanged: async () => {
                await recreateApi(context);
            },
            refreshTree: () => treeProvider.refresh(),
        });
    }
}

export function deactivate(): void {
    // Cleanup.
}

// === Command implementations ===

async function cmdLogin(context: vscode.ExtensionContext): Promise<void> {
    const username = await vscode.window.showInputBox({
        prompt: 'Username',
        placeHolder: 'Enter your username',
    });
    if (!username) return;

    const password = await vscode.window.showInputBox({
        prompt: 'Password',
        password: true,
        placeHolder: 'Enter your password',
    });
    if (!password) return;

    const role = await vscode.window.showQuickPick(
        ['student', 'mentor', 'admin'],
        { placeHolder: 'Select role (student for practice)' }
    );
    if (!role) return;

    try {
        const resp = await api.register(username, password, role);
        await context.secrets.store(SECRET_KEY, resp.access_token);
        api.setToken(resp.access_token);
        vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
        treeProvider.refresh();
        vscode.window.showInformationMessage(`Ego: Logged in as ${username} (${role})`);
    } catch (e) {
        // Maybe already registered — try login.
        try {
            const resp = await api.login(username, password);
            await context.secrets.store(SECRET_KEY, resp.access_token);
            api.setToken(resp.access_token);
            vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
            treeProvider.refresh();
            vscode.window.showInformationMessage(`Ego: Logged in as ${username}`);
        } catch (e2) {
            vscode.window.showErrorMessage(`Ego: Login failed — ${(e2 as Error).message}`);
        }
    }
}

async function cmdSetServer(context: vscode.ExtensionContext): Promise<void> {
    const url = await vscode.window.showInputBox({
        prompt: 'Server URL',
        value: vscode.workspace.getConfiguration('ego').get('serverUrl', 'http://localhost:8000'),
        placeHolder: 'http://localhost:8000',
    });
    if (!url) return;

    await vscode.workspace.getConfiguration('ego').update('serverUrl', url, vscode.ConfigurationTarget.Global);
    const token = await context.secrets.get(SECRET_KEY);
    api = new EgoApi(url, token);
    treeProvider.updateApi(api);
    vscode.window.showInformationMessage(`Ego: Server set to ${url}`);
}

async function cmdCheck(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('Ego: No active editor. Open a task .py file first.');
        return;
    }

    const fileName = vscode.workspace.asRelativePath(editor.document.fileName);
    // Extract task_id from filename: tasks/block_f_simple/task_f1.py -> F1
    const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
    if (!match) {
        vscode.window.showWarningMessage(`Ego: Not a task file: ${fileName}`);
        return;
    }
    const taskId = match[1].replace(/_/g, '.').toUpperCase();

    const code = editor.document.getText();
    statusBar.text = '$(loading~spin) Ego: checking...';

    try {
        const result = await api.check(taskId, code);
        showCheckResult(result, taskId);
        updateStatusBar(result, taskId);
        treeProvider.refresh();
    } catch (e) {
        statusBar.text = '$(error) Ego: check failed';
        vscode.window.showErrorMessage(`Ego: Check failed — ${(e as Error).message}`);
    }
}

async function cmdPull(): Promise<void> {
    const block = await vscode.window.showInputBox({
        prompt: 'Block letter (e.g. F) or task ID (e.g. F1)',
        placeHolder: 'F or F1',
    });
    if (!block) return;

    const isBlock = block.length === 1;
    try {
        const tasks = await api.listTasks(isBlock ? block : undefined);
        const filtered = isBlock
            ? tasks
            : tasks.filter(t => t.id === block.toUpperCase());

        if (filtered.length === 0) {
            vscode.window.showWarningMessage(`Ego: No tasks matched "${block}"`);
            return;
        }

        await pullTasksToWorkspace(api, filtered);
        treeProvider.refresh();
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Pull failed — ${(e as Error).message}`);
    }
}

async function cmdPullAll(): Promise<void> {
    try {
        const tasks = await api.listTasks();
        await pullTasksToWorkspace(api, tasks);
        treeProvider.refresh();
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Pull failed — ${(e as Error).message}`);
    }
}

async function cmdList(): Promise<void> {
    try {
        const tasks = await api.listTasks();
        const items = tasks.map(t => ({
            label: `${t.id}: ${t.title}`,
            description: `Block ${t.block}, v${t.version}`,
            task: t,
        }));
        const picked = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a task to open',
        });
        if (picked) {
            await cmdOpenTask(picked.task);
        }
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: List failed — ${(e as Error).message}`);
    }
}

async function cmdShowTask(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const fileName = vscode.workspace.asRelativePath(editor.document.fileName);
    const match = fileName.match(/task_([a-z0-9_]+)\.py$/);
    if (!match) return;
    const taskId = match[1].replace(/_/g, '.').toUpperCase();

    try {
        const task = await api.getTask(taskId);
        // Show statement as markdown preview.
        const doc = await vscode.workspace.openTextDocument({
            content: task.statement_md,
            language: 'markdown',
        });
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Show task failed — ${(e as Error).message}`);
    }
}

async function cmdOpenTask(task: TaskMeta): Promise<void> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) return;

    const normalized = task.id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}`;
    const pyUri = vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug, `${filename}.py`);
    const mdUri = vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug, `${filename}.md`);

    try {
        // Open .py in editor.
        const doc = await vscode.workspace.openTextDocument(pyUri);
        await vscode.window.showTextDocument(doc, vscode.ViewColumn.One);

        // Open .md in preview (second column).
        try {
            const mdDoc = await vscode.workspace.openTextDocument(mdUri);
            await vscode.commands.executeCommand('markdown.showPreview', mdDoc.uri);
        } catch {
            // .md might not exist yet — pull first.
            const full = await api.getTask(task.id);
            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug));
            await vscode.workspace.fs.writeFile(mdUri, Buffer.from(full.statement_md, 'utf-8'));
            await vscode.workspace.fs.writeFile(pyUri, Buffer.from(full.stub_py, 'utf-8'));
            // Now open.
            const newDoc = await vscode.workspace.openTextDocument(pyUri);
            await vscode.window.showTextDocument(newDoc, vscode.ViewColumn.One);
            const mdDoc = await vscode.workspace.openTextDocument(mdUri);
            await vscode.commands.executeCommand('markdown.showPreview', mdDoc.uri);
        }
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Open task failed — ${(e as Error).message}`);
    }
}

// === Helpers ===

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
            `Ego: ${icon} ${taskId} — PASSED (${result.passed_tests}/${result.total_tests})`
        );
    } else if (result.status === 'no_tests') {
        vscode.window.showWarningMessage(
            `Ego: ${icon} ${taskId} — NO TESTS (task has no tests_code)`
        );
    } else {
        const failedCount = result.total_tests - result.passed_tests;
        vscode.window.showWarningMessage(
            `Ego: ${icon} ${taskId} — ${result.status.toUpperCase()} (${result.passed_tests}/${result.total_tests}, ${failedCount} failed)`
        );
    }

    // Show results in webview panel.
    TestResultsPanel.show(result);
}

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
            const tasks = await api.listTasks();
            const picked = await vscode.window.showQuickPick(
                tasks.map(t => ({ label: `${t.id}: ${t.title}`, taskId: t.id })),
                { placeHolder: 'Select a task for hints' }
            );
            if (!picked) return;
            taskId = picked.taskId;
        } catch (e) {
            vscode.window.showErrorMessage(`Ego: Failed to list tasks — ${(e as Error).message}`);
            return;
        }
    }

    // Ask which hint level.
    const level = await vscode.window.showQuickPick(
        [
            { label: 'Level 1: Rules (Правила)', value: 1 },
            { label: 'Level 2: Rules + Example', value: 2 },
            { label: 'Level 3: Rules + Example + Signature', value: 3 },
        ],
        { placeHolder: `Select hint level for ${taskId}` }
    );
    if (!level) return;

    try {
        const resp = await api.getHints(taskId, level.value);
        if (resp.hints.length === 0) {
            vscode.window.showInformationMessage(`Ego: No hints available for ${taskId}`);
            return;
        }
        // Show hints in a markdown document.
        const mdContent = resp.hints.map(h => `## ${h.title}\n\n${h.content}`).join('\n\n---\n\n');
        const doc = await vscode.workspace.openTextDocument({
            content: `# Hints for ${taskId}\n\n${mdContent}`,
            language: 'markdown',
        });
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Hints failed — ${(e as Error).message}`);
    }
}

async function cmdMyProgress(): Promise<void> {
    try {
        const me = await api.me();
        const progress = await api.getProgress(me.user_id);
        if (progress.length === 0) {
            vscode.window.showInformationMessage('Ego: No progress yet. Run "Ego: Check" on a task.');
            return;
        }
        // Show progress in a markdown table.
        const rows = progress.map(p => {
            const icon = p.status === 'passed' ? '✓' : p.status === 'partial' ? '◐' : '○';
            return `| ${p.task_id} | ${icon} ${p.status} | ${p.passed_tests}/${p.total_tests} | ${p.attempts} |`;
        }).join('\n');
        const mdContent = `# My Progress\n\n| Task | Status | Tests | Attempts |\n|------|--------|-------|----------|\n${rows}\n\n**Total:** ${progress.length} tasks, ${progress.filter(p => p.status === 'passed').length} passed`;
        const doc = await vscode.workspace.openTextDocument({
            content: mdContent,
            language: 'markdown',
        });
        await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Progress failed — ${(e as Error).message}`);
    }
}

async function cmdPush(): Promise<void> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) {
        vscode.window.showErrorMessage('Ego: No workspace folder open.');
        return;
    }

    // Read .ego/progress.json from workspace.
    const progressUri = vscode.Uri.joinPath(wsFolder.uri, '.ego', 'progress.json');
    let progressData: { entries?: Array<{ task_id: string; version: string; status: string; attempts: number; passed_tests: number; total_tests: number; solution_hash?: string }> };
    try {
        const buf = await vscode.workspace.fs.readFile(progressUri);
        progressData = JSON.parse(Buffer.from(buf).toString('utf-8'));
    } catch {
        vscode.window.showWarningMessage('Ego: No .ego/progress.json found. Run "Ego: Check" first.');
        return;
    }

    const entries = progressData.entries || [];
    if (entries.length === 0) {
        vscode.window.showInformationMessage('Ego: No progress entries to push.');
        return;
    }

    // Also read run logs from .ego/runs/ to attach to push.
    const runsDir = vscode.Uri.joinPath(wsFolder.uri, '.ego', 'runs');

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Ego: Pushing ${entries.length} progress entries...`,
            cancellable: false,
        },
        async (progress) => {
            let pushed = 0;
            let errors = 0;
            for (const entry of entries) {
                progress.report({
                    message: `${entry.task_id}: ${entry.status}`,
                    increment: (pushed / entries.length) * 100,
                });
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
                }
            }
            if (errors === 0) {
                vscode.window.showInformationMessage(`Ego: Pushed ${pushed} progress entries to server.`);
            } else {
                vscode.window.showWarningMessage(`Ego: Pushed ${pushed}, ${errors} errors.`);
            }
            treeProvider.refresh();
        }
    );
}

function updateStatusBar(result: CheckResponse, taskId: string): void {
    const icons: Record<string, string> = {
        passed: '$(check)',
        partial: '$(circle-filled)',
        failed: '$(x)',
        error: '$(error)',
        timeout: '$(clock)',
        no_tests: '$(circle-outline)',
    };
    const icon = icons[result.status] || '$(question)';
    statusBar.text = `${icon} Ego: ${taskId} ${result.passed_tests}/${result.total_tests}`;
    statusBar.tooltip = result.log.split('\n')[0];
}
