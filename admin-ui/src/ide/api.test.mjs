import assert from 'node:assert/strict';
import test from 'node:test';
import { createIdeApi, IDE_TOKEN_KEY, IDE_SESSION_EXPIRED_EVENT } from './apiCore.js';

/** Storage stub backed by a Map (the localStorage surface apiCore relies on). */
function makeStorage(initial = {}) {
  const map = new Map(Object.entries(initial));
  return {
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => map.set(String(k), String(v)),
    removeItem: (k) => map.delete(k),
    _map: map,
  };
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

/** fetch stub: records every call, returns queued responses in order. */
function makeFetch(...responses) {
  const queue = [...responses];
  const calls = [];
  const fetchFn = (url, init) => {
    calls.push({ url, init });
    const next = queue.shift();
    if (next === undefined) throw new Error('unexpected fetch call');
    return typeof next === 'function' ? next() : Promise.resolve(next);
  };
  fetchFn.calls = calls;
  return fetchFn;
}

function makeApi({ responses = [], storage = makeStorage(), withEvents = true } = {}) {
  const fetchFn = makeFetch(...responses);
  const events = [];
  const eventTarget = withEvents ? {
    dispatchEvent: (event) => events.push(event.type),
  } : null;
  const api = createIdeApi('http://api.test', storage, fetchFn, eventTarget);
  return { api, fetchFn, storage, events };
}

test('IDE token storage uses the dedicated ego_ide_token key', () => {
  const { api, storage } = makeApi();
  assert.equal(storage.getItem(IDE_TOKEN_KEY), null);
  api.setToken('tok-1');
  assert.equal(api.getToken(), 'tok-1');
  assert.equal(storage._map.get(IDE_TOKEN_KEY), 'tok-1');
  api.clearToken();
  assert.equal(api.getToken(), null);
  assert.equal(storage._map.has(IDE_TOKEN_KEY), false);
});

test('getToken falls back to a token persisted in storage', () => {
  const { api } = makeApi({ storage: makeStorage({ [IDE_TOKEN_KEY]: 'persisted' }) });
  assert.equal(api.getToken(), 'persisted');
});

test('login posts credentials, stores the access token, and sends it as Bearer afterwards', async () => {
  const { api, fetchFn, storage } = makeApi({
    responses: [
      jsonResponse({ access_token: 'jwt-1', token_type: 'bearer', role: 'student', username: 'anna', user_id: 'u1' }),
      jsonResponse({ user_id: 'u1', username: 'anna', role: 'student' }),
    ],
  });

  const login = await api.login('anna', 'secret');
  assert.equal(login.access_token, 'jwt-1');
  assert.equal(fetchFn.calls[0].url, 'http://api.test/auth/login');
  assert.equal(fetchFn.calls[0].init.method, 'POST');
  assert.deepEqual(JSON.parse(fetchFn.calls[0].init.body), { username: 'anna', password: 'secret' });
  assert.equal(fetchFn.calls[0].init.headers.Authorization, undefined);
  assert.equal(storage._map.get(IDE_TOKEN_KEY), 'jwt-1');

  await api.me();
  assert.equal(fetchFn.calls[1].url, 'http://api.test/auth/me');
  assert.equal(fetchFn.calls[1].init.headers.Authorization, 'Bearer jwt-1');
});

test('listTasks and getTask hit the task endpoints and parse JSON', async () => {
  const meta = { id: '1', block: 'F', slug: 'sum', task_id: 'F1', title: 'Sum', level: 'basic',
    tags: ['loops'], version: '1.0.0', content_hash: 'abc', breaking: false, md_path: 'F1.md' };
  const { api, fetchFn } = makeApi({
    responses: [jsonResponse([meta]), jsonResponse({ ...meta, statement_md: '# s', stub_py: 'pass', solution_py: 'x=1' })],
  });

  const tasks = await api.listTasks();
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].task_id, 'F1');
  assert.equal(fetchFn.calls[0].url, 'http://api.test/tasks');

  const full = await api.getTask('F1');
  assert.equal(full.statement_md, '# s');
  assert.equal(fetchFn.calls[1].url, 'http://api.test/tasks/F1');
});

test('getTask URL-encodes task ids with special characters', async () => {
  const { api, fetchFn } = makeApi({ responses: [jsonResponse({ task_id: 'a/b c' })] });
  await api.getTask('a/b c');
  assert.equal(fetchFn.calls[0].url, 'http://api.test/tasks/a%2Fb%20c');
});

test('check posts task_id and student_code, returns parsed results', async () => {
  const body = { task_id: 'F1', version: '1.0.0', status: 'failed', passed_tests: 1, total_tests: 2,
    solution_hash: 'h', log: 'log text', understanding: null,
    results: [{ description: 'sums two', passed: true, expected_repr: '3', actual_repr: '3', error: null }] };
  const { api, fetchFn } = makeApi({ responses: [jsonResponse(body)] });

  const res = await api.check('F1', 'def solve(a, b): return a + b');
  assert.equal(res.status, 'failed');
  assert.equal(res.results[0].passed, true);
  assert.equal(fetchFn.calls[0].url, 'http://api.test/check');
  assert.deepEqual(JSON.parse(fetchFn.calls[0].init.body), { task_id: 'F1', student_code: 'def solve(a, b): return a + b' });
});

test('401 clears the token and dispatches ego:ide-session-expired', async () => {
  const { api, storage, events } = makeApi({
    responses: [jsonResponse({ detail: 'Token expired' }, 401)],
  });
  api.setToken('stale');

  await assert.rejects(() => api.me(), /Token expired/);
  assert.equal(api.getToken(), null);
  assert.equal(storage._map.has(IDE_TOKEN_KEY), false);
  assert.deepEqual(events, [IDE_SESSION_EXPIRED_EVENT]);
});

test('401 without an event target still clears the token and throws', async () => {
  const { api, storage } = makeApi({ withEvents: false, responses: [jsonResponse({}, 401)] });
  api.setToken('stale');
  await assert.rejects(() => api.me(), /Session expired/);
  assert.equal(storage._map.has(IDE_TOKEN_KEY), false);
});

test('non-401 errors surface the server detail string', async () => {
  const { api, events } = makeApi({
    responses: [jsonResponse({ detail: 'Task not found' }, 404)],
  });
  await assert.rejects(() => api.getTask('X'), /Task not found/);
  assert.deepEqual(events, []);
});

test('validation-style detail arrays are joined into one message', async () => {
  const { api } = makeApi({
    responses: [jsonResponse({ detail: [
      { loc: ['body', 'password'], msg: 'field required', type: 'missing' },
      { loc: ['body', 'username'], msg: 'too short', type: 'value_error' },
    ] }, 422)],
  });
  await assert.rejects(() => api.login('a', ''), /field required; too short/);
});

test('error responses without detail fall back to the HTTP status', async () => {
  const { api } = makeApi({ responses: [jsonResponse({}, 500)] });
  await assert.rejects(() => api.listTasks(), /HTTP 500/);
});
