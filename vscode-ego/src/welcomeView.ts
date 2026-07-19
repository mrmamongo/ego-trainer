/** Welcome webview — auto-open on first launch (ADR-0015 / 8bv.9.1). */

import * as vscode from 'vscode';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import { hasEgoDir } from './egoWorkspace';
import { runOfflineInit, runServerInit } from './initWizard';

const SECRET_KEY = 'ego.token';
const SKIP_KEY = 'ego.welcome.skipped';

export class WelcomeView {
    private static panel: vscode.WebviewPanel | undefined;

    static async shouldAutoOpen(context: vscode.ExtensionContext): Promise<boolean> {
        if (context.workspaceState.get<boolean>(SKIP_KEY)) {
            return false;
        }
        const token = await context.secrets.get(SECRET_KEY);
        const ego = await hasEgoDir();
        // Auto-open when: no token OR no .ego/
        return !token || !ego;
    }

    static show(
        context: vscode.ExtensionContext,
        deps: {
            onApiChanged: () => void;
            refreshTree: () => void;
        }
    ): void {
        if (WelcomeView.panel) {
            WelcomeView.panel.reveal(vscode.ViewColumn.One);
            return;
        }

        WelcomeView.panel = vscode.window.createWebviewPanel(
            'egoWelcome',
            'Ego Trainer',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: webviewLocalRoots(context.extensionUri),
            }
        );

        WelcomeView.panel.webview.html = webviewHtml({
            webview: WelcomeView.panel.webview,
            extensionUri: context.extensionUri,
            bundleName: 'welcome.js',
            title: 'Ego Trainer',
        });

        WelcomeView.panel.webview.onDidReceiveMessage(async (msg: { type?: string }) => {
            switch (msg?.type) {
                case 'welcome.connect':
                    WelcomeView.panel?.dispose();
                    await runServerInit(context, deps);
                    break;
                case 'welcome.offline':
                    WelcomeView.panel?.dispose();
                    await runOfflineInit(context, deps);
                    break;
                case 'welcome.skip':
                    await context.workspaceState.update(SKIP_KEY, true);
                    WelcomeView.panel?.dispose();
                    break;
                default:
                    break;
            }
        });

        WelcomeView.panel.onDidDispose(() => {
            WelcomeView.panel = undefined;
        });
    }
}
