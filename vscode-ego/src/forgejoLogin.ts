import * as vscode from 'vscode';
import { EgoApi, type AuthResponse } from './api';
import { ForgejoCallbacks, FORGEJO_CALLBACK_PATH, FORGEJO_EXTENSION_ID, runForgejoFlow } from './forgejoFlow';

const callbacks = new ForgejoCallbacks();

export function registerForgejoUriHandler(context: vscode.ExtensionContext): void {
    context.subscriptions.push(vscode.window.registerUriHandler({
        handleUri: uri => callbacks.handleUri(uri),
    }));
}

/** null = local login, undefined = user cancelled, response = Forgejo login. */
export async function forgejoLogin(api: EgoApi): Promise<AuthResponse | null | undefined> {
    const providers = await api.authProviders();
    if (!providers.forgejo) {
        if (!providers.local) throw new Error('The server has no configured login provider.');
        return null;
    }
    // asExternalUri binds the return to this window, including desktop Remote SSH/WSL.
    const callbackUri = await vscode.env.asExternalUri(vscode.Uri.parse(
        `${vscode.env.uriScheme}://${FORGEJO_EXTENSION_ID}${FORGEJO_CALLBACK_PATH}`,
    ));
    if (!['vscode', 'vscode-insiders'].includes(callbackUri.scheme)) {
        throw new Error('Forgejo sign-in requires desktop VS Code or VS Code Insiders.');
    }
    return vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Ego: Sign in through Forgejo in your browser', cancellable: true },
        async (_progress, cancellation) => runForgejoFlow(
            api,
            callbackUri.toString(true),
            callbacks,
            url => Promise.resolve(vscode.env.openExternal(vscode.Uri.parse(url))),
            () => cancellation.isCancellationRequested,
        ),
    );
}
