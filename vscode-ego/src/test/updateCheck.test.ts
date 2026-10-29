/** Unit tests for the updateCheck pure helpers (self-hosted extension updates).
 *
 * `updateCheckHelpers.ts` has no `vscode` import, so `node --test` can load
 * it without a VS Code host. Run with `npm run test:unit`.
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    CHECK_INTERVAL_MS,
    isOfflineMode,
    isValidVersion,
    normalizedBaseUrl,
    parseLatestRelease,
    sha256Hex,
    updateMessage,
    verifyDownload,
    vsixFileName,
    compareSemver,
    shouldNotify,
    updateErrorMessage,
} from '../updateCheckHelpers';

const DAY = 24 * 60 * 60 * 1000;
const NOW = Date.parse('2026-10-21T12:00:00.000Z');

test('updateErrorMessage handles Error, RPC objects, aggregate errors and empty rejections', () => {
    assert.equal(updateErrorMessage(new Error('Disk full')), 'Disk full');
    assert.equal(updateErrorMessage({ message: 'Remote install failed' }), 'Remote install failed');
    assert.equal(updateErrorMessage(new AggregateError([new Error('Disk full')], 'Install failed')),
        'Install failed; Disk full');
    assert.equal(updateErrorMessage({ code: 'EACCES' }), 'EACCES');
    for (const value of [undefined, null, '', {}, []]) {
        assert.equal(updateErrorMessage(value), 'неизвестная ошибка');
    }
    const cyclic: unknown[] = [];
    cyclic.push(cyclic, 'Install failed');
    assert.equal(updateErrorMessage(cyclic), 'Install failed');
});

// ---------------------------------------------------------------------------
// compareSemver
// ---------------------------------------------------------------------------

test('compareSemver: orders release numbers numerically, not lexically', () => {
    assert.equal(compareSemver('0.2.0', '0.1.9'), 1);
    assert.equal(compareSemver('0.1.9', '0.2.0'), -1);
    assert.equal(compareSemver('0.2.0', '0.2.0'), 0);
    assert.equal(compareSemver('0.10.0', '0.9.0'), 1);
    assert.equal(compareSemver('1.0.0', '0.99.99'), 1);
    assert.equal(compareSemver('10.0.0', '9.9.9'), 1);
    assert.equal(compareSemver(' 0.2.0 ', '0.2.0'), 0);
});

test('compareSemver: pre-releases sort before the release', () => {
    assert.equal(compareSemver('0.2.0', '0.2.0-beta.1'), 1);
    assert.equal(compareSemver('0.2.0-beta.1', '0.2.0'), -1);
    assert.equal(compareSemver('0.2.0-alpha', '0.2.0-beta'), -1);
    assert.equal(compareSemver('0.2.0-beta.2', '0.2.0-beta.10'), -1);
    assert.equal(compareSemver('0.2.0-beta', '0.2.0-beta.1'), -1);
});

test('compareSemver: build metadata is ignored', () => {
    assert.equal(compareSemver('0.2.0+build.5', '0.2.0'), 0);
    assert.equal(compareSemver('0.2.0', '0.2.0+other'), 0);
});

test('compareSemver: invalid versions compare as equal', () => {
    assert.equal(compareSemver('not-a-version', '0.2.0'), 0);
    assert.equal(compareSemver('0.2.0', ''), 0);
    assert.equal(compareSemver('0.2', '0.2.0'), 0);
    assert.equal(compareSemver('v0.2.0', '0.2.0'), 0);
});

test('isValidVersion: strict SemVer only', () => {
    for (const ok of ['0.2.0', '1.0.0', '0.2.0-rc.1', '0.2.0+build.1']) {
        assert.equal(isValidVersion(ok), true, ok);
    }
    for (const bad of ['', '0.2', 'v1.0.0', '01.0.0', '1.0.0.0', null, 2]) {
        assert.equal(isValidVersion(bad), false, String(bad));
    }
});

// ---------------------------------------------------------------------------
// shouldNotify
// ---------------------------------------------------------------------------

test('shouldNotify: newer version within 24 h is throttled', () => {
    const result = shouldNotify({
        current: '0.1.1',
        latest: '0.2.0',
        snoozedVersion: undefined,
        lastCheckIso: new Date(NOW - 60_000).toISOString(),
        now: NOW,
    });
    assert.deepEqual(result, { notify: false, check: false, record: false });
});

test('shouldNotify: newer version after 24 h notifies and records', () => {
    const result = shouldNotify({
        current: '0.1.1',
        latest: '0.2.0',
        snoozedVersion: null,
        lastCheckIso: new Date(NOW - DAY).toISOString(),
        now: NOW,
    });
    assert.deepEqual(result, { notify: true, check: true, record: true });
});

test('shouldNotify: first run (no previous check) notifies', () => {
    const result = shouldNotify({
        current: '0.1.1',
        latest: '0.2.0',
        snoozedVersion: undefined,
        lastCheckIso: undefined,
        now: NOW,
    });
    assert.deepEqual(result, { notify: true, check: true, record: true });
});

test('shouldNotify: same or older version checks but does not notify', () => {
    for (const latest of ['0.1.1', '0.1.0', '0.0.9']) {
        const result = shouldNotify({
            current: '0.1.1', latest, snoozedVersion: undefined, lastCheckIso: null, now: NOW,
        });
        assert.equal(result.notify, false, latest);
        assert.equal(result.check, true);
    }
});

test('shouldNotify: nothing published means no notification', () => {
    for (const latest of [null, undefined, '']) {
        const result = shouldNotify({
            current: '0.1.1', latest, snoozedVersion: undefined, lastCheckIso: null, now: NOW,
        });
        assert.equal(result.notify, false);
        assert.equal(result.check, true);
    }
});

test('shouldNotify: snoozing the exact version suppresses it, others do not', () => {
    const base = {
        current: '0.1.1', latest: '0.2.0', lastCheckIso: null, now: NOW,
    };
    assert.equal(shouldNotify({ ...base, snoozedVersion: '0.2.0' }).notify, false);
    assert.equal(shouldNotify({ ...base, snoozedVersion: '0.1.9' }).notify, true);
    assert.equal(shouldNotify({ ...base, snoozedVersion: null }).notify, true);
});

test('shouldNotify: invalid latest version never notifies', () => {
    const result = shouldNotify({
        current: '0.1.1', latest: 'latest', snoozedVersion: undefined, lastCheckIso: null, now: NOW,
    });
    assert.equal(result.notify, false);
});

test('shouldNotify: corrupt or future timestamp re-records without throttling', () => {
    const future = shouldNotify({
        current: '0.1.1', latest: '0.2.0', snoozedVersion: undefined,
        lastCheckIso: new Date(NOW + 5 * DAY).toISOString(), now: NOW,
    });
    assert.deepEqual(future, { notify: false, check: false, record: true });

    const corrupt = shouldNotify({
        current: '0.1.1', latest: '0.2.0', snoozedVersion: undefined,
        lastCheckIso: 'yesterday-ish', now: NOW,
    });
    assert.equal(corrupt.check, true);
    assert.equal(corrupt.notify, true);
});

test('shouldNotify: 24 h boundary is inclusive of a full day', () => {
    const justUnder = shouldNotify({
        current: '0.1.1', latest: '0.2.0', snoozedVersion: undefined,
        lastCheckIso: new Date(NOW - (CHECK_INTERVAL_MS - 1)).toISOString(), now: NOW,
    });
    assert.equal(justUnder.check, false);
    const exact = shouldNotify({
        current: '0.1.1', latest: '0.2.0', snoozedVersion: undefined,
        lastCheckIso: new Date(NOW - CHECK_INTERVAL_MS).toISOString(), now: NOW,
    });
    assert.equal(exact.check, true);
});

// ---------------------------------------------------------------------------
// sha256 / download verification
// ---------------------------------------------------------------------------

test('sha256Hex: known vector', () => {
    assert.equal(
        sha256Hex(Buffer.from('abc', 'utf-8')),
        'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    );
});

test('verifyDownload: accepts a matching size and sha256', () => {
    const data = Buffer.from('vsix-payload');
    const result = verifyDownload(data, sha256Hex(data), data.length);
    assert.deepEqual(result, { ok: true });
});

test('verifyDownload: sha256 comparison is case-insensitive', () => {
    const data = Buffer.from('vsix-payload');
    assert.equal(verifyDownload(data, sha256Hex(data).toUpperCase(), data.length).ok, true);
});

test('verifyDownload: rejects a wrong checksum', () => {
    const data = Buffer.from('vsix-payload');
    const result = verifyDownload(data, '0'.repeat(64), data.length);
    assert.equal(result.ok, false);
    assert.match(result.error ?? '', /Контрольная сумма/);
});

test('verifyDownload: rejects a size mismatch', () => {
    const data = Buffer.from('vsix-payload');
    const result = verifyDownload(data, sha256Hex(data), data.length + 1);
    assert.equal(result.ok, false);
    assert.match(result.error ?? '', /Размер/);
});

test('verifyDownload: rejects empty data, bad expected fields', () => {
    assert.equal(verifyDownload(Buffer.alloc(0), '0'.repeat(64), 0).ok, false);
    const data = Buffer.from('x');
    assert.equal(verifyDownload(data, 'short', data.length).ok, false);
    assert.equal(verifyDownload(data, sha256Hex(data), -1).ok, false);
});

// ---------------------------------------------------------------------------
// small formatting helpers
// ---------------------------------------------------------------------------

test('updateMessage: exact notification text', () => {
    assert.equal(
        updateMessage('0.2.0', '0.1.1'),
        'Cogito: доступна новая версия 0.2.0 (у тебя 0.1.1).'
    );
});

test('vsixFileName: safe name from a version', () => {
    assert.equal(vsixFileName('0.2.0'), 'cogito-0.2.0.vsix');
    assert.equal(vsixFileName('0.2.0-rc.1'), 'cogito-0.2.0-rc.1.vsix');
    assert.equal(vsixFileName('../evil'), 'cogito-update.vsix');
});

test('isOfflineMode: only local mode disables the check', () => {
    assert.equal(isOfflineMode('offline'), true);
    assert.equal(isOfflineMode('server'), false);
    assert.equal(isOfflineMode(undefined), false);
    assert.equal(isOfflineMode(null), false);
});

test('normalizedBaseUrl: strips trailing slashes, keeps an empty url empty', () => {
    assert.equal(normalizedBaseUrl('http://localhost:8000/'), 'http://localhost:8000');
    assert.equal(normalizedBaseUrl(' https://cogito.example.com// '), 'https://cogito.example.com');
    assert.equal(normalizedBaseUrl(''), '');
    assert.equal(normalizedBaseUrl(undefined), '');
});

test('parseLatestRelease: normalizes the server contract', () => {
    const release = parseLatestRelease({
        version: ' 0.2.0 ',
        sha256: 'AB'.repeat(32),
        size: 12345,
        published_at: '2026-10-21T00:00:00+00:00',
        download_url: '/extension/download',
        notes: 'Новые подсказки',
    });
    assert.equal(release.version, '0.2.0');
    assert.equal(release.sha256, 'ab'.repeat(32));
    assert.equal(release.size, 12345);
    assert.equal(release.download_url, '/extension/download');
    assert.equal(release.notes, 'Новые подсказки');
});

test('parseLatestRelease: rejects unusable payloads with a clear message', () => {
    const bad = [
        null,
        'oops',
        { version: 'latest', sha256: 'a'.repeat(64), size: 1 },
        { version: '0.2.0', sha256: '', size: 1 },
        { version: '0.2.0', sha256: 'a'.repeat(64), size: 0 },
        { version: '0.2.0', sha256: 'a'.repeat(64) },
    ];
    for (const payload of bad) {
        assert.throws(() => parseLatestRelease(payload), /некорректные данные/);
    }
});
