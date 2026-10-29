import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { ChallengeInfo, ChallengeStage, TestResultDTO } from '../api';
import {
    CHALLENGE_DIR, CHALLENGE_FILE, ChallengeLimitError, challengeIdFromTaskId,
    collectChallengeFiles, groupResultsByStage, includeMatches, isValidChallengeId,
    nextStageNumber, orderedStages, parseChallengeMarker, parseStageNav, planStarter,
    serializeChallengeMarker, stageAfter, stageByNumber, stageGroupHeader, stageLine,
    workspaceOf,
} from '../challengeWorkspace';

const WORKSPACE = { entry: 'main.py', include: ['*.py', 'data/*.json'], max_files: 3, max_bytes: 1000 };

function reader(contents: Record<string, string | Uint8Array>) {
    return async (path: string) => {
        const value = contents[path];
        if (value === undefined) throw new Error(`no ${path}`);
        return value;
    };
}

function stage(number: number, status = 'new', extra: Partial<ChallengeStage> = {}): ChallengeStage {
    return {
        id: `KV0${number}`, title: `Stage ${number}`, number, order: number - 1, level: 'easy',
        version: '1.0.0', status, passed_tests: 0, total_tests: 0, current: false, ...extra,
    };
}

function row(stageNumber: number | undefined, passed: boolean, title = ''): TestResultDTO {
    return {
        description: 'case', passed, expected_repr: 'a', actual_repr: 'a', error: null,
        stage: stageNumber, stage_title: title,
    };
}

// === Include / ignore ===

test('include: *.py matches any basename, a path pattern keeps its directory', () => {
    assert.equal(includeMatches('main.py', ['*.py']), true);
    assert.equal(includeMatches('pkg/store.py', ['*.py']), true);
    assert.equal(includeMatches('data/store.json', ['*.py', 'data/*.json']), true);
    assert.equal(includeMatches('pkg/data/store.json', ['data/*.json']), false);
    assert.equal(includeMatches('README.md', ['*.py', 'data/*.json']), false);
    assert.equal(includeMatches('data/a/b.json', ['data/*.json']), false);
});

test('include: ** spans directories and ? is one character', () => {
    assert.equal(includeMatches('src/pkg/m.py', ['src/**/*.py']), true);
    assert.equal(includeMatches('src/m.py', ['src/**/*.py']), true);
    assert.equal(includeMatches('main1.py', ['main?.py']), true);
    assert.equal(includeMatches('main12.py', ['main?.py']), false);
    assert.equal(includeMatches('a+b.py', ['a+b.py']), true);
});

test('collect: hidden dirs, .cogito/, caches and non-included files are skipped', async () => {
    const paths = [
        'main.py', 'pkg/store.py', 'data/store.json', 'notes.md',
        '.git/config', '.env', '.cogito/challenge.json', '__pycache__/x.cpython-311.pyc',
        '.venv/lib/site.py', 'node_modules/pkg/index.js', 'pkg/__pycache__/cached.py',
    ];
    const contents: Record<string, string> = {};
    for (const path of paths) contents[path] = '# ok';
    const { files, decisions } = await collectChallengeFiles({ paths, read: reader(contents), workspace: WORKSPACE });
    assert.deepEqual(Object.keys(files).sort(), ['data/store.json', 'main.py', 'pkg/store.py']);
    const kind = (path: string) => decisions.find((d) => d.path === path)?.kind;
    assert.equal(kind('.git/config'), 'hidden');
    assert.equal(kind('.env'), 'hidden');
    assert.equal(kind('.cogito/challenge.json'), 'reserved');
    assert.equal(kind('__pycache__/x.cpython-311.pyc'), 'reserved');
    assert.equal(kind('.venv/lib/site.py'), 'reserved');
    assert.equal(kind('node_modules/pkg/index.js'), 'reserved');
    assert.equal(kind('pkg/__pycache__/cached.py'), 'reserved');
    assert.equal(kind('notes.md'), 'not-included');
    assert.equal(decisions.length, paths.length);
});

test('collect: Windows-separator paths of a nested scan are not sent', async () => {
    const { files } = await collectChallengeFiles({
        paths: ['main.py', 'pkg\\store.py', '.venv\\lib\\x.py'],
        read: reader({ 'main.py': 'print(1)' }),
        workspace: undefined,
    });
    assert.deepEqual(Object.keys(files), ['main.py']);
});

