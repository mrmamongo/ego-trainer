import { test } from 'node:test';
import assert from 'node:assert/strict';
import { classifyAuthStatus, decideAuthStart } from '../authStatus';

test('stored token with a valid session skips the browser flow', () => {
    assert.equal(decideAuthStart({ hasToken: true, meResult: 'ok' }), 'already');
});

test('expired or forbidden token starts the normal login flow', () => {
    assert.equal(decideAuthStart({ hasToken: true, meResult: 'unauthorized' }), 'login');
});

test('unreachable server neither logs in nor clears the token', () => {
    assert.equal(decideAuthStart({ hasToken: true, meResult: 'unreachable' }), 'unreachable');
});

test('no stored token goes straight to the normal flow', () => {
    assert.equal(decideAuthStart({ hasToken: false, meResult: 'unreachable' }), 'login');
    assert.equal(decideAuthStart({ hasToken: false, meResult: 'unauthorized' }), 'login');
    assert.equal(decideAuthStart({ hasToken: false, meResult: 'ok' }), 'login');
});

test('only 401 and 403 mean the token is invalid', () => {
    assert.equal(classifyAuthStatus(401), 'unauthorized');
    assert.equal(classifyAuthStatus(403), 'unauthorized');
    assert.equal(classifyAuthStatus(500), 'unreachable');
    assert.equal(classifyAuthStatus(502), 'unreachable');
    assert.equal(classifyAuthStatus(404), 'unreachable');
});
