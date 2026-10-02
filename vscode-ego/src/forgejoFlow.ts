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
        if (!await openBrowser(flow.authorization_url)) throw new Error('Could not open the Forgejo login browser.');
        const deadline = Date.now() + Math.min(flow.expires_in, 300) * 1000;
        while (!isCancelled() && Date.now() < deadline) {
            await pause();
            if (isCancelled()) return undefined;
            if (failed) throw new Error('Forgejo login failed or registration is closed.');
            if (!ticket) continue;
            const result = await api.exchangeForgejo(flow.state, verifier, ticket);
            if (isCancelled()) return undefined;
            if (!('pending' in result)) return result;
        }
        if (isCancelled()) return undefined;
        throw new Error('Forgejo login timed out. Run Ego: Login again.');
    } finally {
        unsubscribe();
    }
}
