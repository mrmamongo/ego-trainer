import { test } from 'node:test';
import assert from 'node:assert/strict';
// dashboardLoader imports `vscode` (workspace file helpers). The pure builders
// below never touch it, so a minimal stub keeps the module loadable under node.
const Module = require('node:module') as typeof import('node:module') & {
    _load: (request: string, parent: unknown, isMain: boolean) => unknown;
};
const originalLoad = Module._load;
Module._load = function (request: string, parent: unknown, isMain: boolean) {
    if (request === 'vscode') return { workspace: {}, Uri: {} };
    return originalLoad.call(this, request, parent, isMain);
};
const {
    buildBreakdownCard,
    buildCabinet,
    buildRecommendationCards,
} = require('../dashboardLoader') as typeof import('../dashboardLoader');
Module._load = originalLoad;

import type { Breakdown, ProjectInfo, TaskMetaWithCatalog } from '../api';

function task(over: Partial<TaskMetaWithCatalog> & { id: string }): TaskMetaWithCatalog {
    return {
        block: 'X',
        slug: 'xl_a',
        task_id: over.id,
        title: over.id,
        level: 'medium',
        tags: [],
        version: '1.0.0',
        content_hash: 'h',
        breaking: false,
        md_path: `tasks/${over.id}.md`,
        ...over,
    };
}

const tasks: TaskMetaWithCatalog[] = [
    task({ id: 'XL-A01', project_id: 'xl-a', project_name: 'XL-A', project_order: 1, folder_id: 'xl_a', tags: ['bug'] }),
    task({ id: 'XL-A02', project_id: 'xl-a', project_name: 'XL-A', project_order: 1, folder_id: 'xl_a', tags: ['modify'] }),
    task({ id: 'OOP1', project_id: 'oop', project_name: 'ООП', project_order: 2, folder_id: 'oop', tags: ['classes'] }),
];

const projects: ProjectInfo[] = [
    { id: 'xl-a', name: 'XL-A', order: 1, recommended_after: null, readiness: null },
    {
        id: 'oop',
        name: 'ООП',
        order: 2,
        recommended_after: { project: 'xl-a', min_passed: 2, min_per_kind: 1, note: 'Начни после экзамена' },
        readiness: { met: false, passed: 1, required: 2, per_kind: { bug: 1, modify: 0, new: 0 } },
    },
];

const breakdown: Breakdown = {
    project: 'xl-a',
    kinds: { bug: { passed: 1, total: 1 }, modify: { passed: 0, total: 1 }, new: { passed: 0, total: 0 } },
    tags: {},
};

test('buildRecommendationCards renders the unmet readiness line and per-kind counts', () => {
    const cabinet = buildCabinet({
        tasks, progress: [], evidence: null, account: null, mode: 'server', projectInfo: projects, breakdown,
    });
    const cards = cabinet.cabinet.recommendation_cards;
    assert.deepEqual(cards.map((c) => c.id), ['xl-a', 'oop']);
    assert.equal(cards[0].unmet, false);
    assert.equal(cards[0].readiness_label, null);
    assert.equal(cards[1].unmet, true);
    // The prerequisite name comes from the /projects list, not the raw id.\n    assert.equal(\n        cards[1].readiness_label,\n        'рекомендуем после XL-A: 1/2 · 1/1 баги, 0/1 доработки, 0/1 новое'\n    );
    assert.equal(cards[1].per_kind_label, 'баги 1/1, доработки 0/1, новое 0/1');
    assert.equal(cards[1].note, 'Начни после экзамена');
    assert.equal(cards[1].progress_label, '0/1 решено');
});

test('buildRecommendationCards is empty when the server has no /projects', () => {
    assert.deepEqual(buildRecommendationCards(null, []), []);
    assert.deepEqual(buildRecommendationCards([], []), []);
});

test('buildBreakdownCard fills label and project name, null when empty', () => {
    const card = buildBreakdownCard(breakdown, projects, []);
    assert.ok(card);
    assert.equal(card.project_id, 'xl-a');
    assert.equal(card.project_name, 'XL-A');
    assert.deepEqual(card.rows.map((r) => [r.key, r.passed, r.total]), [['bug', 1, 1], ['modify', 0, 1], ['new', 0, 0]]);
    assert.equal(buildBreakdownCard(null, projects, []), null);
    assert.equal(buildBreakdownCard({ project: 'x', kinds: {}, tags: {} }, projects, []), null);
});

test('buildCabinet without recommendations keeps the cabinet contract', () => {
    const cabinet = buildCabinet({ tasks, progress: [], evidence: null, account: null, mode: 'server' });
    assert.deepEqual(cabinet.cabinet.recommendation_cards, []);
    assert.equal(cabinet.cabinet.breakdown, null);
});
