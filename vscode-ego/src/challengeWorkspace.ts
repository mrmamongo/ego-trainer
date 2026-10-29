/** Pure logic of multi-file challenges (ADR-0018 D18.6).
 *
 * No `vscode` import so it can be unit-tested with node --test: which local
 * files go into a submission, which starter files a first start writes,
 * `.cogito/challenge.json` and the stage list of the tree / stage panel.
 * The host side (VS Code commands, webview) only does I/O around these.
 */

import type { ChallengeInfo, ChallengeStage, ChallengeWorkspace, TestResultDTO } from './api';

// === Paths and file rules ===

/** Challenge sources live under `<Cogito workspace>/challenges/<folder_id>/`. */
export const CHALLENGES_DIR = 'challenges';
/** Marker of the project folder: `{id, server, stage}` (ADR-0018 D18.6). */
export const CHALLENGE_DIR = '.cogito';
export const CHALLENGE_FILE = 'challenge.json';

/** Library defaults, same as `ego.runner` (a server without `workspace`). */
export const DEFAULT_WORKSPACE: ChallengeWorkspace = {
    entry: 'main.py',
    include: ['*.py'],
    max_files: 20,
    max_bytes: 200_000,
};

/** Never sent, even when a pattern matches (`ego.runner._RESERVED_DIRS`). */
export const RESERVED_DIRS = ['.cogito', '__pycache__', '.venv', 'node_modules'];

/**
 * A catalog folder id becomes one path segment; an id that is not a plain
 * name is refused instead of being silently mangled into another folder.
 */
export function isValidChallengeId(id: unknown): id is string {
    return typeof id === 'string' && /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(id);
}

/** Challenge folder id of a stage task (`GET /tasks/<id>` has no stage field). */
export function challengeIdFromTaskId(taskId: string): string | undefined {
    const match = /^stage_\d{2,}_(.+)$/.exec(taskId.trim());
    return match ? match[1] : undefined;
}

/** `folder.yaml` → `workspace`, filled with the defaults of a missing field. */
export function workspaceOf(challenge: Pick<ChallengeInfo, 'workspace'> | undefined): ChallengeWorkspace {
    const raw = (challenge?.workspace ?? {}) as Partial<ChallengeWorkspace> | undefined;
    const include = Array.isArray(raw?.include) ? raw.include.map(String) : DEFAULT_WORKSPACE.include;
    const positive = (value: unknown, fallback: number) =>
        typeof value === 'number' && Number.isFinite(value) && value >= 1 ? Math.floor(value) : fallback;
    return {
        entry: typeof raw?.entry === 'string' && raw.entry.trim() ? raw.entry : DEFAULT_WORKSPACE.entry,
        include: include.length ? include : DEFAULT_WORKSPACE.include,
        max_files: positive(raw?.max_files, DEFAULT_WORKSPACE.max_files),
        max_bytes: positive(raw?.max_bytes, DEFAULT_WORKSPACE.max_bytes),
    };
}

function basename(path: string): string {
    const parts = path.split('/');
    return parts[parts.length - 1];
}

/** Glob of one `include` entry: `*` / `?` within a segment, `**` any depth. */
function globToRegExp(pattern: string): RegExp {
    let source = '';
    for (let i = 0; i < pattern.length; i += 1) {
        const char = pattern[i];
        if (char === '*' && pattern[i + 1] === '*') {
            const slash = pattern[i + 2] === '/' ? 3 : 2;
            source += slash === 3 ? '(?:.*/)?' : '.*';
            i += slash - 1;
        } else if (char === '*') {
            source += '[^/]*';
        } else if (char === '?') {
            source += '[^/]';
        } else {
            source += char.replace(/[.+^${}()|[\]\\]/g, '\\$&');
        }
    }
    return new RegExp(`^${source}$`);
}

/** `*.py` matches every basename; `data/*.json` — a whole path (as on the server). */
export function includeMatches(path: string, include: readonly string[]): boolean {
    const name = basename(path);
    return include.some((pattern) => {
        const regex = globToRegExp(pattern);
        return regex.test(path) || (!pattern.includes('/') && regex.test(name));
    });
}

