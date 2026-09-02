/** Workspace helpers for .ego/ layout and mode detection. */

import * as vscode from 'vscode';
import { studentStubFromSolution } from './studentStub';
import type { ManifestTaskEntry } from './pullSafety';

export type EgoMode = 'server' | 'offline';

export interface EgoConfigFile {
    server_url: string;
    token: string;
    student_id: string;
    student_username: string;
    role: string;
    mode: EgoMode;
    sandbox_timeout_sec?: number;
    sandbox_block_network?: boolean;
    log_truncate_to?: number;
}

export function workspaceRoot(): vscode.Uri | undefined {
    return vscode.workspace.workspaceFolders?.[0]?.uri;
}

export function egoDir(root?: vscode.Uri): vscode.Uri | undefined {
    const base = root ?? workspaceRoot();
    return base ? vscode.Uri.joinPath(base, '.ego') : undefined;
}

export async function hasEgoDir(root?: vscode.Uri): Promise<boolean> {
    const dir = egoDir(root);
    if (!dir) return false;
    try {
        await vscode.workspace.fs.stat(dir);
        return true;
    } catch {
        return false;
    }
}

/**
 * Workspace is initialized when `.ego/config.yaml` exists and parses.
 * Offline mode does not require a JWT; server mode still counts as
 * initialized (login is a separate step).
 */
export async function isEnvironmentReady(root?: vscode.Uri): Promise<boolean> {
    if (!(await hasEgoDir(root))) return false;
    const cfg = await readEgoConfig(root);
    return cfg !== undefined && (cfg.mode === 'offline' || cfg.mode === 'server');
}

export async function readEgoConfig(root?: vscode.Uri): Promise<EgoConfigFile | undefined> {
    const dir = egoDir(root);
    if (!dir) return undefined;
    try {
        const buf = await vscode.workspace.fs.readFile(vscode.Uri.joinPath(dir, 'config.yaml'));
        return JSON.parse(Buffer.from(buf).toString('utf-8')) as EgoConfigFile;
    } catch {
        return undefined;
    }
}

export async function writeEgoConfig(config: EgoConfigFile, root?: vscode.Uri): Promise<void> {
    const dir = egoDir(root);
    if (!dir) throw new Error('No workspace folder open.');
    await vscode.workspace.fs.writeFile(
        vscode.Uri.joinPath(dir, 'config.yaml'),
        Buffer.from(JSON.stringify(config, null, 2), 'utf-8')
    );
}

/** Create .ego/ skeleton (config, empty manifest/progress, runs/, cache/). */
export async function createEgoSkeleton(
    config: EgoConfigFile,
    opts?: { force?: boolean; root?: vscode.Uri }
): Promise<vscode.Uri> {
    const root = opts?.root ?? workspaceRoot();
    if (!root) throw new Error('No workspace folder open.');
    const dir = vscode.Uri.joinPath(root, '.ego');

    if (await hasEgoDir(root)) {
        if (!opts?.force) {
            throw new Error('.ego/ already exists. Re-run init with overwrite if needed.');
        }
        await vscode.workspace.fs.delete(dir, { recursive: true });
    }

    await vscode.workspace.fs.createDirectory(dir);
    await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(dir, 'runs'));
    await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(dir, 'cache', 'sol'));

    await writeEgoConfig(config, root);
    await vscode.workspace.fs.writeFile(
        vscode.Uri.joinPath(dir, 'manifest.yaml'),
        Buffer.from(JSON.stringify({ tasks: [], server_version: '', last_pull_at: null }, null, 2), 'utf-8')
    );
    await vscode.workspace.fs.writeFile(
        vscode.Uri.joinPath(dir, 'progress.json'),
        Buffer.from(
            JSON.stringify(
                {
                    student_id: config.student_id,
                    student_username: config.student_username,
                    entries: [],
                },
                null,
                2
            ),
            'utf-8'
        )
    );
    return dir;
}

export interface EgoManifest {
    tasks: ManifestTaskEntry[];
    server_version?: string;
    last_pull_at?: string | null;
}

export async function manifestFileExists(root?: vscode.Uri): Promise<boolean> {
    const dir = egoDir(root);
    if (!dir) return false;
    try {
        await vscode.workspace.fs.stat(vscode.Uri.joinPath(dir, 'manifest.yaml'));
        return true;
    } catch {
        return false;
    }
}

