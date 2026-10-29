import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { EgoApi, EgoApiError } from '../api';
import { groupResultsByStage } from '../challengeWorkspace';

const originalFetch = globalThis.fetch;

afterEach(() => {
    globalThis.fetch = originalFetch;
});

interface Call {
    url: string;
    method?: string;
    body?: unknown;
}

function mockFetch(status: number, body: unknown): { calls: Call[] } {
    const calls: Call[] = [];
    globalThis.fetch = (async (url: string | URL, init?: RequestInit) => {
        calls.push({
            url: String(url),
            method: init?.method,
            body: init?.body ? JSON.parse(String(init.body)) : undefined,
        });
        return {
            ok: status >= 200 && status < 300,
            status,
            json: async () => body,
        };
    }) as unknown as typeof fetch;
    return { calls };
}

const CHALLENGE = {
    id: 'kv_store',
    project_id: 'challenges',
    code: 'kv_store',
    name: 'Своё хранилище ключ-значение',
    description: '',
    order: 1,
    level: null,
    theory: [],
    workspace: { entry: 'main.py', include: ['*.py'], max_files: 20, max_bytes: 200000 },
    stages: [
        { id: 'KV01', title: 'Разбор команды', number: 1, order: 0, level: 'easy', version: '1.0.0',
            status: 'passed', passed_tests: 3, total_tests: 3, current: false },
        { id: 'KV02', title: 'SET/GET', number: 2, order: 1, level: 'easy', version: '1.0.0',
            status: 'new', passed_tests: 0, total_tests: 0, current: true },
    ],
    starter: { 'main.py': 'print("hi")\n' },
};

test('getChallenge calls GET /challenges/<folder_id> and returns stages, workspace and starter', async () => {
    const { calls } = mockFetch(200, CHALLENGE);
    const info = await new EgoApi('http://ego.test/').getChallenge('kv_store');
    assert.deepEqual(calls, [{ url: 'http://ego.test/challenges/kv_store', method: 'GET', body: undefined }]);
    assert.deepEqual(info, CHALLENGE);
    assert.deepEqual(info?.starter, { 'main.py': 'print("hi")\n' });
});

test('getChallenge encodes the folder id and maps a 404 on an old server to null', async () => {
    const { calls } = mockFetch(200, CHALLENGE);
    await new EgoApi('http://ego.test').getChallenge('a b/c');
    assert.deepEqual(calls.map((call) => call.url), ['http://ego.test/challenges/a%20b%2Fc']);
    mockFetch(404, { detail: 'Challenge not found' });
    assert.equal(await new EgoApi('http://ego.test').getChallenge('kv_store'), null);
});

test('getChallenge: other failures still propagate', async () => {
    mockFetch(500, { detail: 'boom' });
    await assert.rejects(
        new EgoApi('http://ego.test').getChallenge('kv_store'),
        (error: unknown) => error instanceof EgoApiError && error.status === 500 && error.path === '/challenges/kv_store'
    );
    mockFetch(401, {});
    await assert.rejects(new EgoApi('http://ego.test').getChallenge('kv_store'), /Нужно войти/);
});

test('checkFiles posts exactly {task_id, files} to POST /check', async () => {
    const body = {
        task_id: 'KV02', version: '1.0.0', status: 'partial', passed_tests: 1, total_tests: 2,
        solution_hash: 'h', log: '...', results: [
            { description: 'parse', passed: true, expected_repr: 'a', actual_repr: 'a', error: null,
                stage: 1, stage_title: 'Разбор команды' },
            { description: 'get', passed: false, expected_repr: '1', actual_repr: '0', error: null,
                stage: 2, stage_title: 'SET/GET' },
        ],
    };
    const { calls } = mockFetch(200, body);
    const files = { 'main.py': 'print(1)\n', 'storage.py': 'STORE = {}\n' };
    const result = await new EgoApi('http://ego.test').checkFiles('KV02', files);
    assert.deepEqual(calls, [{ url: 'http://ego.test/check', method: 'POST', body: { task_id: 'KV02', files } }]);
    assert.equal('student_code' in (calls[0].body as object), false);
    // Result rows keep stage / stage_title, and group by stage for the panel.
    assert.deepEqual(result.results.map((row) => [row.stage, row.stage_title]),
        [[1, 'Разбор команды'], [2, 'SET/GET']]);
    assert.deepEqual(groupResultsByStage(result.results).map((group) => group.stage), [1, 2]);
});

test('checkFiles: a 422 with a Russian message is an EgoApiError', async () => {
    mockFetch(422, { detail: 'files принимаются только для этапа челленджа' });
    await assert.rejects(
        new EgoApi('http://ego.test').checkFiles('KV02', { 'main.py': '' }),
        (error: unknown) => error instanceof EgoApiError && error.status === 422
            && /только для этапа челленджа/.test(error.message)
    );
});

test('check() still sends student_code, not files', async () => {
    const { calls } = mockFetch(200, { results: [] });
    await new EgoApi('http://ego.test').check('F1', 'def task_f1(): ...');
    assert.deepEqual(calls[0].body, { task_id: 'F1', student_code: 'def task_f1(): ...' });
});
