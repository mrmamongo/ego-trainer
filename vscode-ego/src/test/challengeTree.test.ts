import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { ChallengeInfo, ChallengeStage, TaskMeta } from '../api';
import { buildCatalog } from '../theoryLogic';
import {
    challengeViewInfo, nextStageNumber, orderedStages, stageLine, stageStatusLabel,
} from '../challengeWorkspace';

function task(id: string, extra: Partial<TaskMeta> = {}): TaskMeta {
    return {
        id, block: 'kv_store', slug: 'kv_store', task_id: id, title: `stage ${id}`, level: '', tags: [],
        version: '1.0.0', content_hash: 'h', breaking: false, md_path: '', ...extra,
    };
}

function stage(number: number, status: string, extra: Partial<ChallengeStage> = {}): ChallengeStage {
    return {
        id: `KV0${number}`, title: `Этап ${number}`, number, order: number - 1, level: 'easy',
        version: '1.0.0', status, passed_tests: 0, total_tests: 0, current: false, ...extra,
    };
}

function challenge(stages: ChallengeStage[]): ChallengeInfo {
    return {
        id: 'kv_store', project_id: 'challenges', code: 'kv_store', name: 'KV', description: '',
        order: 1, level: null, theory: [],
        workspace: { entry: 'main.py', include: ['*.py'], max_files: 20, max_bytes: 200000 },
        stages, starter: {},
    };
}

/** Tasks in the order the catalog gives them (block, then stage order). */
function treeStages(stages: ChallengeStage[]): Array<{ task_id: string; number: number; highlighted: boolean; label: string }> {
    const tasks = stages.map((item) => task(item.id, {
        project_id: 'challenges', project_name: 'Challenges', folder_id: 'kv_store',
        folder_name: 'KV', challenge_stage: item.number,
    }));
    const catalog = buildCatalog([task('A1', { block: 'A' }), ...tasks], []);
    // Several projects: with one project alone it would not be named.
    assert.equal(catalog.showProjects, true);
    const project = catalog.projects.find((item) => item.key === 'challenges')!;
    const folder = project.folders.find((item) => item.key === 'challenges/id:kv_store')!;
    assert.equal(folder.challenge, true);
    const ordered = orderedStages(stages);
    const next = nextStageNumber(ordered);
    return folder.tasks.map((item) => {
        const info = ordered.find((candidate) => candidate.id === item.task_id)!;
        return {
            task_id: item.task_id,
            number: info.number,
            highlighted: info.number === next && info.status !== 'passed',
            label: stageLine(info, info.number === next),
        };
    });
}

test('challenge folder: stages in stage order, the next unsolved stage highlighted', () => {
    const rows = treeStages([
        stage(3, 'new'), stage(1, 'passed'), stage(4, 'new'), stage(2, 'failed'),
    ]);
    assert.deepEqual(rows.map((row) => row.task_id), ['KV01', 'KV02', 'KV03', 'KV04']);
    assert.deepEqual(rows.map((row) => row.highlighted), [false, true, false, false]);
    assert.match(rows[1].label, /^○ 02 · Этап 2 — не пройден ▶$/);
    assert.match(rows[0].label, /^✓ 01 · Этап 1 — пройден$/);
});

test('challenge folder: every stage passed — the last one is current, nothing else lit', () => {
    const rows = treeStages([stage(1, 'passed'), stage(2, 'passed'), stage(3, 'passed')]);
    assert.deepEqual(rows.map((row) => row.highlighted), [false, false, false]);
    assert.equal(nextStageNumber(rows.map((row) => stage(row.number, 'passed'))), 3);
});

test('an ordinary folder is not a challenge even with one staged task', () => {
    const catalog = buildCatalog([
        task('F1', { block: 'F', project_id: 'py', folder_id: 'f1' }),
        task('KV01', { block: 'kv_store', project_id: 'challenges', folder_id: 'kv', challenge_stage: 1 }),
    ], []);
    const folder = catalog.projects.find((project) => project.key === 'py')!.folders[0];
    assert.equal(folder.challenge, false);
    const challengeFolder = catalog.projects.find((project) => project.key === 'challenges')!.folders[0];
    assert.equal(challengeFolder.challenge, true);
});

test('an old server (no challenge_stage) keeps the plain task list', () => {
    const catalog = buildCatalog([task('F2', { block: 'F' }), task('F10', { block: 'F' })], []);
    const folder = catalog.projects[0].folders[0];
    assert.equal(folder.challenge, false);
    assert.deepEqual(folder.tasks.map((item) => item.task_id), ['F10', 'F2']);
});

test('stage panel data: statuses with Russian labels, stage on screen, next stage', () => {
    const info = challengeViewInfo(challenge([stage(2, 'partial'), stage(1, 'passed'), stage(3, 'new')]), 2, 'challenges/kv_store');
    assert.equal(info.challenge_id, 'kv_store');
    assert.equal(info.stage, 2);
    assert.equal(info.current_stage, 2);
    assert.equal(info.folder, 'challenges/kv_store');
    assert.equal(info.entry, 'main.py');
    assert.deepEqual(info.stages.map((item) => [item.number, item.status_label]),
        [[1, 'пройден'], [2, 'частично'], [3, 'не начат']]);
    assert.equal(stageStatusLabel('timeout'), 'таймаут');
});
