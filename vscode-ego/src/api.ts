import type { AIAccount, AISession, AISubmission } from './aiTypes';
/** API client for ego-server (FastAPI).
 *
 * All HTTP calls go through this module. Token is stored in VSCode
 * SecretStorage and passed as Bearer header.
 */

export class EgoApiError extends Error {
    readonly status: number;
    readonly path: string;

    constructor(message: string, status: number, path: string) {
        super(message);
        this.name = 'EgoApiError';
        this.status = status;
        this.path = path;
    }
}

export function isAuthenticationError(error: unknown): error is EgoApiError {
    return error instanceof EgoApiError && (error.status === 401 || error.status === 403);
}

export interface TaskMeta {
    id: string;
    block: string;
    slug: string;
    task_id: string;
    title: string;
    level: string;
    tags: string[];
    version: string;
    content_hash: string;
    breaking: boolean;
    md_path: string;
    // Cogito catalog fields (absent on older servers).
    project_id?: string | null;
    project_name?: string | null;
    project_order?: number;
    folder_id?: string | null;
    folder_name?: string | null;
    folder_order?: number;
    /** Ordered lesson ids linked to this task. */
    theory?: string[];
    /** 1-based stage number when the task is a challenge stage (ADR-0018). */
    challenge_stage?: number | null;
}

export interface LessonMeta {
    id: string;
    project_id: string | null;
    folder_id: string | null;
    /** Folder code, same value as TaskMeta.block. */
    block: string;
    title: string;
    order: number;
    version: string;
    content_hash: string;
}

export interface LessonFull extends LessonMeta {
    body_md: string;
}

export interface TaskFull extends TaskMeta {
    statement_md: string;
    stub_py: string;
    solution_py: string;
}

export interface TestResultDTO {
    description: string;
    passed: boolean;
    expected_repr: string;
    actual_repr: string | null;
    error: string | null;
    /** Stage number of a challenge stage check (absent for an ordinary task). */
    stage?: number | null;
    /** Stage title of a challenge stage check. */
    stage_title?: string;
}

export interface CheckResponse {
    task_id: string;
    version: string;
    status: string; // passed | partial | failed | error | timeout | no_tests
    passed_tests: number;
    total_tests: number;
    solution_hash: string;
    results: TestResultDTO[];
    log: string;
    understanding?: { submission_id: string; status: string } | null;
}

export interface Hint {
    level: number;
    title: string;
    content: string;
}

export interface HintsResponse {
    task_id: string;
    hints: Hint[];
}

export interface ProgressRow {
    student_id: string;
    task_id: string;
    version: string;
    status: string;
    attempts: number;
    passed_tests: number;
    total_tests: number;
    last_run_at: string | null;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    role: string;
    username: string;
    user_id: string;
}

export interface AuthProviders { forgejo: boolean; local: boolean }
export interface ForgejoFlow { state: string; authorization_url: string; expires_in: number }

export class EgoApi {
    private serverUrl: string;
    private token: string | undefined;

    constructor(serverUrl: string, token?: string) {
        this.serverUrl = serverUrl.replace(/\/$/, '');
        this.token = token;
    }

    setToken(token: string | undefined): void {
        this.token = token;
    }

    private headers(): Record<string, string> {
        const h: Record<string, string> = { 'Content-Type': 'application/json' };
        if (this.token) {
            h['Authorization'] = `Bearer ${this.token}`;
        }
        return h;
    }

    private async request<T>(
        method: string,
        path: string,
        body?: unknown
    ): Promise<T> {
        const url = `${this.serverUrl}${path}`;
        const resp = await fetch(url, {
            method,
            headers: this.headers(),
            body: body ? JSON.stringify(body) : undefined,
            signal: path === '/ai/me' ? AbortSignal.timeout(10000) : path.startsWith('/ai/') ? AbortSignal.timeout(250000) : path.startsWith('/auth/') ? AbortSignal.timeout(15000) : undefined,
        });

        if (!resp.ok) {
            const data = await resp.json().catch(() => ({ detail: '' })) as { detail?: string };
            const message = resp.status === 401
                ? 'Нужно войти: выполни «Cogito: Войти».'
                : resp.status === 403
                  ? data.detail || 'Недостаточно прав для этого действия.'
                  : data.detail || (resp.status === 404 ? 'Не найдено' : `HTTP ${resp.status}`);
            throw new EgoApiError(message, resp.status, path);
        }
        return resp.json() as Promise<T>;
    }

    // === Auth ===

    async authProviders(): Promise<AuthProviders> {
        try {
            return await this.request<AuthProviders>('GET', '/auth/providers');
        } catch (error) {
            // Older ego-server releases only support username/password.
            if (error instanceof EgoApiError && error.status === 404) return { forgejo: false, local: true };
            throw error;
        }
    }

    async startForgejo(code_challenge: string, callback_uri: string): Promise<ForgejoFlow> {
        const flow = await this.request<ForgejoFlow>('POST', '/auth/forgejo/start', { code_challenge, client: 'vscode', callback_uri });
        if (new URL(flow.authorization_url).origin !== new URL(this.serverUrl).origin) {
            throw new Error('Адрес входа не совпадает с адресом сервера Cogito. Проверь EGO_PUBLIC_URL.');
        }
        return flow;
    }

