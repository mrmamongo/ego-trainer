/** Pull tasks from server into workspace tasks/ + update .ego/manifest. */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import { writeManifest } from './egoWorkspace';

export async function pullTasksToWorkspace(
    api: EgoApi,
    tasks: TaskMeta[],
    opts?: { updateManifest?: boolean }
): Promise<{ pulled: number; errors: number }> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) {
        throw new Error('No workspace folder open.');
    }

    let pulled = 0;
    let errors = 0;
    const manifestEntries: Array<{
        id: string;
        block: string;
        slug: string;
        version: string;
        content_hash: string;
        pulled_at: string;
        md_path: string;
    }> = [];
    const now = new Date().toISOString();

    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: `Ego: Pulling ${tasks.length} tasks...`,
            cancellable: false,
        },
        async (progress) => {
            for (const t of tasks) {
                progress.report({
                    message: `${t.id}: ${t.title}`,
                    increment: tasks.length ? 100 / tasks.length : 100,
                });
                try {
                    const full = await api.getTask(t.id);
                    const normalized = t.id.replace(/\./g, '_').toLowerCase();
                    const filename = `task_${normalized}`;
                    const taskDir = vscode.Uri.joinPath(wsFolder.uri, 'tasks', t.slug);

                    await vscode.workspace.fs.createDirectory(taskDir);

                    const mdUri = vscode.Uri.joinPath(taskDir, `${filename}.md`);
                    await vscode.workspace.fs.writeFile(
                        mdUri,
                        Buffer.from(full.statement_md, 'utf-8')
                    );

                    const pyUri = vscode.Uri.joinPath(taskDir, `${filename}.py`);
                    await vscode.workspace.fs.writeFile(
                        pyUri,
                        Buffer.from(full.stub_py, 'utf-8')
                    );

                    const md_path = vscode.workspace.asRelativePath(mdUri);
                    manifestEntries.push({
                        id: t.id,
                        block: t.block,
                        slug: t.slug,
                        version: t.version,
                        content_hash: t.content_hash,
                        pulled_at: now,
                        md_path,
                    });
                    pulled++;
                } catch (e) {
                    errors++;
                    console.error(`Pull ${t.id} failed:`, e);
                }
            }
        }
    );

    if (opts?.updateManifest !== false) {
        try {
            await writeManifest({
                tasks: manifestEntries,
                server_version: '',
                last_pull_at: now,
            });
        } catch {
            // .ego/ may not exist yet for ad-hoc pull — ignore.
        }
    }

    if (errors === 0) {
        vscode.window.showInformationMessage(`Ego: Pulled ${pulled} tasks.`);
    } else {
        vscode.window.showWarningMessage(`Ego: Pulled ${pulled}, ${errors} errors.`);
    }

    return { pulled, errors };
}
