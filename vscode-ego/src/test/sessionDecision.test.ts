import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decideSession, mergeEgoConfig, planEgoSkeleton } from '../sessionDecision';
import type { EgoConfigFile } from '../egoWorkspace';

const base: EgoConfigFile = {
    server_url: 'http://server',
    token: '',
    student_id: 's1',
    student_username: 'alice',
    role: 'student',
    mode: 'server',
};

test('offline mode ignores a stored token and is ready without login', () => {
    assert.deepEqual(decideSession({ ...base, mode: 'offline' }, 'secret'), {
        mode: 'offline', apiToken: undefined, validateToken: false,
        offline: true, loggedIn: false, ready: true, status: 'offline',
    });
});

test('server mode uses and validates a stored token', () => {
    assert.deepEqual(decideSession(base, 'secret'), {
        mode: 'server', apiToken: 'secret', validateToken: true,
        offline: false, loggedIn: false, ready: true, status: 'server',
    });
});

test('server mode without a token is ready but does not validate', () => {
    assert.equal(decideSession(base, undefined).validateToken, false);
    assert.equal(decideSession(base, undefined).apiToken, undefined);
    assert.equal(decideSession(base, undefined).offline, false);
});

test('missing config defaults to server auth behavior but is not ready', () => {
    assert.deepEqual(decideSession(undefined, 'secret'), {
        mode: 'server', apiToken: 'secret', validateToken: true,
        offline: false, loggedIn: false, ready: false, status: 'server',
    });
});

test('config merge preserves unrelated fields for re-init', () => {
    const merged = mergeEgoConfig(
        { ...base, mode: 'offline', custom_field: 'keep' } as EgoConfigFile & { custom_field: string },
        { ...base, mode: 'server', server_url: 'http://new' }
    );
    assert.equal((merged as EgoConfigFile & { custom_field: string }).custom_field, 'keep');
    assert.equal(merged.mode, 'server');
    assert.equal(merged.server_url, 'http://new');
});

test('skeleton plan writes only missing state files', () => {
    const plan = planEgoSkeleton(base, { ...base, mode: 'offline' }, {
        manifest: true,
        progress: false,
    });
    assert.equal(plan.config.mode, 'offline');
    assert.equal(plan.writeManifest, false);
    assert.equal(plan.writeProgress, true);
});
