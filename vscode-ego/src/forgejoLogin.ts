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
        async (progress, cancellation) => {
            let active = true;
            let cancelled = false;
            const isCancelled = () => cancelled || cancellation.isCancellationRequested;
            const offerManualLogin = (url: string) => {
                progress.report({ message: 'Открой ссылку в браузере вручную. Ожидаю подтверждения входа…' });
                void vscode.window.showInformationMessage(
                    'Браузер не открыт автоматически. Если ты выбрал Copy, открой скопированную ссылку вручную — вход продолжает ожидать подтверждения.',
                    'Скопировать ссылку', 'Отменить вход',
                ).then(async action => {
                    if (!active || isCancelled()) return;
                    if (action === 'Отменить вход') {
                        cancelled = true;
                    } else if (action === 'Скопировать ссылку') {
                        try {
                            await vscode.env.clipboard.writeText(url);
                            if (active && !isCancelled()) progress.report({ message: 'Ссылка скопирована. Открой её в браузере; я жду подтверждения входа…' });
                        } catch {
                            if (active && !isCancelled()) void vscode.window.showErrorMessage('Не удалось скопировать ссылку. Повтори Ego: Login.');
                        }
                    }
                }, () => undefined);
            };
            try {
                return await runForgejoFlow(
                    api,
                    callbackUri.toString(true),
                    callbacks,
                    url => Promise.resolve(vscode.env.openExternal(vscode.Uri.parse(url))),
                    isCancelled,
                    undefined,
                    offerManualLogin,
                );
            } finally {
                active = false;
            }
        },
    );
}