export async function readManifest(root?: vscode.Uri): Promise<EgoManifest | undefined> {
    const dir = egoDir(root);
    if (!dir) return undefined;
    try {
        const raw = JSON.parse(
            Buffer.from(
                await vscode.workspace.fs.readFile(vscode.Uri.joinPath(dir, 'manifest.yaml'))
            ).toString('utf-8')
        ) as unknown;
        if (!raw || typeof raw !== 'object') return undefined;

        const candidate = raw as Partial<EgoManifest>;
        const tasks = candidate.tasks;
        if (!Array.isArray(tasks)) return undefined;
        if (
            (candidate.server_version !== undefined && typeof candidate.server_version !== 'string') ||
            (candidate.last_pull_at !== undefined &&
                candidate.last_pull_at !== null &&
                typeof candidate.last_pull_at !== 'string') ||
            !tasks.every((task) => {
                if (!task || typeof task !== 'object') return false;
                const entry = task as Partial<ManifestTaskEntry>;
                return (
                    typeof entry.id === 'string' &&
                    typeof entry.block === 'string' &&
                    typeof entry.slug === 'string' &&
                    typeof entry.version === 'string' &&
                    typeof entry.content_hash === 'string' &&
                    typeof entry.pulled_at === 'string' &&
                    typeof entry.md_path === 'string' &&
                    (entry.md_modified === undefined || typeof entry.md_modified === 'boolean') &&
                    (entry.stub_modified === undefined || typeof entry.stub_modified === 'boolean')
                );
            })
        ) {
            return undefined;
        }
        return { ...candidate, tasks: tasks as ManifestTaskEntry[] } as EgoManifest;
    } catch {
        return undefined;
    }
}

export async function writeManifest(manifest: EgoManifest, root?: vscode.Uri): Promise<void> {
    const dir = egoDir(root);
    if (!dir) throw new Error('No workspace folder open.');
    await vscode.workspace.fs.writeFile(
        vscode.Uri.joinPath(dir, 'manifest.yaml'),
        Buffer.from(JSON.stringify(manifest, null, 2), 'utf-8')
    );
}

export interface ImportTasksResult {
    imported: number;
    skipped: number;
}

export async function importTasksFolder(
    source: vscode.Uri,
    root?: vscode.Uri
): Promise<ImportTasksResult> {
    const base = root ?? workspaceRoot();
    if (!base) throw new Error('No workspace folder open.');

    const destination = vscode.Uri.joinPath(base, 'docs', 'tasks');
    const normalize = (uri: vscode.Uri) => uri.fsPath.replace(/[\\/]+$/, '').toLowerCase();
    const sourcePath = normalize(source);
    const rootPath = normalize(base);
    const destinationPath = normalize(destination);
    if (
        sourcePath === rootPath ||
        sourcePath === destinationPath ||
        sourcePath.startsWith(`${destinationPath}\\`) ||
        sourcePath.startsWith(`${destinationPath}/`)
    ) {
        throw new Error('Select a tasks folder outside this workspace docs/tasks folder.');
    }

    const files: Array<{ relative: string; uri: vscode.Uri }> = [];
    const visit = async (directory: vscode.Uri, relative: string): Promise<void> => {
        for (const [name, type] of await vscode.workspace.fs.readDirectory(directory)) {
            if ((type & vscode.FileType.SymbolicLink) !== 0) continue;
            const uri = vscode.Uri.joinPath(directory, name);
            const childRelative = relative ? `${relative}/${name}` : name;
            if ((type & vscode.FileType.Directory) !== 0) {
                await visit(uri, childRelative);
            } else if (/^task_.+\.md$/i.test(name)) {
                files.push({ relative: childRelative, uri });
            }
        }
    };
    await visit(source, '');

    let imported = 0;
    let skipped = 0;
    for (const file of files) {
        const relativeMd = file.relative.replace(/\\/g, '/');
        const solution = relativeMd.replace(/\.md$/i, '.solution.py');
        const tests = relativeMd.replace(/\.md$/i, '.tests.py');
        const candidates = [
            { relative: relativeMd, uri: file.uri },
            { relative: solution, uri: vscode.Uri.joinPath(source, ...solution.split('/')) },
            { relative: tests, uri: vscode.Uri.joinPath(source, ...tests.split('/')) },
        ];
        for (const candidate of candidates) {
            let exists = true;
            try {
                await vscode.workspace.fs.stat(candidate.uri);
            } catch {
                exists = false;
            }
            if (!exists) continue;

            const relativeParts = candidate.relative.split('/');
            const target = vscode.Uri.joinPath(destination, ...relativeParts);
            try {
                await vscode.workspace.fs.stat(target);
                skipped += 1;
                continue;
            } catch {
            }
            await vscode.workspace.fs.createDirectory(
                vscode.Uri.joinPath(destination, ...relativeParts.slice(0, -1))
            );
            await vscode.workspace.fs.copy(candidate.uri, target, { overwrite: false });
            imported += 1;
        }
    }
    return { imported, skipped };
}