    async exchangeForgejo(state: string, code_verifier: string, ticket: string): Promise<AuthResponse | { pending: true }> {
        return this.request('POST', '/auth/forgejo/exchange', { state, code_verifier, ticket });
    }

    async register(username: string, password: string, role: string = 'student'): Promise<AuthResponse> {
        return this.request<AuthResponse>('POST', '/auth/register', { username, password, role });
    }

    async login(username: string, password: string): Promise<AuthResponse> {
        return this.request<AuthResponse>('POST', '/auth/login', { username, password });
    }

    async me(): Promise<{ user_id: string; username: string; role: string }> {
        return this.request('GET', '/auth/me');
    }

    // === Tasks ===

    async listTasks(block?: string): Promise<TaskMeta[]> {
        const query = block ? `?block=${block}` : '';
        return this.request<TaskMeta[]>('GET', `/tasks${query}`);
    }

    async getTask(taskId: string, includeSolution: boolean = false): Promise<TaskFull> {
        const query = includeSolution ? '?include_solution=true' : '';
        return this.request<TaskFull>('GET', `/tasks/${taskId}${query}`);
    }

    // === Lessons (theory cards) ===

    /** Older servers have no /lessons: a 404 means "no lessons". */
    async listLessons(folderId?: string): Promise<LessonMeta[]> {
        const query = folderId ? `?folder_id=${encodeURIComponent(folderId)}` : '';
        try {
            return await this.request<LessonMeta[]>('GET', `/lessons${query}`);
        } catch (error) {
            if (error instanceof EgoApiError && error.status === 404) return [];
            throw error;
        }
    }

    async getLesson(lessonId: string): Promise<LessonFull> {
        return this.request<LessonFull>('GET', `/lessons/${encodeURIComponent(lessonId)}`);
    }

    // === Check ===

    async check(taskId: string, studentCode: string): Promise<CheckResponse> {
        return this.request<CheckResponse>('POST', '/check', {
            task_id: taskId,
            student_code: studentCode,
        });
    }

    /**
     * POST /check with `files` — one challenge stage (ADR-0018 D18.5).
     *
     * The server runs the tests of this stage and every earlier one; each
     * result row carries `stage` / `stage_title`.
     */
    async checkFiles(taskId: string, files: Record<string, string>): Promise<CheckResponse> {
        return this.request<CheckResponse>('POST', '/check', {
            task_id: taskId,
            files,
        });
    }

    // === Challenges (ADR-0018) ===

    /**
     * GET /challenges/<folder_id> — stages, workspace and starter files.
     * Older servers have no route: a 404 means "not a challenge / too old".
     */
    async getChallenge(folderId: string): Promise<ChallengeInfo | null> {
        try {
            return await this.request<ChallengeInfo>('GET', `/challenges/${encodeURIComponent(folderId)}`);
        } catch (error) {
            if (error instanceof EgoApiError && error.status === 404) return null;
            throw error;
        }
    }

    // === Hints ===

    async getHints(taskId: string, maxLevel?: number): Promise<HintsResponse> {
        const query = maxLevel ? `?level=${maxLevel}` : '';
        return this.request<HintsResponse>('GET', `/tasks/${taskId}/hints${query}`);
    }

    // === Progress ===

    async pushProgress(body: {
        task_id: string;
        version: string;
        solution_hash: string;
        status: string;
        log: string;
        passed_tests: number;
        total_tests: number;
    }): Promise<ProgressRow> {
        return this.request<ProgressRow>('POST', '/progress/push', body);
    }

    async getProgress(studentId: string): Promise<ProgressRow[]> {
        return this.request<ProgressRow[]>('GET', `/progress/${studentId}`);
    }

    async getAIAccount(): Promise<AIAccount> {
        return this.request('GET', '/ai/me');
    }

    async getAISubmissions(): Promise<AISubmission[]> {
        return this.request('GET', '/ai/submissions');
    }

    async createAISession(body: {
        task_id: string; mode: AISession['mode']; student_code: string; submission_id?: string;
    }): Promise<AISession> {
        return this.request('POST', '/ai/sessions', body);
    }

    async sendAIMessage(sessionId: string, text: string, requestId: string, studentCode?: string): Promise<AISession> {
        return this.request('POST', `/ai/sessions/${encodeURIComponent(sessionId)}/messages`, {
            text, request_id: requestId, student_code: studentCode,
        });
    }

    // === Health ===

    async health(): Promise<{ status: string; version: string }> {
        return this.request('GET', '/health');
    }

    // === Student cabinet (additive; older servers answer 404) ===

    /** GET /progress/me/understanding — evidence for already-checked solutions. */
    async getMyUnderstanding(): Promise<UnderstandingRow[]> {
        return this.request<UnderstandingRow[]>('GET', '/progress/me/understanding');
    }