test('collect: binary files are skipped, unreadable files are skipped', async () => {
    const { files, decisions } = await collectChallengeFiles({
        paths: ['main.py', 'data/store.json', 'missing.py'],
        read: reader({ 'main.py': 'x = 1', 'data/store.json': new Uint8Array([0xff, 0xfe]) }),
        workspace: WORKSPACE,
    });
    assert.deepEqual(Object.keys(files), ['main.py']);
    assert.equal(decisions.find((d) => d.path === 'data/store.json')?.kind, 'binary');
    assert.equal(decisions.find((d) => d.path === 'missing.py')?.kind, 'binary');
    assert.match(decisions.find((d) => d.path === 'missing.py')?.reason ?? '', /не удалось прочитать/);
});

test('collect: max_files throws a Russian error and sends nothing', async () => {
    const contents = { 'a.py': '', 'b.py': '', 'c.py': '', 'd.py': '' };
    await assert.rejects(
        collectChallengeFiles({ paths: Object.keys(contents), read: reader(contents), workspace: WORKSPACE }),
        (error: unknown) => {
            assert.ok(error instanceof ChallengeLimitError);
            assert.match(error.message, /4 файлов — это больше лимита 3/);
            assert.equal(Object.keys(error.decisions).length > 0, true);
            assert.equal(error.decisions.filter((d) => d.kind === 'over-limit').length, 4);
            return true;
        }
    );
});

test('collect: max_bytes counts UTF-8 bytes', async () => {
    const contents = { 'a.py': 'я'.repeat(10), 'b.py': '#'.repeat(10) };  // 20 + 10 bytes
    await assert.rejects(
        collectChallengeFiles({
            paths: Object.keys(contents), read: reader(contents),
            workspace: { ...WORKSPACE, max_bytes: 25 },
        }),
        (error: unknown) => error instanceof ChallengeLimitError && /30 байт — это больше лимита 25/.test(error.message)
    );
});

test('collect: defaults of a missing workspace are *.py / 20 files / 200000 bytes', async () => {
    const { files } = await collectChallengeFiles({
        paths: ['main.py', 'data/store.json'], read: reader({ 'main.py': 'x' }), workspace: undefined,
    });
    assert.deepEqual(Object.keys(files), ['main.py']);
    assert.deepEqual(workspaceOf(undefined), { entry: 'main.py', include: ['*.py'], max_files: 20, max_bytes: 200_000 });
});

// === Starter creation never overwrites ===

test('planStarter: existing files are skipped, missing ones created', () => {
    const plan = planStarter(
        { 'main.py': 'new main', 'commands.py': 'new commands', 'data/store.json': '{}' },
        ['main.py', 'data\\store.json']
    );
    assert.deepEqual(plan.create, { 'commands.py': 'new commands' });
    assert.deepEqual(plan.skipped.sort(), ['data/store.json', 'main.py']);
    assert.deepEqual(plan.rejected, []);
});

test('planStarter: unsafe starter paths are rejected, not written', () => {
    const plan = planStarter(
        { '../escape.py': 'x', '/etc/passwd': 'x', '.cogito/challenge.json': '{}', '__pycache__/a.py': 'x' },
        []
    );
    assert.deepEqual(plan.create, {});
    assert.equal(plan.rejected.length, 4);
    assert.ok(plan.rejected.every((item) => /за папку|абсолютный|запрещён|отправлять нельзя/.test(item.reason)));
});

test('planStarter: a second start writes nothing', () => {
    const starter = { 'main.py': 'v1' };
    const first = planStarter(starter, []);
    assert.deepEqual(first.create, starter);
    const second = planStarter(starter, Object.keys(first.create));
    assert.deepEqual(second.create, {});
    assert.deepEqual(second.skipped, ['main.py']);
});

// === .cogito/challenge.json ===

test('challenge.json round trip keeps id, server and stage', () => {
    const marker = { id: 'kv_store', server: 'https://cogito.example', stage: 2 };
    const text = serializeChallengeMarker(marker);
    assert.equal(JSON.parse(text) && Object.keys(JSON.parse(text)).join(','), 'id,server,stage');
    assert.deepEqual(parseChallengeMarker(text), marker);
    assert.deepEqual(parseChallengeMarker(serializeChallengeMarker(parseChallengeMarker(text)!)), marker);
    assert.equal(CHALLENGE_DIR, '.cogito');
    assert.equal(`${CHALLENGE_DIR}/${CHALLENGE_FILE}`, '.cogito/challenge.json');
});