/** Why a project-relative path is never collected (`..`, absolute, reserved). */
export function pathProblem(path: string): string | undefined {
    if (!path) return 'путь к файлу пустой';
    if (path.includes('\\')) return `путь \`${path}\` должен быть записан через \`/\``;
    if (path.startsWith('/') || /^[A-Za-z]:/.test(path)) return `путь \`${path}\` абсолютный`;
    const parts = path.split('/');
    if (parts.includes('..')) return `путь \`${path}\` выходит за папку проекта (\`..\` запрещён)`;
    if (parts.includes('') || parts.includes('.')) return `путь \`${path}\` некорректен: лишние \`/\` или сегменты \`.\``;
    const reserved = parts.filter((part) => RESERVED_DIRS.includes(part));
    if (reserved.length) return `путь \`${path}\`: папку \`${reserved[0]}/\` отправлять нельзя`;
    return undefined;
}

// === Which files to send ===

export type ChallengeFileKind =
    | 'matched'
    | 'not-included'
    | 'hidden'
    | 'reserved'
    | 'binary'
    | 'over-limit';

export interface ChallengeFileDecision {
    path: string;
    content: string;
    /** `matched` is sent; every other kind is skipped with `reason`. */
    kind: ChallengeFileKind;
    reason: string;
}

export interface ChallengeCollectInput {
    /** Relative POSIX paths of every file of the student's project folder. */
    paths: readonly string[];
    /** Content reader; a `Uint8Array` is binary and never sent. */
    read: (path: string) => Promise<string | Uint8Array>;
    workspace?: Partial<ChallengeWorkspace> | undefined;
}

export interface ChallengeCollectResult {
    /** The submission `{path: content}` (only `matched` files). */
    files: Record<string, string>;
    /** Every file with its decision, for a report. */
    decisions: ChallengeFileDecision[];
}

function utf8Size(text: string): number {
    return Buffer.byteLength(text, 'utf-8');
}

/**
 * Decide which local files go into a `POST /check` submission.
 *
 * Hidden directories/files (name starts with `.`), `.cogito/`,
 * `__pycache__/`, `.venv/` and `node_modules/` are skipped; a file must
 * match `include`. `max_files` / `max_bytes` (UTF-8 size) give Russian
 * errors — nothing is sent above a limit rather than a truncated project.
 * Files are taken in path order, so a report is stable.
 */
export async function collectChallengeFiles(input: ChallengeCollectInput): Promise<ChallengeCollectResult> {
    const workspace = workspaceOf({ workspace: input.workspace as ChallengeWorkspace });
    const decisions: ChallengeFileDecision[] = [];
    const candidates: ChallengeFileDecision[] = [];
    for (const raw of [...input.paths].sort()) {
        const path = raw.replace(/\\/g, '/');
        const skip = (kind: ChallengeFileKind, reason: string) =>
            decisions.push({ path, content: '', kind, reason });
        if (path.split('/').slice(0, -1).some((part) => RESERVED_DIRS.includes(part))) {
            skip('reserved', `путь \`${path}\`: эту папку отправлять нельзя (${RESERVED_DIRS.join(', ')})`);
            continue;
        }
        if (path.includes('\\') || pathProblem(path)) {
            // Root-relative scan output uses `\` on Windows: not a project path.
            skip('not-included', pathProblem(path) ?? `путь \`${path}\` должен быть записан через \`/\``);
            continue;
        }
        if (path.split('/').some((part) => part.startsWith('.'))) {
            skip('hidden', 'скрытая папка или файл — не отправляется');
            continue;
        }
        if (!includeMatches(path, workspace.include)) {
            skip('not-included', `не подходит под include (${workspace.include.join(', ')})`);
            continue;
        }
        let content: string | Uint8Array;
        try {
            content = await input.read(path);
        } catch (error) {
            skip('binary', `не удалось прочитать файл: ${(error as Error).message}`);
            continue;
        }
        if (typeof content !== 'string') {
            skip('binary', 'двоичный файл — не отправляется');
            continue;
        }
        candidates.push({ path, content, kind: 'matched', reason: '' });
    }

    const limits: string[] = [];
    if (candidates.length > workspace.max_files) {
        limits.push(
            `в проекте ${candidates.length} файлов — это больше лимита ${workspace.max_files} ` +
            `(include: ${workspace.include.join(', ')}). Убери лишние файлы или сузь include.`
        );
    }
    const total = candidates.reduce((sum, file) => sum + utf8Size(file.content), 0);
    if (total > workspace.max_bytes) {
        limits.push(
            `проект занимает ${total} байт — это больше лимита ${workspace.max_bytes}. ` +
            'Убери лишние файлы или сузь include.'
        );
    }
    if (limits.length) {
        const over: ChallengeCollectResult = {
            files: {},
            decisions: [
                ...decisions,
                ...candidates.map((file) => ({ ...file, kind: 'over-limit' as const, reason: limits.join(' ') })),
            ],
        };
        throw new ChallengeLimitError(limits.join('\n'), over.decisions);
    }

    const files: Record<string, string> = {};
    for (const file of candidates) files[file.path] = file.content;
    return { files, decisions: [...decisions, ...candidates] };
}

