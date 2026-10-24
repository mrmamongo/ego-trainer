import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    planPull,
    type ManifestTaskEntry,
    type PullTaskMeta,
} from '../pullSafety';

const task = (id: string, overrides: Partial<PullTaskMeta> = {}): PullTaskMeta => ({
    id,
    version: '1.0.0',
    content_hash: `hash-${id}`,
    ...overrides,
});

const entry = (
    id: string,
    overrides: Partial<ManifestTaskEntry> = {}
): ManifestTaskEntry => ({
    id,
    block: 'block-a',
    slug: id.toLowerCase(),
    version: '1.0.0',
    content_hash: `hash-${id}`,
    pulled_at: '2026-01-01T00:00:00.000Z',
    md_path: `tasks/${id}.md`,
    ...overrides,
});

const ids = (tasks: PullTaskMeta[]): string[] => tasks.map((t) => t.id);
const allPresent = () => true;

test('planPull fetches a new task missing from the manifest', () => {
    const plan = planPull([task('F1')], [], allPresent);
    assert.deepEqual(ids(plan.fetch), ['F1']);
    assert.deepEqual(ids(plan.upToDate), []);
});

test('planPull keeps an unchanged task up to date', () => {
    const plan = planPull([task('F1')], [entry('F1')], allPresent);
    assert.deepEqual(ids(plan.fetch), []);
    assert.deepEqual(ids(plan.upToDate), ['F1']);
});

test('planPull fetches a task whose hash changed', () => {
    const plan = planPull(
        [task('F1', { content_hash: 'new-hash' })],
        [entry('F1')],
        allPresent
    );
    assert.deepEqual(ids(plan.fetch), ['F1']);
    assert.deepEqual(ids(plan.upToDate), []);
});

test('planPull fetches a task whose version changed', () => {
    const plan = planPull(
        [task('F1', { version: '2.0.0' })],
        [entry('F1')],
        allPresent
    );
    assert.deepEqual(ids(plan.fetch), ['F1']);
    assert.deepEqual(ids(plan.upToDate), []);
});

test('planPull fetches a task whose local .md/.py are missing', () => {
    const plan = planPull([task('F1')], [entry('F1')], () => false);
    assert.deepEqual(ids(plan.fetch), ['F1']);
    assert.deepEqual(ids(plan.upToDate), []);
    assert.equal(plan.fetch[0].version, '1.0.0');
});

test('planPull passes the manifest entry to the existence check', () => {
    const seen: Array<[string, string]> = [];
    const manifest = [entry('f1', { content_hash: 'hash-F1' })];
    planPull([task('F1')], manifest, (manifestEntry, serverTask) => {
        seen.push([manifestEntry.id, serverTask.id]);
        return true;
    });
    assert.deepEqual(seen, [['f1', 'F1']]);
});

test('planPull matches ids case-insensitively', () => {
    const plan = planPull(
        [task('f1', { content_hash: 'hash-f1' })],
        [entry('F1', { content_hash: 'hash-f1' })],
        allPresent
    );
    assert.deepEqual(ids(plan.upToDate), ['f1']);
});

test('planPull matches manifest ids case-insensitively', () => {
    const plan = planPull([task('F1')], [entry('f1', { content_hash: 'hash-F1' })], allPresent);
    assert.deepEqual(ids(plan.upToDate), ['F1']);
});

test('planPull with an empty manifest fetches everything', () => {
    const tasks = [task('F1'), task('F2'), task('H3')];
    const plan = planPull(tasks, [], allPresent);
    assert.deepEqual(ids(plan.fetch), ['F1', 'F2', 'H3']);
    assert.deepEqual(ids(plan.upToDate), []);
});

test('planPull splits a mixed list and preserves input order', () => {
    const tasks = [
        task('F1', { content_hash: 'h-f1' }),
        task('F2', { content_hash: 'changed' }),
        task('F3', { content_hash: 'h-f3' }),
        task('H1', { content_hash: 'h-h1' }),
    ];
    const manifest = [
        entry('F1', { content_hash: 'h-f1' }),
        entry('F2', { content_hash: 'h-f2' }),
        entry('F3', { content_hash: 'h-f3' }),
        entry('H1', { content_hash: 'h-h1' }),
    ];
    const plan = planPull(tasks, manifest, (_e, t) => t.id !== 'F3');
    assert.deepEqual(ids(plan.fetch), ['F2', 'F3']);
    assert.deepEqual(ids(plan.upToDate), ['F1', 'H1']);
    assert.equal(plan.fetch[0], tasks[1]);
    assert.equal(plan.upToDate[0], tasks[0]);
});

test('planPull with no server tasks returns empty lists', () => {
    const plan = planPull([], [entry('F1')], allPresent);
    assert.deepEqual(plan, { fetch: [], upToDate: [] });
});
