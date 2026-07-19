/** Ego: Switch Mode — Server ↔ Offline (8bv.9.4). */

import * as vscode from 'vscode';
import { EgoApi } from './api';
import {
    createEgoSkeleton,
    hasEgoDir,
    readEgoConfig,
    scanDocsTasks,
    writeEgoConfig,
    writeManifest,
    type EgoMode,
} from './egoWorkspace';

export interface ModeSwitchDeps {
    getApi: () => EgoApi;
    setApi: (api: EgoApi) => void;
    getToken: () => Promise<string | undefined> | Thenable<string | undefined>;
    refreshTree: () => void;
    refreshDashboard: () => Promise<void>;
    setModeUi: (mode: EgoMode) => void;
    runServerInit: () => Promise<void>;
}

export async function switchMode(deps: ModeSwitchDeps): Promise<EgoMode | undefined> {
    const current = (await readEgoConfig())?.mode ?? 'server';
    const picked = await vscode.window.showQuickPick(
        [
            {
                label: 'Server',
                description: current === 'server' ? '(current)' : 'Connect / use ego-server',
                mode: 'server' as const,
            },
            {
                label: 'Offline',
                description: current === 'offline' ? '(current)' : 'Local .ego/ + docs/tasks',
                mode: 'offline' as const,
            },
        ],
        { placeHolder: 'Select Ego mode' }
    );
    if (!picked || picked.mode === current) {
        if (picked?.mode === current) {
            vscode.window.showInformationMessage(`Ego: Already in ${picked.label} mode.`);
        }
        return undefined;
    }

    if (picked.mode === 'server') {
        return applyServerMode(deps);
    }
    return applyOfflineMode(deps);
}

async function applyServerMode(deps: ModeSwitchDeps): Promise<EgoMode | undefined> {
    const token = await deps.getToken();
    if (!token) {
        const go = await vscode.window.showWarningMessage(
            'Ego: No login token. Run Init (Connect to Server) or Login?',
            'Init',
            'Cancel'
        );
        if (go === 'Init') {
            await deps.runServerInit();
            return 'server';
        }
        return undefined;
    }

    let cfg = await readEgoConfig();
    if (!cfg) {
        await deps.runServerInit();
        return 'server';
    }

    const api = deps.getApi();
    api.setToken(token);
    try {
        await api.health();
        await api.me();
    } catch (e) {
        const fallback = await vscode.window.showWarningMessage(
            `Ego: Server unreachable (${(e as Error).message}). Stay Offline?`,
            'Stay Offline',
            'Retry later'
        );
        if (fallback === 'Stay Offline') {
            return undefined;
        }
        // Still switch config — user may fix server later.
    }

    cfg = { ...cfg, mode: 'server', token: '' };
    await writeEgoConfig(cfg);
    await vscode.commands.executeCommand('setContext', 'ego.offline', false);
    await vscode.commands.executeCommand('setContext', 'ego.loggedIn', true);
    await vscode.commands.executeCommand('setContext', 'ego.ready', true);
    deps.setModeUi('server');
    deps.refreshTree();
    await deps.refreshDashboard();
    vscode.window.showInformationMessage('Ego: Switched to Server mode.');
    return 'server';
}

async function applyOfflineMode(deps: ModeSwitchDeps): Promise<EgoMode> {
    // Clear token from in-memory API (keep SecretStorage).
    deps.getApi().setToken(undefined);

    let cfg = await readEgoConfig();
    if (!cfg || !(await hasEgoDir())) {
        // Minimal offline skeleton if missing.
        const scanned = await scanDocsTasks();
        await createEgoSkeleton(
            {
                server_url: vscode.workspace
                    .getConfiguration('ego')
                    .get<string>('serverUrl', 'http://localhost:8000'),
                token: '',
                student_id: 'local',
                student_username: 'local',
                role: 'student',
                mode: 'offline',
            },
            { force: false }
        );
        await writeManifest({
            tasks: scanned.map((t) => ({
                id: t.id,
                block: t.block,
                slug: t.slug,
                version: '0.0.0',
                content_hash: '',
                pulled_at: new Date().toISOString(),
                md_path: t.md_path,
            })),
            server_version: '',
            last_pull_at: null,
        });
        cfg = await readEgoConfig();
    } else {
        await writeEgoConfig({ ...cfg, mode: 'offline', token: '' });
    }

    await vscode.commands.executeCommand('setContext', 'ego.offline', true);
    await vscode.commands.executeCommand('setContext', 'ego.ready', true);
    deps.setModeUi('offline');
    deps.refreshTree();
    await deps.refreshDashboard();
    vscode.window.showInformationMessage('Ego: Switched to Offline mode.');
    return 'offline';
}

/** Auto-fallback when server health fails during normal use. */
export async function maybeFallbackOffline(
    deps: Pick<ModeSwitchDeps, 'refreshTree' | 'refreshDashboard' | 'setModeUi' | 'getApi'>,
    reason: string
): Promise<void> {
    const cfg = await readEgoConfig();
    if (!cfg || cfg.mode === 'offline') return;
    deps.getApi().setToken(undefined);
    await writeEgoConfig({ ...cfg, mode: 'offline', token: '' });
    await vscode.commands.executeCommand('setContext', 'ego.offline', true);
    deps.setModeUi('offline');
    deps.refreshTree();
    await deps.refreshDashboard();
    vscode.window.showWarningMessage(`Ego: ${reason} — switched to Offline mode.`);
}
