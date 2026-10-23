import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
    aiAccessReasonLabel,
    compareCatalogOrder,
    compareProjectOrder,
    effectiveDefenseRequired,
    groupCatalog,
    isOpenState,
    naturalCompare,
    newestEvidenceByTask,
    percent,
    pickNextTask,
    taskState,
    taskStateLabel,
    understandingStatusLabel,
    type CatalogTask,
    type TaskState,
    type UnderstandingEvidence,
} from '../dashboardLogic';

interface Task extends CatalogTask {
    title: string;
    version: string;
}

function task(over: Partial<Task> & { id: string }): Task {
    return { block: 'A', title: over.id, version: '1.0.0', ...over };
}

function evidence(over: Partial<UnderstandingEvidence> & { task_id: string }): UnderstandingEvidence {
    return { version: '1.0.0', solution_hash: 'h1', understanding: 'confirmed', ...over };
}

// === Natural order ===

test('naturalCompare puts V2 before V10 and keeps dotted ids in order', () => {
    for (const [a, b] of [
        ['V2', 'V10'],
        ['F1.2', 'F1.10'],
        ['task_2', 'task_10'],
        ['A2', 'B1'],
    ]) {
        assert.ok(naturalCompare(a, b) < 0, `${a} should sort before ${b}`);
        assert.ok(naturalCompare(b, a) > 0, `${b} should sort after ${a}`);
    }
    assert.equal(naturalCompare('V2', 'V2'), 0);
});

// === Catalog order and «Продолжить» ===

test('catalog order follows project_order, then folder_order, then natural id', () => {
    const tasks = [
        task({ id: 'V10', project_order: 1, folder_order: 0 }),
        task({ id: 'V2', project_order: 1, folder_order: 0 }),
        task({ id: 'V3', project_order: 0, folder_order: 9 }),
        task({ id: 'V1', project_order: 1, folder_order: -1 }),
    ];
    const ordered = [...tasks]
        .sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b))
        .map((t) => t.id);
    assert.deepEqual(ordered, ['V3', 'V1', 'V2', 'V10']);
});

test('numeric order fields sent as strings still order the catalog', () => {
    const tasks = [
        task({ id: 'V1', project_order: '10' as unknown as number }),
        task({ id: 'V2', project_order: '2' as unknown as number }),
        task({ id: 'V3' }),
    ];
    const ordered = [...tasks].sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b));
    assert.deepEqual(ordered.map((t) => t.id), ['V3', 'V2', 'V1']);
});

test('next task is the first not-passed task in catalog order', () => {
    const tasks = [
        task({ id: 'V10', project_order: 1 }),
        task({ id: 'V2', project_order: 1 }),
        task({ id: 'V1', project_order: 0 }),
    ];
    // V1 is passed; the catalog order then continues with V2 (not V10).
    const states = new Map<string, TaskState>([
        ['V1', 'passed'],
        ['V2', 'started'],
        ['V10', 'new'],
    ]);
    const next = pickNextTask(tasks, (t) => states.get(t.id) ?? 'new');
    assert.equal(next?.id, 'V2');
});

test('next task skips nothing but passed and is undefined when everything is passed', () => {
    const tasks = [task({ id: 'V1' }), task({ id: 'V2' })];
    const states: Record<string, TaskState> = { V1: 'passed', V2: 'defense' };
    assert.equal(pickNextTask(tasks, (t) => states[t.id] ?? 'new')?.id, 'V2');
    assert.equal(pickNextTask(tasks, () => 'passed'), undefined);
    assert.equal(pickNextTask([], () => 'new'), undefined);
});

test('pickNextTask does not mutate its input', () => {
    const tasks = [task({ id: 'V2' }), task({ id: 'V1' })];
    pickNextTask(tasks, () => 'new');
    assert.deepEqual(tasks.map((t) => t.id), ['V2', 'V1']);
});

test('isOpenState treats everything except passed as open', () => {
    const states: TaskState[] = ['passed', 'defense', 'started', 'failed', 'new'];
    assert.deepEqual(states.filter(isOpenState), ['defense', 'started', 'failed', 'new']);
});

