/** Pull tasks from server into workspace tasks/ + update .ego/manifest. */

import * as vscode from 'vscode';
import { EgoApi, TaskMeta } from './api';
import { manifestFileExists, readManifest, writeManifest } from './egoWorkspace';
import {
    assertSafeCatalogSegment,
    decideTextFile,
    mergeManifestEntries,
    planPull,
    type ManifestTaskEntry,
} from './pullSafety';

async function readText(uri: vscode.Uri): Promise<string | undefined> {
    try {
        return Buffer.from(await vscode.workspace.fs.readFile(uri)).toString('utf-8');
    } catch {
        return undefined;
    }
}

async function fileExists(uri: vscode.Uri): Promise<boolean> {
    try {
        await vscode.workspace.fs.stat(uri);
        return true;
    } catch {
        return false;
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

/** Local task file names — same derivation as `pullTasksToWorkspace`. */
function taskFilenames(id: string, slug: string): { md: string; py: string } {
    assertSafeCatalogSegment(slug, 'task slug');
    const normalized = id.replace(/\./g, '_').toLowerCase();
    const filename = `task_${normalized}`;
    assertSafeCatalogSegment(filename, 'task filename');
    return { md: `${filename}.md`, py: `${filename}.py` };
}

/**
 * `ego.pullAll` / `ego.pull` / init wizard: download only new or changed tasks.
 * Single-task pull (`ego.pullTask`) passes `force: true` and always fetches.
 */
export async function pullTasksToWorkspace(
    api: EgoApi,
    tasks: TaskMeta[],
    opts?: { updateManifest?: boolean; force?: boolean }
): Promise<{
    pulled: number;
    upToDate: number;
    errors: number;
    preservedStudentSolutions: number;
    statementBackups: number;
}> {
    const wsFolder = vscode.workspace.workspaceFolders?.[0];
    if (!wsFolder) throw new Error('Папка проекта не открыта.');

    let pulled = 0;
    let errors = 0;
    let preservedStudentSolutions = 0;
    let statementBackups = 0;
    const now = new Date().toISOString();
    const updateManifest = opts?.updateManifest !== false;
    const force = opts?.force === true;
    const existingManifest = updateManifest ? await readManifest(wsFolder.uri) : undefined;
    if (
        updateManifest &&
        (await manifestFileExists(wsFolder.uri)) &&
        existingManifest === undefined
    ) {
        const message = 'манифест повреждён: исправь его или сохрани копию перед скачиванием задач.';
        void vscode.window.showErrorMessage(`Cogito: ${message}`);
        throw new Error(message);
    }

    const manifestEntries: ManifestTaskEntry[] = [];
    let upToDate = 0;
    let toFetch: TaskMeta[] = tasks;

    if (!force) {
        // planPull's existence check is sync — stat task files up front.
        const manifestById = new Map(
            (existingManifest?.tasks ?? []).map((entry) => [entry.id.toLowerCase(), entry])
        );
        const present = new Set<string>();
        for (const task of tasks) {
            const entry = manifestById.get(task.id.toLowerCase());
            if (!entry) continue;
            try {
                const { md, py } = taskFilenames(task.id, task.slug);
                // Prefer the live catalog path; fall back to the manifest path.
                const taskDir = vscode.Uri.joinPath(wsFolder.uri, 'tasks', task.slug);
                const manifestDir = vscode.Uri.joinPath(wsFolder.uri, ...entry.md_path.split('/').slice(0, -1));
                const dir = (await fileExists(vscode.Uri.joinPath(taskDir, md))) ? taskDir : manifestDir;
                if (
                    (await fileExists(vscode.Uri.joinPath(dir, md))) &&
                    (await fileExists(vscode.Uri.joinPath(dir, py)))
                ) {
                    present.add(task.id.toLowerCase());
                }
            } catch {
                // Unsafe slug/filename — let the fetch path report it.
            }
        }
        const plan = planPull(tasks, existingManifest?.tasks ?? [], (_entry, task) =>
            present.has(task.id.toLowerCase())
        );
        toFetch = plan.fetch;
        upToDate = plan.upToDate.length;
    }

    if (toFetch.length > 0) {
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `Cogito: Обновление задач: ${toFetch.length} из ${tasks.length}...`,
                cancellable: false,
            },
            async (progress) => {
                for (const t of toFetch) {
                    progress.report({
                        message: `${t.id}: ${t.title}`,
                        increment: toFetch.length ? 100 / toFetch.length : 100,
                    });
                    try {
                        const { md: mdName, py: pyName } = taskFilenames(t.id, t.slug);
                        const filename = mdName.replace(/\.md$/, '');
                        const full = await api.getTask(t.id);
                        const taskDir = vscode.Uri.joinPath(wsFolder.uri, 'tasks', t.slug);
                        await vscode.workspace.fs.createDirectory(taskDir);
                        // The task moved to another folder: bring the student's files along
                        // so the normal conflict handling below keeps their solution.
                        const previous = existingManifest?.tasks.find((e) => e.id.toLowerCase() === t.id.toLowerCase());
                        if (previous?.md_path) {
                            const oldDir = vscode.Uri.joinPath(wsFolder.uri, ...previous.md_path.split('/').slice(0, -1));
                            if (oldDir.toString() !== taskDir.toString() && !(await fileExists(vscode.Uri.joinPath(taskDir, pyName)))) {
                                for (const name of [mdName, pyName, `${filename}.server.py`]) {
                                    const from = vscode.Uri.joinPath(oldDir, name);
                                    if (await fileExists(from)) {
                                        await vscode.workspace.fs.rename(from, vscode.Uri.joinPath(taskDir, name), { overwrite: false });
                                    }
                                }
                            }
                        }

                        const mdUri = vscode.Uri.joinPath(taskDir, mdName);
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

                        const pyUri = vscode.Uri.joinPath(taskDir, pyName);
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
    }

    if (updateManifest) {
        try {
            await writeManifest({
                tasks: mergeManifestEntries(existingManifest?.tasks ?? [], manifestEntries),
                server_version: existingManifest?.server_version ?? '',
                last_pull_at: now,
            }, wsFolder.uri);
        } catch (error) {
            errors++;
            const detail = error instanceof Error ? error.message : 'неизвестная ошибка';
            void vscode.window.showWarningMessage(
                `Cogito: не удалось записать манифест; файлы могли скачаться, но данные о прогрессе и каталоге устарели: ${detail}`
            );
        }
    }

    let message: string;
    if (tasks.length > 0 && upToDate === tasks.length) {
        message = `Cogito: все задачи уже актуальны (${upToDate})`;
    } else {
        message = `Cogito: обновлено ${pulled}, уже актуальны ${upToDate}`;
        const details: string[] = [];
        if (errors > 0) details.push(`ошибок: ${errors}`);
        if (preservedStudentSolutions > 0) details.push(`сохранено твоих решений: ${preservedStudentSolutions}`);
        if (statementBackups > 0) details.push(`копий условий: ${statementBackups}`);
        if (details.length > 0) message += `. ${details.join(', ')}.`;
        else message += '.';
    }
    if (errors === 0) vscode.window.showInformationMessage(message);
    else vscode.window.showWarningMessage(message);

    return { pulled, upToDate, errors, preservedStudentSolutions, statementBackups };
}
