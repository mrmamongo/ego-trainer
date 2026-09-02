import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseRunSummary, sortRecentRuns, type TaskRunSummary } from '../runHistory';

const base = {
    id: 'run-1',
    started_at: '2026-01-01T10:00:00.000Z',
    finished_at: '2026-01-01T10:01:00.000Z',
    status: 'passed',
    passed_tests: 2,
    total_tests: 2,
};

test('parseRunSummary accepts timestamps and falls back either way', () => {
    assert.deepEqual(parseRunSummary({ ...base, finished_at: undefined }), {
        ...base,
        finished_at: base.started_at,
    });
    assert.deepEqual(parseRunSummary({ ...base, started_at: undefined }), {
        ...base,
        started_at: base.finished_at,
    });
});

test('parseRunSummary rejects malformed required and numeric fields', () => {
    for (const raw of [
        null,
        { ...base, id: 1 },
        { ...base, status: '' },
        { ...base, started_at: 'not-a-date' },
        { ...base, passed_tests: Number.NaN },
        { ...base, total_tests: -1 },
    ]) {
        assert.equal(parseRunSummary(raw), undefined);
    }
});

test('sortRecentRuns sorts by timestamp, breaks ties by id, limits, and does not mutate', () => {
    const runs = ['b', 'a', 'c'].map((id) => ({
        ...base,
        id,
        started_at: id === 'c' ? '2026-01-02T10:00:00.000Z' : '2026-01-01T10:00:00.000Z',
        finished_at: id === 'c' ? '2026-01-02T10:01:00.000Z' : '2026-01-01T10:01:00.000Z',
    })) as TaskRunSummary[];
    const original = [...runs];
    assert.deepEqual(sortRecentRuns(runs, 2).map((run) => run.id), ['c', 'a']);
    assert.deepEqual(runs, original);
});