export interface StudentStubResult {
    generated: number;
    skipped: number;
    errors: number;
}

export async function generateStudentStubs(
    scanned: Array<{ id: string; block: string; slug: string; md_path: string }>,
    root?: vscode.Uri
): Promise<StudentStubResult> {
    const base = root ?? workspaceRoot();
    if (!base) throw new Error('No workspace folder open.');

    let generated = 0;
    let skipped = 0;
    let errors = 0;
    for (const task of scanned) {
        const mdUri = vscode.Uri.joinPath(base, ...task.md_path.replace(/\\/g, '/').split('/'));
        const solutionUri = vscode.Uri.joinPath(
            mdUri,
            '..',
            `${mdUri.path.split('/').pop()?.replace(/\.md$/i, '')}.solution.py`
        );
        const stubUri = vscode.Uri.joinPath(
            base,
            'tasks',
            task.slug,
            `${mdUri.path.split('/').pop()?.replace(/\.md$/i, '')}.py`
        );
        try {
            await vscode.workspace.fs.stat(solutionUri);
        } catch {
            continue;
        }
        try {
            await vscode.workspace.fs.stat(stubUri);
            skipped += 1;
            continue;
        } catch {
        }
        try {
            const source = Buffer.from(
                await vscode.workspace.fs.readFile(solutionUri)
            ).toString('utf-8');
            const stub = studentStubFromSolution(source);
            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(base, 'tasks', task.slug));
            await vscode.workspace.fs.writeFile(stubUri, Buffer.from(stub, 'utf-8'));
            generated += 1;
        } catch (error) {
            errors += 1;
            const detail = error instanceof Error ? error.message : 'unknown error';
            void vscode.window.showWarningMessage(
                `Ego: Could not generate a student stub for ${task.id}: ${detail}`
            );
        }
    }
    return { generated, skipped, errors };
}

/** Scan docs/tasks for .md files → lightweight task descriptors for offline init. */
export async function scanDocsTasks(root?: vscode.Uri): Promise<
    Array<{ id: string; block: string; slug: string; md_path: string }>
> {
    const base = root ?? workspaceRoot();
    if (!base) throw new Error('No workspace folder open.');
    const docsTasks = vscode.Uri.joinPath(base, 'docs', 'tasks');
    try {
        await vscode.workspace.fs.stat(docsTasks);
    } catch {
        throw new Error('No docs/tasks/ directory found in workspace.');
    }

    const mdFiles = await vscode.workspace.findFiles(
        new vscode.RelativePattern(base, 'docs/tasks/**/*.md'),
        null,
        500
    );

    const out: Array<{ id: string; block: string; slug: string; md_path: string }> = [];
    for (const uri of mdFiles) {
        const rel = vscode.workspace.asRelativePath(uri, false);
        // docs/tasks/block_f_simple/task_f1.md
        const parts = rel.replace(/\\/g, '/').split('/');
        if (parts.length < 3 || parts[0] !== 'docs' || parts[1] !== 'tasks') continue;
        const slug = parts.length >= 4 ? parts[2] : 'imported';
        const file = parts[parts.length - 1]; // task_f1.md
        const m = file.match(/^task_(.+)\.md$/);
        if (!m) continue;
        const id = m[1].replace(/_/g, '.').toUpperCase();
        const block = slug.startsWith('block_')
            ? slug.slice('block_'.length).split('_')[0].toUpperCase()
            : slug.toUpperCase();
        out.push({ id, block, slug, md_path: rel });
    }
    out.sort((a, b) => a.id.localeCompare(b.id));
    return out;
}
