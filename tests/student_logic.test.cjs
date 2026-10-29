const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  aiAccessReasonLabel, breakdownRows, compareCatalogOrder, compareProjectOrder,
  effectiveDefenseRequired, groupCatalog, hasBreakdown, indexProjects, isOpenState,
  naturalCompare, newestEvidenceByTask, percent, pickNextTask, readinessLine, recommendationHint,
  taskState, taskStateLabel, understandingStatusLabel, unmetRecommendations,
} = require('../ego_server/static/student-logic.js');

function task(over) {
  return { block: 'A', title: over.id, version: '1.0.0', ...over };
}
function evidence(over) {
  return { version: '1.0.0', solution_hash: 'h1', understanding: 'confirmed', ...over };
}

test('naturalCompare puts V2 before V10 and keeps dotted ids in order', () => {
  for (const [a, b] of [['V2', 'V10'], ['F1.2', 'F1.10'], ['task_2', 'task_10'], ['A2', 'B1']]) {
    assert.ok(naturalCompare(a, b) < 0, `${a} should sort before ${b}`);
    assert.ok(naturalCompare(b, a) > 0, `${b} should sort after ${a}`);
  }
  assert.equal(naturalCompare('V2', 'V2'), 0);
});

test('catalog order follows project_order, then folder_order, then natural id', () => {
  const tasks = [
    task({ id: 'V10', project_order: 1, folder_order: 0 }),
    task({ id: 'V2', project_order: 1, folder_order: 0 }),
    task({ id: 'V3', project_order: 0, folder_order: 9 }),
    task({ id: 'V1', project_order: 1, folder_order: -1 }),
  ];
  const ordered = [...tasks].sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b)).map((t) => t.id);
  assert.deepEqual(ordered, ['V3', 'V1', 'V2', 'V10']);
});

test('numeric order fields sent as strings still order the catalog', () => {
  const tasks = [task({ id: 'V1', project_order: '10' }), task({ id: 'V2', project_order: '2' }), task({ id: 'V3' })];
  const ordered = [...tasks].sort((a, b) => compareProjectOrder(a, b) || compareCatalogOrder(a, b));
  assert.deepEqual(ordered.map((t) => t.id), ['V3', 'V2', 'V1']);
});

test('next task is the first not-passed task in catalog order', () => {
  const tasks = [task({ id: 'V10', project_order: 1 }), task({ id: 'V2', project_order: 1 }), task({ id: 'V1', project_order: 0 })];
  const states = new Map([['V1', 'passed'], ['V2', 'started'], ['V10', 'new']]);
  assert.equal(pickNextTask(tasks, (t) => states.get(t.id) ?? 'new')?.id, 'V2');
});

test('next task skips nothing but passed and is undefined when everything is passed', () => {
  const tasks = [task({ id: 'V1' }), task({ id: 'V2' })];
  const states = { V1: 'passed', V2: 'defense' };
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
  assert.deepEqual(['passed', 'defense', 'started', 'failed', 'new'].filter(isOpenState), ['defense', 'started', 'failed', 'new']);
});

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
  assert.equal(taskState(t, passed, undefined, false), 'passed');
  assert.equal(taskState(t, passed, undefined, null), 'passed');
});

