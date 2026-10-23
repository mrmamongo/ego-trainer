import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { LessonFull, LessonMeta, TaskMeta } from '../api';
import {
    buildCatalog, createReadState, lessonKey, resolveTheory, shouldSuggestTheory,
    type MementoLike, type TheoryDeps, type TheoryItem,
} from '../theoryLogic';

function task(id: string, extra: Partial<TaskMeta> = {}): TaskMeta {
    return {
        id, block: 'F', slug: 'block_f', task_id: id, title: id, level: '', tags: [],
        version: '1.0.0', content_hash: 'h', breaking: false, md_path: '', ...extra,
    };
}

function lesson(id: string, extra: Partial<LessonMeta> = {}): LessonMeta {
    return {
        id, project_id: null, folder_id: null, block: 'F', title: id, order: 0,
        version: '1.0.0', content_hash: `hash-${id}`, ...extra,
    };
}

test('old server data falls back to "Блок <block>" folders without a project level', () => {
    const catalog = buildCatalog([task('F2'), task('F1'), task('H1', { block: 'H' })], []);
    assert.equal(catalog.showProjects, false);
    assert.equal(catalog.projects.length, 1);
    const folders = catalog.projects[0].folders;
    assert.deepEqual(folders.map((f) => f.name), ['Блок F', 'Блок H']);
    assert.deepEqual(folders[0].tasks.map((t) => t.task_id), ['F1', 'F2']);
});

test('catalog fields group Project -> Folder and sort by order then name', () => {
    const meta = (id: string, p: string, po: number, f: string, fo: number) => task(id, {
        project_id: p, project_name: p.toUpperCase(), project_order: po,
        folder_id: `${p}-${f}`, folder_name: f, folder_order: fo, block: f,
    });
    const catalog = buildCatalog([
        meta('A1', 'py', 2, 'Zeta', 1), meta('A2', 'py', 2, 'Alpha', 2), meta('A3', 'py', 2, 'Beta', 1),
        meta('B1', 'go', 1, 'Basics', 0),
    ], []);
    assert.equal(catalog.showProjects, true);
    assert.deepEqual(catalog.projects.map((p) => p.name), ['GO', 'PY']);
    assert.deepEqual(catalog.projects[1].folders.map((f) => f.name), ['Beta', 'Zeta', 'Alpha']);
});

test('lessons are attached to their folder and sorted by order then id', () => {
    const tasks = [task('F1', { project_id: 'p', project_name: 'P', folder_id: 'f', folder_name: 'Роли' })];
    const lessons = [
        lesson('b', { project_id: 'p', folder_id: 'f', order: 2 }),
        lesson('a', { project_id: 'p', folder_id: 'f', order: 2 }),
        lesson('c', { project_id: 'p', folder_id: 'f', order: 1 }),
    ];
    const catalog = buildCatalog(tasks, lessons);
    assert.equal(catalog.showProjects, false);
    const [folder] = catalog.projects[0].folders;
    assert.equal(folder.name, 'Роли');
    assert.deepEqual(folder.lessons.map((l) => l.id), ['c', 'a', 'b']);
    assert.equal(folder.tasks.length, 1);
});

test('lesson-only folder uses block fallback name and joins a known project', () => {
    const tasks = [task('F1', { project_id: 'p', project_name: 'Python', folder_id: 'f1', folder_name: 'Один' })];
    const lessons = [lesson('x', { project_id: 'p', folder_id: 'f2', block: 'G' })];
    const catalog = buildCatalog(tasks, lessons);
    assert.equal(catalog.projects.length, 1);
    assert.deepEqual(catalog.projects[0].folders.map((f) => f.name), ['Блок G', 'Один']);
    assert.equal(catalog.projects[0].name, 'Python');
});

test('read-state keys include id and content_hash', () => {
    assert.notEqual(lessonKey('x', 'h1'), lessonKey('x', 'h2'));
    assert.notEqual(lessonKey('x', 'h1'), lessonKey('y', 'h1'));
});

function fakeMemento(): MementoLike & { data: Map<string, unknown> } {
    const data = new Map<string, unknown>();
    return {
        data,
        get: <T>(key: string, def: T) => (data.has(key) ? data.get(key) as T : def),
        update: async (key, value) => { if (value === undefined) data.delete(key); else data.set(key, value); },
    };
}

test('read state toggles per version, notifies listeners and cleans up on unread', async () => {
    const memento = fakeMemento();
    const state = createReadState(memento);
    let changes = 0;
    const off = state.onDidChange(() => { changes++; });
    assert.equal(state.isRead('x', 'h1'), false);
    await state.setRead('x', 'h1', true);
    assert.equal(state.isRead('x', 'h1'), true);
    assert.equal(state.isRead('x', 'h2'), false, 'new content_hash is unread again');
    await state.setRead('x', 'h1', false);
    assert.equal(state.isRead('x', 'h1'), false);
    assert.equal(memento.data.size, 0);
    assert.equal(changes, 2);
    off();
    await state.setRead('x', 'h1', true);
    assert.equal(changes, 2);
});

function theoryDeps(hashes: Record<string, string>, calls: string[]): TheoryDeps {
    return {
        listLessons: async () => Object.entries(hashes).map(([id, content_hash]) => lesson(id, { content_hash })),
        getLesson: async (id): Promise<LessonFull> => {
            calls.push(id);
            if (!(id in hashes)) throw new Error('404');
            return { ...lesson(id, { content_hash: hashes[id], title: `T-${id}` }), body_md: `# ${id}` };
        },
        render: (md) => `<p>${md}</p>`,
    };
}

test('resolveTheory keeps task order, caches by content_hash and refetches on change', async () => {
    const cache = new Map<string, TheoryItem>();
    const calls: string[] = [];
    let items = await resolveTheory(['b', 'a'], theoryDeps({ a: '1', b: '1' }, calls), cache);
    assert.deepEqual(items.map((i) => i.id), ['b', 'a']);
    assert.equal(items[0].html, '<p># b</p>');
    assert.deepEqual(calls, ['b', 'a']);

    items = await resolveTheory(['b', 'a'], theoryDeps({ a: '1', b: '1' }, calls), cache);
    assert.equal(items.length, 2);
    assert.deepEqual(calls, ['b', 'a'], 'served from cache');

    await resolveTheory(['b', 'a'], theoryDeps({ a: '2', b: '1' }, calls), cache);
    assert.deepEqual(calls, ['b', 'a', 'a'], 'only the changed lesson is refetched');
});

test('resolveTheory skips unavailable lessons and survives a failing lesson list', async () => {
    const calls: string[] = [];
    const deps = theoryDeps({ a: '1' }, calls);
    const items = await resolveTheory(['missing', 'a'], { ...deps, listLessons: async () => { throw new Error('boom'); } }, new Map());
    assert.deepEqual(items.map((i) => i.id), ['a']);
    assert.deepEqual(await resolveTheory([], deps, new Map()), []);
});

test('shouldSuggestTheory only after a not-fully-passed check with theory', () => {
    const theory = [{ id: 'a' }];
    assert.equal(shouldSuggestTheory({ status: 'partial' }, theory), true);
    assert.equal(shouldSuggestTheory({ status: 'failed' }, theory), true);
    assert.equal(shouldSuggestTheory({ status: 'passed' }, theory), false);
    assert.equal(shouldSuggestTheory({ status: 'no_tests' }, theory), false);
    assert.equal(shouldSuggestTheory({ status: 'failed' }, []), false);
    assert.equal(shouldSuggestTheory(null, theory), false);
});
