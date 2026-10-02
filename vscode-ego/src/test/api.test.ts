import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { EgoApi, EgoApiError } from '../api';

const originalFetch = globalThis.fetch;

afterEach(() => {
    globalThis.fetch = originalFetch;
});

function mockFetch(status: number, body: unknown): void {
    globalThis.fetch = (async () => ({
        ok: status >= 200 && status < 300,
        status,
        json: async () => body,
    })) as unknown as typeof fetch;
}

test('401 throws EgoApiError with path and login message', async () => {
    mockFetch(401, {});
    await assert.rejects(
        new EgoApi('http://localhost:8000').me(),
        (error: unknown) => {
            assert.ok(error instanceof EgoApiError);
            assert.equal(error.status, 401);
            assert.equal(error.path, '/auth/me');
            assert.match(error.message, /Ego: Login/);
            return true;
        }
    );
});

test('Forgejo start sends a window-bound editor URI and rejects a foreign login origin', async () => {
    const callbackUri = 'vscode://ego-trainer.ego-trainer/auth/forgejo/callback?windowId=14';
    const challenge = 'c'.repeat(43);
    let loginUrl = 'https://ego.example/auth/forgejo/authorize?state=' + 's'.repeat(43);
    globalThis.fetch = (async (url: string | URL | Request, init?: RequestInit) => {
        assert.equal(url, 'https://ego.example/auth/forgejo/start');
        assert.equal(init?.method, 'POST');
        assert.deepEqual(JSON.parse(String(init?.body)), {
            code_challenge: challenge, client: 'vscode', callback_uri: callbackUri,
        });
        return {
            ok: true, status: 200,
            json: async () => ({ state: 's'.repeat(43), authorization_url: loginUrl, expires_in: 300 }),
        };
    }) as typeof fetch;
    const api = new EgoApi('https://ego.example');
    assert.equal((await api.startForgejo(challenge, callbackUri)).authorization_url, loginUrl);
    loginUrl = 'https://attacker.example/login';
    await assert.rejects(api.startForgejo(challenge, callbackUri), /does not match/);
});

test('403 throws EgoApiError with forbidden message', async () => {
    mockFetch(403, {});
    await assert.rejects(
        new EgoApi('http://localhost:8000').getProgress('student-1'),
        (error: unknown) => {
            assert.ok(error instanceof EgoApiError);
            assert.equal(error.status, 403);
            assert.equal(error.path, '/progress/student-1');
            assert.match(error.message, /Forbidden/);
            return true;
        }
    );
});

test('generic API errors preserve JSON detail', async () => {
    mockFetch(500, { detail: 'Database is unavailable' });
    await assert.rejects(
        new EgoApi('http://localhost:8000').health(),
        (error: unknown) => {
            assert.ok(error instanceof EgoApiError);
            assert.equal(error.status, 500);
            assert.equal(error.path, '/health');
            assert.equal(error.message, 'Database is unavailable');
            return true;
        }
    );
});

test('successful requests return JSON', async () => {
    const value = { status: 'ok', version: '1.0.0' };
    mockFetch(200, value);
    assert.deepEqual(await new EgoApi('http://localhost:8000').health(), value);
});

test('register serializes the student role', async () => {
    let request: { method?: string; body?: string } | undefined;
    globalThis.fetch = (async (_url: string, init?: RequestInit) => {
        request = { method: init?.method, body: init?.body as string };
        return { ok: true, status: 201, json: async () => ({ access_token: 'token' }) };
    }) as unknown as typeof fetch;

    await new EgoApi('http://localhost:8000').register('alice', 'secret');
    assert.equal(request?.method, 'POST');
    assert.deepEqual(JSON.parse(request?.body || '{}'), {
        username: 'alice',
        password: 'secret',
        role: 'student',
    });
});
