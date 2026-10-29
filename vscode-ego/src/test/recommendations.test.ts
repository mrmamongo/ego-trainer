import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { Breakdown, ProjectInfo, Readiness } from '../api';
import {
    KIND_TAGS,
    breakdownRows,
    hasBreakdown,
    indexProjects,
    readinessLine,
    recommendationTooltip,
    unmetRecommendations,
} from '../recommendations';

function project(over: { id: string; name?: string; order?: number; recommended_after?: ProjectInfo['recommended_after']; readiness?: ProjectInfo['readiness'] }): ProjectInfo {
    return {
        id: over.id,
        name: over.name ?? over.id,
        order: over.order ?? 0,
        recommended_after: over.recommended_after ?? null,
        readiness: over.readiness ?? null,
    };
}

const rec = { project: 'xl-a', min_passed: 21, min_per_kind: null, note: 'Курс ООП рекомендуем начинать после экзамена XL-A' };

const names = (id: string) => (id === 'xl-a' ? 'XL-A' : id === 'oop' ? 'ООП' : undefined);

// === Readiness line ===

test('readinessLine is null without a recommendation or once it is met', () => {
    assert.equal(readinessLine(null), null);
    assert.equal(readinessLine(undefined), null);
    assert.equal(readinessLine(project({ id: 'plain' })), null);
    assert.equal(
        readinessLine(project({ id: 'oop', recommended_after: rec, readiness: { met: true, passed: 21, required: 21, per_kind: {} } })),
        null
    );
    // A recommendation without readiness data (old payload) is not rendered.
    assert.equal(readinessLine(project({ id: 'oop', recommended_after: rec })), null);
});

test('readinessLine renders «рекомендуем после XL-A: 14/21»', () => {
    const row = project({
        id: 'oop',
        recommended_after: rec,
        readiness: { met: false, passed: 14, required: 21, per_kind: {} },
    });
    assert.equal(readinessLine(row, names), 'рекомендуем после XL-A: 14/21');
    // Unknown prerequisite name falls back to the id.
    assert.equal(readinessLine(row), 'рекомендуем после xl-a: 14/21');
});

test('readinessLine appends per-kind counts when min_per_kind is set', () => {
    const row = project({
        id: 'oop',
        recommended_after: { ...rec, min_passed: 12, min_per_kind: 3 },
        readiness: { met: false, passed: 12, required: 12, per_kind: { bug: 3, modify: 2, new: 0 } },
    });
    assert.equal(
        readinessLine(row, names),
        'рекомендуем после XL-A: 12/12 · 3/3 баги, 2/3 доработки, 0/3 новое'
    );
});

test('readinessLine survives a partial readiness row from an older server', () => {
    // No counts and no per_kind: the line still renders, with «?» instead of NaN.
    const bare = project({
        id: 'oop',
        recommended_after: { ...rec, min_passed: 12, min_per_kind: 3 },
        readiness: { met: false, per_kind: null as unknown as Record<string, number> } as unknown as Readiness,
    });
    assert.equal(readinessLine(bare, names), 'рекомендуем после XL-A: ?/?');
    assert.match(recommendationTooltip(bare, names) ?? '', /Пройдено задач «XL-A»: \? из \?\./);
    // Times passed but kinds not counted: the per-kind part is omitted.
    const noKinds = project({
        id: 'oop',
        recommended_after: { ...rec, min_per_kind: 3 },
        readiness: { met: false, passed: 4, required: 12, per_kind: {} },
    });
    assert.equal(readinessLine(noKinds, names), 'рекомендуем после XL-A: 4/12');
});

// === Tooltip ===

test('recommendationTooltip carries the author note and the numbers', () => {
    const row = project({
        id: 'oop',
        recommended_after: { ...rec, min_passed: 12, min_per_kind: 3 },
        readiness: { met: false, passed: 10, required: 12, per_kind: { bug: 3, modify: 1, new: 0 } },
    });
    const tooltip = recommendationTooltip(row, names);
    assert.ok(tooltip);
    assert.ok(tooltip.startsWith('Курс ООП рекомендуем начинать после экзамена XL-A'));
    assert.match(tooltip, /Пройдено задач «XL-A»: 10 из 12\./);
    assert.match(tooltip, /баги 3\/3, доработки 1\/3, новое 0\/3/);
    assert.match(tooltip, /Это рекомендация — можно начинать в любой момент\./);
});

test('recommendationTooltip is null when met, absent or note-free numbers only', () => {
    assert.equal(recommendationTooltip(null), null);
    assert.equal(recommendationTooltip(project({ id: 'plain' })), null);
    assert.equal(
        recommendationTooltip(project({ id: 'k', recommended_after: rec, readiness: { met: true, passed: 21, required: 21, per_kind: {} } })),
        null
    );
    const noNote = project({
        id: 'k',
        recommended_after: { ...rec, note: '' },
        readiness: { met: false, passed: 1, required: 21, per_kind: {} },
    });
    assert.match(recommendationTooltip(noNote, names) ?? '', /^Пройдено задач «XL-A»: 1 из 21\./);
});

// === Project index ===

test('indexProjects and unmetRecommendations tolerate missing data', () => {
    assert.equal(indexProjects(null).size, 0);
    assert.equal(indexProjects(undefined).size, 0);
    assert.deepEqual(unmetRecommendations(undefined), []);
    const map = indexProjects([project({ id: 'a' }), project({ id: 'b' })]);
    assert.deepEqual([...map.keys()], ['a', 'b']);
});

test('unmetRecommendations keeps declared-and-unmet projects in catalog order', () => {
    const list = [
        project({ id: 'oop', order: 2, recommended_after: rec, readiness: { met: false, passed: 1, required: 21, per_kind: {} } }),
        project({ id: 'plain', order: 3 }),
        project({ id: 'meta', order: 1, recommended_after: { ...rec, project: 'python-start' }, readiness: { met: false, passed: 0, required: 5, per_kind: {} } }),
        project({ id: 'done', order: 0, recommended_after: rec, readiness: { met: true, passed: 21, required: 21, per_kind: {} } }),
    ];
    assert.deepEqual(unmetRecommendations(list).map((p) => p.id), ['meta', 'oop']);
});

// === Breakdown ===

const breakdown: Breakdown = {
    project: 'xl-a',
    kinds: { bug: { passed: 3, total: 9 }, modify: { passed: 1, total: 9 }, new: { passed: 0, total: 9 } },
    tags: { 'chat-context': { passed: 2, total: 9 } },
};

test('breakdownRows lists bug / modify / new with labels and percents', () => {
    assert.deepEqual(KIND_TAGS, ['bug', 'modify', 'new']);
    const rows = breakdownRows(breakdown);
    assert.deepEqual(rows.map((r) => [r.key, r.label, r.passed, r.total, r.percent]), [
        ['bug', 'Баги', 3, 9, 33],
        ['modify', 'Доработки', 1, 9, 11],
        ['new', 'Новое', 0, 9, 0],
    ]);
});

test('breakdownRows fills missing kinds and hasBreakdown detects useful data', () => {
    assert.deepEqual(breakdownRows({ project: null, kinds: {}, tags: {} }).map((r) => r.total), [0, 0, 0]);
    assert.deepEqual(breakdownRows(null).map((r) => r.passed), [0, 0, 0]);
    assert.equal(hasBreakdown(breakdown), true);
    assert.equal(hasBreakdown({ project: null, kinds: { bug: { passed: 0, total: 0 } }, tags: {} }), false);
    assert.equal(hasBreakdown(null), false);
});
