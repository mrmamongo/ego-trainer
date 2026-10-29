import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { runInNewContext } from 'node:vm';
import { sha256Hex } from '../updateCheckHelpers';
import type { UpdateCheckDeps } from '../updateCheck';

/** Exercise the public update command, including its real catch/notification path. */
async function runUpdate(installError?: unknown, storageScheme = 'file') {
    const errors: string[] = [];
    const logs: string[] = [];
    const installed: Array<{ scheme: string; fsPath: string }> = [];
    const notices: string[] = [];
    const body = Buffer.from('verified-vsix');
    const sourcePath = require.resolve('../updateCheck');
    const localRequire = createRequire(sourcePath);
    const fakeVscode = {
        Uri: {
            joinPath: (base: { scheme: string; fsPath: string }, name: string) =>
                ({ scheme: base.scheme, fsPath: `${base.fsPath}/${name}` }),
            file: (fsPath: string) => ({ scheme: 'file', fsPath }),
        },
        ProgressLocation: { Notification: 15 },
        window: {
            withProgress: async (_options: unknown, work: () => Promise<Buffer>) => work(),
            showInformationMessage: async (message: string) => {
                notices.push(message);
                return message.includes('доступна новая версия') ? 'Обновить' : undefined;
            },
            showErrorMessage: async (message: string) => { errors.push(message); },
        },
        workspace: { fs: {
            createDirectory: async () => {},
            writeFile: async () => {},
        } },
        commands: { executeCommand: async (command: string, target: { scheme: string; fsPath: string }) => {
            assert.equal(command, 'workbench.extensions.installExtension');
            installed.push(target);
            if (installError !== undefined) throw installError;
        } },
    };
    const module = { exports: {} as typeof import('../updateCheck') };
    runInNewContext(readFileSync(sourcePath, 'utf8'), {
        module, exports: module.exports, Buffer, AbortSignal,
        require: (id: string) => id === 'vscode' ? fakeVscode : localRequire(id),
        fetch: async (url: string) => ({
            ok: true,
            json: async () => ({ version: '0.2.2', sha256: sha256Hex(body), size: body.length }),
            arrayBuffer: async () => body,
        }),
    }, { filename: sourcePath });
    await module.exports.checkForUpdatesManually({
        context: {
            globalStorageUri: { scheme: storageScheme, fsPath: '/storage' },
            globalState: { get: () => undefined, update: async () => {} },
        },
        currentVersion: '0.2.0',
        serverUrl: 'https://cogito.example',
        mode: async () => 'server',
        log: (message: string) => logs.push(message),
    } as unknown as UpdateCheckDeps);
    return { errors, logs, installed, notices };
}

test('update installation preserves a string rejection from VS Code', async () => {
    const result = await runUpdate('No Servers to Install');
    assert.deepEqual(result.errors, [
        'Cogito: не удалось установить обновление — No Servers to Install',
    ]);
    assert.ok(result.logs.some(message => message.includes('No Servers to Install')));
    assert.ok(result.logs.some(message => message.includes('(install, version 0.2.2)')));
    assert.equal(result.installed.length, 1);
    assert.equal(result.notices.some(message => message.includes('установлена.')), false);
});

test('update installation preserves multiple installer errors', async () => {
    const result = await runUpdate([new Error('Access denied'), new Error('Disk full')]);
    assert.match(result.errors[0], /Access denied/);
    assert.match(result.errors[0], /Disk full/);
    assert.doesNotMatch(result.errors[0], /undefined/);
});

test('successful installation still offers a window reload', async () => {
    const result = await runUpdate();
    assert.deepEqual(result.errors, []);
    assert.deepEqual(result.installed, [{ scheme: 'file', fsPath: '/storage/updates/cogito-0.2.2.vsix' }]);
    assert.ok(result.notices.some(message => message.includes('версия 0.2.2 установлена.')));
});

test('update installation translates vscode-userdata storage into a file URI for VS Code', async () => {
    const result = await runUpdate(undefined, 'vscode-userdata');
    assert.deepEqual(result.installed, [{ scheme: 'file', fsPath: '/storage/updates/cogito-0.2.2.vsix' }]);
});

test('update installation preserves remote storage URIs', async () => {
    const result = await runUpdate(undefined, 'vscode-remote');
    assert.equal(result.installed[0].scheme, 'vscode-remote');
});
