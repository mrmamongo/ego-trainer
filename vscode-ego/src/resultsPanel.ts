/** Webview panel for showing test results beautifully.
 *
 * Instead of dumping to Output channel, show a rich HTML panel with:
 * - Status header (passed/failed/partial)
 * - Per-test breakdown with expected vs actual
 * - Error tracebacks
 */

import * as vscode from 'vscode';
import { CheckResponse } from './api';

export class TestResultsPanel {
    private static panel: vscode.WebviewPanel | undefined;

    static show(result: CheckResponse): void {
        if (TestResultsPanel.panel) {
            TestResultsPanel.panel.reveal(vscode.ViewColumn.Two);
        } else {
            TestResultsPanel.panel = vscode.window.createWebviewPanel(
                'egoTestResults',
                `Ego: ${result.task_id} Results`,
                vscode.ViewColumn.Two,
                { enableScripts: false }
            );
            TestResultsPanel.panel.onDidDispose(() => {
                TestResultsPanel.panel = undefined;
            });
        }
        TestResultsPanel.panel.webview.html = TestResultsPanel._html(result);
    }

    private static _html(result: CheckResponse): string {
        const statusColors: Record<string, string> = {
            passed: '#22c55e',
            partial: '#f59e0b',
            failed: '#ef4444',
            error: '#ef4444',
            timeout: '#ef4444',
            no_tests: '#6b7280',
        };
        const statusIcons: Record<string, string> = {
            passed: '✓',
            partial: '◐',
            failed: '✗',
            error: '⚠',
            timeout: '⏱',
            no_tests: '○',
        };
        const color = statusColors[result.status] || '#6b7280';
        const icon = statusIcons[result.status] || '?';

        const testRows = result.results.map(tr => {
            const rowColor = tr.passed ? '#22c55e' : '#ef4444';
            const rowIcon = tr.passed ? '✓' : '✗';
            let detail = '';
            if (!tr.passed) {
                detail = `
                    <div class="detail">
                        <div><span class="label">Expected:</span> <code>${escapeHtml(tr.expected_repr)}</code></div>
                        ${tr.actual_repr !== null ? `<div><span class="label">Got:</span> <code>${escapeHtml(tr.actual_repr)}</code></div>` : ''}
                        ${tr.error ? `<div class="error"><span class="label">Error:</span> <pre>${escapeHtml(tr.error)}</pre></div>` : ''}
                    </div>`;
            }
            return `
                <div class="test-row" style="border-left-color: ${rowColor}">
                    <div class="test-header">
                        <span class="test-icon" style="color: ${rowColor}">${rowIcon}</span>
                        <span>${escapeHtml(tr.description)}</span>
                    </div>
                    ${detail}
                </div>`;
        }).join('\n');

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: var(--vscode-font-family, 'Segoe UI', sans-serif);
            padding: 16px;
            color: var(--vscode-foreground, #333);
            background: var(--vscode-editor-background, #fff);
        }
        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            border-radius: 8px;
            background: ${color}22;
            border: 1px solid ${color};
            margin-bottom: 16px;
        }
        .header .icon {
            font-size: 28px;
            color: ${color};
        }
        .header .title {
            font-size: 18px;
            font-weight: 600;
        }
        .header .summary {
            font-size: 14px;
            opacity: 0.8;
        }
        .test-row {
            border-left: 3px solid;
            padding: 8px 12px;
            margin: 4px 0;
            background: var(--vscode-editor-inactive-selection-background, #f5f5f5);
        }
        .test-header {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .test-icon {
            font-weight: bold;
        }
        .detail {
            margin-top: 8px;
            padding-left: 24px;
            font-size: 13px;
        }
        .detail .label {
            font-weight: 600;
            opacity: 0.7;
        }
        .detail code {
            background: var(--vscode-textCodeBlock-background, #eee);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family, monospace);
        }
        .detail .error pre {
            margin-top: 4px;
            padding: 8px;
            background: #fee;
            border-radius: 4px;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .no-tests {
            padding: 24px;
            text-align: center;
            opacity: 0.6;
        }
    </style>
</head>
<body>
    <div class="header">
        <span class="icon">${icon}</span>
        <div>
            <div class="title">Task ${escapeHtml(result.task_id)} — ${result.status.toUpperCase()}</div>
            <div class="summary">${result.passed_tests}/${result.total_tests} tests passed</div>
        </div>
    </div>
    ${result.total_tests === 0
        ? '<div class="no-tests">No tests available for this task.</div>'
        : testRows
    }
</body>
</html>`;
    }
}

function escapeHtml(s: string): string {
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
