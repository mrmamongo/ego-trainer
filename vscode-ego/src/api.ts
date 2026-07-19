/** API client for ego-server (FastAPI).
 *
 * All HTTP calls go through this module. Token is stored in VSCode
 * SecretStorage and passed as Bearer header.
 */

import * as vscode from 'vscode';

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
        });

        if (resp.status === 401) {
            throw new Error('Authentication required. Run "Ego: Login" first.');
        }
        if (resp.status === 403) {
            throw new Error('Forbidden. Your role does not allow this action.');
        }
        if (resp.status === 404) {
            const data = await resp.json().catch(() => ({detail: ''})) as { detail?: string };
            throw new Error(data.detail || 'Not found');
        }
        if (!resp.ok) {
            const data = await resp.json().catch(() => ({detail: ''})) as { detail?: string };
            throw new Error(data.detail || `HTTP ${resp.status}`);
        }
        return resp.json() as Promise<T>;
    }

    // === Auth ===

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

    // === Check ===

    async check(taskId: string, studentCode: string): Promise<CheckResponse> {
        return this.request<CheckResponse>('POST', '/check', {
            task_id: taskId,
            student_code: studentCode,
        });
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

    // === Health ===

    async health(): Promise<{ status: string; version: string }> {
        return this.request('GET', '/health');
    }
}