// === Task state ===

test('taskState classifies progress rows', () => {
    const t = { id: 'V1', version: '1.0.0' };
    const row = { task_id: 'V1', version: '1.0.0', status: 'partial' };
    assert.equal(taskState(t, null, null, null), 'new');
    assert.equal(taskState(t, row, null, null), 'started');
    assert.equal(taskState(t, { ...row, status: 'failed' }, null, null), 'failed');
    assert.equal(taskState(t, { ...row, status: 'timeout' }, null, null), 'failed');
    assert.equal(taskState(t, { ...row, status: 'PASSED' }, null, null), 'passed');
});

test('defense_required turns a passed-but-unconfirmed solution into defense', () => {
    const t = { id: 'V1', version: '1.0.0' };
    const passed = { task_id: 'V1', version: '1.0.0', status: 'passed', solution_hash: 'h1' };
    assert.equal(taskState(t, passed, undefined, true), 'defense');
    assert.equal(taskState(t, passed, evidence({ task_id: 'V1', understanding: 'pending' }), true), 'defense');
    assert.equal(taskState(t, passed, evidence({ task_id: 'V1' }), true), 'passed');
    // Not required (or unknown) → no defense claims.
    assert.equal(taskState(t, passed, undefined, false), 'passed');
    assert.equal(taskState(t, passed, undefined, null), 'passed');
});

test('evidence for another version or solution does not confirm the task', () => {
    const t = { id: 'V1', version: '2.0.0' };
    const passed = { task_id: 'V1', version: '2.0.0', status: 'passed', solution_hash: 'h2' };
    assert.equal(taskState(t, passed, evidence({ task_id: 'V1', version: '1.0.0' }), true), 'defense');
    assert.equal(taskState(t, passed, evidence({ task_id: 'V1', solution_hash: 'old' }), true), 'defense');
    // Stale server progress (older version than the current task) is not a pass.
    const stale = { task_id: 'V1', version: '1.0.0', status: 'passed', solution_hash: 'h1' };
    assert.equal(taskState(t, stale, evidence({ task_id: 'V1', version: '1.0.0' }), true), 'defense');
});

test('newestEvidenceByTask keeps the latest row per task', () => {
    const rows = [
        evidence({ task_id: 'V1', understanding: 'pending', created_at: '2026-10-01T00:00:00Z' }),
        evidence({ task_id: 'V1', understanding: 'confirmed', created_at: '2026-10-02T00:00:00Z' }),
        evidence({ task_id: 'V2', understanding: 'needs_review', created_at: '2026-10-03T00:00:00Z' }),
    ];
    const map = newestEvidenceByTask(rows);
    assert.equal(map.get('V1')?.understanding, 'confirmed');
    assert.equal(map.get('V2')?.understanding, 'needs_review');
});

test('effectiveDefenseRequired needs both the server flag and an evidence list', () => {
    assert.equal(effectiveDefenseRequired(true, true), true);
    assert.equal(effectiveDefenseRequired(false, true), null);
    assert.equal(effectiveDefenseRequired(true, false), null);
    assert.equal(effectiveDefenseRequired(null, true), null);
});

// === Grouping ===

