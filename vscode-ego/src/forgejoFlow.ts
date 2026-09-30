/** Client proof stays in memory and is never included in the browser URL. */
import { createHash, randomBytes } from 'node:crypto';
import { createServer } from 'node:http';
import type { AddressInfo } from 'node:net';
import type { AuthResponse, ForgejoFlow } from './api';

interface LoginApi {
    startForgejo(challenge: string, port: number): Promise<ForgejoFlow>;
    exchangeForgejo(state: string, verifier: string, ticket: string): Promise<AuthResponse | { pending: true }>;
}

export async function runForgejoFlow(
    api: LoginApi,
    openBrowser: (url: string) => Promise<boolean>,
    isCancelled: () => boolean,
    pause: () => Promise<void> = () => new Promise(resolve => setTimeout(resolve, 1500)),
): Promise<AuthResponse | undefined> {
    const verifier = randomBytes(32).toString('base64url');
    const challenge = createHash('sha256').update(verifier).digest('base64url');
    let expectedState = '';
    let ticket = '';
    let failed = false;
    // Completion proof returns to this machine. Sharing a login URL cannot
    // deliver a victim's login token to a remote flow initiator.
    const listener = createServer((request, response) => {
        let url: URL;
        try { url = new URL(request.url ?? '/', 'http://127.0.0.1'); }
        catch { response.writeHead(400); response.end('Invalid login callback'); return; }
        const valid = request.method === 'GET' && url.pathname === '/callback'
            && expectedState !== '' && url.searchParams.get('state') === expectedState;
        const received = url.searchParams.get('ticket') ?? '';
        const error = url.searchParams.get('error') === 'login_failed';
        if (!valid || (!error && !/^[A-Za-z0-9_-]{43}$/.test(received))) {
            response.writeHead(400); response.end('Invalid login callback'); return;
        }
        if (error) failed = true;
        else if (!ticket) ticket = received;
        response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer', 'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'" });
        response.end('<!doctype html><html lang="ru"><meta charset="utf-8"><title>Ego Trainer</title><p>Вернись в VSCode. Эту вкладку можно закрыть.</p></html>');
    });
    await new Promise<void>((resolve, reject) => {
        listener.once('error', reject);
        listener.listen(0, '127.0.0.1', resolve);
    });
    try {
        const flow = await api.startForgejo(challenge, (listener.address() as AddressInfo).port);
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
        listener.closeAllConnections();
        await new Promise<void>(resolve => listener.close(() => resolve()));
    }
}
