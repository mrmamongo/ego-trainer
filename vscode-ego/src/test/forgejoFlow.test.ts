import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { runForgejoFlow } from '../forgejoFlow';

const auth = { access_token: 'ego-token', token_type: 'bearer', role: 'student', username: 'alice', user_id: 'user-id' };
const state = 's'.repeat(43);
const ticket = 't'.repeat(43);

test('browser completion reaches the native listener; both proofs are needed', async () => {
    let port = 0;
    let challenge = '';
    let attempts = 0;
    const result = await runForgejoFlow({
        async startForgejo(proof, callbackPort) {
            challenge = proof; port = callbackPort;
            return { state, authorization_url: 'https://ego.example/auth/forgejo/authorize?state=' + state, expires_in: 300 };
        },
        async exchangeForgejo(returnedState, verifier, returnedTicket) {
            attempts++;
            assert.equal(returnedState, state);
            assert.equal(returnedTicket, ticket);
            assert.equal(createHash('sha256').update(verifier).digest('base64url'), challenge);
            return auth;
        },
    }, async url => {
        assert.equal(new URL(url).searchParams.size, 1);
        assert.equal(new URL(url).searchParams.has('code_verifier'), false);
        const forged = await fetch(`http://127.0.0.1:${port}/callback?state=wrong&ticket=${ticket}`);
        assert.equal(forged.status, 400);
        const response = await fetch(`http://127.0.0.1:${port}/callback?state=${state}&ticket=${ticket}`);
        assert.equal(response.status, 200);
        assert.equal((await response.text()).includes('ego-token'), false);
        return true;
    }, () => false, async () => {});
    assert.deepEqual(result, auth);
    assert.equal(attempts, 1);
    await assert.rejects(fetch(`http://127.0.0.1:${port}/callback`)); // listener is closed
});

test('cancelled login never opens the browser or exchanges a token', async () => {
    const result = await runForgejoFlow({
        async startForgejo() { return { state, authorization_url: 'https://ego.example', expires_in: 300 }; },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, async () => { assert.fail('must not open'); }, () => true);
    assert.equal(result, undefined);
});

test('provider failure returned locally ends login without token exchange', async () => {
    let port = 0;
    await assert.rejects(runForgejoFlow({
        async startForgejo(_challenge, callbackPort) { port = callbackPort; return { state, authorization_url: 'https://ego.example', expires_in: 300 }; },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, async () => { await fetch(`http://127.0.0.1:${port}/callback?state=${state}&error=login_failed`); return true; }, () => false, async () => {}), /login failed/);
});
