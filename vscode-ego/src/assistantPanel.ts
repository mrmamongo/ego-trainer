/** Native tutor sidebar. Access, review, charging and defense remain server-owned. */
import * as vscode from 'vscode';
import { createHash, randomUUID } from 'node:crypto';
import { EgoApi, EgoApiError } from './api';
import type { AssistantData, AISession } from './aiTypes';
import { readEgoConfig } from './egoWorkspace';
import { webviewHtml, webviewLocalRoots } from './webviewHost';

interface ChatContext {
    data: AssistantData;
    api: EgoApi;
    code: string;
    getCode?: () => Promise<string>;
    autoDefend: boolean;
    submissionCodeHash?: string;
}

export class AssistantPanel {
    private static view: vscode.WebviewView | undefined;
    private static extensionUri: vscode.Uri;
    private static getApi: () => EgoApi;
    private static ready = false;
    private static current: ChatContext | undefined;
    private static contexts = new Map<string, ChatContext>();

    static configure(extensionUri: vscode.Uri, getApi: () => EgoApi): void {
        this.extensionUri = extensionUri;
        this.getApi = getApi;
    }

    static register(context: vscode.ExtensionContext): void {
        context.subscriptions.push(vscode.window.registerWebviewViewProvider('egoAssistant', {
            resolveWebviewView: view => {
                this.view = view;
                this.ready = false;
                view.webview.options = { enableScripts: true, localResourceRoots: webviewLocalRoots(this.extensionUri) };
                view.webview.onDidReceiveMessage(msg => this.onMessage(msg), undefined, context.subscriptions);
                view.onDidDispose(() => {
                    if (this.view === view) { this.view = undefined; this.ready = false; }
                }, undefined, context.subscriptions);
                view.webview.html = webviewHtml({ webview: view.webview, extensionUri: this.extensionUri,
                    bundleName: 'assistant.js', title: 'Cogito · Учебный ассистент' });
            },
        }, { webviewOptions: { retainContextWhenHidden: true } }));
    }

    /** Clear account/session state when changing login, server or workspace. */
    static close(): void {
        this.contexts.clear();
        this.current = undefined;
        this.publish();
    }

    private static select(taskId: string, code: string, submissionId?: string, getCode?: () => Promise<string>): ChatContext {
        let context = this.contexts.get(taskId);
        if (!context) {
            context = { api: this.getApi(), code, getCode, autoDefend: false,
                data: { taskId, account: null, session: null, busy: false, error: '' } };
            this.contexts.set(taskId, context);
        }
        context.code = code;
        context.getCode = getCode ?? context.getCode;
        const hash = createHash('sha256').update(code).digest('hex');
        if (!submissionId && context.submissionCodeHash && context.submissionCodeHash !== hash) {
            context.data.submissionId = undefined;
            context.submissionCodeHash = undefined;
            context.autoDefend = false;
            if (context.data.session?.mode === 'defend') context.data.session = null;
        }
        if (submissionId && submissionId !== context.data.submissionId) {
            context.data.session = null;
            context.data.submissionId = submissionId;
        }
        if (submissionId) context.submissionCodeHash = hash;
        this.current = context;
        this.publish();
        return context;
    }

    static async follow(taskId: string, code: string, getCode?: () => Promise<string>): Promise<void> {
        const previous = this.current;
        const context = this.select(taskId, code, undefined, getCode);
        if (context !== previous && this.ready && this.view?.visible) await this.refresh(context);
    }

    static async show(taskId: string, code: string, submissionId?: string, getCode?: () => Promise<string>): Promise<void> {
        const context = this.select(taskId, code, submissionId, getCode);
        context.autoDefend = !!submissionId;
        await vscode.commands.executeCommand('egoAssistant.focus');
        if (this.ready && this.current === context && !context.data.busy) await this.refresh(context);
    }

    private static publish(): void {
        if (!this.ready || !this.view) return;
        const data = this.current?.data ?? { taskId: '', account: null, session: null, busy: false, error: '' };
        void this.view.webview.postMessage({ type: 'assistant.data', payload: data });
    }

    private static attached(context: ChatContext): boolean {
        return this.contexts.get(context.data.taskId) === context;
    }

