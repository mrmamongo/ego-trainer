/** Ego: Init wizard — server + offline modes (8bv.9.2 / 8bv.9.3). */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import {
    createEgoSkeleton,
    scanDocsTasks,
    writeManifest,
    type EgoMode,
} from './egoWorkspace';
import { pullTasksToWorkspace } from './pullTasks';

const SECRET_KEY = 'ego.token';

export interface InitDeps {
    onApiChanged: () => void;
    refreshTree: () => void;
}

/** Server mode: URL → health → login/register → .ego/ → pull all. */
export async function runServerInit(
    context: vscode.ExtensionContext,
    deps: InitDeps
): Promise<boolean> {
    const defaultUrl = vscode.workspace.getConfiguration('ego').get<string>(
        'serverUrl',
        'http://localhost:8000'
    );
    const url = await vscode.window.showInputBox({
        prompt: 'Ego server URL',
        value: defaultUrl,
        placeHolder: 'http://localhost:8000',
        ignoreFocusOut: true,
    });
    if (!url) return false;

    const probe = new EgoApi(url);
    try {
        await probe.health();
    } catch (e) {
        const choice = await vscode.window.showWarningMessage(
            `Ego: Server unreachable (${(e as Error).message}). Use Offline instead?`,
            'Use Offline',
            'Cancel'
        );
        if (choice === 'Use Offline') {
            return runOfflineInit(context, deps);
        }
        return false;
    }

    await vscode.workspace
        .getConfiguration('ego')
        .update('serverUrl', url, vscode.ConfigurationTarget.Global);

    const authMode = await vscode.window.showQuickPick(
        [
            { label: 'Existing user', description: 'Login', mode: 'login' as const },
            { label: 'New user', description: 'Register', mode: 'register' as const },
        ],
        { placeHolder: 'Login or register?', ignoreFocusOut: true }
    );
    if (!authMode) return false;

    const username = await vscode.window.showInputBox({
        prompt: 'Username',
        ignoreFocusOut: true,
    });
    if (!username) return false;

    const password = await vscode.window.showInputBox({
        prompt: 'Password',
        password: true,
        ignoreFocusOut: true,
    });
    if (!password) return false;

    let role = 'student';
    if (authMode.mode === 'register') {
        const picked = await vscode.window.showQuickPick(
            ['student', 'mentor', 'admin'],
            { placeHolder: 'Select role', ignoreFocusOut: true }
        );
        if (!picked) return false;
        role = picked;
    }

    return vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Ego: Initializing (server)…',
            cancellable: false,
        },
        async (progress) => {
            progress.report({ message: 'Authenticating…' });
            let auth;
            try {
                if (authMode.mode === 'register') {
                    auth = await probe.register(username, password, role);
                } else {
                    auth = await probe.login(username, password);
                }
            } catch (e) {
                if (authMode.mode === 'register') {
                    // Maybe already exists — try login.
                    try {
                        auth = await probe.login(username, password);
                    } catch (e2) {
                        vscode.window.showErrorMessage(
                            `Ego: Auth failed — ${(e2 as Error).message}`
                        );
                        return false;
                    }
                } else {
                    vscode.window.showErrorMessage(
                        `Ego: Login failed — ${(e as Error).message}`
                    );
                    return false;
                }
            }

            progress.report({ message: 'Creating .ego/…' });
            await context.secrets.store(SECRET_KEY, auth.access_token);
            probe.setToken(auth.access_token);

            try {
                await createEgoSkeleton(
                    {
                        server_url: url,
                        token: '', // JWT lives in SecretStorage
                        student_id: auth.user_id,
                        student_username: auth.username,
                        role: auth.role,
                        mode: 'server' satisfies EgoMode,
                    },
                    { force: true }
                );
            } catch (e) {
                vscode.window.showErrorMessage(
                    `Ego: Failed to create .ego/ — ${(e as Error).message}`
                );
                return false;
            }

            progress.report({ message: 'Pulling tasks…' });
            try {
                const tasks = await probe.listTasks();
                await pullTasksToWorkspace(probe, tasks, { updateManifest: true });
            } catch (e) {
                vscode.window.showWarningMessage(
                    `Ego: .ego/ created but pull failed — ${(e as Error).message}`
                );
            }

            await vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
            await vscode.commands.executeCommand('setContext', 'ego.ready', true);
            deps.onApiChanged();
            deps.refreshTree();

            vscode.window.showInformationMessage(
                `Ego: Connected as ${auth.username} (${auth.role}).`
            );
            // Dashboard opens here once 8bv.9.5 lands.
            await vscode.commands.executeCommand('ego.dashboard');
            return true;
        }
    );
}

/** Offline mode: scan docs/tasks/ → create .ego/ + manifest (no login). */
export async function runOfflineInit(
    context: vscode.ExtensionContext,
    deps: InitDeps
): Promise<boolean> {
    return vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Ego: Initializing (offline)…',
            cancellable: false,
        },
        async (progress) => {
            progress.report({ message: 'Scanning docs/tasks/…' });
            let scanned;
            try {
                scanned = await scanDocsTasks();
            } catch (e) {
                const pick = await vscode.window.showOpenDialog({
                    canSelectFiles: false,
                    canSelectFolders: true,
                    canSelectMany: false,
                    openLabel: 'Select docs/tasks folder',
                });
                if (!pick?.[0]) {
                    vscode.window.showErrorMessage(`Ego: ${(e as Error).message}`);
                    return false;
                }
                // If user picked a folder, try relative scan from workspace only for now.
                vscode.window.showErrorMessage(
                    'Ego: Please open the repo root as workspace (docs/tasks/ expected).'
                );
                return false;
            }

            if (scanned.length === 0) {
                vscode.window.showWarningMessage('Ego: No task .md files found under docs/tasks/.');
            }

            progress.report({ message: 'Creating .ego/…' });
            try {
                await createEgoSkeleton(
                    {
                        server_url: '',
                        token: '',
                        student_id: 'local',
                        student_username: 'local-user',
                        role: 'student',
                        mode: 'offline',
                    },
                    { force: true }
                );
            } catch (e) {
                vscode.window.showErrorMessage(
                    `Ego: Failed to create .ego/ — ${(e as Error).message}`
                );
                return false;
            }

            const now = new Date().toISOString();
            await writeManifest({
                tasks: scanned.map((t) => ({
                    id: t.id,
                    block: t.block,
                    slug: t.slug,
                    version: '0.0.0',
                    content_hash: '',
                    pulled_at: now,
                    md_path: t.md_path,
                })),
                server_version: '',
                last_pull_at: now,
            });

            await vscode.commands.executeCommand('setContext', 'ego.loggedIn', false);
            await vscode.commands.executeCommand('setContext', 'ego.ready', true);
            await vscode.commands.executeCommand('setContext', 'ego.offline', true);
            deps.refreshTree();

            vscode.window.showInformationMessage(
                `Ego: Offline ready — ${scanned.length} tasks from docs/tasks/.`
            );
            await vscode.commands.executeCommand('ego.dashboard');
            return true;
        }
    );
}

/** Re-export for typing convenience when wiring pull from extension. */
export type { TaskMeta };
