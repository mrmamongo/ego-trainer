/** Pure update-decision helpers (no `vscode` import → unit-testable).
 *
 * The runtime flow in `updateCheck.ts` composes these with the editor API;
 * keeping the decisions here means `node --test` can load them without a
 * VS Code host.
 */

import * as crypto from 'crypto';

/** VS Code commands may reject with strings or arrays, rather than Error. */
export function updateErrorMessage(error: unknown): string {
    const seen = new Set<object>();
    function describe(value: unknown): string {
        if (typeof value === 'string') return value.trim();
        if (!value || typeof value !== 'object' || seen.has(value)) return '';
        seen.add(value);
        if (Array.isArray(value)) return value.map(describe).filter(Boolean).join('; ');
        const detail = value as { message?: unknown; errors?: unknown; code?: unknown };
        const message = typeof detail.message === 'string' ? detail.message.trim() : '';
        const errors = Array.isArray(detail.errors) ? describe(detail.errors) : '';
        const code = typeof detail.code === 'string' ? detail.code.trim() : '';
        return [message, errors].filter(Boolean).join('; ') || code;
    }
    return describe(error) || 'неизвестная ошибка';
}

/** Global state key: ISO timestamp of the last check attempt. */
export const LAST_CHECK_KEY = 'ego.updateCheck.lastCheck';

/** Global state key: the version the student chose «Позже» for. */
export const SNOOZED_KEY = 'ego.updateCheck.snoozedVersion';

/** At most one automatic check per 24 hours. */
export const CHECK_INTERVAL_MS = 24 * 60 * 60 * 1000;

/** Delay before the automatic check, so activation stays fast. */
export const AUTO_CHECK_DELAY_MS = 10_000;

/** Public server paths (no authentication). */
export const LATEST_PATH = '/extension/latest';
export const DOWNLOAD_PATH = '/extension/download';

const SEMVER_RE =
    /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;

type Prerelease = { numeric: 0; value: number } | { numeric: 1; value: string };

/**
 * Compare two SemVer versions: negative when `a < b`, 0 when equal,
 * positive when `a > b`. Build metadata is ignored; a pre-release sorts
 * before its release. Invalid input compares as equal (0), so the extension
 * never "updates" to a version it cannot parse.
 */
export function compareSemver(a: string, b: string): number {
    const pa = SEMVER_RE.exec(String(a ?? '').trim());
    const pb = SEMVER_RE.exec(String(b ?? '').trim());
    if (!pa || !pb) return 0;
    for (let i = 1; i <= 3; i++) {
        const diff = Number(pa[i]) - Number(pb[i]);
        if (diff !== 0) return diff < 0 ? -1 : 1;
    }
    const preA = pa[4];
    const preB = pb[4];
    if (preA === undefined && preB === undefined) return 0;
    if (preA === undefined) return 1; // a release is newer than any pre-release
    if (preB === undefined) return -1;
    const idsA = preA.split('.').map(toPrerelease);
    const idsB = preB.split('.').map(toPrerelease);
    for (let i = 0; i < Math.min(idsA.length, idsB.length); i++) {
        const x = idsA[i];
        const y = idsB[i];
        if (x.numeric !== y.numeric) return x.numeric === 0 ? -1 : 1; // numeric < alphanumeric
        if (x.value === y.value) continue;
        if (x.numeric === 0) return (x.value as number) < (y.value as number) ? -1 : 1;
        return (x.value as string) < (y.value as string) ? -1 : 1;
    }
    if (idsA.length === idsB.length) return 0;
    return idsA.length < idsB.length ? -1 : 1;
}

function toPrerelease(id: string): Prerelease {
    return /^\d+$/.test(id) ? { numeric: 0, value: Number(id) } : { numeric: 1, value: id };
}

/** True when `version` is a SemVer that can be shown and installed. */
export function isValidVersion(version: unknown): version is string {
    return typeof version === 'string' && SEMVER_RE.test(version.trim());
}

export interface ShouldNotifyInput {
    /** Version of the running extension. */
    current: string;
    /** Version published on the server (null/undefined when none). */
    latest: string | null | undefined;
    /** Version the student chose «Позже» for (null/undefined when none). */
    snoozedVersion: string | null | undefined;
    /** ISO time of the previous check attempt. */
    lastCheckIso: string | null | undefined;
    /** Current time (epoch ms). */
    now: number;
}

export interface ShouldNotifyResult {
    /** Show the «new version» notification. */
    notify: boolean;
    /** Perform a (silent) server check now. */
    check: boolean;
    /** Store `now` as the last check time. */
    record: boolean;
}