test('evidence for another version or solution does not confirm the task', () => {
  const t = { id: 'V1', version: '2.0.0' };
  const passed = { task_id: 'V1', version: '2.0.0', status: 'passed', solution_hash: 'h2' };
  assert.equal(taskState(t, passed, evidence({ task_id: 'V1', version: '1.0.0' }), true), 'defense');
  assert.equal(taskState(t, passed, evidence({ task_id: 'V1', solution_hash: 'old' }), true), 'defense');
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

test('groupCatalog groups project → folder and counts passed via the visitor', () => {
  const tasks = [
    task({ id: 'V1', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f2', folder_name: 'Папка 2', folder_order: 2 }),
    task({ id: 'V2', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f1', folder_name: 'Папка 1', folder_order: 1 }),
    task({ id: 'V10', project_id: 'p1', project_name: 'Основы', project_order: 1, folder_id: 'f1', folder_name: 'Папка 1', folder_order: 1 }),
    task({ id: 'V3', project_id: 'p0', project_name: 'Введение', project_order: 0, folder_id: 'g1', folder_name: 'Старт', folder_order: 0 }),
  ];
  const passed = new Set(['V2', 'V3']);
  const { projects, hasProjects } = groupCatalog(tasks, (project, folder, t) => {
    if (passed.has(t.id)) { project.passed++; folder.passed++; }
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
  const { projects, hasProjects } = groupCatalog([task({ id: 'F1', block: 'F' }), task({ id: 'F2', block: 'F' }), task({ id: 'H1', block: 'H' })]);
  assert.equal(hasProjects, false);
  assert.deepEqual(projects.map((p) => p.name), ['Блок F', 'Блок H']);
  assert.equal(projects[0].total, 2);
  assert.equal(projects[0].folders.length, 1);
  assert.equal(projects[0].folders[0].total, 2);
  assert.equal(projects[1].folders[0].total, 1);
});

test('groupCatalog keeps folder-less tasks in one «Без папки» bucket per project', () => {
  const { projects } = groupCatalog([
    task({ id: 'V1', project_id: 'p1', project_name: 'Проект', folder_id: 'f1', folder_name: 'Папка' }),
    task({ id: 'V2', project_id: 'p1', project_name: 'Проект', folder_id: null }),
    task({ id: 'V3', project_id: 'p1', project_name: 'Проект' }),
  ]);
  assert.equal(projects.length, 1);
  assert.equal(projects[0].folders.length, 2);
  assert.deepEqual(projects[0].folders.find((f) => f.id === null)?.tasks.map((t) => t.id), ['V2', 'V3']);
});

test('groupCatalog sorts tasks inside every folder in catalog order', () => {
  const { projects } = groupCatalog([task({ id: 'V10' }), task({ id: 'V2' }), task({ id: 'V1' })]);
  assert.deepEqual(projects[0].folders[0].tasks.map((t) => t.id), ['V1', 'V2', 'V10']);
});

test('taskStateLabel is Russian for every state', () => {
  assert.deepEqual(['passed', 'defense', 'started', 'failed', 'new'].map(taskStateLabel), ['Решена', 'Ждёт защиты понимания', 'В работе', 'Есть ошибки', 'Не начата']);
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

// === Soft recommendations (GET /projects) ===

function project(over) {
  return {
    id: over.id, name: over.name || over.id, order: over.order ?? 0,
    recommended_after: over.recommended_after ?? null, readiness: over.readiness ?? null,
  };
}

function recommendation(over) {
  return { project: 'xl-a', min_passed: 21, min_per_kind: null, note: 'После экзамена XL-A', ...over };
}

test('indexProjects maps rows by id and tolerates a missing list', () => {
  assert.equal(indexProjects(null).size, 0);
  assert.equal(indexProjects({}).size, 0);
  const map = indexProjects([project({ id: 'xl-a' }), project({ id: 'oop' }), null, { name: 'no id' }]);
  assert.deepEqual([...map.keys()], ['xl-a', 'oop']);
});

test('readinessLine is null without a recommendation or once it is met', () => {
  assert.equal(readinessLine(null), null);
  assert.equal(readinessLine(project({ id: 'plain' })), null);
  assert.equal(readinessLine(project({ id: 'oop', recommended_after: recommendation(), readiness: { met: true, passed: 21, required: 21, per_kind: {} } })), null);
});

test('readinessLine renders «рекомендуем после XL-A: 14/21»', () => {
  const row = project({
    id: 'oop',
    recommended_after: recommendation(),
    readiness: { met: false, passed: 14, required: 21, per_kind: {} },
  });
  assert.equal(readinessLine(row), 'рекомендуем после xl-a: 14/21');
  assert.equal(readinessLine(row, (id) => (id === 'xl-a' ? 'XL-A' : id)), 'рекомендуем после XL-A: 14/21');
});

test('readinessLine appends per-kind counts when min_per_kind is set', () => {
  const row = project({
    id: 'oop',
    recommended_after: recommendation({ min_passed: 12, min_per_kind: 3 }),
    readiness: { met: false, passed: 12, required: 12, per_kind: { bug: 3, modify: 2, new: 0 } },
  });
  assert.equal(
    readinessLine(row, () => 'XL-A'),
    'рекомендуем после XL-A: 12/12 · 3/3 баги, 2/3 доработки, 0/3 новое'
  );
});

test('readinessLine survives a partial readiness row from an older server', () => {
  // No counts and no per_kind: «?» instead of NaN, no crash.
  const bare = project({
    id: 'oop',
    recommended_after: recommendation({ min_passed: 12, min_per_kind: 3 }),
    readiness: { met: false, per_kind: null },
  });
  assert.equal(readinessLine(bare, () => 'XL-A'), 'рекомендуем после XL-A: ?/?');
  // Times passed but kinds not counted: the per-kind part is omitted.
  const noKinds = project({
    id: 'oop',
    recommended_after: recommendation({ min_per_kind: 3 }),
    readiness: { met: false, passed: 4, required: 12, per_kind: {} },
  });
  assert.equal(readinessLine(noKinds, () => 'XL-A'), 'рекомендуем после XL-A: 4/12');
});

test('unmetRecommendations keeps only declared-and-unmet, in catalog order', () => {
  const list = [
    project({ id: 'oop', order: 2, recommended_after: recommendation(), readiness: { met: false, passed: 1, required: 21 } }),
    project({ id: 'plain', order: 3 }),
    project({ id: 'meta', order: 1, recommended_after: recommendation({ project: 'python-start' }), readiness: { met: false, passed: 0, required: 5 } }),
    project({ id: 'done', order: 0, recommended_after: recommendation(), readiness: { met: true, passed: 21, required: 21 } }),
  ];
  assert.deepEqual(unmetRecommendations(list).map((p) => p.id), ['meta', 'oop']);
  assert.deepEqual(unmetRecommendations(null), []);
});

test('breakdownRows lists bug/modify/new with percents', () => {
  const rows = breakdownRows({
    kinds: { bug: { passed: 3, total: 9 }, modify: { passed: 1, total: 9 }, new: { passed: 0, total: 9 } },
  });
  assert.deepEqual(rows.map((r) => [r.key, r.label, r.passed, r.total]), [
    ['bug', 'Баги', 3, 9], ['modify', 'Доработки', 1, 9], ['new', 'Новое', 0, 9],
  ]);
  assert.equal(rows[0].percent, 33);
  assert.equal(hasBreakdown({ kinds: { bug: { passed: 0, total: 9 } } }), true);
  assert.equal(hasBreakdown({ kinds: {} }), false);
  assert.equal(hasBreakdown(null), false);
});

test('recommendationHint: note only when met, line plus note when unmet', () => {
  const nameOf = () => 'XL-A';
  const list = [
    project({ id: 'python-start', recommended_after: recommendation(), readiness: { met: false, passed: 10, required: 21, per_kind: {} } }),
    project({ id: 'done', recommended_after: recommendation({ note: '' }), readiness: { met: true, passed: 21, required: 21, per_kind: {} } }),
  ];
  assert.equal(
    recommendationHint('python-start', list, (row) => readinessLine(row, nameOf)),
    'Открыть задачу. Рекомендация: рекомендуем после XL-A: 10/21. После экзамена XL-A. Это совет, а не ограничение.'
  );
  // A note that already ends with punctuation is not double-punctuated.
  assert.equal(
    recommendationHint('done', [project({ id: 'done', recommended_after: recommendation({ note: 'Сначала XL-A!' }) })], () => null),
    'Открыть задачу. Рекомендация «Сначала XL-A!».'
  );
  // Met (no line) → the note alone; it never claims numbers it does not have.
  assert.equal(recommendationHint('done', list, () => null), null);
  assert.equal(recommendationHint('xl-a', list, (row) => readinessLine(row, nameOf)), null);
  assert.equal(recommendationHint(null, list, () => null), null);
  assert.equal(recommendationHint('python-start', null, () => null), null);
});

test('the student page fetches /projects and the XL-A breakdown, degrading silently', () => {
  const source = fs.readFileSync(path.join(__dirname, '..', 'ego_server', 'static', 'student.js'), 'utf8');
  assert.match(source, /request\('\/projects'\)/);
  assert.match(source, /\/progress\/me\/breakdown\?project=/);
  // Optional endpoints go through allSettled: a 404 on an old server hides the card.
  assert.match(source, /Promise\.allSettled\(/);
});