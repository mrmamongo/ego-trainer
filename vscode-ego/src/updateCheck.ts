/** In-extension update notifications for the Cogito VS Code extension.
 *
 * The extension is distributed by our own ego-server (`/extension/latest` +
 * `/extension/download`, public — no JWT needed). On activation (after a
 * short delay, never blocking it) and at most once per 24 h the extension
 * asks the server for the newest version. A newer one produces the
 * notification «Cogito: доступна новая версия X (у тебя Y).» with
 * «Обновить», «Позже» and, when the server sends release notes, «Что
 * нового». «Обновить» downloads the package, verifies its size and sha256,
 * installs it with `workbench.extensions.installExtension` and offers to
 * reload the window.
 *
 * Pure decisions live in `updateCheckHelpers.ts` (unit-tested by
 * `src/test/updateCheck.test.ts`); this module only wires them to the
 * editor: network, notifications, globalState and downloads.
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import {
    AUTO_CHECK_DELAY_MS,
    CHECK_INTERVAL_MS,
    DOWNLOAD_PATH,
    LAST_CHECK_KEY,
    LATEST_PATH,
    SNOOZED_KEY,
    compareSemver,
    isOfflineMode,
    isValidVersion,
    normalizedBaseUrl,
    parseLatestRelease,
    shouldNotify,
    updateMessage,
    updateErrorMessage,
    verifyDownload,
    vsixFileName,
    type LatestRelease,
} from './updateCheckHelpers';

export * from './updateCheckHelpers';

export interface UpdateCheckDeps {
    context: vscode.ExtensionContext;
    /** Version of the running extension. */
    currentVersion: string;
    /** Configured `ego.serverUrl`. */
    serverUrl: string;
    /** Workspace `.ego/config.yaml` mode, when a workspace is open. */
    mode: () => Promise<string | null | undefined>;
    /** Diagnostic sink (output channel); the UI stays quiet on automatic failures. */
    log?: (message: string) => void;
}

class UpdateError extends Error {
    constructor(message: string, readonly status?: number) {
        super(message);
        this.name = 'UpdateError';
    }
}

async function fetchLatest(serverUrl: string, currentVersion: string): Promise<LatestRelease> {
    const base = normalizedBaseUrl(serverUrl);
    if (!base) throw new UpdateError('не указан адрес сервера Cogito (настройка ego.serverUrl).');
    let response: Response;
    try {
        response = await fetch(`${base}${LATEST_PATH}`, {
            headers: {
                Accept: 'application/json',
                'X-Cogito-Extension-Version': currentVersion,
            },
            signal: AbortSignal.timeout(10_000),
        });
    } catch (error) {
        throw new UpdateError(`сервер недоступен (${updateErrorMessage(error)}).`);
    }
    if (response.status === 404) {
        throw new UpdateError('на сервере пока не опубликовано расширение.', 404);
    }
    if (!response.ok) {
        throw new UpdateError(`сервер ответил HTTP ${response.status}.`, response.status);
    }
    return parseLatestRelease(await response.json().catch(() => null));
}

async function fetchVsix(serverUrl: string): Promise<Buffer> {
    const base = normalizedBaseUrl(serverUrl);
    let response: Response;
    try {
        response = await fetch(`${base}${DOWNLOAD_PATH}`, {
            headers: { Accept: 'application/octet-stream' },
            signal: AbortSignal.timeout(120_000),
        });
    } catch (error) {
        throw new UpdateError(`не удалось скачать файл (${updateErrorMessage(error)}).`);
    }
    if (!response.ok) {
        throw new UpdateError(`не удалось скачать файл (HTTP ${response.status}).`, response.status);
    }
    return Buffer.from(await response.arrayBuffer());
}

/** Ask `/extension/latest`; failures are logged and, unless quiet, shown. */
async function checkLatest(
    deps: UpdateCheckDeps,
    quiet: boolean
): Promise<LatestRelease | null> {
    try {
        return await fetchLatest(deps.serverUrl, deps.currentVersion);
    } catch (error) {
        const message = updateErrorMessage(error);
        deps.log?.(`update check failed: ${message}`);
        if (!quiet) {
            void vscode.window.showWarningMessage(
                `Cogito: не удалось проверить обновления — ${message}`
            );
        }
        return null;
    }
}

