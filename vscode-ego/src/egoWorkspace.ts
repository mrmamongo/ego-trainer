/** Workspace helpers for .ego/ layout and mode detection. */

import * as vscode from 'vscode';

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

export async function writeManifest(
    manifest: {
        tasks: Array<{
            id: string;
            block: string;
            slug: string;
            version: string;
            content_hash: string;
            pulled_at: string;
            md_path: string;
            md_modified?: boolean;
            stub_modified?: boolean;
        }>;
        server_version?: string;
        last_pull_at?: string | null;
    },
    root?: vscode.Uri
): Promise<void> {
    const dir = egoDir(root);
    if (!dir) throw new Error('No workspace folder open.');
    await vscode.workspace.fs.writeFile(
        vscode.Uri.joinPath(dir, 'manifest.yaml'),
        Buffer.from(JSON.stringify(manifest, null, 2), 'utf-8')
    );
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
        const rel = vscode.workspace.asRelativePath(uri);
        // docs/tasks/block_f_simple/task_f1.md
        const parts = rel.replace(/\\/g, '/').split('/');
        if (parts.length < 4) continue;
        const slug = parts[2]; // block_f_simple
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