    private static async refresh(context: ChatContext): Promise<void> {
        if (context.data.busy) return;
        await this.perform(context, async () => {
            context.data.offline = (await readEgoConfig())?.mode === 'offline';
            if (context.data.offline) { context.data.account = null; return; }
            context.data.account = await context.api.getAIAccount();
            if (!this.attached(context)) return;
            if (!context.data.submissionId) {
                const [submissions, task, code] = await Promise.all([
                    context.api.getAISubmissions(), context.api.getTask(context.data.taskId),
                    context.getCode ? context.getCode() : Promise.resolve(context.code),
                ]);
                const hash = createHash('sha256').update(code).digest('hex');
                if (!this.attached(context)) return;
                context.data.submissionId = submissions.find(s => s.task_id === context.data.taskId
                    && s.solution_hash === hash && s.version === task.version && s.understanding !== 'confirmed')?.id;
                context.submissionCodeHash = context.data.submissionId ? hash : undefined;
            }
            if (context.autoDefend && context.data.account.available && !context.data.session) {
                context.autoDefend = false;
                await this.start(context, 'defend');
            }
        });
    }

    private static async start(context: ChatContext, mode: AISession['mode']): Promise<void> {
        const code = context.getCode ? await context.getCode() : context.code;
        if (!this.attached(context)) return;
        if (mode === 'defend' && context.submissionCodeHash !== createHash('sha256').update(code).digest('hex')) {
            context.data.submissionId = undefined;
            throw new Error('Код изменился после проверки. Проверь задачу снова, чтобы защищать текущее решение.');
        }
        context.data.session = await context.api.createAISession({
            task_id: context.data.taskId, mode, student_code: code,
            submission_id: mode === 'defend' ? context.data.submissionId : undefined,
        });
        if (this.attached(context) && mode === 'defend' && context.data.session.messages.length === 0) await this.send(context, '');
    }

    private static async send(context: ChatContext, text: string): Promise<void> {
        const session = context.data.session;
        if (!session) return;
        const code = session.mode !== 'defend' && context.getCode ? await context.getCode() : undefined;
        if (!this.attached(context)) return;
        context.data.session = await context.api.sendAIMessage(session.id, text, randomUUID(), code);
        context.data.account = context.data.session.account;
    }

    private static async perform(context: ChatContext, operation: () => Promise<void>): Promise<void> {
        if (context.data.busy || !this.attached(context)) return;
        context.data.busy = true;
        context.data.error = '';
        this.publish();
        try { await operation(); }
        catch (error) {
            context.data.error = error instanceof EgoApiError && error.status === 401
                ? 'Войди в Cogito, чтобы проверить доступ к ассистенту.' : (error as Error).message;
            if (this.attached(context)) {
                try { context.data.account = await context.api.getAIAccount(); } catch { /* preserve original error */ }
            }
        } finally { context.data.busy = false; this.publish(); }
    }

    private static async onMessage(msg: { type?: string; taskId?: string; mode?: string; text?: string }): Promise<void> {
        if (msg.type === 'ready') { this.ready = true; this.publish(); }
        if (msg.type === 'assistant.tasks') { await vscode.commands.executeCommand('egoTaskTree.focus'); return; }
        if (msg.type === 'assistant.login') { await vscode.commands.executeCommand('ego.login'); return; }
        if (msg.type === 'assistant.connect') { await vscode.commands.executeCommand('ego.init'); return; }
        const context = this.current;
        if (!context) return;
        if (msg.type === 'ready' || msg.type === 'assistant.refresh') { await this.refresh(context); return; }
        // A queued click from the previous task cannot send text to the new task.
        if (msg.taskId !== context.data.taskId || context.data.busy) return;
        await this.perform(context, async () => {
            if (msg.type === 'assistant.start' && ['hint', 'explain', 'defend'].includes(msg.mode || '')) {
                await this.start(context, msg.mode as AISession['mode']);
            } else if (msg.type === 'assistant.send' && typeof msg.text === 'string' && msg.text.trim()) {
                if (!context.data.session) await this.start(context, 'hint');
                await this.send(context, msg.text);
            }
        });
    }
}
