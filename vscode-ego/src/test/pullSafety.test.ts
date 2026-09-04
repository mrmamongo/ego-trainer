import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    assertSafeCatalogSegment,
    decideTextFile,
    mergeManifestEntries,
    type ManifestTaskEntry,
} from '../pullSafety';

test('assertSafeCatalogSegment accepts catalog slugs', () => {
    for (const value of ['block_f_simple', 'more-domains.v2', 'task1']) {
        assert.doesNotThrow(() => assertSafeCatalogSegment(value, 'slug'));
    }
});

test('assertSafeCatalogSegment rejects traversal, devices, and metacharacters', () => {
    for (const value of [
        '', '.', '..', '../tasks', '..\\tasks', '.hidden', 'trailing.', 'CON', 'prn.txt',
        'AUX', 'nul', 'COM1', 'lpt9', 'slug space', 'slug$bad', 'slug;bad', 'slug|bad',
    ]) {
        assert.throws(() => assertSafeCatalogSegment(value, 'slug'));
    }
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

test('decideTextFile returns create for a missing file', () => {
    assert.equal(decideTextFile(undefined, 'incoming'), 'create');
});

test('decideTextFile treats CRLF and LF as equal', () => {
    assert.equal(decideTextFile('one\r\ntwo\r\n', 'one\ntwo\n'), 'unchanged');
});

test('decideTextFile detects semantic whitespace changes', () => {
    assert.equal(decideTextFile('one\ntwo', 'one\n two'), 'conflict');
    assert.equal(decideTextFile('one\ntwo', 'one\ntwo\n'), 'conflict');
});

test('mergeManifestEntries preserves existing tasks when incoming is a subset', () => {
    const oldTask = entry('old-task');
    const currentTask = entry('current-task');

    assert.deepEqual(
        mergeManifestEntries([oldTask, currentTask], [entry('current-task', { version: '2.0.0' })]),
        [entry('current-task', { version: '2.0.0' }), oldTask].sort((a, b) =>
            a.id.localeCompare(b.id)
        )
    );
});

test('mergeManifestEntries updates server metadata while preserving local flags', () => {
    const existing = entry('task-a', { md_modified: true, stub_modified: false });
    const incoming = entry('TASK-A', {
        block: 'block-b',
        version: '2.0.0',
        content_hash: 'new-hash',
        pulled_at: '2026-02-01T00:00:00.000Z',
        md_path: 'tasks/new-path.md',
    });

    assert.deepEqual(mergeManifestEntries([existing], [incoming]), [
        { ...incoming, md_modified: true, stub_modified: false },
    ]);
});

test('mergeManifestEntries lets explicit incoming flags override local flags', () => {
    const existing = entry('task-a', { md_modified: true, stub_modified: false });
    const incoming = entry('task-a', { md_modified: false, stub_modified: true });

    assert.deepEqual(mergeManifestEntries([existing], [incoming]), [incoming]);
});

test('mergeManifestEntries matches ids case-insensitively', () => {
    const existing = entry('Task-A', { md_modified: true });
    const incoming = entry('task-a', { version: '3.0.0' });

    assert.deepEqual(mergeManifestEntries([existing], [incoming]), [
        { ...incoming, md_modified: true },
    ]);
});

test('mergeManifestEntries sorts deterministically and does not mutate inputs', () => {
    const existing = [entry('z-task'), entry('A-task')];
    const incoming = [entry('m-task'), entry('a-task', { version: '2.0.0' })];
    const existingBefore = existing.map((item) => ({ ...item }));
    const incomingBefore = incoming.map((item) => ({ ...item }));

    const merged = mergeManifestEntries(existing, incoming);

    assert.deepEqual(merged.map((item) => item.id), ['a-task', 'm-task', 'z-task']);
    assert.deepEqual(existing, existingBefore);
    assert.deepEqual(incoming, incomingBefore);
    assert.notEqual(merged[0], incoming[1]);
});
