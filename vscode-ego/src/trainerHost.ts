/* Host side of the interactive trainers (`trace` / `parsons`).
 *
 * WIRING — the webview side is `taskView.svelte` + `taskViewPanel.ts`.
 *
 * 1. Task data (taskViewPanel.ts, `loadTaskViewData` -> `TaskViewData`):
 *      trainer: trainerKindFromTags(meta.tags)   // 'trace' wins over 'parsons', else undefined
 *    In server mode take it from `full.tags` (GET /tasks/<id>); in offline mode
 *    read the `tags:` list of the task YAML next to the .md/.py, or leave it
 *    undefined so the task view renders as before (`trainer?: TrainerKind` is
 *    already declared in webview/shared/types.ts).
 *
 * 2. Panel (taskViewPanel.ts): keep a small holder next to the panel and hand it
 *    every message before the task-view switch:
 *
 *      import { TRAINER_MSG, handleTrainerMessage, type TrainerContext } from './trainerHost';
 *
 *      private static async trainer(): Promise<TrainerContext | undefined> {
 *          const cur = this.current, panel = this.panel;
 *          if (!cur || !panel) return undefined;
 *          const pyUri = await taskPyUri(cur);  // same candidates as openTaskPy()/
 *                                               // readLocalStub(): tasks/<slug>/, md_path sibling,
 *                                               // then workspace.findFiles(task_<id>.py, anywhere)
 *          if (!pyUri) return undefined;
 *          return {
 *              pyUri,
 *              // Read through the open document when it exists so unsaved edits are kept.
 *              readFile: async () => vscode.workspace.textDocuments.find(d => d.uri.toString() === pyUri.toString())?.getText()
 *                  ?? Buffer.from(await vscode.workspace.fs.readFile(pyUri)).toString('utf-8'),
 *              // Full-document replace + save (endings and bytes come from trainer.ts, which
 *              // keeps the file's own line terminators). Do not run format-on-save here.
 *              writeFile: async (text) => {
 *                  const doc = await vscode.workspace.openTextDocument(pyUri);
 *                  const edit = new vscode.WorkspaceEdit();
 *                  edit.replace(doc.uri, new vscode.Range(doc.positionAt(0), doc.positionAt(doc.getText().length)), text);
 *                  await vscode.workspace.applyEdit(edit);
 *                  await doc.save();
 *              },
 *              runCheck: () => this.deps!.checkTask(cur.id),
 *              post: (message) => void panel.webview.postMessage(message),
 *          };
 *      }
 *
 *      private static async onMessage(msg: { type?: string; taskId?: string }): Promise<void> {
 *          const cur = this.current, deps = this.deps;
 *          if (!deps) return;
 *          if (isTrainerMessage(msg)) {           // before the taskId filter below
 *              const trainer = await this.trainer();
 *              if (trainer && await handleTrainerMessage(msg, trainer)) return;
 *          }
 *          ...existing taskId check and switch...
 *      }
 *
 * 3. Webview: `import TraceTrainer from './TraceTrainer.svelte'` (or ParsonsTrainer)
 *    inside taskView.svelte and render it with `kind={data.trainer} taskId={data.id}`
 *    (or with a `trainer === 'trace'` svelte-if). The component subscribes to the
 *    `trainerState` store (webview/shared/store.ts), filled by `taskView.ts`:
 *
 *      if (msg.type === TRAINER_MSG.state) trainerState.set(msg.payload.state);
 *
 *    It posts `{ type: 'trainer.load', kind, taskId }` on mount and
 *    `{ type: 'trainer.submit', taskId, answers | lines }` on submit.
 *
 * 4. Switching tasks: `TaskViewPanel.pushData()` already posts `taskView.setData`;
 *    the components also (re)load on `trainer.load` with `{ taskId }`.
 */

import type { TrainerKind, TrainerState } from './trainer';
import { parseParsons, parseTrace, patchParsons, patchTrace } from './trainer';

/** Message types (request from the webview -> host). */
export const TRAINER_MSG = {
    /** webview -> host: `{ kind, taskId? }`; host answers with `trainer.state`. */
    load: 'trainer.load',
    /** host -> webview: `{ state: TrainerState }`. */
    state: 'trainer.state',
    /** webview -> host: `{ taskId?, answers }` (trace) or `{ taskId?, lines }` (parsons). */
    submit: 'trainer.submit',
    /** host -> webview after a submit: `{ ok, error?, state? }`. */
    submitted: 'trainer.submitted',
} as const;

export interface TrainerMessage {
    type?: string;
    taskId?: string;
    kind?: TrainerKind;
    /** trace: `{ name: literal }`. */
    answers?: Record<string, string>;
    /** parsons: `[{ id, level }]` in display order. */
    lines?: { id?: unknown; level?: unknown }[];
}

