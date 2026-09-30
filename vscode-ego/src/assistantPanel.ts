/** Text-only assistant. All access, model calls, reviews and charges live on the server. */
import * as vscode from 'vscode';
import { randomUUID } from 'node:crypto';
import { EgoApi } from './api';
import type { AssistantData, AISession } from './aiTypes';
import { webviewHtml, webviewLocalRoots } from './webviewHost';

export class AssistantPanel {
    private static panel: vscode.WebviewPanel | undefined;
    private static extensionUri: vscode.Uri;
    private static getApi: () => EgoApi;

    static configure(extensionUri: vscode.Uri, getApi: () => EgoApi): void {
        this.extensionUri = extensionUri;
        this.getApi = getApi;
    }

    static close(): void {
        this.panel?.dispose();
        this.panel = undefined;
    }

    static async show(taskId: string, code: string, submissionId?: string, getCode?: () => Promise<string>): Promise<void> {
        this.close();
        const panel = vscode.window.createWebviewPanel('egoAssistant', `Ассистент · ${taskId}`,
            vscode.ViewColumn.Beside, {
                enableScripts: true, retainContextWhenHidden: true,
                localResourceRoots: webviewLocalRoots(this.extensionUri),
            });
        this.panel = panel;
        const api = this.getApi();
        const data: AssistantData = { taskId, account: null, session: null, submissionId,
            busy: false, error: '' };
        let ready = false;
        const publish = () => { if (ready) void panel.webview.postMessage({ type: 'assistant.data', payload: data }); };
        const refresh = async () => {
            data.account = await api.getAIAccount();
            if (!data.submissionId) {
                const [submissions, task] = await Promise.all([api.getAISubmissions(), api.getTask(taskId)]);
                // Bind the defense to the current editor contents, not an older solution.
                const { createHash } = await import('node:crypto');
                const hash = createHash('sha256').update(code).digest('hex');
                data.submissionId = submissions.find((s) => s.task_id === taskId &&
                    s.solution_hash === hash && s.version === task.version && s.understanding !== 'confirmed')?.id;
            }
        };
        const send = async (text: string) => {
            if (!data.session) return;
            const freshCode = data.session.mode !== 'defend' && getCode ? await getCode() : undefined;
            data.session = await api.sendAIMessage(data.session.id, text, randomUUID(), freshCode);
            data.account = data.session.account;
        };
        const start = async (mode: AISession['mode']) => {
            data.session = await api.createAISession({ task_id: taskId, mode,
                student_code: code, submission_id: mode === 'defend' ? data.submissionId : undefined });
            if (mode === 'defend' && data.session.messages.length === 0) await send('');
        };
        panel.webview.onDidReceiveMessage(async (msg: { type?: string; mode?: string; text?: string }) => {
            if (data.busy) return;
            data.busy = true;
            data.error = '';
            if (msg.type === 'ready') ready = true;
            publish();
            try {
                if (msg.type === 'ready' || msg.type === 'assistant.refresh') {
                    await refresh();
                    if (submissionId && data.account?.available && !data.session) await start('defend');
                } else if (msg.type === 'assistant.start' && ['hint', 'explain', 'defend'].includes(msg.mode || '')) {
                    await start(msg.mode as AISession['mode']);
                } else if (msg.type === 'assistant.send' && typeof msg.text === 'string' && msg.text.trim()) {
                    if (!data.session) await start('hint');
                    await send(msg.text);
                }
            } catch (e) {
                data.error = (e as Error).message;
                // Reload balance after failures: rejected drafts also incur provider costs.
                try { data.account = await api.getAIAccount(); } catch { /* display original error */ }
            } finally {
                data.busy = false;
                publish();
            }
        });
        panel.onDidDispose(() => { if (this.panel === panel) this.panel = undefined; });
        panel.webview.html = webviewHtml({ webview: panel.webview, extensionUri: this.extensionUri,
            bundleName: 'assistant.js', title: `Ассистент · ${taskId}` });
    }
}
