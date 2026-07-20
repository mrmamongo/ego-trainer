/** Shared open-task helpers: .py in Col1 + Task view in Col2. */

import * as vscode from 'vscode';
import { TaskMeta } from './api';
import { TaskViewPanel } from './taskViewPanel';

/** Open .py stub in column 1. Returns whether opened. */
export async function openTaskPy(
    taskId: string,
    slug?: string,
    mdPath?: string
): Promise<boolean> {
    const root = vscode.workspace.workspaceFolders?.[0]?.uri;
    if (!root) {
        vscode.window.showErrorMessage('Ego: No workspace folder open.');
        return false;
    }
    const normalized = taskId.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}.py`;
    const candidates: vscode.Uri[] = [];
    if (slug) {
        candidates.push(vscode.Uri.joinPath(root, 'tasks', slug, filename));
    }
    if (mdPath) {
        const parts = mdPath.split('/');
        parts[parts.length - 1] = filename;
        candidates.push(vscode.Uri.joinPath(root, ...parts));
    }
    const found = await vscode.workspace.findFiles(
        new vscode.RelativePattern(root, `**/${filename}`),
        '**/node_modules/**',
        5
    );
    found.sort((a, b) => {
        const ar = vscode.workspace.asRelativePath(a);
        const br = vscode.workspace.asRelativePath(b);
        return (ar.startsWith('tasks/') ? 0 : 1) - (br.startsWith('tasks/') ? 0 : 1);
    });
    candidates.push(...found);

    const seen = new Set<string>();
    for (const uri of candidates) {
        const key = uri.toString();
        if (seen.has(key)) continue;
        seen.add(key);
        try {
            const doc = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.One);
            return true;
        } catch {
            // next
        }
    }
    vscode.window.showWarningMessage(
        `Ego: No .py stub for ${taskId}. Pull the task or create tasks/<block>/${filename}.`
    );
    return false;
}

/** Open task: .py Col1 + Task view Col2. */
export async function openTaskWithView(
    task: TaskMeta,
    status = 'new'
): Promise<void> {
    await openTaskPy(task.id, task.slug, task.md_path || undefined);
    await TaskViewPanel.showFromMeta(task, status);
}

/** Open from dashboard/tree row fields. */
export async function openTaskById(opts: {
    id: string;
    title: string;
    slug: string;
    version: string;
    status?: string;
    md_path?: string;
}): Promise<void> {
    await openTaskPy(opts.id, opts.slug, opts.md_path);
    await TaskViewPanel.show({
        id: opts.id,
        title: opts.title,
        slug: opts.slug,
        version: opts.version,
        status: opts.status || 'new',
        md_path: opts.md_path,
    });
}
