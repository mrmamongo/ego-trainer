import * as vscode from 'vscode';
import { EgoApi, type AuthResponse } from './api';
import { runForgejoFlow } from './forgejoFlow';

/** null = local login, undefined = user cancelled, response = Forgejo login. */
export async function forgejoLogin(api: EgoApi): Promise<AuthResponse | null | undefined> {
    const providers = await api.authProviders();
    if (!providers.forgejo) {
        if (!providers.local) throw new Error('The server has no configured login provider.');
        return null;
    }
    return vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Ego: Sign in through Forgejo in your browser', cancellable: true },
        async (_progress, cancellation) => runForgejoFlow(
            api,
            url => Promise.resolve(vscode.env.openExternal(vscode.Uri.parse(url))),
            () => cancellation.isCancellationRequested,
        ),
    );
}