test('groupCatalog groups project → folder and counts passed via the visitor', () => {
    const tasks = [
        task({ id: 'V1', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f2', folder_name: 'Папка 2', folder_order: 2 }),
        task({ id: 'V2', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f1', folder_name: 'Папка 1', folder_order: 1 }),
        task({ id: 'V10', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f1', folder_name: 'Папка 1', folder_order: 1 }),
        task({ id: 'V3', project_id: 'p0', project_name: 'Введение', project_order: 0, folder_id: 'g1', folder_name: 'Старт', folder_order: 0 }),
    ];
    const passed = new Set(['V2', 'V3']);
    const { projects, hasProjects } = groupCatalog(tasks, (project, folder, t) => {
        if (passed.has(t.id)) {
            project.passed++;
            folder.passed++;
        }
    });
    assert.equal(hasProjects, true);
    assert.deepEqual(projects.map((p) => p.name), ['Введение', 'Основы']);
    const basics = projects[1];
    assert.equal(basics.total, 3);
    assert.equal(basics.passed, 1);
    assert.deepEqual(basics.folders.map((f) => f.name), ['Папка 1', 'Папка 2']);
    assert.deepEqual(basics.folders[0].tasks.map((t) => t.id), ['V2', 'V10']);
    assert.equal(basics.folders[0].passed, 1);
    assert.equal(basics.folders[0].total, 2);
    assert.equal(basics.folders[1].passed, 0);
    assert.deepEqual(projects[0].folders[0].tasks.map((t) => t.id), ['V3']);
});

test('groupCatalog falls back to block groups when catalog fields are absent', () => {
    const tasks = [task({ id: 'F1', block: 'F' }), task({ id: 'F2', block: 'F' }), task({ id: 'H1', block: 'H' })];
    const { projects, hasProjects } = groupCatalog(tasks);
    assert.equal(hasProjects, false);
    // Equal order: groups are ordered by natural name.
    assert.deepEqual(projects.map((p) => p.name), ['Блок F', 'Блок H']);
    assert.equal(projects[0].total, 2);
    assert.equal(projects[0].folders.length, 1);
    assert.equal(projects[0].folders[0].total, 2);
    assert.equal(projects[1].folders[0].total, 1);
});

test('groupCatalog keeps folder-less tasks in one «Без папки» bucket per project', () => {
    const tasks = [
        task({ id: 'V1', project_id: 'p1', project_name: 'Проект', folder_id: 'f1', folder_name: 'Папка' }),
        task({ id: 'V2', project_id: 'p1', project_name: 'Проект', folder_id: null }),
        task({ id: 'V3', project_id: 'p1', project_name: 'Проект' }),
    ];
    const { projects } = groupCatalog(tasks);
    assert.equal(projects.length, 1);
    assert.equal(projects[0].folders.length, 2);
    const loose = projects[0].folders.find((f) => f.id === null);
    assert.deepEqual(loose?.tasks.map((t) => t.id), ['V2', 'V3']);
});

test('groupCatalog sorts tasks inside every folder in catalog order', () => {
    const { projects } = groupCatalog([task({ id: 'V10' }), task({ id: 'V2' }), task({ id: 'V1' })]);
    assert.deepEqual(projects[0].folders[0].tasks.map((t) => t.id), ['V1', 'V2', 'V10']);
});

// === Labels ===

test('taskStateLabel is Russian for every state', () => {
    assert.deepEqual(
        (['passed', 'defense', 'started', 'failed', 'new'] as TaskState[]).map(taskStateLabel),
        ['Решена', 'Ждёт защиты понимания', 'В работе', 'Есть ошибки', 'Не начата']
    );
});

test('understandingStatusLabel maps server evidence statuses', () => {
    assert.equal(understandingStatusLabel('confirmed'), 'Понимание подтверждено');
    assert.equal(understandingStatusLabel('pending'), 'Защита идёт');
    assert.equal(understandingStatusLabel('active'), 'Защита идёт');
    assert.equal(understandingStatusLabel('needs_review'), 'Нужна проверка наставника');
    assert.equal(understandingStatusLabel(''), 'Ждёт защиты понимания');
    assert.equal(understandingStatusLabel(null), 'Ждёт защиты понимания');
});

test('aiAccessReasonLabel translates known reason codes and keeps sentences', () => {
    assert.equal(aiAccessReasonLabel('available'), 'доступен');
    assert.equal(aiAccessReasonLabel('disabled'), 'доступ не выдан — обратись к наставнику');
    assert.equal(aiAccessReasonLabel('low_balance'), 'бюджет исчерпан');
    assert.equal(aiAccessReasonLabel('Доступ отозван'), 'Доступ отозван');
});

test('percent rounds and guards empty totals', () => {
    assert.equal(percent(1, 3), 33);
    assert.equal(percent(3, 3), 100);
    assert.equal(percent(0, 3), 0);
    assert.equal(percent(0, 0), 0);
    assert.equal(percent(5, 2), 100);
});