/** The project is over `max_files` / `max_bytes`: nothing was collected. */
export class ChallengeLimitError extends Error {
    readonly decisions: ChallengeFileDecision[];

    constructor(message: string, decisions: ChallengeFileDecision[]) {
        super(message);
        this.name = 'ChallengeLimitError';
        this.decisions = decisions;
    }
}

// === Starter files (never overwrite) ===

export interface StarterPlan {
    /** Files to write (`{path: content}`, validated starter paths only). */
    create: Record<string, string>;
    /** Existing files left untouched. */
    skipped: string[];
    /** Starter paths refused (absolute, `..`, reserved) with the reason. */
    rejected: Array<{ path: string; reason: string }>;
}

/**
 * Plan the first write of a starter project: a file that already exists is
 * never overwritten (ADR-0018 D18.6), whatever its content.
 */
export function planStarter(
    starter: Record<string, string> | undefined,
    existing: Iterable<string>
): StarterPlan {
    const present = new Set([...existing].map((path) => path.replace(/\\/g, '/')));
    const plan: StarterPlan = { create: {}, skipped: [], rejected: [] };
    for (const [raw, content] of Object.entries(starter ?? {})) {
        const path = raw.replace(/\\/g, '/');
        const problem = pathProblem(path);
        if (problem) {
            plan.rejected.push({ path, reason: problem });
            continue;
        }
        if (present.has(path)) {
            plan.skipped.push(path);
            continue;
        }
        plan.create[path] = content;
    }
    return plan;
}

// === `.cogito/challenge.json` ===

export interface ChallengeMarker {
    /** Challenge folder id. */
    id: string;
    /** Server address the project was started from. */
    server: string;
    /** Stage number the panel opens first. */
    stage: number;
}

/** Read a stored marker; `undefined` for anything that is not one. */
export function parseChallengeMarker(raw: string): ChallengeMarker | undefined {
    let data: unknown;
    try {
        data = JSON.parse(raw);
    } catch {
        return undefined;
    }
    if (!data || typeof data !== 'object') return undefined;
    const marker = data as Partial<ChallengeMarker>;
    if (typeof marker.id !== 'string' || !marker.id) return undefined;
    const stage = typeof marker.stage === 'number' && Number.isFinite(marker.stage) ? Math.trunc(marker.stage) : 0;
    return { id: marker.id, server: typeof marker.server === 'string' ? marker.server : '', stage };
}

/** The marker file text (2-space JSON, trailing newline). */
export function serializeChallengeMarker(marker: ChallengeMarker): string {
    return JSON.stringify({ id: marker.id, server: marker.server, stage: marker.stage }, null, 2) + '\n';
}

// === Stages ===

/** Stages in stage order (the number is the stage; `order` is a tie-break). */
export function orderedStages(stages: readonly ChallengeStage[] | undefined): ChallengeStage[] {
    return [...(stages ?? [])].sort((a, b) => a.number - b.number || a.order - b.order);
}

/**
 * The stage the panel opens and highlights: the first one that is not
 * passed (soft — every stage stays open), else the last one.
 */
export function nextStageNumber(stages: readonly ChallengeStage[] | undefined): number {
    const ordered = orderedStages(stages);
    const firstOpen = ordered.find((stage) => stage.status !== 'passed');
    if (firstOpen) return firstOpen.number;
    return ordered.length ? ordered[ordered.length - 1].number : 1;
}

/** The stage with `number`, or the `nextStageNumber` one when it is gone. */
export function stageByNumber(
    stages: readonly ChallengeStage[] | undefined,
    number: number | undefined
): ChallengeStage | undefined {
    const ordered = orderedStages(stages);
    return ordered.find((stage) => stage.number === number)
        ?? ordered.find((stage) => stage.number === nextStageNumber(ordered));
}

/** The stage after `number` (in order); `undefined` after the last one. */
export function stageAfter(
    stages: readonly ChallengeStage[] | undefined,
    number: number
): ChallengeStage | undefined {
    return orderedStages(stages).find((stage) => stage.number > number);
}

