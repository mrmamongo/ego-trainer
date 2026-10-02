import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { ForgejoCallbacks, runForgejoFlow, type ForgejoCallback } from '../forgejoFlow';

const auth = { access_token: 'ego-token', token_type: 'bearer', user_id: 'u', username: 'alice', role: 'student' };
const state = 's'.repeat(43);
const ticket = 't'.repeat(43);
const callbackUri = 'vscode://ego-trainer.ego-trainer/auth/forgejo/callback?windowId=14';
const flow = { state, authorization_url: 'https://ego.example/auth/forgejo/authorize?state=' + state, expires_in: 300 };
const callback: ForgejoCallback = {
    scheme: 'vscode', authority: 'ego-trainer.ego-trainer', path: '/auth/forgejo/callback',
    query: new URLSearchParams({ state, ticket }).toString(),
};

test('VS Code completion keeps window routing and needs both client proofs', async () => {
    const callbacks = new ForgejoCallbacks();
    let challenge = '';
    let attempts = 0;
    const result = await runForgejoFlow({
        async startForgejo(proof, destination) {
            challenge = proof;
            assert.equal(destination, callbackUri);
            return flow;
        },
        async exchangeForgejo(returnedState, verifier, returnedTicket) {
            attempts++;
            assert.equal(returnedState, state);
            assert.equal(returnedTicket, ticket);
            assert.equal(createHash('sha256').update(verifier).digest('base64url'), challenge);
            return auth;
        },
    }, callbackUri, callbacks, async url => {
        assert.equal(new URL(url).searchParams.size, 1);
        assert.equal(new URL(url).searchParams.has('code_verifier'), false);
        callbacks.handleUri(callback);
        // Duplicate/failure callbacks cannot replace the accepted completion.
        callbacks.handleUri({ ...callback, query: new URLSearchParams({ state, error: 'login_failed' }).toString() });
        return true;
    }, () => false, async () => {});
    assert.deepEqual(result, auth);
    assert.equal(attempts, 1);
    callbacks.handleUri(callback); // A completed flow is no longer listening.
    assert.equal(attempts, 1);
});

test('wrong editor, route, state, malformed and ambiguous callbacks cannot exchange', async () => {
    const callbacks = new ForgejoCallbacks();
    let cancelled = false;
    let pauses = 0;
    const result = await runForgejoFlow({
        async startForgejo() { return flow; },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, callbackUri, callbacks, async () => {
        for (const invalid of [
            { ...callback, scheme: 'vscode-insiders' },
            { ...callback, authority: 'other.extension' },
            { ...callback, path: '/wrong' },
            { ...callback, query: new URLSearchParams({ state: 'wrong', ticket }).toString() },
            { ...callback, query: new URLSearchParams({ state, ticket: 'invalid' }).toString() },
            { ...callback, query: callback.query + '&state=' + state },
            { ...callback, query: callback.query + '&ticket=' + ticket },
            { ...callback, query: callback.query + '&error=login_failed' },
        ]) callbacks.handleUri(invalid);
        return true;
    }, () => cancelled, async () => { if (++pauses === 2) cancelled = true; });
    assert.equal(result, undefined);
});

test('already cancelled login does not start or open the browser', async () => {
    const result = await runForgejoFlow({
        async startForgejo() { assert.fail('must not start'); },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, callbackUri, new ForgejoCallbacks(), async () => { assert.fail('must not open'); }, () => true);
    assert.equal(result, undefined);
});

test('provider failure ends login without token exchange', async () => {
    const callbacks = new ForgejoCallbacks();
    await assert.rejects(runForgejoFlow({
        async startForgejo() { return flow; },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, callbackUri, callbacks, async () => {
        callbacks.handleUri({ ...callback, query: new URLSearchParams({ state, error: 'login_failed' }).toString() });
        return true;
    }, () => false, async () => {}), /login failed/);
});

test('cancellation after a valid callback does not exchange; later attempts have fresh state', async () => {
    const callbacks = new ForgejoCallbacks();
    let cancelled = false;
    const result = await runForgejoFlow({
        async startForgejo() { return flow; },
        async exchangeForgejo() { assert.fail('cancelled flow must not exchange'); },
    }, callbackUri, callbacks, async () => {
        callbacks.handleUri(callback); cancelled = true; return true;
    }, () => cancelled, async () => {});
    assert.equal(result, undefined);
    await assert.rejects(runForgejoFlow({
        async startForgejo() { return { ...flow, state: 'n'.repeat(43), expires_in: 0 }; },
        async exchangeForgejo() { assert.fail('stale callback must not exchange'); },
    }, callbackUri, callbacks, async () => { callbacks.handleUri(callback); return true; }, () => false), /timed out/);
});

test('failure to open browser releases the callback subscription', async () => {
    const callbacks = new ForgejoCallbacks();
    await assert.rejects(runForgejoFlow({
        async startForgejo() { return flow; },
        async exchangeForgejo() { assert.fail('must not exchange'); },
    }, callbackUri, callbacks, async () => false, () => false), /Could not open/);
    callbacks.handleUri(callback);
});