async function safeMode(deps: UpdateCheckDeps): Promise<string | null | undefined> {
    try {
        return await deps.mode();
    } catch {
        return undefined;
    }
}

async function showNotes(release: LatestRelease): Promise<void> {
    const doc = await vscode.workspace.openTextDocument({
        content: `# Cogito ${release.version}\n\n${release.notes ?? ''}\n`,
        language: 'markdown',
    });
    await vscode.commands.executeCommand('markdown.showPreview', doc.uri);
}

/** Download, verify (size + sha256) and install the release, then offer a reload. */
async function installRelease(deps: UpdateCheckDeps, release: LatestRelease): Promise<void> {
    let stage = 'download';
    try {
        const data = await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `Cogito: скачиваю обновление ${release.version}…`,
                cancellable: false,
            },
            async () => {
                const body = await fetchVsix(deps.serverUrl);
                stage = 'verify';
                const check = verifyDownload(body, release.sha256, release.size);
                if (!check.ok) throw new UpdateError(`файл не прошёл проверку: ${check.error}`);
                return body;
            }
        );
        stage = 'storage';
        const updatesDir = vscode.Uri.joinPath(deps.context.globalStorageUri, 'updates');
        await vscode.workspace.fs.createDirectory(updatesDir);
        const target = vscode.Uri.joinPath(updatesDir, vsixFileName(release.version));
        await vscode.workspace.fs.writeFile(target, data);
        stage = 'install';
        // Recent desktop hosts expose globalStorageUri through vscode-userdata.
        // The VSIX installer routes only file / vscode-remote resources.
        const installTarget = target.scheme === 'vscode-userdata'
            ? vscode.Uri.file(target.fsPath)
            : target;
        await vscode.commands.executeCommand(
            'workbench.extensions.installExtension',
            installTarget
        );
        stage = 'state';
        await deps.context.globalState.update(SNOOZED_KEY, undefined);
        deps.log?.(`update installed: ${release.version}`);
        stage = 'reload prompt';
        const choice = await vscode.window.showInformationMessage(
            `Cogito: версия ${release.version} установлена. Перезагрузи окно, чтобы она заработала.`,
            'Перезагрузить окно'
        );
        if (choice === 'Перезагрузить окно') {
            await vscode.commands.executeCommand('workbench.action.reloadWindow');
        }
    } catch (error) {
        const message = updateErrorMessage(error);
        deps.log?.(`update install failed (${stage}, version ${release.version}): ${message}`);
        void vscode.window.showErrorMessage(`Cogito: не удалось установить обновление — ${message}`);
    }
}

interface EvaluateOptions {
    /** Automatic checks stay silent when the version is current. */
    automatic: boolean;
    /** A manual check ignores «Позже». */
    ignoreSnooze: boolean;
}

/**
 * Compare a fetched release with the running version and act: notify with
 * «Обновить» / «Позже» / «Что нового», or stay quiet. Returns the decision
 * from `shouldNotify` restricted to the fetched version.
 */
async function evaluateRelease(
    deps: UpdateCheckDeps,
    release: LatestRelease,
    opts: EvaluateOptions
): Promise<boolean> {
    const { context, currentVersion } = deps;
    const newer = compareSemver(release.version, currentVersion) > 0;
    if (!newer) {
        if (!opts.automatic) {
            void vscode.window.showInformationMessage(
                `Cogito: у тебя последняя версия ${currentVersion}.`
            );
        }
        return false;
    }
    const snoozed = opts.ignoreSnooze
        ? undefined
        : context.globalState.get<string>(SNOOZED_KEY);
    const decision = shouldNotify({
        current: currentVersion,
        latest: release.version,
        snoozedVersion: snoozed,
        lastCheckIso: null,
        now: Date.now(),
    });
    if (!decision.notify) return false;

    const actions = ['Обновить'];
    if (release.notes && release.notes.trim()) actions.push('Что нового');
    actions.push('Позже');

    const choice = await vscode.window.showInformationMessage(
        updateMessage(release.version, currentVersion),
        ...actions
    );
    if (choice === 'Позже') {
        await context.globalState.update(SNOOZED_KEY, release.version);
        return true;
    }
    if (choice === 'Что нового') {
        await showNotes(release);
        return true;
    }
    if (choice === 'Обновить') {
        await installRelease(deps, release);
    }
    return true;
}

