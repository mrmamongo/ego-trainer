// Exercise the real login adapter with VS Code API stubs; no network or tokens.
const assert = require('node:assert/strict');
const Module = require('node:module');
const { createHash } = require('node:crypto');
const originalLoad = Module._load;
const state = 's'.repeat(43), ticket = 't'.repeat(43);
const loginUrl = 'https://ego.example/auth/forgejo/authorize?state=' + state;
const auth = { access_token: 'test-token', token_type: 'bearer', user_id: 'u', username: 'alice', role: 'student' };

function uri(raw) {
    const parsed = new URL(raw);
    return { scheme: parsed.protocol.slice(0, -1), authority: parsed.host, path: parsed.pathname,
        query: parsed.search.slice(1), toString: () => raw };
}

async function scenario(name, mode) {
    let handler, challenge, resolveChoice;
    let prompts = 0, copies = 0, exchanges = 0, starts = 0;
    const cancellation = { isCancellationRequested: false };
    const reports = [];
    const deliver = () => handler.handleUri(uri('vscode://ego-trainer.ego-trainer/auth/forgejo/callback?' + new URLSearchParams({ state, ticket })));
    const pendingChoice = new Promise(resolve => { resolveChoice = resolve; });
    const vscode = {
        Uri: { parse: uri }, ProgressLocation: { Notification: 15 },
        env: {
            uriScheme: 'vscode',
            asExternalUri: async value => uri(value.toString() + '?windowId=14'),
            async openExternal(value) {
                assert.equal(value.toString(), loginUrl);
                if (mode === 'launcherThrows') throw new Error('launcher unavailable');
                if (mode === 'progressCancel') cancellation.isCancellationRequested = true;
                return false; // Native Copy (and Cancel) return the same boolean.
            },
            clipboard: { async writeText(value) {
                assert.equal(value, loginUrl); copies++; deliver();
            } },
        },
        window: {
            registerUriHandler(value) { handler = value; return { dispose() { handler = undefined; } }; },
            withProgress: async (_options, task) => task({ report: value => reports.push(value.message) }, cancellation),
            showInformationMessage(message, ...actions) {
                prompts++;
                assert.match(message, /Copy/);
                assert.deepEqual(actions, ['Скопировать ссылку', 'Отменить вход']);
                if (mode === 'nativeCopy') { setImmediate(deliver); return Promise.resolve(undefined); }
                if (mode === 'staleChoice') { setImmediate(deliver); return pendingChoice; }
                return Promise.resolve(mode === 'manualCancel' ? 'Отменить вход' : 'Скопировать ссылку');
            },
            showErrorMessage(message) { assert.fail(message); },
        },
    };
    Module._load = function(request, parent, isMain) {
        return request === 'vscode' ? vscode : originalLoad.call(this, request, parent, isMain);
    };
    const context = { subscriptions: [] };
    try {
        delete require.cache[require.resolve('../out/forgejoLogin.js')];
        const { registerForgejoUriHandler, forgejoLogin } = require('../out/forgejoLogin.js');
        registerForgejoUriHandler(context);
        const result = await forgejoLogin({
            async authProviders() { return { forgejo: true, local: false }; },
            async startForgejo(proof, destination) {
                starts++; challenge = proof;
                assert.equal(destination, 'vscode://ego-trainer.ego-trainer/auth/forgejo/callback?windowId=14');
                return { state, authorization_url: loginUrl, expires_in: 300 };
            },
            async exchangeForgejo(returnedState, verifier, returnedTicket) {
                exchanges++;
                assert.equal(returnedState, state); assert.equal(returnedTicket, ticket);
                assert.equal(createHash('sha256').update(verifier).digest('base64url'), challenge);
                return auth;
            },
        });
        assert.equal(starts, 1);
        const cancelled = mode === 'manualCancel' || mode === 'progressCancel';
        assert.deepEqual(result, cancelled ? undefined : auth);
        assert.equal(exchanges, cancelled ? 0 : 1);
        assert.equal(prompts, mode === 'progressCancel' ? 0 : 1);
        assert.equal(copies, mode === 'manualCopy' || mode === 'launcherThrows' ? 1 : 0);
        if (mode === 'staleChoice') {
            resolveChoice('Скопировать ссылку');
            await new Promise(resolve => setImmediate(resolve));
            assert.equal(copies, 0, 'a stale notification must not change the clipboard');
        }
        if (!cancelled) assert.ok(reports.length > 0);
        console.log('login smoke:', name, 'passed');
    } finally {
        for (const disposable of context.subscriptions) disposable.dispose();
        Module._load = originalLoad;
    }
}

(async () => {
    await scenario('native Copy then manual browser return', 'nativeCopy');
    await scenario('fallback Copy then browser return', 'manualCopy');
    await scenario('explicit fallback cancellation', 'manualCancel');
    await scenario('progress cancellation', 'progressCancel');
    await scenario('launcher exception then manual browser return', 'launcherThrows');
    await scenario('late notification action after completed login', 'staleChoice');
})().catch(error => { console.error(error); process.exitCode = 1; });
