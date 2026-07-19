/** Dashboard webview host (ADR-0015 / 8bv.9.5). */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import { loadDashboardData, type DashboardData, type DashboardRow } from './dashboardLoader';
import { readEgoConfig } from './egoWorkspace';

export interface DashboardDeps {
    getApi: () => EgoApi;
    refreshTree: () => void;
    openTask: (task: TaskMeta) => Promise<void>;
    checkTask: (taskId: string) => Promise<void>;
    showHints: (taskId: string) => Promise<void>;
    pullAll: () => Promise<void>;
    pushProgress: () => Promise<void>;
}

export class DashboardView {
    private static panel: vscode.WebviewPanel | undefined;
    private static extensionUri: vscode.Uri | undefined;
    private static deps: DashboardDeps | undefined;
    private static ready = false;
    private static lastData: DashboardData | undefined;
    private static rowsById = new Map<string, DashboardRow>();

    static configure(extensionUri: vscode.Uri, deps: DashboardDeps): void {
        DashboardView.extensionUri = extensionUri;
        DashboardView.deps = deps;
    }

    static async show(): Promise<void> {
        const extensionUri = DashboardView.extensionUri;
        const deps = DashboardView.deps;
        if (!extensionUri || !deps) {
            vscode.window.showErrorMessage('Ego: Dashboard not configured.');
            return;
        }

        if (DashboardView.panel) {
            DashboardView.panel.reveal(vscode.ViewColumn.One);
            await DashboardView.refresh();
            return;
        }

        DashboardView.ready = false;
        DashboardView.panel = vscode.window.createWebviewPanel(
            'egoDashboard',
            'Ego Trainer',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: webviewLocalRoots(extensionUri),
            }
        );

        DashboardView.panel.webview.html = webviewHtml({
            webview: DashboardView.panel.webview,
            extensionUri,
            bundleName: 'dashboard.js',
            title: 'Ego Trainer',
        });

        DashboardView.panel.webview.onDidReceiveMessage(async (msg: { type?: string; taskId?: string }) => {
            await DashboardView.onMessage(msg);
        });

        DashboardView.panel.onDidDispose(() => {
            DashboardView.panel = undefined;
            DashboardView.ready = false;
        });
    }

    static async refresh(): Promise<void> {
        const deps = DashboardView.deps;
        if (!deps) return;
        const data = await loadDashboardData(deps.getApi());
        DashboardView.lastData = data;
        DashboardView.rowsById = new Map(data.rows.map((r) => [r.id, r]));
        if (DashboardView.ready && DashboardView.panel) {
            DashboardView.panel.webview.postMessage({
                type: 'dashboard.setData',
                payload: data,
            });
        }
    }

    private static async onMessage(msg: { type?: string; taskId?: string }): Promise<void> {
        const deps = DashboardView.deps;
        if (!deps || !msg?.type) return;

        switch (msg.type) {
            case 'ready':
                DashboardView.ready = true;
                await DashboardView.refresh();
                if (DashboardView.lastData && DashboardView.panel) {
                    DashboardView.panel.webview.postMessage({
                        type: 'dashboard.setData',
                        payload: DashboardView.lastData,
                    });
                }
                break;
            case 'dashboard.refresh':
                await DashboardView.refresh();
                deps.refreshTree();
                break;
            case 'dashboard.open':
                if (msg.taskId) await DashboardView.openRow(msg.taskId);
                break;
            case 'dashboard.check':
                if (msg.taskId) await deps.checkTask(msg.taskId);
                await DashboardView.refresh();
                deps.refreshTree();
                break;
            case 'dashboard.hints':
                if (msg.taskId) await deps.showHints(msg.taskId);
                break;
            case 'dashboard.pullAll': {
                const cfg = await readEgoConfig();
                if (cfg?.mode === 'offline') {
                    vscode.window.showWarningMessage('Ego: Pull All is unavailable in offline mode.');
                    return;
                }
                await deps.pullAll();
                await DashboardView.refresh();
                deps.refreshTree();
                break;
            }
            case 'dashboard.push':
                await deps.pushProgress();
                await DashboardView.refresh();
                break;
            default:
                break;
        }
    }

    private static async openRow(taskId: string): Promise<void> {
        const deps = DashboardView.deps;
        const row = DashboardView.rowsById.get(taskId);
        if (!deps || !row) {
            vscode.window.showWarningMessage(`Ego: Unknown task ${taskId}`);
            return;
        }

        const cfg = await readEgoConfig();
        if (cfg?.mode === 'offline' && row.md_path) {
            await openOfflineTask(row);
            return;
        }

        const task: TaskMeta = {
            id: row.id,
            block: row.block,
            slug: row.slug,
            task_id: row.id,
            title: row.title,
            level: '',
            tags: [],
            version: row.version,
            content_hash: '',
            breaking: false,
            md_path: row.md_path || '',
        };
        await deps.openTask(task);
    }
}

/** Offline: open docs/tasks .md + sibling/generated .py if present. */
async function openOfflineTask(row: DashboardRow): Promise<void> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root || !row.md_path) return;

    const mdUri = vscode.Uri.joinPath(root, ...row.md_path.split('/'));
    const normalized = row.id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}`;

    // Prefer workspace tasks/ stub if pulled earlier; else sibling .py under docs/tasks.
    const candidates = [
        vscode.Uri.joinPath(root, 'tasks', row.slug, `${filename}.py`),
        vscode.Uri.joinPath(mdUri, '..', `${filename}.py`),
    ];

    let pyOpened = false;
    for (const pyUri of candidates) {
        try {
            const doc = await vscode.workspace.openTextDocument(pyUri);
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.One);
            pyOpened = true;
            break;
        } catch {
            // try next
        }
    }

    try {
        const mdDoc = await vscode.workspace.openTextDocument(mdUri);
        if (pyOpened) {
            await vscode.commands.executeCommand('markdown.showPreviewToSide', mdDoc.uri);
        } else {
            await vscode.window.showTextDocument(mdDoc, vscode.ViewColumn.One);
            await vscode.commands.executeCommand('markdown.showPreview', mdDoc.uri);
            vscode.window.showInformationMessage(
                `Ego: No .py stub for ${row.id} yet. Create tasks/${row.slug}/${filename}.py to solve.`
            );
        }
    } catch (e) {
        vscode.window.showErrorMessage(`Ego: Open failed — ${(e as Error).message}`);
    }
}

/** @deprecated use DashboardView.show */
export async function showDashboard(): Promise<void> {
    await DashboardView.show();
}