export interface TrainerContext {
    /** The student's `.py` task file. */
    pyUri: { toString(): string };
    readFile: () => Promise<string>;
    /** Write the whole (already patched by this module) file text and save. */
    writeFile: (text: string) => Promise<void>;
    /** Runs the normal check flow (server or offline) after a save. */
    runCheck: () => Promise<void> | void;
    /** Posts `TRAINER_MSG.state` / `TRAINER_MSG.submitted` messages to the webview. */
    post: (message: { type: string; payload?: unknown }) => void;
}

/** Result of a handled message (handy for tests and for the wiring). */
export interface TrainerHandled {
    handled: true;
    state?: TrainerState;
    error?: string;
}

/** True for any trainer.* message, so the caller can short-circuit its switch. */
export function isTrainerMessage(msg: { type?: string } | undefined): boolean {
    const type = msg?.type;
    return type === TRAINER_MSG.load || type === TRAINER_MSG.submit;
}

/**
 * Handle `trainer.load` / `trainer.submit`. Returns `false` for other messages so
 * the caller keeps its normal task-view handling.
 */
export async function handleTrainerMessage(
    msg: TrainerMessage | undefined,
    ctx: TrainerContext
): Promise<boolean> {
    const result = await runTrainerMessage(msg, ctx);
    return result.handled;
}

/** Same as {@link handleTrainerMessage} but always returns the outcome. */
export async function runTrainerMessage(
    msg: TrainerMessage | undefined,
    ctx: TrainerContext
): Promise<TrainerHandled | { handled: false }> {
    if (!msg || !isTrainerMessage(msg)) return { handled: false };
    const kind = normalizeKind(msg.kind);
    if (!kind) {
        const unsupported: TrainerState = { kind: null, supported: false, reason: 'Тренажёр не выбран.' };
        ctx.post({ type: TRAINER_MSG.state, payload: { state: unsupported } });
        return { handled: true, state: unsupported };
    }
    let text: string;
    try {
        text = await ctx.readFile();
    } catch (error) {
        const failed: TrainerState = { kind, supported: false, reason: 'Не удалось прочитать файл задания.' };
        ctx.post({ type: TRAINER_MSG.state, payload: { state: failed, error: (error as Error).message } });
        return { handled: true, state: failed };
    }

    if (msg.type === TRAINER_MSG.load) {
        const state = parseTrainer(kind, text);
        ctx.post({ type: TRAINER_MSG.state, payload: { state } });
        return { handled: true, state };
    }

    // submit
    try {
        const patched = kind === 'trace' ? tracePatch(text, msg.answers) : parsonsPatch(text, msg.lines);
        if (patched !== text) await ctx.writeFile(patched);
        const state = parseTrainer(kind, patched);
        ctx.post({ type: TRAINER_MSG.state, payload: { state } });
        ctx.post({ type: TRAINER_MSG.submitted, payload: { ok: true } });
        await ctx.runCheck();
        return { handled: true, state };
    } catch (error) {
        const message = (error as Error).message;
        ctx.post({ type: TRAINER_MSG.submitted, payload: { ok: false, error: message } });
        return { handled: true, error: message };
    }
}

function parseTrainer(kind: TrainerKind, text: string): TrainerState {
    return kind === 'trace' ? parseTrace(text) : parseParsons(text);
}

function tracePatch(text: string, answers: Record<string, string> | undefined): string {
    if (!answers || Object.keys(answers).length === 0) throw new Error('Нет ответов для отправки.');
    return patchTrace(text, answers);
}

function parsonsPatch(text: string, lines: TrainerMessage['lines']): string {
    const state = parseParsons(text);
    if (!state.supported) throw new Error(state.reason);
    if (!Array.isArray(lines) || lines.length !== state.lines.length) {
        throw new Error('Собранное тело не совпадает со строками из комментария.');
    }
    const byId = new Map(state.lines.map((line) => [line.id, line]));
    const used = new Set<number>();
    const arranged = lines.map((line) => {
        const id = typeof line.id === 'number' ? line.id : Number(line.id);
        const source = byId.get(id);
        if (!source || used.has(id)) throw new Error('Неизвестная строка в сборке.');
        used.add(id);
        const level = typeof line.level === 'number' ? line.level : Number(line.level);
        return { id, text: source.text, level: Number.isFinite(level) ? Math.max(0, Math.trunc(level)) : 0 };
    });
    return patchParsons(text, arranged);
}

function normalizeKind(kind: unknown): TrainerKind | null {
    return kind === 'trace' || kind === 'parsons' ? kind : null;
}

/** Pick the trainer kind from task tags (`trace` wins over `parsons`). */
export function trainerKindFromTags(tags: readonly string[] | null | undefined): TrainerKind | undefined {
    const lowered = (tags ?? []).map((tag) => String(tag).trim().toLowerCase());
    if (lowered.includes('trace')) return 'trace';
    if (lowered.includes('parsons')) return 'parsons';
    return undefined;
}