    /** GET /ai/me — tutor access and budget (the `AIAccount` shape). */
    async getAiMe(): Promise<AIAccount> {
        return this.request<AIAccount>('GET', '/ai/me');
    }

    /** GET /progress/me — the current student's own progress rows. */
    async getMyProgress(): Promise<ProgressRow[]> {
        return this.request<ProgressRow[]>('GET', '/progress/me');
    }

    /**
     * GET /projects — project list with soft recommendations and the caller's
     * readiness. Older servers have no route: a 404 means "no projects info".
     */
    async listProjects(): Promise<ProjectInfo[]> {
        try {
            return await this.request<ProjectInfo[]>('GET', '/projects');
        } catch (error) {
            if (error instanceof EgoApiError && error.status === 404) return [];
            throw error;
        }
    }

    /**
     * GET /progress/me/breakdown?project=… — per-tag passed/total.
     * Older servers have no route: a 404 means "no breakdown".
     */
    async getMyBreakdown(project: string): Promise<Breakdown | null> {
        try {
            return await this.request<Breakdown>('GET', `/progress/me/breakdown?project=${encodeURIComponent(project)}`);
        } catch (error) {
            if (error instanceof EgoApiError && error.status === 404) return null;
            throw error;
        }
    }
}

// === Multi-file challenges (GET /challenges/<folder_id>, ADR-0018 D18.5) ===

/** File rules of a challenge project (`folder.yaml` → `workspace`). */
export interface ChallengeWorkspace {
    /** What `python <entry>` runs (default `main.py`). */
    entry: string;
    /** Glob patterns of the files collected for a submission. */
    include: string[];
    max_files: number;
    max_bytes: number;
}

/** One stage of a challenge: a full task plus the caller's progress on it. */
export interface ChallengeStage {
    /** Task id (`GET /tasks/<id>` opens its statement). */
    id: string;
    title: string;
    /** 1-based stage number. */
    number: number;
    order: number;
    level: string;
    version: string;
    /** new | passed | partial | failed | error | timeout (server vocabulary). */
    status: string;
    passed_tests: number;
    total_tests: number;
    /** The stage a first start goes to (server's first not-passed stage). */
    current: boolean;
}

/** GET /challenges/<folder_id> — one `kind: challenge` catalog folder. */
export interface ChallengeInfo {
    id: string;
    project_id: string;
    code: string;
    name: string;
    description: string;
    order: number;
    level: string | null;
    theory: string[];
    workspace: ChallengeWorkspace;
    stages: ChallengeStage[];
    /** Starting project `{path: content}` of `starter/` (may be empty). */
    starter: Record<string, string>;
}

// === Soft recommendations (GET /projects) ===

/** ``recommended_after`` from project.yaml — advisory, never enforced. */
export interface RecommendedAfter {
    project: string;
    min_passed: number;
    min_per_kind: number | null;
    note: string;
}

/** Caller's progress against a recommendation. */
export interface Readiness {
    met: boolean;
    passed: number;
    required: number;
    per_kind: Record<string, number>;
}

/** One row of GET /projects. */
export interface ProjectInfo {
    id: string;
    name: string;
    order: number;
    recommended_after: RecommendedAfter | null;
    readiness: Readiness | null;
}

export interface KindCount {
    passed: number;
    total: number;
}

/** GET /progress/me/breakdown (bug / modify / new + other tags). */
export interface Breakdown {
    project: string | null;
    kinds: Record<string, KindCount>;
    tags: Record<string, KindCount>;
}

// === Student cabinet contracts (shared worker contract, backward compatible) ===

/**
 * Catalog location fields added to TaskMeta. Older servers omit them, so every
 * consumer must treat a missing value as null / [].
 */
export interface TaskCatalogFields {
    project_id: string | null;
    project_name: string | null;
    project_order: number;
    folder_id: string | null;
    folder_name: string | null;
    folder_order: number;
    theory: string[];
}

/**
 * One row of GET /progress/me/understanding (see `submission_views` in
 * ego_server/ai.py): evidence for a checked solution, without code or billing.
 */
export interface UnderstandingRow {
    id: string;
    task_id: string;
    version: string;
    solution_hash: string;
    /** pending | confirmed | needs_review | active (server vocabulary). */
    understanding: string;
    evidence: { stage: string; quote: string }[];
    created_at: string;
}

/**
 * TaskMeta with the optional catalog fields. Optional types keep old-server
 * listings assignable to it directly.
 */
export type TaskMetaWithCatalog = TaskMeta & Partial<TaskCatalogFields>;

/**
 * Normalize catalog fields of a server task: a missing field is null / 0 / [],
 * as the shared contract requires for old servers.
 */
export function catalogFieldsOf(task: TaskMetaWithCatalog): TaskCatalogFields {
    return {
        project_id: task.project_id ?? null,
        project_name: task.project_name ?? null,
        project_order: task.project_order ?? 0,
        folder_id: task.folder_id ?? null,
        folder_name: task.folder_name ?? null,
        folder_order: task.folder_order ?? 0,
        theory: Array.isArray(task.theory) ? task.theory : [],
    };
}