export const STAGE_STATUS_LABELS: Record<string, string> = {
    passed: 'пройден',
    partial: 'частично',
    failed: 'не пройден',
    error: 'ошибка',
    timeout: 'таймаут',
    new: 'не начат',
};

export function stageStatusLabel(status: string): string {
    return STAGE_STATUS_LABELS[status] ?? status;
}

/** Stage icon/decoration of one stage line (`✓ 02 · SET/GET — пройден`). */
export function stageLine(stage: ChallengeStage, highlighted: boolean): string {
    const icon = stage.status === 'passed' ? '✓' : '○';
    const current = highlighted ? ' ▶' : '';
    return `${icon} ${String(stage.number).padStart(2, '0')} · ${stage.title} — ${stageStatusLabel(stage.status)}${current}`;
}

// === Results grouped by stage ===

export interface StageResultGroup {
    /** `null` for rows without a stage (an ordinary task or an old server). */
    stage: number | null;
    title: string;
    results: TestResultDTO[];
    passed: number;
    total: number;
    /** Every row of the group passed. */
    passedAll: boolean;
}

/** Group check results by stage, stage 1 first; stage-less rows last. */
export function groupResultsByStage(results: readonly TestResultDTO[] | undefined): StageResultGroup[] {
    const groups = new Map<number | null, StageResultGroup>();
    for (const row of results ?? []) {
        const stage = typeof row.stage === 'number' ? row.stage : null;
        let group = groups.get(stage);
        if (!group) {
            group = { stage, title: row.stage_title || '', results: [], passed: 0, total: 0, passedAll: false };
            groups.set(stage, group);
        }
        group.results.push(row);
        group.total += 1;
        if (row.passed) group.passed += 1;
        if (!group.title && row.stage_title) group.title = row.stage_title;
    }
    const out = [...groups.values()];
    for (const group of out) group.passedAll = group.total > 0 && group.passed === group.total;
    return out.sort((a, b) => (a.stage ?? Number.MAX_SAFE_INTEGER) - (b.stage ?? Number.MAX_SAFE_INTEGER));
}

/** Header of one stage group in the results panel. */
export function stageGroupHeader(group: StageResultGroup): string {
    if (group.stage === null) return 'Результаты';
    const title = group.title ? `: ${group.title}` : '';
    const verdict = group.passedAll ? 'пройден' : 'не пройден';
    return `Этап ${group.stage}${title} — ${group.passed}/${group.total}, ${verdict}`;
}

// === Stage panel data ===

/** Stage panel block of `taskView.setData` (mirrors `webview/shared/types.ts`). */
export interface ChallengeViewInfo {
    challenge_id: string;
    name: string;
    stage: number;
    folder: string;
    current_stage: number;
    stages: Array<{
        number: number;
        id: string;
        title: string;
        status: string;
        status_label: string;
        passed_tests: number;
        total_tests: number;
    }>;
    entry: string;
}

/** The stage panel of one stage: every stage with its status, `stage` on screen. */
export function challengeViewInfo(
    challenge: ChallengeInfo,
    stage: number,
    folder: string
): ChallengeViewInfo {
    const ordered = orderedStages(challenge.stages);
    return {
        challenge_id: challenge.id,
        name: challenge.name,
        stage,
        folder,
        current_stage: nextStageNumber(ordered),
        stages: ordered.map((item) => ({
            number: item.number,
            id: item.id,
            title: item.title,
            status: item.status,
            status_label: stageStatusLabel(item.status),
            passed_tests: item.passed_tests,
            total_tests: item.total_tests,
        })),
        entry: workspaceOf(challenge).entry,
    };
}

// === Stage panel navigation ===

export interface StageNavMessage {
    type: 'challenge.stage';
    challengeId: string;
    stage: number;
}

/** Host message of a stage click in the stage panel; `null` if malformed. */
export function parseStageNav(message: unknown): StageNavMessage | null {
    if (!message || typeof message !== 'object') return null;
    const msg = message as Partial<StageNavMessage>;
    if (msg.type !== 'challenge.stage' || typeof msg.challengeId !== 'string') return null;
    const stage = typeof msg.stage === 'number' ? msg.stage : Number(msg.stage);
    if (!Number.isInteger(stage) || stage < 1) return null;
    return { type: 'challenge.stage', challengeId: msg.challengeId, stage };
}