/**
 * Decide whether the automatic update check runs and whether it notifies.
 *
 * - `check`: false while the previous attempt is younger than 24 h; a
 *   stored timestamp in the future or corrupt only gets re-recorded.
 * - `notify`: true when `latest` is strictly newer than `current` and the
 *   student has not snoozed exactly that version.
 * - `record`: true whenever a check runs — a failed attempt (server down,
 *   nothing published) also counts, so the retry is at most once per 24 h.
 */
export function shouldNotify(input: ShouldNotifyInput): ShouldNotifyResult {
    const { current, latest, snoozedVersion, lastCheckIso, now } = input;
    const last = lastCheckIso ? Date.parse(lastCheckIso) : NaN;
    if (lastCheckIso && Number.isFinite(last)) {
        const elapsed = now - last;
        if (elapsed >= 0 && elapsed < CHECK_INTERVAL_MS) {
            return { notify: false, check: false, record: false };
        }
        if (elapsed < 0) {
            return { notify: false, check: false, record: true };
        }
    }
    const notify =
        isValidVersion(current) &&
        isValidVersion(latest) &&
        compareSemver(latest, current) > 0 &&
        !(typeof snoozedVersion === 'string' && snoozedVersion.trim() === latest.trim());
    return { notify, check: true, record: true };
}

export interface InstallVerification {
    ok: boolean;
    error?: string;
}

/** Lowercase hex sha256 of `data`. */
export function sha256Hex(data: Buffer): string {
    return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Verify a downloaded `.vsix` against the size and sha256 announced by
 * `/extension/latest` before anything is installed.
 */
export function verifyDownload(
    data: Buffer,
    expectedSha256: string,
    expectedSize: number
): InstallVerification {
    if (!Buffer.isBuffer(data) || data.length === 0) {
        return { ok: false, error: 'Файл расширения не загрузился.' };
    }
    if (!Number.isInteger(expectedSize) || expectedSize <= 0) {
        return { ok: false, error: 'Сервер не сообщил размер файла расширения.' };
    }
    if (data.length !== expectedSize) {
        return {
            ok: false,
            error: `Размер файла не совпал: ожидалось ${expectedSize} байт, получено ${data.length}.`,
        };
    }
    const expected = String(expectedSha256 ?? '').trim().toLowerCase();
    if (!/^[0-9a-f]{64}$/.test(expected)) {
        return { ok: false, error: 'Сервер не сообщил корректную контрольную сумму.' };
    }
    if (sha256Hex(data) !== expected) {
        return { ok: false, error: 'Контрольная сумма расширения не совпала.' };
    }
    return { ok: true };
}

/** File name for a downloaded release; never derived from untrusted input. */
export function vsixFileName(version: string): string {
    return isValidVersion(version) ? `cogito-${version.trim()}.vsix` : 'cogito-update.vsix';
}

/** Text of the «new version» notification. */
export function updateMessage(latest: string, current: string): string {
    return `Cogito: доступна новая версия ${latest} (у тебя ${current}).`;
}

/** True when the workspace is in local mode, which disables update checks. */
export function isOfflineMode(mode: string | null | undefined): boolean {
    return mode === 'offline';
}

/** Release metadata served by `GET /extension/latest`. */
export interface LatestRelease {
    version: string;
    sha256: string;
    size: number;
    published_at?: string;
    download_url?: string;
    notes?: string;
    mandatory?: boolean;
}

/** Base server URL without trailing slashes ('' when unset). */
export function normalizedBaseUrl(serverUrl: string | null | undefined): string {
    return String(serverUrl || '').trim().replace(/\/+$/, '');
}

/**
 * Validate the JSON body of `GET /extension/latest`; throws a Russian,
 * user-facing message when the server answered with something unusable.
 */
export function parseLatestRelease(data: unknown): LatestRelease {
    const body = data as Partial<LatestRelease> | null;
    if (
        !body ||
        typeof body !== 'object' ||
        !isValidVersion(body.version) ||
        typeof body.sha256 !== 'string' ||
        !/^[0-9a-f]{64}$/i.test(body.sha256.trim()) ||
        !Number.isInteger(body.size) ||
        (body.size as number) <= 0
    ) {
        throw new Error('сервер вернул некорректные данные о версии расширения.');
    }
    const release: LatestRelease = {
        version: (body.version as string).trim(),
        sha256: body.sha256.trim().toLowerCase(),
        size: body.size as number,
    };
    if (typeof body.published_at === 'string') release.published_at = body.published_at;
    if (typeof body.download_url === 'string') release.download_url = body.download_url;
    if (typeof body.notes === 'string') release.notes = body.notes;
    if (body.mandatory === true) release.mandatory = true;
    return release;
}