// === Entry points used by extension.ts ===

let timer: NodeJS.Timeout | undefined;
let running = false;

/** Schedule the automatic check ~10 s after activation (activation never waits). */
export function scheduleUpdateCheck(deps: UpdateCheckDeps): vscode.Disposable {
    const channel = vscode.window.createOutputChannel('Cogito: обновления');
    const withLog: UpdateCheckDeps = {
        ...deps,
        log:
            deps.log ??
            ((message) => channel.appendLine(`${new Date().toISOString()} ${message}`)),
    };
    timer = setTimeout(() => {
        timer = undefined;
        void runAutomaticCheck(withLog);
    }, AUTO_CHECK_DELAY_MS);
    if (typeof timer.unref === 'function') timer.unref();
    return {
        dispose: () => {
            if (timer) clearTimeout(timer);
            timer = undefined;
            channel.dispose();
        },
    };
}

/** One automatic check: 24 h throttle; offline mode and failures stay silent. */
export async function runAutomaticCheck(deps: UpdateCheckDeps): Promise<void> {
    if (running) return;
    running = true;
    try {
        if (isOfflineMode(await safeMode(deps))) return;
        const now = Date.now();
        const decision = shouldNotify({
            current: deps.currentVersion,
            latest: null,
            snoozedVersion: deps.context.globalState.get<string>(SNOOZED_KEY),
            lastCheckIso: deps.context.globalState.get<string>(LAST_CHECK_KEY),
            now,
        });
        if (!decision.check) return;
        if (decision.record) {
            // Recorded before the request: a hung server must not stack checks.
            await deps.context.globalState.update(LAST_CHECK_KEY, new Date(now).toISOString());
        }
        const release = await checkLatest(deps, true);
        if (!release) return;
        await evaluateRelease(deps, release, { automatic: true, ignoreSnooze: false });
    } catch (error) {
        deps.log?.(`automatic update check failed: ${updateErrorMessage(error)}`);
    } finally {
        running = false;
    }
}

/** «Cogito: Проверить обновления» — every failure gets a clear message. */
export async function checkForUpdatesManually(deps: UpdateCheckDeps): Promise<void> {
    const release = await checkLatest(deps, false);
    if (!release) return;
    await evaluateRelease(deps, release, { automatic: false, ignoreSnooze: true });
}

/**
 * Version of the running extension: its own `package.json` first, then the
 * version VS Code installed from. `0.0.0` (never "newer") as a last resort.
 */
export function currentExtensionVersion(context: vscode.ExtensionContext): string {
    try {
        const raw = fs.readFileSync(path.join(context.extensionPath, 'package.json'), 'utf-8');
        const version = (JSON.parse(raw) as { version?: unknown }).version;
        if (isValidVersion(version)) return version.trim();
    } catch {
        // Fall through to the VS Code API below.
    }
    const id = String(context.extension?.id ?? '');
    const name = id.slice(id.indexOf('.') + 1);
    if (id.includes('.') && name) {
        try {
            const installed = vscode.extensions.getExtension(id);
            const version = installed?.packageJSON?.version;
            if (isValidVersion(version)) return version.trim();
        } catch {
            // Unknown extension in this host — keep the fallback.
        }
    }
    return '0.0.0';
}

/** Check interval, re-exported for tests and tooling. */
export const UPDATE_CHECK_INTERVAL_MS = CHECK_INTERVAL_MS;
