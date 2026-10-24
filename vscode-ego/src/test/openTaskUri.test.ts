import { test } from 'node:test';
import assert from 'node:assert/strict';
import { openTaskIdFromUri } from '../forgejoFlow';

function uri(path: string, query = '') {
    return { path, query };
}

test('open URI returns a safe task id and preserves VS Code window routing', () => {
    assert.equal(openTaskIdFromUri(uri('/open', 'task=V01')), 'V01');
    assert.equal(openTaskIdFromUri(uri('/open', 'windowId=14&task=XL-A02')), 'XL-A02');
    assert.equal(openTaskIdFromUri(uri('/open', 'task=F1.2')), 'F1.2');
});

test('open URI rejects missing, duplicate and unsafe task parameters', () => {
    for (const query of ['', 'task=', 'task=V1&task=V2', 'task=..', 'task=V1%2Fsecret', 'task=%3Cscript%3E']) {
        assert.equal(openTaskIdFromUri(uri('/open', query)), null, query);
    }
});

test('login callbacks and unrelated routes are not task deep links', () => {
    assert.equal(openTaskIdFromUri(uri('/auth/forgejo/callback', 'task=V1')), null);
    assert.equal(openTaskIdFromUri(uri('/other', 'task=V1')), null);
});