test('parseChallengeMarker: junk is undefined, missing server/stage get defaults', () => {
    for (const raw of ['', 'not json', '[]', '{"stage": 2}', '{"id": ""}']) {
        assert.equal(parseChallengeMarker(raw), undefined, raw);
    }
    assert.deepEqual(parseChallengeMarker('{"id":"kv"}'), { id: 'kv', server: '', stage: 0 });
    assert.deepEqual(parseChallengeMarker('{"id":"kv","stage":2.9}'), { id: 'kv', server: '', stage: 2 });
});

test('challenge id: a plain folder id becomes a safe path segment', () => {
    for (const id of ['kv_store', 'kv-store', 'kv1']) assert.equal(isValidChallengeId(id), true, id);
    for (const id of ['', '..', '../x', 'a/b', 'a\\b', '_x', 'a'.repeat(65), 42]) {
        assert.equal(isValidChallengeId(id), false, String(id));
    }
    assert.equal(challengeIdFromTaskId('stage_03_set_get'), 'set_get');
    assert.equal(challengeIdFromTaskId('stage_11_save_json'), 'save_json');
    assert.equal(challengeIdFromTaskId('KV01'), undefined);
});

// === Stages: order, next, highlight ===

test('stages are ordered by number and the next unsolved one is highlighted', () => {
    const stages = [stage(3), stage(1, 'passed'), stage(2, 'partial')];
    assert.deepEqual(orderedStages(stages).map((s) => s.number), [1, 2, 3]);
    assert.equal(nextStageNumber(stages), 2);
    assert.equal(stageByNumber(stages, 3)?.number, 3);
    assert.equal(stageByNumber(stages, 9)?.number, 2, 'a stored stage that is gone falls back to next');
    assert.equal(stageAfter(stages, 2)?.number, 3);
    assert.equal(stageAfter(stages, 3), undefined);
});

test('every stage passed: the last stage stays current; empty list starts at 1', () => {
    assert.equal(nextStageNumber([stage(1, 'passed'), stage(2, 'passed')]), 2);
    assert.equal(nextStageNumber([]), 1);
    assert.equal(nextStageNumber(undefined), 1);
    assert.equal(stageByNumber([], 1), undefined);
});

test('stage lines mark the highlighted stage and its status', () => {
    const lines = [stage(1, 'passed'), stage(2, 'new'), stage(3)]
        .map((s) => stageLine(s, s.number === nextStageNumber([stage(1, 'passed'), stage(2, 'new'), stage(3)])));
    assert.match(lines[0], /^✓ 01 · Stage 1 — пройден$/);
    assert.match(lines[1], /^○ 02 · Stage 2 — не начат ▶$/);
    assert.doesNotMatch(lines[2], /▶/);
});

test('results are grouped by stage in order, stage-less rows last', () => {
    const groups = groupResultsByStage([
        row(2, false, 'SET/GET'), row(1, true, 'parse'), row(2, true, 'SET/GET'), row(undefined, true),
    ]);
    assert.deepEqual(groups.map((g) => g.stage), [1, 2, null]);
    assert.equal(groups[1].passed, 1);
    assert.equal(groups[1].total, 2);
    assert.equal(groups[1].passedAll, false);
    assert.equal(groups[0].passedAll, true);
    assert.equal(stageGroupHeader(groups[0]), 'Этап 1: parse — 1/1, пройден');
    assert.equal(stageGroupHeader(groups[1]), 'Этап 2: SET/GET — 1/2, не пройден');
    assert.equal(stageGroupHeader(groups[2]), 'Результаты');
    assert.deepEqual(groupResultsByStage(undefined), []);
});

test('stage panel messages: only challenge.stage with a positive integer stage', () => {
    assert.deepEqual(parseStageNav({ type: 'challenge.stage', challengeId: 'kv', stage: 2 }),
        { type: 'challenge.stage', challengeId: 'kv', stage: 2 });
    assert.deepEqual(parseStageNav({ type: 'challenge.stage', challengeId: 'kv', stage: '3' })?.stage, 3);
    for (const bad of [null, { type: 'challenge.stage', challengeId: 'kv', stage: 0 },
        { type: 'challenge.stage', challengeId: 'kv', stage: 1.5 }, { type: 'other', challengeId: 'kv', stage: 1 },
        { type: 'challenge.stage', stage: 1 }]) {
        assert.equal(parseStageNav(bad), null);
    }
});

test('workspaceOf fills a partial server workspace with the defaults', () => {
    const info: Pick<ChallengeInfo, 'workspace'> = { workspace: { include: ['*.py'], max_files: 5 } as never };
    assert.deepEqual(workspaceOf(info), { entry: 'main.py', include: ['*.py'], max_files: 5, max_bytes: 200_000 });
});
