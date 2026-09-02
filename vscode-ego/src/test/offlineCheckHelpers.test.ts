/** Unit tests for offlineCheckHelpers (8bv.9.9 Windows/offline slice).
 *
 * Pure, deterministic, no `vscode` / `child_process` / fs. Run with Node's
 * built-in test runner via `npm run test:unit`
 * (`node --test out/test/*.test.js`).
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    normalizeCwd,
    cwdCacheKey,
    shouldUseShell,
    childEnv,
    validateTaskId,
} from '../offlineCheckHelpers';

// ---------------------------------------------------------------------------
// normalizeCwd / cwdCacheKey — Windows vs posix normalization
// ---------------------------------------------------------------------------

test('normalizeCwd: posix keeps forward slashes and is case-sensitive', () => {
    assert.equal(normalizeCwd('/home/user/ego', 'linux'), '/home/user/ego');
    assert.equal(normalizeCwd('/home/user/ego/', 'linux'), '/home/user/ego');
    assert.equal(normalizeCwd('/home//user///ego', 'linux'), '/home/user/ego');
    // POSIX is case-sensitive: distinct ids stay distinct.
    assert.notEqual(
        normalizeCwd('/Home/User', 'linux'),
        normalizeCwd('/home/user', 'linux')
    );
});

test('normalizeCwd: win32 converts backslashes and lower-cases', () => {
    assert.equal(
        normalizeCwd('C:\\Users\\ego\\tasks', 'win32'),
        'c:/users/ego/tasks'
    );
    // Mixed separators collapse to a single forward slash.
    assert.equal(
        normalizeCwd('C:\\Users/ego\\tasks', 'win32'),
        'c:/users/ego/tasks'
    );
    // Case-insensitive on win32: same directory shares a key.
    assert.equal(
        normalizeCwd('C:\\Users\\Ego', 'win32'),
        normalizeCwd('c:\\users\\ego', 'win32')
    );
    // Trailing slash stripped (root '/' preserved).
    assert.equal(normalizeCwd('C:\\ego\\', 'win32'), 'c:/ego');
});

test('normalizeCwd: POSIX root "/" is preserved', () => {
    assert.equal(normalizeCwd('/', 'linux'), '/');
    assert.equal(normalizeCwd('/', 'win32'), '/');
});

test('normalizeCwd: empty / whitespace input yields empty key', () => {
    assert.equal(normalizeCwd('', 'linux'), '');
    assert.equal(normalizeCwd('   ', 'linux'), '');
    assert.equal(normalizeCwd('', 'win32'), '');
});

test('cwdCacheKey is an alias of normalizeCwd', () => {
    assert.equal(
        cwdCacheKey('C:\\Ego\\Tasks', 'win32'),
        normalizeCwd('C:\\Ego\\Tasks', 'win32')
    );
    assert.equal(
        cwdCacheKey('/home/ego/tasks', 'linux'),
        normalizeCwd('/home/ego/tasks', 'linux')
    );
});

// ---------------------------------------------------------------------------
// validateTaskId — allowed and rejected ids
// ---------------------------------------------------------------------------

test('validateTaskId: accepts ASCII letters, digits, ".", "_", "-"', () => {
    for (const id of [
        'block_f.task-1_2',
        'block_f',
        'task-1',
        'Task_2.3',
        'A1.B2-C3_D4',
        'a',
        '0',
    ]) {
        const res = validateTaskId(id);
        assert.equal(res.ok, true, `expected ok for "${id}"`);
    }
});

test('validateTaskId: rejects shell metacharacters and whitespace', () => {
    const rejected = [
        'block f',           // space
        'block\tf',          // tab
        'block;rm',          // command separator
        'block|grep',        // pipe
        'block&bg',          // background
        'block$HOME',        // variable expansion
        'block`whoami`',     // backtick command substitution
        'block$(whoami)',    // $(...) command substitution
        'block>out',         // redirect
        'block<in',          // redirect
        'block*glob',        // glob
        'block?glob',        // glob
        'block(parens)',     // parens
        'block"quote',       // double quote
        "block'quote",       // single quote
        'block\\path',       // backslash
        'block\nnewline',    // newline
        '../escape',         // path traversal
        'block/slash',       // slash
        'block:colon',       // colon (drive / stream separator)
    ];
    for (const id of rejected) {
        const res = validateTaskId(id);
        assert.equal(res.ok, false, `expected reject for "${id}"`);
        if (!res.ok) {
            assert.ok(res.error.length > 0, `error message non-empty for "${id}"`);
        }
    }
});

test('validateTaskId: rejects empty / non-string', () => {
    assert.deepEqual(validateTaskId(''), { ok: false, error: 'Task id is required.' });
    assert.deepEqual(
        validateTaskId(undefined as unknown as string),
        { ok: false, error: 'Task id is required.' }
    );
    assert.deepEqual(
        validateTaskId(null as unknown as string),
        { ok: false, error: 'Task id is required.' }
    );
});

test('validateTaskId: error message previews long ids', () => {
    const long = 'a'.repeat(60) + ' bad';
    const res = validateTaskId(long);
    assert.equal(res.ok, false);
    if (!res.ok) {
        assert.ok(res.error.includes('…'), 'preview uses ellipsis for long id');
        assert.ok(!res.error.includes(long.slice(40)), 'preview omits invalid suffix after first 40 chars');
    }
});

// ---------------------------------------------------------------------------
// childEnv — env preservation + UTF-8 forcing
// ---------------------------------------------------------------------------

test('childEnv: preserves caller-supplied env entries', () => {
    const env = { PATH: '/usr/bin', MY_FLAG: 'keep-me', EGO_DB_PATH: '/tmp/ego.db' };
    const out = childEnv(env);
    assert.equal(out.PATH, '/usr/bin');
    assert.equal(out.MY_FLAG, 'keep-me');
    assert.equal(out.EGO_DB_PATH, '/tmp/ego.db');
});

test('childEnv: forces UTF-8 on stdout/stderr and interpreter', () => {
    const out = childEnv({});
    assert.equal(out.PYTHONIOENCODING, 'utf-8');
    assert.equal(out.PYTHONUTF8, '1');
});

test('childEnv: UTF-8 keys override caller-supplied values', () => {
    const out = childEnv({ PYTHONIOENCODING: 'latin-1', PYTHONUTF8: '0' });
    assert.equal(out.PYTHONIOENCODING, 'utf-8');
    assert.equal(out.PYTHONUTF8, '1');
});

test('childEnv: does not mutate the input env object', () => {
    const env: NodeJS.ProcessEnv = { PYTHONIOENCODING: 'latin-1', KEEP: 'x' };
    childEnv(env);
    assert.equal(env.PYTHONIOENCODING, 'latin-1', 'input env untouched');
    assert.equal(env.PYTHONUTF8, undefined, 'input env untouched');
});

// ---------------------------------------------------------------------------
// shouldUseShell — platform decision
// ---------------------------------------------------------------------------

test('shouldUseShell: true on win32, false elsewhere', () => {
    assert.equal(shouldUseShell('win32'), true);
    assert.equal(shouldUseShell('linux'), false);
    assert.equal(shouldUseShell('darwin'), false);
    assert.equal(shouldUseShell('aix'), false);
    assert.equal(shouldUseShell(''), false);
});

test('shouldUseShell: defaults to current process.platform', () => {
    // No argument → must match a decision based on process.platform.
    const expected = process.platform === 'win32';
    assert.equal(shouldUseShell(), expected);
});
