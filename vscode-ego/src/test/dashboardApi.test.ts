import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { EgoApi, EgoApiError, catalogFieldsOf } from '../api';

const originalFetch = globalThis.fetch;

afterEach(() => {
    globalThis.fetch = originalFetch;
});

function mockFetch(status: number, body: unknown): { calls: string[] } {
    const calls: string[] = [];
    globalThis.fetch = (async (url: string | URL) => {
        calls.push(String(url));
        return {
            ok: status >= 200 && status < 300,
            status,
            json: async () => body,
        };
    }) as unknown as typeof fetch;
    return { calls };
}

test('getMyUnderstanding calls GET /progress/me/understanding', async () => {
    const { calls } = mockFetch(200, [{ task_id: 'V1', understanding: 'pending' }]);
    const rows = await new EgoApi('http://ego.test').getMyUnderstanding();
    assert.deepEqual(calls, ['http://ego.test/progress/me/understanding']);
    assert.equal(rows[0].task_id, 'V1');
});

test('getAiMe calls GET /ai/me and returns the account contract', async () => {
    const account = {
        student_id: 's1', enabled: true, defense_required: true, available: true,
        reason: 'available', balance_usd: '1.50', reserved_usd: '0', spent_usd: '0.10',
    };
    const { calls } = mockFetch(200, account);
    assert.deepEqual(await new EgoApi('http://ego.test').getAiMe(), account);
    assert.deepEqual(calls, ['http://ego.test/ai/me']);
});

test('getMyProgress calls GET /progress/me', async () => {
    const { calls } = mockFetch(200, []);
    await new EgoApi('http://ego.test').getMyProgress();
    assert.deepEqual(calls, ['http://ego.test/progress/me']);
});

test('old servers: 404 on understanding and lessons surfaces as EgoApiError', async () => {
    mockFetch(404, { detail: 'Not Found' });
    await assert.rejects(
        new EgoApi('http://ego.test').getMyUnderstanding(),
        (error: unknown) => error instanceof EgoApiError && error.status === 404
    );
    // Old servers without /lessons: no theory cards, not an error.
    assert.deepEqual(await new EgoApi('http://ego.test').listLessons(), []);
});

test('listLessons encodes the folder filter', async () => {
    const { calls } = mockFetch(200, []);
    await new EgoApi('http://ego.test/').listLessons('p1/f 2');
    assert.deepEqual(calls, ['http://ego.test/lessons?folder_id=p1%2Ff%202']);
});

test('catalogFieldsOf fills missing catalog fields for old servers', () => {
    const old = { id: 'V1', block: 'A', slug: 's', task_id: 'V1', title: 't', level: 'l', tags: [], version: '1', content_hash: 'h', breaking: false, md_path: 'm' };
    assert.deepEqual(catalogFieldsOf(old), {
        project_id: null, project_name: null, project_order: 0,
        folder_id: null, folder_name: null, folder_order: 0, theory: [],
    });
    assert.deepEqual(
        catalogFieldsOf({ ...old, project_id: 'p1', theory: ['roles-accumulator'] }),
        {
            project_id: 'p1', project_name: null, project_order: 0,
            folder_id: null, folder_name: null, folder_order: 0, theory: ['roles-accumulator'],
        }
    );
});
