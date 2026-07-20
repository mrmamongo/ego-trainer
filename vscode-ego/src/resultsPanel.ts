/** Webview panel for showing test results (Svelte bundle, ADR-0015). */

import * as vscode from 'vscode';
import { CheckResponse } from './api';
import { webviewHtml, webviewLocalRoots } from './webviewHost';

export class TestResultsPanel {
    private static panel: vscode.WebviewPanel | undefined;
    private static extensionUri: vscode.Uri | undefined;
    private static pending: CheckResponse | undefined;
    private static ready = false;

    /** Call once from activate() so we can resolve out/webview assets. */
    static configure(extensionUri: vscode.Uri): void {
        TestResultsPanel.extensionUri = extensionUri;
    }

    static show(result: CheckResponse): void {
        const extensionUri = TestResultsPanel.extensionUri;
        if (!extensionUri) {
            vscode.window.showErrorMessage('Ego: TestResultsPanel not configured (missing extensionUri)');
            return;
        }

        TestResultsPanel.pending = result;

        if (TestResultsPanel.panel) {
            TestResultsPanel.panel.title = `Ego: ${result.task_id} Results`;
            TestResultsPanel.panel.reveal(vscode.ViewColumn.Two);
            if (TestResultsPanel.ready) {
                TestResultsPanel.postResult(result);
            }
            return;
        }

        TestResultsPanel.ready = false;
        TestResultsPanel.panel = vscode.window.createWebviewPanel(
            'egoTestResults',
            `Ego: ${result.task_id} Results`,
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: webviewLocalRoots(extensionUri),
            }
        );

        TestResultsPanel.panel.webview.html = webviewHtml({
            webview: TestResultsPanel.panel.webview,
            extensionUri,
            bundleName: 'results.js',
            title: `Ego: ${result.task_id} Results`,
        });

        TestResultsPanel.panel.webview.onDidReceiveMessage((msg: { type?: string }) => {
            if (msg?.type === 'ready') {
                TestResultsPanel.ready = true;
                if (TestResultsPanel.pending) {
                    TestResultsPanel.postResult(TestResultsPanel.pending);
                }
            }
        });

        TestResultsPanel.panel.onDidDispose(() => {
            TestResultsPanel.panel = undefined;
            TestResultsPanel.ready = false;
            TestResultsPanel.pending = undefined;
        });
    }

    private static postResult(result: CheckResponse): void {
        TestResultsPanel.panel?.webview.postMessage({
            type: 'setResult',
            payload: result,
        });
    }
}
