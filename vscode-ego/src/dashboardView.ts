/** Dashboard webview host (ADR-0015 / 8bv.9.5). */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import { loadDashboardData, type DashboardData, type DashboardRow } from './dashboardLoader';
import { readEgoConfig } from './egoWorkspace';
import { openTaskById } from './openTask';

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

    static isOpen(): boolean {
        return DashboardView.panel !== undefined;
    }

    static async show(): Promise<void> {
        const extensionUri = DashboardView.extensionUri;
        const deps = DashboardView.deps;
        if (!extensionUri || !deps) {
            vscode.window.showErrorMessage('Cogito: личный кабинет не настроен.');
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
            'Cogito',
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
            title: 'Cogito',
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
            case 'dashboard.next': {
                // «Продолжить»: first not-passed task in catalog order.
                const nextId = DashboardView.lastData?.cabinet?.next_task_id;
                if (nextId) await DashboardView.openRow(nextId);
                else vscode.window.showInformationMessage('Cogito: все задачи пройдены.');
                break;
            }
            case 'dashboard.defend':
                // Understanding check lives in the tutor sidebar; it opens on
                // the next check of that task (the extension.ts check flow).
                if (msg.taskId) {
                    await DashboardView.openRow(msg.taskId);
                    await vscode.commands.executeCommand('ego.assistant', msg.taskId);
                }
                break;
            case 'dashboard.ai':
                await vscode.commands.executeCommand('ego.assistant');
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
                    vscode.window.showWarningMessage('Cogito: скачивание задач недоступно в локальном режиме.');
                    return;
                }
                await deps.pullAll();
                await DashboardView.refresh();
                deps.refreshTree();
                break;
            }
            case 'dashboard.push': {
                const cfg = await readEgoConfig();
                if (cfg?.mode === 'offline') {
                    vscode.window.showWarningMessage(
                        'Cogito: отправка прогресса недоступна в локальном режиме. Сначала переключись на сервер.'
                    );
                    return;
                }
                await deps.pushProgress();
                await DashboardView.refresh();
                break;
            }
            default:
                break;
        }
    }

    private static async openRow(taskId: string): Promise<void> {
        const row = DashboardView.rowsById.get(taskId);
        if (!row) {
            vscode.window.showWarningMessage(`Cogito: задача ${taskId} не найдена.`);
            return;
        }
        await openTaskById({
            id: row.id,
            title: row.title,
            slug: row.slug,
            version: row.version,
            status: row.status,
            md_path: row.md_path,
        });
    }
}

/** @deprecated use DashboardView.show */
export async function showDashboard(): Promise<void> {
    await DashboardView.show();
}
