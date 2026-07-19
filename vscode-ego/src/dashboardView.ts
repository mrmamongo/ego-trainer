/** Dashboard webview stub — full UI in 8bv.9.5. */

import * as vscode from 'vscode';

/** Placeholder until Svelte dashboard lands (8bv.9.5). */
export async function showDashboard(): Promise<void> {
    const choice = await vscode.window.showInformationMessage(
        'Ego: Dashboard UI is next (8bv.9.5). Use Ego Tasks sidebar or Ego: List Tasks for now.',
        'List Tasks',
        'OK'
    );
    if (choice === 'List Tasks') {
        await vscode.commands.executeCommand('ego.list');
    }
}
