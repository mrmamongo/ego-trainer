/** Client proof stays in memory and is never included in the browser URL. */
import { createHash, randomBytes } from 'node:crypto';
import type { AuthResponse, ForgejoFlow } from './api';

interface LoginApi {
    startForgejo(challenge: string, callbackUri: string): Promise<ForgejoFlow>;
    exchangeForgejo(state: string, verifier: string, ticket: string): Promise<AuthResponse | { pending: true }>;
}

export const FORGEJO_CALLBACK_PATH = '/auth/forgejo/callback';
export const FORGEJO_EXTENSION_ID = 'ego-trainer.ego-trainer';

/** VS Code supplies the decoded query, including its window routing parameter. */
export interface ForgejoCallback {
    scheme: string;
    authority: string;
    path: string;
    query: string;
}

export const OPEN_TASK_PATH = '/open';
const SAFE_TASK_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;

/** A browser deep link opens exactly one catalog task; other URIs stay login callbacks. */
export function openTaskIdFromUri(uri: Pick<ForgejoCallback, 'path' | 'query'>): string | null {
    if (uri.path !== OPEN_TASK_PATH) return null;
    const params = new URLSearchParams(uri.query);
    if (params.getAll('task').length !== 1) return null;
    const taskId = params.get('task') ?? '';
    return SAFE_TASK_ID.test(taskId) ? taskId : null;
}

export class ForgejoCallbacks {
    private readonly listeners = new Set<(uri: ForgejoCallback) => void>();

    handleUri(uri: ForgejoCallback): void {
        for (const listener of this.listeners) listener(uri);
    }

    subscribe(listener: (uri: ForgejoCallback) => void): () => void {
        this.listeners.add(listener);
        return () => { this.listeners.delete(listener); };
    }
}

export async function runForgejoFlow(
    api: LoginApi,
    callbackUri: string,
    callbacks: ForgejoCallbacks,
    openBrowser: (url: string) => Promise<boolean>,
    isCancelled: () => boolean,
    pause: () => Promise<void> = () => new Promise(resolve => setTimeout(resolve, 250)),
    onBrowserUnavailable: (url: string) => void = () => {},
): Promise<AuthResponse | undefined> {
    if (isCancelled()) return undefined;
    const verifier = randomBytes(32).toString('base64url');
    const challenge = createHash('sha256').update(verifier).digest('base64url');
    const expectedScheme = new URL(callbackUri).protocol.slice(0, -1);
    let expectedState = '';
    let ticket = '';
    let failed = false;
    // The independent completion proof returns to this editor window. The
    // verifier alone cannot consume a login opened on someone else's machine.
    const unsubscribe = callbacks.subscribe(uri => {
        if (ticket || failed || uri.scheme !== expectedScheme
            || uri.authority !== FORGEJO_EXTENSION_ID || uri.path !== FORGEJO_CALLBACK_PATH) return;
        const params = new URLSearchParams(uri.query);
        if (!expectedState || params.getAll('state').length !== 1 || params.get('state') !== expectedState) return;
        if (params.getAll('error').length === 1 && params.get('error') === 'login_failed' && !params.has('ticket')) {
            failed = true;
        } else if (!params.has('error') && params.getAll('ticket').length === 1) {
            const received = params.get('ticket') ?? '';
            if (/^[A-Za-z0-9_-]{43}$/.test(received)) ticket = received;
        }
    });
    try {
        const flow = await api.startForgejo(challenge, callbackUri);
        expectedState = flow.state;
        if (isCancelled()) return undefined;
        const deadline = Date.now() + Math.min(flow.expires_in, 300) * 1000;
        let opened = false;
        try { opened = await openBrowser(flow.authorization_url); }
        catch { /* Manual opening can still complete the same login attempt. */ }
        if (isCancelled()) return undefined;
        // VS Code returns false for Copy as well as Cancel. Only the explicit
        // login cancellation or expiry ends our callback subscription.
        if (!opened && !ticket && !failed && Date.now() < deadline) {
            onBrowserUnavailable(flow.authorization_url);
        }
        while (!isCancelled() && Date.now() < deadline) {
            await pause();
            if (isCancelled()) return undefined;
            if (failed) throw new Error('Вход через Forgejo не удался, либо регистрация закрыта.');
            if (!ticket) continue;
            const result = await api.exchangeForgejo(flow.state, verifier, ticket);
            if (isCancelled()) return undefined;
            if (!('pending' in result)) return result;
        }
        if (isCancelled()) return undefined;
        throw new Error('Время входа через Forgejo истекло. Запусти «Cogito: Войти» ещё раз.');
    } finally {
        unsubscribe();
    }
}
