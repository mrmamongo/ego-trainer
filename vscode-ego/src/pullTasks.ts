/** Pull tasks from server into workspace tasks/ + update .ego/manifest. */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import { manifestFileExists, readManifest, writeManifest } from './egoWorkspace';
import {
    assertSafeCatalogSegment,
    decideTextFile,
    mergeManifestEntries,
    type ManifestTaskEntry,
} from './pullSafety';

async function readText(uri: vscode.Uri): Promise<string | undefined> {
    try {
        return Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf-8');
    } catch {
        return undefined;
    }
}

async function uniqueBackupUri(taskDir: vscode.Uri, filename: string): Promise<vscode.Uri> {
    const stamp = Date.now();
    let suffix = 0;
    while (true) {
        const name = `${filename}.student-backup-${stamp}${suffix ? `-${suffix}` : ''}.md`;
        const uri = vscode.Uri.joinPath(taskDir, name);
        try {
            await vscode.workspace.fs.stat(uri);
            suffix++;
        } catch {
            return uri;
        }
    }
}

export async function pullTasksToWorkspace(
    api: EgoApi,
    tasks: TaskMeta[],
    opts?: { updateManifest?: boolean }
): Promise<{
    pulled: number;
    errors: number;
    preservedStudentSolutions: number;
    statementBackups: number;
}> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) throw new Error('No workspace folder open.');

    let pulled = 0;
    let errors = 0;
    let preservedStudentSolutions = 0;
    let statementBackups = 0;
    const now = new Date().toISOString();
    const updateManifest = opts?.updateManifest !== false;
    const existingManifest = updateManifest ? await readManifest(wsFolder.uri) : undefined;
    if (
        updateManifest &&
        (await manifestFileExists(wsFolder.uri)) &&
        existingManifest === undefined
    ) {
        const message = 'manifest is invalid; repair/back it up before pulling tasks.';
        void vscode.window.showErrorMessage(`Ego: ${message}`);
        throw new Error(message);
    }
    const manifestEntries: ManifestTaskEntry[] = [];

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
                    assertSafeCatalogSegment(t.slug, 'task slug');
                    const normalized = t.id.replace(/\./g, '_').toLowerCase();
                    const filename = `task_${normalized}`;
                    assertSafeCatalogSegment(filename, 'task filename');
                    const full = await api.getTask(t.id);
                    const taskDir = vscode.Uri.joinPath(wsFolder.uri, 'tasks', t.slug);
                    await vscode.workspace.fs.createDirectory(taskDir);

                    const mdUri = vscode.Uri.joinPath(taskDir, `${filename}.md`);
                    const existingMd = await readText(mdUri);
                    const mdDecision = decideTextFile(existingMd, full.statement_md);
                    if (mdDecision === 'conflict') {
                        const backupUri = await uniqueBackupUri(taskDir, filename);
                        await vscode.workspace.fs.copy(mdUri, backupUri, { overwrite: false });
                        await vscode.workspace.fs.writeFile(mdUri, Buffer.from(full.statement_md, 'utf-8'));
                        statementBackups++;
                    } else if (mdDecision === 'create') {
                        await vscode.workspace.fs.writeFile(mdUri, Buffer.from(full.statement_md, 'utf-8'));
                    }

                    const pyUri = vscode.Uri.joinPath(taskDir, `${filename}.py`);
                    const existingPy = await readText(pyUri);
                    const pyDecision = decideTextFile(existingPy, full.stub_py);
                    let stub_modified: boolean | undefined;
                    if (pyDecision === 'create') {
                        await vscode.workspace.fs.writeFile(pyUri, Buffer.from(full.stub_py, 'utf-8'));
                    } else if (pyDecision === 'conflict') {
                        const serverUri = vscode.Uri.joinPath(taskDir, `${filename}.server.py`);
                        await vscode.workspace.fs.writeFile(serverUri, Buffer.from(full.stub_py, 'utf-8'));
                        preservedStudentSolutions++;
                        stub_modified = true;
                    }

                    const md_modified = mdDecision === 'conflict' ? true : undefined;
                    manifestEntries.push({
                        id: t.id,
                        block: t.block,
                        slug: t.slug,
                        version: t.version,
                        content_hash: t.content_hash,
                        pulled_at: now,
                        md_path: vscode.workspace.asRelativePath(mdUri).replace(/\\/g, '/'),
                        ...(md_modified ? { md_modified } : {}),
                        ...(stub_modified ? { stub_modified } : {}),
                    });
                    pulled++;
                } catch (e) {
                    errors++;
                    console.error(`Pull ${t.id} failed:`, e);
                }
            }
        }
    );

    if (updateManifest) {
        try {
            await writeManifest({
                tasks: mergeManifestEntries(existingManifest?.tasks ?? [], manifestEntries),
                server_version: existingManifest?.server_version ?? '',
                last_pull_at: now,
            }, wsFolder.uri);
        } catch (error) {
            errors++;
            const detail = error instanceof Error ? error.message : 'unknown error';
            void vscode.window.showWarningMessage(
                `Ego: Manifest write failed; files may be pulled but progress/catalog metadata is stale: ${detail}`
            );
        }
    }

    const message = `Ego: Pulled ${pulled}, ${errors} errors, preserved ${preservedStudentSolutions} student solutions, ${statementBackups} statement backups.`;
    if (errors === 0) vscode.window.showInformationMessage(message);
    else vscode.window.showWarningMessage(message);

    return { pulled, errors, preservedStudentSolutions, statementBackups };
}
