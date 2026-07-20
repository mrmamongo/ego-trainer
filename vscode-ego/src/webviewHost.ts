/** Shared helpers for Svelte webview panels (CSP nonce + script URI). */

import * as vscode from 'vscode';
import * as crypto from 'node:crypto';

/** Generate a CSP-safe nonce for webview scripts. */
export function createNonce(): string {
    return crypto.randomBytes(16).toString('base64');
}

/** Absolute path to a built webview bundle under out/webview/. */
export function webviewBundleUri(
    webview: vscode.Webview,
    extensionUri: vscode.Uri,
    bundleName: string
): vscode.Uri {
    const diskPath = vscode.Uri.joinPath(extensionUri, 'out', 'webview', bundleName);
    return webview.asWebviewUri(diskPath);
}

/** Minimal HTML shell that loads a bundled IIFE and mounts into #app. */
export function webviewHtml(opts: {
    webview: vscode.Webview;
    extensionUri: vscode.Uri;
    bundleName: string;
    title: string;
}): string {
    const nonce = createNonce();
    const scriptUri = webviewBundleUri(opts.webview, opts.extensionUri, opts.bundleName);
    const csp = [
        `default-src 'none'`,
        `style-src ${opts.webview.cspSource} 'unsafe-inline'`,
        `script-src 'nonce-${nonce}'`,
        `img-src ${opts.webview.cspSource} https: data:`,
        `font-src ${opts.webview.cspSource}`,
    ].join('; ');

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="${csp}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(opts.title)}</title>
</head>
<body>
    <div id="app"></div>
    <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
}

/** localResourceRoots for webview panels that load out/webview bundles. */
export function webviewLocalRoots(extensionUri: vscode.Uri): vscode.Uri[] {
    return [vscode.Uri.joinPath(extensionUri, 'out', 'webview')];
}

export function escapeHtml(s: string): string {
    return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
