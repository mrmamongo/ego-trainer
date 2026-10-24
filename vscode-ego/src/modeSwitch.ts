/** Cogito: Переключить режим — Server ↔ Offline (8bv.9.4). */

import * as vscode from 'vscode';
import { EgoApi } from './api';
import {
    createEgoSkeleton,
    hasEgoDir,
    manifestFileExists,
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
                label: 'Сервер',
                description: current === 'server' ? '(сейчас)' : 'Подключиться к серверу Cogito',
                mode: 'server' as const,
            },
            {
                label: 'Локально',
                description: current === 'offline' ? '(сейчас)' : 'Без сервера: .ego/ и docs/tasks',
                mode: 'offline' as const,
            },
        ],
        { placeHolder: 'Выбери режим Cogito' }
    );
    if (!picked || picked.mode === current) {
        if (picked?.mode === current) {
            vscode.window.showInformationMessage(`Cogito: режим «${picked.label}» уже включён.`);
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
            'Cogito: ты не вошёл в аккаунт. Подключить папку к серверу?',
            'Подключить',
            'Отмена'
        );
        if (go === 'Подключить') {
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
            `Cogito: сервер недоступен (${(e as Error).message}). Остаться в локальном режиме?`,
            'Остаться локально',
            'Позже'
        );
        if (fallback === 'Остаться локально') {
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
    vscode.window.showInformationMessage('Cogito: включён режим «Сервер».');
    return 'server';
}

async function applyOfflineMode(deps: ModeSwitchDeps): Promise<EgoMode> {
    // Clear token from in-memory API (keep SecretStorage).
    deps.getApi().setToken(undefined);

    let cfg = await readEgoConfig();
    if (!cfg || !(await hasEgoDir())) {
        // Minimal offline skeleton if missing.
        const scanned = await scanDocsTasks();
        const root = vscode.workspace.workspaceFolders?.[0]?.uri;
        const manifestExisted = root ? await manifestFileExists(root) : false;
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
            }
        );
        if (root && !manifestExisted) {
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
            }, root);
        }
        cfg = await readEgoConfig();
    } else {
        await writeEgoConfig({ ...cfg, mode: 'offline', token: '' });
    }

    await vscode.commands.executeCommand('setContext', 'ego.offline', true);
    await vscode.commands.executeCommand('setContext', 'ego.ready', true);
    deps.setModeUi('offline');
    deps.refreshTree();
    await deps.refreshDashboard();
    vscode.window.showInformationMessage('Cogito: включён режим «Локально».');
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
    vscode.window.showWarningMessage(`Cogito: ${reason} — переключаюсь в режим «Локально».`);
}
