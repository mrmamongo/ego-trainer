/** Welcome webview — auto-open when workspace is not initialized (ADR-0015 / 8bv.9.1 / 8bv.9.11). */

import * as vscode from 'vscode';
import { webviewHtml, webviewLocalRoots } from './webviewHost';
import { isEnvironmentReady, workspaceRoot } from './egoWorkspace';
import { runOfflineInit, runServerInit } from './initWizard';

const SKIP_KEY = 'ego.welcome.skipped';

export class WelcomeView {
    private static panel: vscode.WebviewPanel | undefined;

    /**
     * Auto-open when a workspace folder is open but Ego has not been
     * initialized (no readable `.ego/config.yaml`). Skip suppresses
     * auto-open until Ego: Show Welcome / Init.
     *
     * Offline init is enough (no JWT required). Server mode without a token
     * still counts as initialized — login is separate.
     */
    static async shouldAutoOpen(context: vscode.ExtensionContext): Promise<boolean> {
        if (context.workspaceState.get<boolean>(SKIP_KEY)) {
            return false;
        }
        // No folder → nothing to init; don't spam Welcome on empty window.
        if (!workspaceRoot()) {
            return false;
        }
        return !(await isEnvironmentReady());
    }

    /** Show Welcome if env is not ready. Returns false when not ready (caller should abort). */
    static async ensureInitialized(
        context: vscode.ExtensionContext,
        deps: {
            onApiChanged: () => void | Promise<void>;
            refreshTree: () => void;
        },
        opts?: { reason?: string }
    ): Promise<boolean> {
        if (await isEnvironmentReady()) {
            return true;
        }
        if (opts?.reason) {
            vscode.window.showWarningMessage(opts.reason);
        } else {
            vscode.window.showWarningMessage(
                'Ego: Workspace not initialized. Connect to a server or use Offline mode.'
            );
        }
        WelcomeView.show(context, deps);
        return false;
    }

    static show(
        context: vscode.ExtensionContext,
        deps: {
            onApiChanged: () => void | Promise<void>;
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
